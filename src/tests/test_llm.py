from typing import cast

import pytest

from pilot_kit import llm
from pilot_kit.llm import chatgpt_signed_in as real_chatgpt_signed_in


class Recorder:
    def __init__(self, **kwargs):
        self.kwargs = kwargs


def kwargs_of(model) -> dict:
    """The factory returns a chat model type; the tests replace it with `Recorder`."""
    return cast(Recorder, model).kwargs


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    for name in (
        "LLM_PROVIDER",
        "LLM_MODEL",
        "LLM_TIMEOUT",
        "LLM_ENABLE_THINKING",
        "NVIDIA_API_KEY",
        "NVIDIA_BASE_URL",
    ):
        monkeypatch.delenv(name, raising=False)
    monkeypatch.setattr(llm, "load_env", lambda: None)
    monkeypatch.setattr(llm, "chatgpt_signed_in", lambda: False)
    monkeypatch.setattr(llm, "ChatNVIDIA", Recorder)


def test_provider_priority_order_is_openai_then_nim():
    assert llm.PROVIDERS == ("openai", "nim")


def test_auto_provider_prefers_chatgpt_then_nim(monkeypatch):
    assert llm.auto_provider() == "nim"
    monkeypatch.setattr(llm, "chatgpt_signed_in", lambda: True)
    assert llm.auto_provider() == "openai"


def test_explicit_provider_beats_the_automatic_choice(monkeypatch):
    monkeypatch.setattr(llm, "chatgpt_signed_in", lambda: True)
    monkeypatch.setenv("LLM_PROVIDER", "nim")
    assert llm.provider_name() == "nim"


def test_empty_provider_falls_back_to_the_automatic_choice(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "")
    assert llm.provider_name() == "nim"


def test_nim_passes_key_base_url_timeout_and_default_model(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "nim")
    monkeypatch.setenv("NVIDIA_API_KEY", "nvapi-test")
    monkeypatch.setenv("NVIDIA_BASE_URL", "http://0.0.0.0:8000/v1")
    assert kwargs_of(llm.make_chat_model()) == {
        "model": "nvidia/nemotron-3.5-lightning-30b-a3b",
        "timeout": 180.0,
        "api_key": "nvapi-test",
        "base_url": "http://0.0.0.0:8000/v1",
    }


def test_a_placeholder_nvidia_key_is_not_sent(monkeypatch):
    monkeypatch.setenv("NVIDIA_API_KEY", "nvapi-xxxxxxxxxxxxxxxxxxxxxxxxxxxx")
    assert "api_key" not in kwargs_of(llm.make_chat_model(provider="nim"))


def test_model_and_timeout_come_from_the_environment(monkeypatch):
    monkeypatch.setenv("LLM_MODEL", "qwen/qwen3-8b")
    monkeypatch.setenv("LLM_TIMEOUT", "30")
    kwargs = kwargs_of(llm.make_chat_model(provider="nim"))
    assert kwargs["model"] == "qwen/qwen3-8b"
    assert kwargs["timeout"] == 30.0


def test_thinking_off_is_sent_to_nim_only_when_set(monkeypatch):
    assert "model_kwargs" not in kwargs_of(llm.make_chat_model(provider="nim"))
    monkeypatch.setenv("LLM_ENABLE_THINKING", "false")
    assert kwargs_of(llm.make_chat_model(provider="nim"))["model_kwargs"] == {
        "chat_template_kwargs": {"enable_thinking": False}
    }


def test_unknown_provider_is_rejected(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "ollama")
    with pytest.raises(ValueError, match="LLM_PROVIDER"):
        llm.make_chat_model()
    assert llm.model_name("ollama") == ""


def test_openai_requires_a_chatgpt_sign_in():
    with pytest.raises(RuntimeError, match="chatgpt_login"):
        llm.make_chat_model(provider="openai")


def test_openai_uses_the_codex_oauth_model_without_an_api_key(monkeypatch):
    from langchain_openai.chat_models import codex

    monkeypatch.setattr(llm, "chatgpt_signed_in", lambda: True)
    monkeypatch.setattr(codex, "_ChatOpenAICodex", Recorder)
    monkeypatch.setenv("OPENAI_API_KEY", "must-not-be-used")
    assert kwargs_of(llm.make_chat_model(provider="openai")) == {
        "model": "gpt-5.5",
        "timeout": 180.0,
        "max_retries": 2,
    }


def test_an_empty_token_file_is_not_a_sign_in(tmp_path, monkeypatch):
    token = tmp_path / "chatgpt-auth.json"
    monkeypatch.setattr(llm, "chatgpt_store_path", lambda: token)
    assert real_chatgpt_signed_in() is False
    token.write_text("")
    assert real_chatgpt_signed_in() is False
    token.write_text("{}")
    assert real_chatgpt_signed_in() is True


def test_chatgpt_models_are_reduced_to_id_name_and_visibility():
    from pilot_kit.chatgpt_models import parse_models

    payload = {
        "models": [
            {"slug": "model-a", "display_name": "Model A", "visibility": "list", "extra": 1},
            {"id": "model-b"},
            "not a dict",
        ]
    }
    assert parse_models(payload) == [
        {"id": "model-a", "name": "Model A", "visibility": "list"},
        {"id": "model-b", "name": "", "visibility": ""},
    ]

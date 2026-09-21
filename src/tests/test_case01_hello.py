import httpx2
import openai
import pytest
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage, HumanMessage

from case01_hello.graph import build_graph
from pilot_kit.retry import DEFAULT_ATTEMPTS


async def test_the_graph_answers_with_the_injected_model():
    llm = GenericFakeChatModel(messages=iter([AIMessage("Hello!")]))
    result = await build_graph(llm=llm).ainvoke({"messages": [HumanMessage("hi")]})
    assert result["messages"][-1].content == "Hello!"


async def test_a_transient_model_error_is_retried(monkeypatch):
    async def no_sleep(_seconds):
        return None

    monkeypatch.setattr("pilot_kit.retry.asyncio.sleep", no_sleep)

    class FlakyLLM:
        calls = 0

        async def ainvoke(self, *_args, **_kwargs):
            FlakyLLM.calls += 1
            if FlakyLLM.calls == 1:
                raise ConnectionResetError("reset by peer")
            return AIMessage("recovered")

    result = await build_graph(llm=FlakyLLM()).ainvoke({"messages": [HumanMessage("hi")]})  # ty: ignore[invalid-argument-type]
    assert result["messages"][-1].content == "recovered"
    assert FlakyLLM.calls == 2


class CountingLLM:
    """A chat model that fails with the queued errors, then answers. Counts underlying calls."""

    def __init__(self, *errors: Exception) -> None:
        self.errors = list(errors)
        self.calls = 0

    async def ainvoke(self, *_args, **_kwargs):
        self.calls += 1
        if self.errors:
            raise self.errors.pop(0)
        return AIMessage("recovered")


async def run_graph(llm: CountingLLM):
    graph = build_graph(llm=llm)  # ty: ignore[invalid-argument-type]
    return await graph.ainvoke({"messages": [HumanMessage("hi")]})


async def test_a_transient_error_costs_exactly_the_default_number_of_model_calls(monkeypatch):
    async def no_sleep(_seconds):
        return None

    monkeypatch.setattr("pilot_kit.retry.asyncio.sleep", no_sleep)
    llm = CountingLLM(*[TimeoutError("slow")] * 10)
    with pytest.raises(TimeoutError):
        await run_graph(llm)
    assert llm.calls == DEFAULT_ATTEMPTS


async def test_a_permanent_error_costs_exactly_one_model_call():
    request = httpx2.Request("POST", "https://example.invalid")
    error = openai.AuthenticationError(
        "bad key", response=httpx2.Response(401, request=request), body=None
    )
    llm = CountingLLM(error)
    with pytest.raises(openai.AuthenticationError):
        await run_graph(llm)
    assert llm.calls == 1

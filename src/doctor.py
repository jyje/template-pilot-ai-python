"""Diagnostics: environment and the chat model backend.

Usage: uv run python doctor.py

Add a section for your own product's API here (see `product_section`) as soon as the pilot has one.
"""

from __future__ import annotations

import asyncio
import os
import sys

from langchain_core.messages import HumanMessage

from pilot_kit.env import env_is_set, load_env
from pilot_kit.llm import (
    PROVIDERS,
    chatgpt_recovery_hint,
    chatgpt_signed_in,
    chatgpt_store_path,
    make_chat_model,
    model_name,
    provider_name,
)
from pilot_kit.retry import with_retries

load_env()
# Keep LangSmith out of diagnostics runs.
os.environ["LANGSMITH_TRACING"] = "false"

PASS, FAIL, SKIP = "  [PASS]", "  [FAIL]", "  [SKIP]"
SEP = "-" * 52


def section(title: str) -> None:
    print(f"\n{SEP}\n {title}\n{SEP}")


def check(label: str, ok: bool, detail: str = "") -> bool:
    print(f"{PASS if ok else FAIL} {label}" + (f"\n         {detail}" if detail else ""))
    return ok


def skip(label: str, why: str) -> None:
    print(f"{SKIP} {label}\n         {why}")


def env_section(provider: str) -> bool:
    section("1. Environment")
    ok = check(
        f"LLM_PROVIDER is one of {PROVIDERS}",
        provider in PROVIDERS,
        f"value: {provider}" + ("" if os.getenv("LLM_PROVIDER") else " (auto: first configured)"),
    )
    if provider == "openai":
        signed_in = chatgpt_signed_in()
        ok &= check(
            "Signed in to ChatGPT (no OPENAI_API_KEY needed)",
            signed_in,
            str(chatgpt_store_path()) if signed_in else chatgpt_recovery_hint(),
        )
    elif provider == "nim":
        hosted = env_is_set("NVIDIA_API_KEY")
        self_hosted = bool(os.getenv("NVIDIA_BASE_URL"))
        ok &= check(
            "NVIDIA_API_KEY (hosted catalog) or NVIDIA_BASE_URL (self-hosted NIM)",
            hosted or self_hosted,
            "hosted: key set" if hosted else f"self-hosted: {os.getenv('NVIDIA_BASE_URL')}",
        )
    check("LLM_MODEL", True, model_name(provider) if provider in PROVIDERS else "n/a")
    return ok


def product_section() -> bool:
    """Replace with a live call to your product's API, skipped when its key is not set."""
    section("2. Your product")
    skip("Live call", "not implemented yet: add one call to your product's API here")
    return True


def llm_section(provider: str) -> bool:
    section("3. Chat model backend")
    if provider not in PROVIDERS:
        skip("Basic inference", "invalid LLM_PROVIDER")
        return True
    if provider == "openai" and not chatgpt_signed_in():
        skip("Basic inference", "not signed in to ChatGPT")
        return True
    if provider == "nim" and not (env_is_set("NVIDIA_API_KEY") or os.getenv("NVIDIA_BASE_URL")):
        skip("Basic inference", "no NVIDIA_API_KEY or NVIDIA_BASE_URL")
        return True
    try:
        chat = make_chat_model()  # built once, outside the retry: a bad setup will not fix itself
        reply = asyncio.run(
            with_retries(lambda: chat.ainvoke([HumanMessage("Reply with the single word: ok")]))
        )
    except Exception as exc:  # noqa: BLE001 - diagnostics report every failure kind
        return check("Basic inference", False, f"{type(exc).__name__}: {exc}")
    return check("Basic inference", bool(reply.text), f"reply: {reply.text.strip()[:60]!r}")


def main() -> int:
    provider = provider_name()
    results = [env_section(provider), product_section(), llm_section(provider)]
    print(f"\n{SEP}\n {'All checks passed' if all(results) else 'Some checks failed'}\n{SEP}")
    return 0 if all(results) else 1


if __name__ == "__main__":
    sys.exit(main())

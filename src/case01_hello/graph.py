"""Case 01: the smallest useful graph. One node calls the chat model.

This is a placeholder to copy from. Replace it with the pilot's real graph, keeping the habits:

- backends resolve lazily, so importing the module needs no credentials and tests inject fakes;
- the chat model is built once, off the event loop (the NIM client does blocking I/O on creation);
- only the model call is retried, never a whole graph run.

Try it in LangGraph Studio with `uv run --extra studio langgraph dev`.
"""

from __future__ import annotations

import asyncio
from typing import Annotated, TypedDict

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import AnyMessage, SystemMessage
from langgraph.graph import END, START, StateGraph
from langgraph.graph.message import add_messages

from pilot_kit.llm import make_chat_model
from pilot_kit.retry import with_retries

SYSTEM_PROMPT = "You are a concise assistant. Answer in one or two sentences."


class HelloState(TypedDict):
    messages: Annotated[list[AnyMessage], add_messages]


def build_graph(*, llm: BaseChatModel | None = None):
    """Build the graph. Pass `llm` in tests; otherwise the configured provider is used."""
    model = llm
    model_lock = asyncio.Lock()

    async def chat_model() -> BaseChatModel:
        nonlocal model
        async with model_lock:
            if model is None:
                model = await asyncio.to_thread(make_chat_model)
            return model

    async def respond(state: HelloState) -> dict:
        chat = await chat_model()
        reply = await with_retries(
            lambda: chat.ainvoke([SystemMessage(SYSTEM_PROMPT), *state["messages"]])
        )
        return {"messages": [reply]}

    # ty does not yet accept a TypedDict class where langgraph wants its state type var.
    builder = StateGraph(HelloState)  # ty: ignore[invalid-argument-type]
    builder.add_node("respond", respond)
    builder.add_edge(START, "respond")
    builder.add_edge("respond", END)
    return builder.compile()


graph = build_graph()

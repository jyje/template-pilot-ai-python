"""Run Case 01 on a message and print the reply.

Usage: uv run python -m case01_hello.main ["your own message"]
"""

from __future__ import annotations

import asyncio
import sys

from langchain_core.messages import HumanMessage

from case01_hello.graph import graph
from pilot_kit.env import load_env
from pilot_kit.llm import model_name, provider_name
from pilot_kit.text import message_text

DEFAULT_MESSAGE = "Say hello and tell me which model you are."


async def main(message: str) -> None:
    load_env()
    print(f"LLM: {provider_name()} / {model_name()}")
    print(f"\n> {message}")
    result = await graph.ainvoke({"messages": [HumanMessage(message)]})
    print(f"  {message_text(result['messages'][-1])}")


if __name__ == "__main__":
    asyncio.run(main(" ".join(sys.argv[1:]) or DEFAULT_MESSAGE))

from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage, HumanMessage

from case01_hello.graph import build_graph


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

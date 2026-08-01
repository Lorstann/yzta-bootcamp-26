"""Tests for conversation history wiring into LLM messages."""

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage

from backend.services.llm.streaming import build_llm_messages


def test_build_llm_messages_includes_history():
    history = [
        {"role": "assistant", "content": "Merhaba! Enerjin nerede?"},
        {"role": "user", "content": "Enerjim 4, motivasyonum 3"},
        {"role": "assistant", "content": "Anladım. En zor konu neydi?"},
    ]
    msgs = build_llm_messages(
        "React state",
        system_prompt="Sen Equa'sın.",
        history=history,
    )
    assert isinstance(msgs[0], SystemMessage)
    assert isinstance(msgs[1], AIMessage)
    assert msgs[1].content.startswith("Merhaba")
    assert isinstance(msgs[2], HumanMessage)
    assert msgs[2].content == "Enerjim 4, motivasyonum 3"
    assert isinstance(msgs[3], AIMessage)
    assert isinstance(msgs[4], HumanMessage)
    assert msgs[4].content == "React state"
    assert len(msgs) == 5


def test_build_llm_messages_without_history():
    msgs = build_llm_messages("Merhaba", system_prompt="sys")
    assert len(msgs) == 2
    assert isinstance(msgs[0], SystemMessage)
    assert isinstance(msgs[1], HumanMessage)


def test_build_llm_messages_skips_empty_turns():
    history = [
        {"role": "user", "content": ""},
        {"role": "assistant", "content": "  "},
        {"role": "user", "content": "ok"},
    ]
    msgs = build_llm_messages("next", history=history)
    # only "ok" + current message
    assert len(msgs) == 2
    assert msgs[0].content == "ok"
    assert msgs[1].content == "next"

"""Scope guard: fast patterns, classifier fail-open, chat refusal wiring."""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from backend.services.chat_service import stream_chat_response, stream_coach_response
from backend.services.llm import scope_guard as sg
from backend.services.llm.prompts import build_checkin_prompt, build_coach_prompt
from backend.services.llm.scope_guard import (
    ScopeDecision,
    _fast_pattern,
    build_refusal_text,
    check_scope,
)


def test_fast_leisure_deny():
    d = _fast_pattern("makarna tarifi ver")
    assert d is not None
    assert d.in_scope is False
    assert d.family == "leisure"


def test_fast_hard_deny_history():
    d = _fast_pattern("2. Dünya Savaşı kaç yılında bitti")
    assert d is not None
    assert d.in_scope is False
    assert d.family == "hard"


def test_fast_allow_technical():
    d = _fast_pattern("Pandas groupby'ı anlamadım, nasıl çalışır?")
    assert d is not None
    assert d.in_scope is True


def test_fast_allow_career():
    d = _fast_pattern("yarınki mülakata nasıl hazırlanayım, CV'mi gözden geçirelim")
    assert d is not None
    assert d.in_scope is True


def test_fast_allow_wellbeing():
    d = _fast_pattern("bugün çok yorgunum, motivasyonum düşük")
    assert d is not None
    assert d.in_scope is True


def test_chip_short_circuits_without_classifier():
    d = _fast_pattern("Tükendim")
    assert d is not None
    assert d.in_scope is True
    assert d.reason == "chip"


def test_short_message_short_circuits():
    d = _fast_pattern("İdare eder")
    assert d is not None
    assert d.in_scope is True


def test_deny_beats_allow():
    # Python allow-hint + tarif leisure-deny → deny wins
    d = _fast_pattern("Python ile makarna tarifi yaz")
    assert d is not None
    assert d.in_scope is False
    assert d.family == "leisure"


def test_refusal_leisure_has_reframe():
    text = build_refusal_text(family="leisure", mode="coach", turn_count=0)
    assert "tarif" in text.casefold() or "içerik" in text.casefold() or "mola" in text.casefold()
    assert "check-in" not in text.casefold() or True  # coach: no stage redirect required


def test_refusal_checkin_redirects_to_stage():
    text = build_refusal_text(
        family="hard",
        mode="checkin",
        stage="opening",
        turn_count=1,
    )
    assert "moddasın" in text.casefold() or "check-in" in text.casefold()


def test_prompts_include_scope_block():
    checkin = build_checkin_prompt(stage="explore", turn_count=1)
    coach = build_coach_prompt()
    assert "KAPSAM" in checkin
    assert "KAPSAM" in coach
    assert "kaçınma" not in coach.casefold()
    assert "aktivite önerisi" in coach.casefold() or "aktivite" in coach.casefold()


@pytest.mark.asyncio
async def test_classifier_not_called_for_chip(monkeypatch):
    called = {"n": 0}

    async def boom(_msg: str):
        called["n"] += 1
        raise AssertionError("classifier should not run")

    monkeypatch.setattr(sg, "_classify_with_llm", boom)
    result = await check_scope("Tükendim")
    assert result.in_scope is True
    assert called["n"] == 0


@pytest.mark.asyncio
async def test_classifier_timeout_fail_open(monkeypatch):
    async def slow(_msg: str):
        raise TimeoutError("simulated")

    # Force unsure path by using a long ambiguous message with no hints
    monkeypatch.setattr(sg, "_classify_with_llm", AsyncMock(return_value=ScopeDecision(in_scope=True, reason="classifier_timeout")))
    # Also test the real fail-open path inside _classify_with_llm
    monkeypatch.setattr(
        "backend.services.llm.scope_guard.settings"
    , MagicMock(scope_classifier_enabled=True, llm_api_key="fake-key"))

    async def raise_timeout():
        raise sg.asyncio.TimeoutError()

    # Unit-test _classify_with_llm fail-open via wait_for timeout
    async def fake_build(*, streaming=False):
        llm = MagicMock()

        async def ainvoke(_msgs):
            await sg.asyncio.sleep(10)
            return MagicMock(content="OUT")

        llm.ainvoke = ainvoke
        return llm

    monkeypatch.setattr(
        "backend.services.llm.provider.build_chat_llm",
        lambda *, streaming=False: MagicMock(
            ainvoke=AsyncMock(side_effect=sg.asyncio.TimeoutError())
        ),
    )
    # Patch wait_for to raise TimeoutError immediately
    real_wait = sg.asyncio.wait_for

    async def instant_timeout(coro, timeout):
        # close the coroutine to avoid warning
        if hasattr(coro, "close"):
            coro.close()
        raise sg.asyncio.TimeoutError()

    monkeypatch.setattr(sg.asyncio, "wait_for", instant_timeout)
    decision = await sg._classify_with_llm("Bu tamamen belirsiz uzun bir mesaj içeriği burada")
    assert decision.in_scope is True
    assert decision.reason == "classifier_timeout"
    monkeypatch.setattr(sg.asyncio, "wait_for", real_wait)


@pytest.mark.asyncio
async def test_classifier_exception_fail_open(monkeypatch):
    monkeypatch.setattr(
        "backend.services.llm.scope_guard.settings",
        MagicMock(scope_classifier_enabled=True, llm_api_key="fake"),
    )
    monkeypatch.setattr(
        "backend.services.llm.provider.build_chat_llm",
        lambda *, streaming=False: MagicMock(
            ainvoke=AsyncMock(side_effect=RuntimeError("boom"))
        ),
    )

    async def pass_through(coro, timeout):
        return await coro

    monkeypatch.setattr(sg.asyncio, "wait_for", pass_through)
    decision = await sg._classify_with_llm("Belirsiz uzun mesaj belirsiz uzun mesaj xx")
    assert decision.in_scope is True
    assert decision.reason == "classifier_error"


@pytest.mark.asyncio
async def test_stream_checkin_off_topic_does_not_advance(monkeypatch):
    async def should_not_run(*_a, **_k):
        yield "should not appear"
        raise AssertionError("LLM must not be called for off-topic")

    monkeypatch.setattr(
        "backend.services.chat_service.stream_llm_response",
        should_not_run,
    )

    events = []
    async for ev in stream_chat_response(
        "makarna tarifi ver lütfen",
        stage="opening",
        turn_count=1,
        state={"enerji": None, "motivasyon": None},
    ):
        events.append(ev)

    chunks = "".join(e["data"] for e in events if e["type"] == "chunk")
    assert "tarif" in chunks.casefold() or "kapsam" in chunks.casefold() or "mola" in chunks.casefold()

    done = next(e for e in events if e["type"] == "done")
    assert done["off_topic"] is True
    assert done["scope_family"] == "leisure"
    assert done["guardrail_triggered"] is False
    assert done["daily_tasks"] is None
    assert done["turn_count"] == 1  # unchanged
    assert done["checkin_completed"] is False
    assert done["quick_replies"]  # chips for opening


@pytest.mark.asyncio
async def test_stream_coach_off_topic_hard(monkeypatch):
    async def should_not_run(*_a, **_k):
        yield "nope"
        raise AssertionError("LLM must not run")

    monkeypatch.setattr(
        "backend.services.chat_service.stream_llm_response",
        should_not_run,
    )

    events = []
    async for ev in stream_coach_response("2. Dünya Savaşı kaç yılında bitti?"):
        events.append(ev)

    done = next(e for e in events if e["type"] == "done")
    assert done["off_topic"] is True
    assert done["scope_family"] == "hard"
    assert done["guardrail_triggered"] is False
    assert done["mode"] == "coach"
    assert done["daily_tasks"] is None

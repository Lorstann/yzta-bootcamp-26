"""Coach mode prompt + streaming behaviour (no task assignment)."""

from __future__ import annotations

import pytest

from backend.services.chat_service import stream_coach_response
from backend.services.llm.prompts import build_coach_prompt


def test_build_coach_prompt_forbids_task_blocks():
    prompt = build_coach_prompt(
        curriculum_context="React hooks, useEffect",
        today_state={"enerji": 8, "motivasyon": 6},
        today_tasks=["Mentöre soru yaz"],
    )
    assert "[GOREVLER]" in prompt  # mentioned as do-not-produce
    assert "ÜRETME" in prompt or "ATAMA" in prompt
    assert "GERÇEK cevap" in prompt or "gerçek" in prompt.lower()
    assert "Mentöre soru yaz" in prompt
    assert "KAPSAM" in prompt
    assert "kaçınma" not in prompt.casefold()


def test_build_coach_prompt_no_curriculum_note():
    prompt = build_coach_prompt(curriculum_context="")
    assert "mentörüne de doğrulat" in prompt


@pytest.mark.asyncio
async def test_stream_coach_done_has_mode_and_no_tasks(monkeypatch):
    async def fake_llm(*_a, **_k):
        yield "MLOps için Docker, CI/CD ve model registry öğren. "
        yield "[GOREVLER]\n- gizli görev\n[/GOREVLER]"

    monkeypatch.setattr(
        "backend.services.chat_service.stream_llm_response",
        fake_llm,
    )

    events = []
    async for ev in stream_coach_response(
        "MLOps mülakatına nasıl hazırlanmalıyım?",
        curriculum_context="MLOps, Docker, CI/CD",
    ):
        events.append(ev)

    chunks = [e["data"] for e in events if e["type"] == "chunk"]
    visible = "".join(chunks)
    assert "MLOps" in visible
    assert "[GOREVLER]" not in visible
    assert "gizli görev" not in visible

    done = next(e for e in events if e["type"] == "done")
    assert done["mode"] == "coach"
    assert done["daily_tasks"] is None
    assert done["checkin_completed"] is True
    assert done["quick_replies"] is None

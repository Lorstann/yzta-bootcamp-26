"""Tone bans and opener rotation."""

from backend.services.checkin_flow import opener_hint
from backend.services.llm.prompts import build_checkin_prompt, build_coach_prompt


def test_checkin_prompt_bans_reflective_openers():
    prompt = build_checkin_prompt(stage="explore", turn_count=2)
    lower = prompt.casefold()
    # Ban list must be present
    assert "asla kullanma" in lower
    assert "duyduğum şu" in lower  # listed as forbidden
    # Must NOT instruct the model to start with reflective listening
    assert "önce yansıtıcı dinleme" not in lower
    assert '("duyduğum şu...")' not in lower
    assert '("duyduğum şu…")' not in lower


def test_coach_prompt_bans_reflective_openers():
    prompt = build_coach_prompt()
    lower = prompt.casefold()
    assert "asla kullanma" in lower
    assert "duyduğum şu" in lower
    assert "önce yansıtıcı dinleme" not in lower


def test_opener_hint_rotates_by_turn():
    a = opener_hint(0)
    b = opener_hint(1)
    c = opener_hint(4)  # wraps to 0
    assert a != b
    assert a == c
    assert "kalıp" in a.casefold() or "başla" in a.casefold()


def test_checkin_prompt_includes_opener_hint_and_wellbeing():
    prompt = build_checkin_prompt(
        stage="closing",
        turn_count=3,
        wellbeing_context="ÖĞRENCİ PROFİLİ\n- Program: Veri Bilimi",
    )
    assert "Veri Bilimi" in prompt
    assert "başlık |" in prompt.casefold() or "başlık |" in prompt
    assert opener_hint(3) in prompt

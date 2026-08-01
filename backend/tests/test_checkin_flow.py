"""Tests for check-in stage machine."""

from backend.services.checkin_flow import (
    MAX_TURNS,
    empty_state,
    energy_to_mood,
    merge_state,
    next_stage,
    should_force_complete,
)


def test_opening_when_energy_unknown():
    assert next_stage(empty_state(), 0) == "opening"


def test_skip_opening_when_energy_and_motivation_known():
    state = {"enerji": 5, "motivasyon": 6, "engel": None, "yuk": None, "hazir": False}
    assert next_stage(state, 1) == "explore"


def test_focus_when_blocker_known():
    state = {
        "enerji": 5,
        "motivasyon": 6,
        "engel": "React hooks",
        "yuk": "orta",
        "hazir": False,
    }
    assert next_stage(state, 2) == "focus"


def test_closing_at_soft_turn():
    state = {
        "enerji": 5,
        "motivasyon": 6,
        "engel": "React",
        "yuk": None,
        "hazir": False,
    }
    assert next_stage(state, 4) == "closing"


def test_closing_when_hazir():
    state = {
        "enerji": 5,
        "motivasyon": 6,
        "engel": "React",
        "yuk": None,
        "hazir": True,
    }
    assert next_stage(state, 2) == "closing"


def test_completed_at_max_turns():
    assert next_stage(empty_state(), MAX_TURNS) == "completed"


def test_force_complete_with_tasks():
    assert should_force_complete(2, ["görev 1"]) is True


def test_force_complete_at_max_without_tasks():
    assert should_force_complete(MAX_TURNS, None) is True
    assert should_force_complete(3, None) is False


def test_merge_state_cumulative():
    current = empty_state()
    current["enerji"] = 4
    incoming = {"motivasyon": 3, "engel": "SQL", "hazir": False}
    merged = merge_state(current, incoming)  # type: ignore[arg-type]
    assert merged["enerji"] == 4
    assert merged["motivasyon"] == 3
    assert merged["engel"] == "SQL"


def test_merge_does_not_clear_with_null():
    current = {"enerji": 7, "motivasyon": 8, "engel": "x", "yuk": "dusuk", "hazir": False}
    incoming = {"enerji": None, "motivasyon": 5, "engel": None}
    merged = merge_state(current, incoming)  # type: ignore[arg-type]
    assert merged["enerji"] == 7
    assert merged["motivasyon"] == 5
    assert merged["engel"] == "x"


def test_energy_to_mood():
    assert energy_to_mood(10) == 5
    assert energy_to_mood(1) == 1
    assert energy_to_mood(None) is None

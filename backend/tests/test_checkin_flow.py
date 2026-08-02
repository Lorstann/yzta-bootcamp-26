"""Tests for check-in stage machine + word scales + chat mode."""

from backend.services.checkin_flow import (
    MAX_TURNS,
    SOFT_CLOSE_TURN,
    apply_user_scale_signals,
    coerce_scale,
    default_quick_replies,
    empty_state,
    energy_to_mood,
    label_for_score,
    merge_state,
    next_stage,
    resolve_mode,
    should_force_complete,
)


def test_opening_when_energy_unknown():
    assert next_stage(empty_state(), 0) == "opening"


def test_explore_when_only_energy_known():
    state = {"enerji": 10, "motivasyon": None, "engel": None, "yuk": None, "hazir": False}
    assert next_stage(state, 1) == "explore"


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
    assert SOFT_CLOSE_TURN == 3
    assert next_stage(state, SOFT_CLOSE_TURN) == "closing"


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
    assert MAX_TURNS == 4
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


def test_resolve_mode():
    assert resolve_mode("in_progress", "opening") == "checkin"
    assert resolve_mode("completed", "completed") == "coach"
    assert resolve_mode("in_progress", "completed") == "coach"


def test_coerce_scale_accepts_labels_and_ints():
    assert coerce_scale("enerji", "İyiyim") == 8
    assert coerce_scale("enerji", "iyiyim") == 8
    assert coerce_scale("motivasyon", "Ateşliyim") == 10
    assert coerce_scale("enerji", 6) == 6
    assert coerce_scale("enerji", "99") is None
    assert coerce_scale("enerji", "bilinmeyen") is None


def test_label_for_score():
    assert label_for_score("enerji", 8) == "İyiyim"
    assert label_for_score("motivasyon", 2) == "Hiç yok"
    assert label_for_score("enerji", None) is None


def test_default_quick_replies():
    opening = default_quick_replies("opening")
    assert "İyiyim" in opening
    explore_motivation = default_quick_replies("explore", {"enerji": 8})
    assert "İstekliyim" in explore_motivation
    explore = default_quick_replies(
        "explore", {"enerji": 8, "motivasyon": 6, "engel": None}
    )
    assert "Mülakat stresi" in explore
    assert default_quick_replies("closing") == []


def test_apply_user_scale_signals_energy_chip():
    state = empty_state()
    updated = apply_user_scale_signals("Turbo moddayım", state)
    assert updated["enerji"] == 10
    assert updated["motivasyon"] is None

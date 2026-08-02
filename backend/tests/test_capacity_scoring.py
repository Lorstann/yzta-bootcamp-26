"""
backend/tests/test_capacity_scoring.py
Pure capacity engine unit tests.
"""

from backend.services.capacity import (
    BASE_SCORE,
    clamp_llm_delta,
    compute_capacity,
    estimate_live,
)


def test_new_user_onboarding_only_baseline():
    """No behavioural signals → onboarding factors dominate, near base."""
    result = compute_capacity(self_reported_stress=3, signal_days=0)
    assert result["w_behavior"] == 0.0
    # stress 3 → 0 delta → score ≈ 60
    assert 55 <= result["score"] <= 65
    assert result["factors"]["onboarding_stres"] == 0.0


def test_high_stress_lowers_score_for_new_user():
    result = compute_capacity(self_reported_stress=5, signal_days=0)
    assert result["score"] < BASE_SCORE
    assert result["factors"]["onboarding_stres"] < 0


def test_low_energy_lowers_score_with_signals():
    high = compute_capacity(energy=9, motivation=8, signal_days=5)
    low = compute_capacity(energy=2, motivation=2, signal_days=5)
    assert low["score"] < high["score"]
    assert low["factors"]["enerji"] < 0


def test_missed_days_penalty():
    ok = compute_capacity(missed_days_7=0, signal_days=5, energy=6)
    bad = compute_capacity(missed_days_7=5, signal_days=5, energy=6)
    assert bad["score"] < ok["score"]
    assert bad["factors"]["sureklilik"] < 0


def test_confidence_blend_ramps_with_signal_days():
    r0 = compute_capacity(energy=2, self_reported_stress=1, signal_days=0)
    r3 = compute_capacity(energy=2, self_reported_stress=1, signal_days=3)
    r5 = compute_capacity(energy=2, self_reported_stress=1, signal_days=5)
    assert r0["w_behavior"] == 0.0
    assert 0.5 < r3["w_behavior"] < 1.0
    assert r5["w_behavior"] == 1.0
    # With full behaviour weight, low energy bites harder
    assert r5["score"] < r0["score"]


def test_ema_and_daily_clamp():
    # Huge swing would go near 0 raw, but daily clamp ±20 from previous 80
    result = compute_capacity(
        energy=1,
        motivation=1,
        missed_days_7=6,
        completion_rate=0.0,
        open_tasks=10,
        signal_days=5,
        previous_score=80,
    )
    assert result["score"] >= 60  # 80 - 20
    assert result["score"] <= 100


def test_score_clamped_0_100():
    result = compute_capacity(
        energy=10,
        motivation=10,
        workload="dusuk",
        completion_rate=1.0,
        missed_days_7=0,
        signal_days=5,
        self_reported_stress=1,
        competencies={"experience_years": 10, "skills": ["a"] * 20},
        llm_delta=15,
    )
    assert 0 <= result["score"] <= 100


def test_llm_delta_clamped():
    assert clamp_llm_delta(50) == 15.0
    assert clamp_llm_delta(-100) == -15.0
    assert clamp_llm_delta(None) == 0.0
    assert clamp_llm_delta("abc") == 0.0
    assert clamp_llm_delta(7) == 7.0


def test_llm_delta_applied():
    base = compute_capacity(signal_days=5, energy=6, motivation=6)
    bumped = compute_capacity(
        signal_days=5, energy=6, motivation=6, llm_delta=10
    )
    assert bumped["score"] > base["score"]
    assert bumped["factors"]["llm_delta"] == 10.0


def test_curriculum_null_disabled():
    no_cur = compute_capacity(
        weekly_available_hours=10,
        curriculum_weekly_hours=None,
        signal_days=0,
    )
    both = compute_capacity(
        weekly_available_hours=10,
        curriculum_weekly_hours=25,
        signal_days=0,
    )
    assert no_cur["factors"]["mufredat_yuku"] == 0.0
    assert both["factors"]["mufredat_yuku"] < 0


def test_level_from_competencies():
    none = compute_capacity(signal_days=0)
    skilled = compute_capacity(
        signal_days=0,
        competencies={"experience_years": 3, "skills": ["Python", "SQL", "React"]},
    )
    assert skilled["score"] > none["score"]
    assert skilled["factors"]["seviye"] > 0


def test_estimate_live_drops_on_low_energy():
    live = estimate_live(70, {"enerji": 2, "motivasyon": 2, "yuk": "yuksek"})
    assert live < 70


def test_workload_deltas():
    low = compute_capacity(workload="dusuk", signal_days=5, energy=6)
    high = compute_capacity(workload="yuksek", signal_days=5, energy=6)
    assert low["score"] > high["score"]

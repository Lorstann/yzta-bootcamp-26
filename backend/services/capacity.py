"""
backend/services/capacity.py
Hybrid capacity score engine — pure functions, no DB / FastAPI.
"""

from __future__ import annotations

from typing import Any, Mapping, Optional

BASE_SCORE = 60.0
EMA_ALPHA = 0.5
DAILY_CLAMP = 20.0
LLM_DELTA_CLAMP = 15.0

_STRESS_DELTAS = {1: 8.0, 2: 4.0, 3: 0.0, 4: -5.0, 5: -10.0}
_WORKLOAD_DELTAS = {"dusuk": 6.0, "orta": 0.0, "yuksek": -8.0}


def _clamp(value: float, lo: float = 0.0, hi: float = 100.0) -> float:
    return max(lo, min(hi, value))


def _scale_delta(value: float | None, *, center: float, span: float, weight: float) -> float:
    """Map a 1-10 style signal around `center` to ±weight."""
    if value is None:
        return 0.0
    return _clamp((float(value) - center) / span * weight, -abs(weight), abs(weight))


def _level_delta(competencies: Mapping[str, Any] | None) -> float:
    if not competencies or not isinstance(competencies, Mapping):
        return 0.0
    years = competencies.get("experience_years")
    skills = competencies.get("skills")
    skill_count = len(skills) if isinstance(skills, list) else 0
    years_f = 0.0
    if isinstance(years, (int, float)) and not isinstance(years, bool):
        years_f = float(years)
    # Experience + skills → up to +6 (more capacity to take load)
    delta = min(4.0, years_f) + min(2.0, skill_count * 0.2)
    return _clamp(delta, 0.0, 6.0)


def _curriculum_delta(
    curriculum_weekly_hours: float | None,
    available_hours: float | None,
) -> float:
    if curriculum_weekly_hours is None or available_hours is None:
        return 0.0
    gap = float(curriculum_weekly_hours) - float(available_hours)
    if gap <= 0:
        return min(4.0, -gap * 0.2)  # spare capacity → small boost
    # Overload: −1 per extra hour, capped at −10
    return _clamp(-gap, -10.0, 0.0)


def _stress_delta(stress: int | None) -> float:
    if stress is None:
        return 0.0
    return _STRESS_DELTAS.get(int(stress), 0.0)


def compute_capacity(
    *,
    energy: float | None = None,
    motivation: float | None = None,
    workload: str | None = None,
    completion_rate: float | None = None,
    missed_days_7: int = 0,
    open_tasks: int = 0,
    signal_days: int = 0,
    self_reported_stress: int | None = None,
    weekly_available_hours: float | None = None,
    curriculum_weekly_hours: float | None = None,
    competencies: Mapping[str, Any] | None = None,
    previous_score: float | None = None,
    llm_delta: float = 0.0,
) -> dict[str, Any]:
    """
    Deterministic weighted capacity score (0-100) with confidence blend,
    EMA smoothing, daily ±20 clamp, and optional LLM delta (±15).

    Returns {"score": float, "factors": dict, "raw_score": float, "w_behavior": float}.
    """
    w_behavior = min(1.0, max(0.0, float(signal_days) / 5.0))
    w_onboarding = 1.0 - w_behavior

    # --- Behavioural deltas (scaled by w_behavior) ---
    enerji = _scale_delta(energy, center=5.5, span=4.5, weight=15.0)
    motivasyon = _scale_delta(motivation, center=5.5, span=4.5, weight=10.0)

    yuk_key = (workload or "").strip().lower() if workload else None
    yuk = _WORKLOAD_DELTAS.get(yuk_key, 0.0) if yuk_key else 0.0

    if completion_rate is None:
        gorev = 0.0
    else:
        gorev = _clamp((float(completion_rate) - 0.6) * 20.0, -12.0, 12.0)

    sureklilik = _clamp(-3.0 * max(0, int(missed_days_7) - 1), -12.0, 0.0)
    acik = _clamp(-3.0 * max(0, int(open_tasks) - 3), -9.0, 0.0)

    behavioral = (enerji + motivasyon + yuk + gorev + sureklilik + acik) * w_behavior

    # --- Onboarding / profile deltas (scaled by w_onboarding, but seviye always on) ---
    stres = _stress_delta(self_reported_stress) * w_onboarding
    # When we have lots of behaviour data, stress still contributes lightly
    if w_behavior >= 1.0 and self_reported_stress is not None:
        stres = _stress_delta(self_reported_stress) * 0.25

    seviye = _level_delta(competencies)
    mufredat = _curriculum_delta(curriculum_weekly_hours, weekly_available_hours)

    llm = _clamp(float(llm_delta or 0.0), -LLM_DELTA_CLAMP, LLM_DELTA_CLAMP)

    raw = BASE_SCORE + behavioral + stres + seviye + mufredat + llm
    raw = _clamp(raw)

    # EMA + daily clamp against previous
    if previous_score is not None:
        blended = EMA_ALPHA * raw + (1.0 - EMA_ALPHA) * float(previous_score)
        lower = float(previous_score) - DAILY_CLAMP
        upper = float(previous_score) + DAILY_CLAMP
        score = _clamp(blended, lower, upper)
        score = _clamp(score)
    else:
        score = raw

    factors: dict[str, Any] = {
        "base": BASE_SCORE,
        "enerji": round(enerji * w_behavior, 2),
        "motivasyon": round(motivasyon * w_behavior, 2),
        "yuk": round(yuk * w_behavior, 2),
        "gorev_tamamlama": round(gorev * w_behavior, 2),
        "sureklilik": round(sureklilik * w_behavior, 2),
        "acik_gorev": round(acik * w_behavior, 2),
        "onboarding_stres": round(stres, 2),
        "seviye": round(seviye, 2),
        "mufredat_yuku": round(mufredat, 2),
        "llm_delta": round(llm, 2),
        "w_behavior": round(w_behavior, 2),
        "raw_score": round(raw, 2),
        "previous_score": (
            round(float(previous_score), 2) if previous_score is not None else None
        ),
    }

    return {
        "score": round(score, 2),
        "factors": factors,
        "raw_score": round(raw, 2),
        "w_behavior": round(w_behavior, 2),
    }


def estimate_live(
    previous_score: float | None,
    state: Mapping[str, Any] | None = None,
) -> float:
    """
    Lightweight live estimate for chat stream (no DB write).
    Applies only energy/motivation/workload deltas on top of previous score.
    """
    prev = float(previous_score) if previous_score is not None else BASE_SCORE
    state = state or {}
    energy = state.get("enerji")
    motivation = state.get("motivasyon")
    workload = state.get("yuk")

    energy_f = float(energy) if energy is not None else None
    motivation_f = float(motivation) if motivation is not None else None
    yuk_key = (str(workload).strip().lower() if workload else None)

    delta = (
        _scale_delta(energy_f, center=5.5, span=4.5, weight=15.0) * 0.5
        + _scale_delta(motivation_f, center=5.5, span=4.5, weight=10.0) * 0.5
        + (_WORKLOAD_DELTAS.get(yuk_key, 0.0) if yuk_key else 0.0) * 0.5
    )
    return round(_clamp(prev + delta), 2)


def clamp_llm_delta(value: Any) -> float:
    """Parse and clamp kapasite_delta from [DURUM] JSON."""
    if value is None or value == "":
        return 0.0
    if isinstance(value, bool):
        return 0.0
    try:
        n = float(value)
    except (TypeError, ValueError):
        return 0.0
    return _clamp(n, -LLM_DELTA_CLAMP, LLM_DELTA_CLAMP)

"""
backend/services/checkin_flow.py
Server-side check-in stage machine + turn limits.
Pure functions — no DB / FastAPI imports.
"""

from __future__ import annotations

from typing import Any, Literal, Optional, TypedDict

Stage = Literal["opening", "explore", "focus", "closing", "completed"]

MAX_TURNS = 6
SOFT_CLOSE_TURN = 4
HISTORY_WINDOW = 12

VALID_WORKLOAD = frozenset({"dusuk", "orta", "yuksek"})


class CheckinState(TypedDict, total=False):
    enerji: Optional[int]
    motivasyon: Optional[int]
    engel: Optional[str]
    yuk: Optional[str]
    hazir: bool


def empty_state() -> CheckinState:
    return {
        "enerji": None,
        "motivasyon": None,
        "engel": None,
        "yuk": None,
        "hazir": False,
    }


def state_from_session(session: Any) -> CheckinState:
    """Build CheckinState from ORM / SimpleNamespace session fields."""
    return {
        "enerji": getattr(session, "energy_level", None),
        "motivasyon": getattr(session, "motivation_level", None),
        "engel": getattr(session, "main_blocker", None),
        "yuk": getattr(session, "workload_level", None),
        "hazir": False,
    }


def merge_state(current: CheckinState, incoming: CheckinState | None) -> CheckinState:
    """Cumulative merge: non-null incoming fields overwrite current."""
    if not incoming:
        return dict(current)  # type: ignore[return-value]
    merged: CheckinState = dict(current)  # type: ignore[assignment]
    for key in ("enerji", "motivasyon", "engel", "yuk"):
        val = incoming.get(key)  # type: ignore[literal-required]
        if val is not None and val != "":
            merged[key] = val  # type: ignore[literal-required]
    if incoming.get("hazir") is True:
        merged["hazir"] = True
    return merged


def next_stage(state: CheckinState, turn_count: int) -> Stage:
    """
    Advance stage from known signals + turn count.

    - energy + motivation known → skip opening
    - blocker known → skip explore
    - turn_count >= SOFT_CLOSE_TURN or hazir → closing
    - turn_count >= MAX_TURNS → completed
    """
    if turn_count >= MAX_TURNS:
        return "completed"

    energy = state.get("enerji")
    motivation = state.get("motivasyon")
    blocker = state.get("engel")
    hazir = bool(state.get("hazir"))

    if turn_count >= SOFT_CLOSE_TURN or hazir:
        return "closing"

    if energy is None or motivation is None:
        return "opening"

    if not blocker:
        return "explore"

    return "focus"


def should_force_complete(turn_count: int, daily_tasks: list[str] | None) -> bool:
    """Force-complete when max turns hit even without a task block."""
    if daily_tasks:
        return True
    return turn_count >= MAX_TURNS


def energy_to_mood(energy: int | None) -> int | None:
    """Map 1-10 energy → 1-5 mood_score when user hasn't set emoji mood."""
    if energy is None:
        return None
    return max(1, min(5, round(energy / 2)))


def stage_instruction(stage: Stage) -> str:
    """Single-stage instruction injected into the system prompt."""
    if stage == "opening":
        return (
            "Bu turda sıcak bir karşılama yap ve enerji + motivasyonunu "
            "(1-10) tek soruda sor. Başka konu açma."
        )
    if stage == "explore":
        return (
            "Enerji/motivasyonu zaten biliyorsun — ASLA tekrar sorma. "
            "Kısa empati kur, sonra bugün veya dünden aklında kalan "
            "en zorlayıcı konuyu / engeli sor."
        )
    if stage == "focus":
        return (
            "Engeli biliyorsun — tekrar sorma. Öğrencinin durumuna göre "
            "bugün müfredattan neye odaklanabileceğini sor veya "
            "kapasitesine uygun bir odak öner. Tek soru."
        )
    if stage == "closing":
        return (
            "Görüşmeyi nazikçe kapat. Öğrencinin durumuna uygun en fazla "
            "3 günlük görev ver. Enerji ≤ 4 ise en fazla 1 görev ver ve "
            "dinlenmeyi meşrulaştır. Görevleri MUTLAKA [GOREVLER] bloğunda yaz."
        )
    return "Check-in tamamlandı. Kısa bir kapanış cümlesi yeter; yeni soru sorma."

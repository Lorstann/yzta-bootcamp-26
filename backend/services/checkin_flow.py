"""
backend/services/checkin_flow.py
Server-side check-in stage machine + turn limits + word scales.
Pure functions — no DB / FastAPI imports.
"""

from __future__ import annotations

from typing import Any, Literal, Optional, TypedDict

Stage = Literal["opening", "explore", "focus", "closing", "completed"]
ChatMode = Literal["checkin", "coach"]
ScaleKind = Literal["enerji", "motivasyon"]

MAX_TURNS = 4
SOFT_CLOSE_TURN = 3
HISTORY_WINDOW = 12

VALID_WORKLOAD = frozenset({"dusuk", "orta", "yuksek"})

# Word-scale labels → stored int (1-10). Risk/capacity math stays numeric.
ENERGY_CHOICES: dict[str, int] = {
    "Tükendim": 2,
    "Yorgunum": 4,
    "İdare eder": 6,
    "İyiyim": 8,
    "Turbo moddayım": 10,
}

MOTIVATION_CHOICES: dict[str, int] = {
    "Hiç yok": 2,
    "Zorlanıyorum": 4,
    "Fena değil": 6,
    "İstekliyim": 8,
    "Ateşliyim": 10,
}

_ENERGY_BY_SCORE = {v: k for k, v in ENERGY_CHOICES.items()}
_MOTIVATION_BY_SCORE = {v: k for k, v in MOTIVATION_CHOICES.items()}

_EXPLORE_REPLIES = (
    "Zaman yetmiyor",
    "Konuyu anlamadım",
    "Motivasyonum düşük",
    "Mülakat stresi",
    "Başka bir şey",
)


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


def resolve_mode(session_status: str | None, stage: Stage | str | None = None) -> ChatMode:
    """Route to coach after today's check-in is done."""
    if (session_status or "").lower() == "completed":
        return "coach"
    if stage == "completed":
        return "coach"
    return "checkin"


def label_for_score(kind: ScaleKind, value: int | None) -> str | None:
    """Map stored 1-10 int back to a word label (nearest choice)."""
    if value is None:
        return None
    table = _ENERGY_BY_SCORE if kind == "enerji" else _MOTIVATION_BY_SCORE
    if value in table:
        return table[value]
    # Nearest even score in {2,4,6,8,10}
    nearest = min(table.keys(), key=lambda s: abs(s - int(value)))
    return table[nearest]


def _normalize_label(label: str) -> str:
    """Case-insensitive compare that treats Turkish İ/I as ascii i."""
    return (
        (label or "")
        .replace("İ", "i")
        .replace("I", "i")
        .replace("ı", "i")
        .casefold()
        .strip()
    )


def score_from_label(kind: ScaleKind, label: str) -> int | None:
    """Resolve a word label (case-insensitive, strip) to 1-10 int."""
    table = ENERGY_CHOICES if kind == "enerji" else MOTIVATION_CHOICES
    cleaned = (label or "").strip()
    if not cleaned:
        return None
    if cleaned in table:
        return table[cleaned]
    target = _normalize_label(cleaned)
    for key, score in table.items():
        if _normalize_label(key) == target:
            return score
    return None


def coerce_scale(kind: ScaleKind, value: Any) -> int | None:
    """Accept int 1-10 or a word label; return clamped int or None."""
    if value is None or value == "":
        return None
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        n = int(value)
        if 1 <= n <= 10:
            return n
        return None
    if isinstance(value, str):
        stripped = value.strip()
        try:
            n = int(stripped)
            if 1 <= n <= 10:
                return n
        except ValueError:
            pass
        return score_from_label(kind, stripped)
    return None


def default_quick_replies(stage: Stage | str) -> list[str]:
    """Deterministic chip suggestions when the LLM omits [SECENEKLER]."""
    if stage == "opening":
        return list(ENERGY_CHOICES.keys())
    if stage == "explore":
        return list(_EXPLORE_REPLIES)
    if stage == "focus":
        return [
            "Müfredattan bir konu",
            "Mülakat hazırlığı",
            "Bugün dinlenmek",
            "Başka bir şey",
        ]
    return []


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
    energy_labels = " / ".join(ENERGY_CHOICES.keys())
    motivation_labels = " / ".join(MOTIVATION_CHOICES.keys())
    if stage == "opening":
        return (
            "Bu turda sıcak bir karşılama yap ve bugünkü enerjisini "
            f"şu etiketlerden biriyle sor: {energy_labels}. "
            "Rakam (1-10) ASLA kullanma. Başka konu açma. "
            "Yanıtında [SECENEKLER] bloğunda enerji etiketlerini listele."
        )
    if stage == "explore":
        return (
            "Enerji/motivasyonu zaten biliyorsun — ASLA tekrar sorma. "
            "Kısa empati kur, sonra bugün veya dünden aklında kalan "
            "en zorlayıcı konuyu / engeli sor. "
            "Motivasyon henüz yoksa etiketlerle sor: "
            f"{motivation_labels}."
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
            "3 günlük görev ver. Enerji düşükse (Tükendim/Yorgunum) en fazla "
            "1 görev ver ve dinlenmeyi meşrulaştır. "
            "Görevleri MUTLAKA [GOREVLER] bloğunda yaz."
        )
    return "Check-in tamamlandı. Kısa bir kapanış cümlesi yeter; yeni soru sorma."

"""
backend/services/wellbeing.py
Burnout level + prompt context from student profile.
Pure functions — no DB / FastAPI imports.
"""

from __future__ import annotations

from typing import Any, Literal, Mapping, Sequence

BurnoutLevel = Literal["dusuk", "orta", "yuksek"]


def burnout_level(
    energy: int | None = None,
    motivation: int | None = None,
    capacity: float | None = None,
    streak_days: int | None = None,
) -> BurnoutLevel:
    """
    Heuristic burnout band from today's signals + capacity.

    yuksek: energy ≤ 3 or motivation ≤ 3 or capacity < 30
    orta:   energy ≤ 5 or motivation ≤ 5 or capacity < 50
    dusuk:  otherwise (or no signal yet)
    """
    score_hits = 0
    if energy is not None and int(energy) <= 3:
        return "yuksek"
    if motivation is not None and int(motivation) <= 3:
        return "yuksek"
    if capacity is not None and float(capacity) < 30:
        return "yuksek"

    if energy is not None and int(energy) <= 5:
        score_hits += 1
    if motivation is not None and int(motivation) <= 5:
        score_hits += 1
    if capacity is not None and float(capacity) < 50:
        score_hits += 1
    # Long streak without rest can push to orta
    if streak_days is not None and int(streak_days) >= 7:
        score_hits += 1

    if score_hits >= 1:
        return "orta"
    return "dusuk"


def _list_field(interests: Mapping[str, Any] | None, key: str) -> list[str]:
    if not interests or not isinstance(interests, Mapping):
        return []
    raw = interests.get(key)
    if not isinstance(raw, Sequence) or isinstance(raw, (str, bytes)):
        return []
    out: list[str] = []
    for item in raw:
        if isinstance(item, str) and item.strip():
            out.append(item.strip())
    return out


def build_wellbeing_context(
    profile: Mapping[str, Any] | None,
    state: Mapping[str, Any] | None = None,
    *,
    streak_days: int | None = None,
) -> str:
    """
    Prompt block for personalization. Empty profile → ask gently, don't invent.
    """
    profile = profile or {}
    state = state or {}

    city = (profile.get("city") or "") if isinstance(profile.get("city"), str) else ""
    district = (
        (profile.get("district") or "")
        if isinstance(profile.get("district"), str)
        else ""
    )
    track = (
        (profile.get("program_track") or "")
        if isinstance(profile.get("program_track"), str)
        else ""
    )
    interests = profile.get("interests")
    hobbies = _list_field(interests if isinstance(interests, Mapping) else None, "hobbies")
    recharge = _list_field(
        interests if isinstance(interests, Mapping) else None, "recharge"
    )

    capacity = profile.get("capacity_score")
    cap_f: float | None = None
    if capacity is not None:
        try:
            cap_f = float(capacity)
        except (TypeError, ValueError):
            cap_f = None

    energy = state.get("enerji")
    motivation = state.get("motivasyon")
    level = burnout_level(
        energy=int(energy) if energy is not None else None,
        motivation=int(motivation) if motivation is not None else None,
        capacity=cap_f,
        streak_days=streak_days,
    )

    has_any = bool(city.strip() or track.strip() or hobbies or recharge)
    if not has_any:
        return (
            "ÖĞRENCİ PROFİLİ: Bilgi yok. Kişisel öneri (park, hobi, şehir) "
            "UYDURMA. İhtiyaç olursa nazikçe şehir / hobi / program sor."
        )

    lines = [
        "ÖĞRENCİ PROFİLİ (kişiselleştirme için — uydurma, sadece buradakini kullan):"
    ]
    if track.strip():
        lines.append(f"- Program: {track.strip()}")
    if city.strip():
        loc = city.strip()
        if district.strip():
            loc = f"{loc} / {district.strip()}"
        lines.append(f"- Şehir: {loc}")
    if hobbies:
        lines.append(f"- Hobiler: {', '.join(hobbies)}")
    if recharge:
        lines.append(f"- Şarj olduğu şeyler: {', '.join(recharge)}")
    lines.append(f"- Burnout riski: {level}")
    lines.append(
        "Konum önerisi: sadece o şehirde yaygın bilinen büyük park/sahil/"
        "kent ormanı tipi yerleri söyle; adres, saat, fiyat, etkinlik tarihi "
        "ASLA uydurma. Emin değilsen mekan ismi verme."
    )
    return "\n".join(lines)

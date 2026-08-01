"""
backend/services/profile_service.py
S08/S09/S10–S12: Profile, onboarding, LinkedIn extract, learned profile merge.
"""

from __future__ import annotations

import json
import logging
import re
import uuid
from decimal import Decimal
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.config import settings
from backend.domain.errors.app_error import AppError
from backend.repositories.user_repo import StudentProfileRepository, UserRepository

logger = logging.getLogger(__name__)


def _normalize_interests(raw: Any) -> dict[str, list[str]] | None:
    if raw is None:
        return None
    if hasattr(raw, "model_dump"):
        raw = raw.model_dump()
    if not isinstance(raw, dict):
        return None

    def _clean_list(value: Any) -> list[str]:
        if not isinstance(value, list):
            return []
        out: list[str] = []
        seen: set[str] = set()
        for item in value:
            if not isinstance(item, str):
                continue
            cleaned = item.strip()[:80]
            if not cleaned:
                continue
            key = cleaned.casefold()
            if key in seen:
                continue
            seen.add(key)
            out.append(cleaned)
        return out[:20]

    return {
        "hobbies": _clean_list(raw.get("hobbies")),
        "recharge": _clean_list(raw.get("recharge")),
        "notes": _clean_list(raw.get("notes")),
    }


def to_public_profile(profile) -> dict[str, Any]:
    return {
        "user_id": str(profile.user_id),
        "capacity_score": float(profile.capacity_score)
        if profile.capacity_score is not None
        else None,
        "linkedin_url": profile.linkedin_url,
        "bio": profile.bio,
        "competencies": profile.competencies,
        "city": getattr(profile, "city", None),
        "district": getattr(profile, "district", None),
        "program_track": getattr(profile, "program_track", None),
        "interests": getattr(profile, "interests", None),
        "onboarding_completed": profile.onboarding_completed,
    }


async def get_profile(
    db: AsyncSession, *, user_id: uuid.UUID
) -> dict[str, Any]:
    repo = StudentProfileRepository(db)
    profile = await repo.get_by_user_id(user_id)
    if profile is None:
        raise AppError("Profile not found", code="NOT_FOUND", status_code=404)
    return to_public_profile(profile)


async def update_onboarding(
    db: AsyncSession,
    *,
    user_id: uuid.UUID,
    capacity_score: Decimal,
    bio: str | None,
    onboarding_completed: bool,
    city: str | None = None,
    district: str | None = None,
    program_track: str | None = None,
    interests: Any = None,
) -> dict[str, Any]:
    repo = StudentProfileRepository(db)
    profile = await repo.get_by_user_id(user_id)
    interests_payload = _normalize_interests(interests)

    if profile is None:
        user_repo = UserRepository(db)
        user = await user_repo.get_by_id(user_id)
        if user is None:
            raise AppError("User not found", code="NOT_FOUND", status_code=404)
        from backend.db.models.user import StudentProfile

        profile = StudentProfile(
            user_id=user_id,
            tenant_id=user.tenant_id,
            capacity_score=capacity_score,
            bio=bio,
            city=(city or "").strip() or None,
            district=(district or "").strip() or None,
            program_track=(program_track or "").strip() or None,
            interests=interests_payload,
            onboarding_completed=onboarding_completed,
        )
        await repo.create(profile)
    else:
        profile.capacity_score = capacity_score
        if bio is not None:
            profile.bio = bio
        if city is not None:
            profile.city = city.strip() or None
        if district is not None:
            profile.district = district.strip() or None
        if program_track is not None:
            profile.program_track = program_track.strip() or None
        if interests_payload is not None:
            profile.interests = interests_payload
        profile.onboarding_completed = onboarding_completed
        await db.flush()

    from backend.repositories.capacity_repo import CapacitySnapshotRepository

    snap_repo = CapacitySnapshotRepository(db)
    await snap_repo.record(
        tenant_id=profile.tenant_id,
        user_id=user_id,
        score=capacity_score,
    )

    logger.info(
        "Onboarding updated | user_id=%s capacity=%s city=%s track=%s",
        user_id,
        capacity_score,
        getattr(profile, "city", None),
        getattr(profile, "program_track", None),
    )
    return to_public_profile(profile)


def _merge_string_lists(*lists: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for lst in lists:
        for item in lst:
            cleaned = (item or "").strip()[:80]
            if not cleaned:
                continue
            key = cleaned.casefold()
            if key in seen:
                continue
            seen.add(key)
            out.append(cleaned)
    return out[:20]


async def merge_learned_profile(
    db: AsyncSession,
    *,
    user_id: uuid.UUID,
    learned: dict[str, Any] | None,
) -> dict[str, Any] | None:
    """
    Merge AI-detected profile hints without overwriting user-entered fields.
    Only fills None/empty scalars; appends new hobby/recharge items.
    """
    if not learned:
        return None

    repo = StudentProfileRepository(db)
    profile = await repo.get_by_user_id(user_id)
    if profile is None:
        logger.warning("Learned profile skipped — no profile | user_id=%s", user_id)
        return None

    changed = False

    sehir = learned.get("sehir") or learned.get("city")
    if isinstance(sehir, str) and sehir.strip() and not (profile.city or "").strip():
        profile.city = sehir.strip()[:120]
        changed = True

    ilce = learned.get("ilce") or learned.get("district")
    if (
        isinstance(ilce, str)
        and ilce.strip()
        and not (profile.district or "").strip()
    ):
        profile.district = ilce.strip()[:120]
        changed = True

    program = learned.get("program") or learned.get("program_track")
    if (
        isinstance(program, str)
        and program.strip()
        and not (profile.program_track or "").strip()
    ):
        profile.program_track = program.strip()[:200]
        changed = True

    current = profile.interests if isinstance(profile.interests, dict) else {}
    hobbies_cur = [
        str(x).strip()
        for x in (current.get("hobbies") or [])
        if isinstance(x, str) and x.strip()
    ]
    recharge_cur = [
        str(x).strip()
        for x in (current.get("recharge") or [])
        if isinstance(x, str) and x.strip()
    ]
    notes_cur = [
        str(x).strip()
        for x in (current.get("notes") or [])
        if isinstance(x, str) and x.strip()
    ]

    hobiler = learned.get("hobiler") or learned.get("hobbies") or []
    sarj = learned.get("sarj") or learned.get("recharge") or []
    if not isinstance(hobiler, list):
        hobiler = []
    if not isinstance(sarj, list):
        sarj = []

    new_hobbies = _merge_string_lists(
        hobbies_cur, [str(x) for x in hobiler if isinstance(x, str)]
    )
    new_recharge = _merge_string_lists(
        recharge_cur, [str(x) for x in sarj if isinstance(x, str)]
    )

    if new_hobbies != hobbies_cur or new_recharge != recharge_cur:
        profile.interests = {
            "hobbies": new_hobbies,
            "recharge": new_recharge,
            "notes": notes_cur,
        }
        changed = True

    if not changed:
        return to_public_profile(profile)

    await db.flush()
    logger.info(
        "Learned profile merged | user_id=%s city=%s track=%s hobbies=%s",
        user_id,
        profile.city,
        profile.program_track,
        len(new_hobbies),
    )
    return to_public_profile(profile)


def _compute_streak(checkin_dates: list) -> int:
    """Count consecutive calendar days ending at the most recent checkin_date."""
    if not checkin_dates:
        return 0
    from datetime import timedelta

    sorted_days = sorted(set(checkin_dates), reverse=True)
    streak = 1
    for i in range(len(sorted_days) - 1):
        expected = sorted_days[i] - timedelta(days=1)
        if sorted_days[i + 1] == expected:
            streak += 1
        else:
            break
    return streak


async def get_profile_stats(
    db: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    user_id: uuid.UUID,
) -> dict[str, Any]:
    from backend.repositories.capacity_repo import CapacitySnapshotRepository
    from backend.repositories.checkin_repo import CheckinRepository, WeeklyTaskRepository

    checkin_repo = CheckinRepository(db)
    task_repo = WeeklyTaskRepository(db)
    snap_repo = CapacitySnapshotRepository(db)

    total_checkins = await checkin_repo.count_for_user(
        tenant_id=tenant_id, user_id=user_id
    )
    history = await checkin_repo.list_history(
        tenant_id=tenant_id, user_id=user_id, limit=365
    )
    streak = _compute_streak([s.checkin_date for s in history])
    tasks = await task_repo.list_for_user(tenant_id=tenant_id, user_id=user_id)
    completed_tasks = sum(1 for t in tasks if t.is_completed)
    snapshots = await snap_repo.list_for_user(
        tenant_id=tenant_id, user_id=user_id, limit=30
    )
    capacity_history = [
        {
            "score": float(s.score),
            "recorded_at": s.recorded_at.isoformat(),
        }
        for s in snapshots
    ]

    logger.info(
        "Profile stats | user_id=%s checkins=%s streak=%s",
        user_id,
        total_checkins,
        streak,
    )
    return {
        "total_checkins": total_checkins,
        "streak_days": streak,
        "completed_tasks": completed_tasks,
        "open_tasks": sum(1 for t in tasks if not t.is_completed),
        "capacity_history": capacity_history,
    }


def _extract_text_from_pdf(data: bytes) -> str:
    from backend.services.document_text import extract_text_from_pdf

    return extract_text_from_pdf(data)


def _heuristic_competencies(text: str) -> dict[str, Any]:
    skills = []
    for match in re.findall(
        r"\b(Python|JavaScript|TypeScript|React|Node\.?js|SQL|Docker|AWS|Git)\b",
        text,
        flags=re.IGNORECASE,
    ):
        skills.append(match)
    # dedupe preserve order
    seen = set()
    unique = []
    for s in skills:
        key = s.lower()
        if key not in seen:
            seen.add(key)
            unique.append(s)
    return {
        "skills": unique[:20],
        "summary": text[:400] if text else "",
        "experience_years": None,
    }


async def _extract_competencies_llm(text: str) -> dict[str, Any]:
    """LinkedIn metninden yapılandırılmış yetkinlik JSON'u (Gemini / OpenAI / Anthropic)."""
    from langchain_core.messages import HumanMessage, SystemMessage

    from backend.services.llm.provider import build_chat_llm

    prompt = (
        "Extract competencies as JSON with keys skills (string[]), "
        "summary (string), experience_years (number|null) from this LinkedIn text. "
        "Return ONLY valid JSON, no markdown.\n\n"
        f"{text[:6000]}"
    )
    llm = build_chat_llm(streaming=False)
    response = await llm.ainvoke(
        [
            SystemMessage(content="You extract structured competency JSON from resumes."),
            HumanMessage(content=prompt),
        ]
    )
    raw = response.content if isinstance(response.content, str) else str(response.content)
    raw = raw.strip()
    if raw.startswith("```"):
        raw = re.sub(r"^```(?:json)?\s*", "", raw)
        raw = re.sub(r"\s*```$", "", raw)
    return json.loads(raw or "{}")


async def extract_linkedin_competencies(
    db: AsyncSession,
    *,
    user_id: uuid.UUID,
    filename: str,
    data: bytes,
) -> dict[str, Any]:
    text = ""
    if filename.lower().endswith(".pdf"):
        text = _extract_text_from_pdf(data)
    else:
        try:
            text = data.decode("utf-8", errors="ignore")
        except Exception:
            text = ""

    fallback_required = len(text.strip()) < 40
    competencies: dict[str, Any]

    if fallback_required:
        competencies = {
            "skills": [],
            "summary": "",
            "experience_years": None,
            "notes": "PDF okunamadı — chat fallback gerekli",
        }
        source = "fallback"
    elif settings.llm_api_key:
        try:
            competencies = await _extract_competencies_llm(text)
            source = "llm"
        except Exception as exc:
            logger.error("LLM competency extract failed: %s", exc)
            competencies = _heuristic_competencies(text)
            source = "heuristic"
    else:
        competencies = _heuristic_competencies(text)
        source = "heuristic"

    repo = StudentProfileRepository(db)
    profile = await repo.get_by_user_id(user_id)
    if profile is None:
        raise AppError("Profile not found", code="NOT_FOUND", status_code=404)
    profile.competencies = competencies
    await db.flush()

    logger.info(
        "Competencies saved | user_id=%s source=%s fallback=%s",
        user_id,
        source,
        fallback_required,
    )
    return {
        "competencies": competencies,
        "source": source,
        "fallback_required": fallback_required,
    }

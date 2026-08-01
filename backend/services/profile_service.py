"""
backend/services/profile_service.py
S08/S09/S10–S12: Profile, onboarding, LinkedIn extract.
"""

from __future__ import annotations

import json
import logging
import re
import uuid
from decimal import Decimal
from io import BytesIO
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.config import settings
from backend.domain.errors.app_error import AppError
from backend.repositories.user_repo import StudentProfileRepository, UserRepository

logger = logging.getLogger(__name__)


def to_public_profile(profile) -> dict[str, Any]:
    return {
        "user_id": str(profile.user_id),
        "capacity_score": float(profile.capacity_score)
        if profile.capacity_score is not None
        else None,
        "linkedin_url": profile.linkedin_url,
        "bio": profile.bio,
        "competencies": profile.competencies,
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
) -> dict[str, Any]:
    repo = StudentProfileRepository(db)
    profile = await repo.get_by_user_id(user_id)
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
            onboarding_completed=onboarding_completed,
        )
        await repo.create(profile)
    else:
        profile.capacity_score = capacity_score
        if bio is not None:
            profile.bio = bio
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
        "Onboarding updated | user_id=%s capacity=%s", user_id, capacity_score
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
    try:
        from pypdf import PdfReader

        reader = PdfReader(BytesIO(data))
        parts = []
        for page in reader.pages:
            parts.append(page.extract_text() or "")
        return "\n".join(parts).strip()
    except Exception as exc:
        logger.error("PDF parse failed: %s", exc)
        return ""


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

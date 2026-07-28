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

    logger.info(
        "Onboarding updated | user_id=%s capacity=%s", user_id, capacity_score
    )
    return to_public_profile(profile)


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
            from openai import AsyncOpenAI

            client = AsyncOpenAI(api_key=settings.llm_api_key)
            prompt = (
                "Extract competencies as JSON with keys skills (string[]), "
                "summary (string), experience_years (number|null) from this LinkedIn text:\n\n"
                f"{text[:6000]}"
            )
            resp = await client.chat.completions.create(
                model=settings.llm_model,
                messages=[{"role": "user", "content": prompt}],
                response_format={"type": "json_object"},
            )
            competencies = json.loads(resp.choices[0].message.content or "{}")
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

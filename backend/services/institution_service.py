"""
backend/services/institution_service.py
S20–S25: Institution dashboard data.
"""

from __future__ import annotations

import logging
import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.repositories.risk_repo import RiskSignalRepository
from backend.repositories.user_repo import StudentProfileRepository, UserRepository
from backend.services.risk_service import compute_roi, compute_student_risk

logger = logging.getLogger(__name__)


async def list_students_with_risk(
    db: AsyncSession, *, tenant_id: uuid.UUID
) -> list[dict[str, Any]]:
    user_repo = UserRepository(db)
    profile_repo = StudentProfileRepository(db)
    risk_repo = RiskSignalRepository(db)

    users = [u for u in await user_repo.get_by_tenant(tenant_id) if u.role == "student"]
    rows: list[dict[str, Any]] = []

    for user in users:
        profile = await profile_repo.get_by_user_id(user.id)
        active = await risk_repo.get_active_for_user(user.id)
        if active is None:
            scored = await compute_student_risk(
                db, tenant_id=tenant_id, user_id=user.id
            )
            level = scored["level"]
            rationale = scored["rationale"]
            metrics = scored["metrics"]
        else:
            level = "red" if active.level == "high_risk" else active.level
            rationale = active.rationale
            metrics = active.metrics

        rows.append(
            {
                "user_id": str(user.id),
                "full_name": user.full_name,
                "email": user.email,
                "risk_level": level,
                "rationale": rationale,
                "metrics": metrics,
                "capacity_score": float(profile.capacity_score)
                if profile and profile.capacity_score is not None
                else None,
            }
        )

    logger.info("Institution student list | tenant_id=%s count=%s", tenant_id, len(rows))
    return rows


async def get_roi_metrics(
    db: AsyncSession, *, tenant_id: uuid.UUID
) -> dict[str, Any]:
    return await compute_roi(db, tenant_id=tenant_id)

"""
backend/services/institution_service.py
S20–S25: Institution dashboard data (batch queries, no N+1).
"""

from __future__ import annotations

import logging
import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.risk import RiskSignal
from backend.db.models.user import StudentProfile, User
from backend.repositories.checkin_repo import CheckinRepository, WeeklyTaskRepository
from backend.services.risk_service import compute_roi

logger = logging.getLogger(__name__)

_RISK_ORDER = {"red": 0, "high_risk": 0, "yellow": 1, "green": 2}


def _derive_risk_from_metrics(
    *,
    missed_checkin: bool,
    completion_rate: float,
    capacity: float,
) -> tuple[str, str, dict[str, Any]]:
    metrics = {
        "task_completion_rate": round(completion_rate, 2),
        "capacity_score": capacity,
        "missed_checkin": missed_checkin,
    }
    if missed_checkin and completion_rate < 0.3:
        return "red", "Check-in kaçırıldı ve görev tamamlanma oranı düşük.", metrics
    if capacity < 40 or completion_rate < 0.5:
        return "yellow", "Kapasite düşük veya görevler yarım kaldı.", metrics
    return "green", "Check-in ve görev metrikleri stabil.", metrics


async def list_students_with_risk(
    db: AsyncSession, *, tenant_id: uuid.UUID
) -> list[dict[str, Any]]:
    """Batch-load students, profiles, and active signals — no per-row writes."""
    users_result = await db.execute(
        select(User).where(User.tenant_id == tenant_id, User.role == "student")
    )
    users = list(users_result.scalars().all())
    if not users:
        return []

    user_ids = [u.id for u in users]

    profiles_result = await db.execute(
        select(StudentProfile).where(StudentProfile.user_id.in_(user_ids))
    )
    profiles = {p.user_id: p for p in profiles_result.scalars().all()}

    signals_result = await db.execute(
        select(RiskSignal).where(
            RiskSignal.tenant_id == tenant_id,
            RiskSignal.user_id.in_(user_ids),
            RiskSignal.is_active.is_(True),
        )
    )
    active_by_user: dict[uuid.UUID, RiskSignal] = {}
    for sig in signals_result.scalars().all():
        # Prefer highest severity if multiple active
        existing = active_by_user.get(sig.user_id)
        if existing is None or _RISK_ORDER.get(sig.level, 9) < _RISK_ORDER.get(
            existing.level, 9
        ):
            active_by_user[sig.user_id] = sig

    checkin_repo = CheckinRepository(db)
    task_repo = WeeklyTaskRepository(db)
    rows: list[dict[str, Any]] = []

    for user in users:
        active = active_by_user.get(user.id)
        profile = profiles.get(user.id)

        if active is not None:
            level = "red" if active.level == "high_risk" else active.level
            rationale = active.rationale
            metrics = active.metrics or {}
            updated_at = (
                active.created_at.isoformat()
                if getattr(active, "created_at", None)
                else None
            )
        else:
            current = await checkin_repo.get_current(
                tenant_id=tenant_id, user_id=user.id
            )
            tasks = await task_repo.list_for_user(
                tenant_id=tenant_id, user_id=user.id
            )
            completed = sum(1 for t in tasks if t.is_completed)
            total = len(tasks)
            completion_rate = (completed / total) if total else 1.0
            capacity = (
                float(profile.capacity_score)
                if profile and profile.capacity_score is not None
                else 70.0
            )
            missed_checkin = current is None or current.status == "pending"
            level, rationale, metrics = _derive_risk_from_metrics(
                missed_checkin=missed_checkin,
                completion_rate=completion_rate,
                capacity=capacity,
            )
            metrics["open_tasks"] = total - completed
            updated_at = None

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
                "updated_at": updated_at,
            }
        )

    rows.sort(
        key=lambda r: (
            _RISK_ORDER.get(str(r["risk_level"]), 9),
            (r.get("full_name") or r["email"] or "").lower(),
        )
    )

    logger.info("Institution student list | tenant_id=%s count=%s", tenant_id, len(rows))
    return rows


async def get_roi_metrics(
    db: AsyncSession, *, tenant_id: uuid.UUID
) -> dict[str, Any]:
    return await compute_roi(db, tenant_id=tenant_id)

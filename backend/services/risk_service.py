"""
backend/services/risk_service.py
S17/S22/S25: Risk scoring and institution signals (no raw chat).
"""

from __future__ import annotations

import logging
import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.risk import RiskSignal
from backend.repositories.checkin_repo import CheckinRepository, WeeklyTaskRepository
from backend.repositories.risk_repo import RiskSignalRepository
from backend.repositories.user_repo import StudentProfileRepository, UserRepository

logger = logging.getLogger(__name__)


async def record_high_risk_signal(
    session: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    user_id: uuid.UUID,
    category: str,
) -> None:
    """S17: Guardrail triggered → institution HIGH_RISK (no chat content)."""
    repo = RiskSignalRepository(session)
    rationale_map = {
        "critical": "Kritik güvenlik anahtar kelimesi tespit edildi; mentör görüşmesi önerilir.",
        "dropout": "Bırakma niyeti sinyali; proaktif mentör takibi önerilir.",
        "depression": "Düşük ruh hali sinyali; şefkatli yönlendirme uygulandı.",
    }
    await repo.create_signal(
        tenant_id=tenant_id,
        user_id=user_id,
        level="high_risk",
        category=category,
        rationale=rationale_map.get(category, "Yüksek risk sinyali."),
        metrics={"source": "guardrail", "category": category},
    )
    logger.info(
        "HIGH_RISK sinyali kaydedildi | user_id=%s category=%s",
        user_id,
        category,
    )


async def compute_student_risk(
    session: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    user_id: uuid.UUID,
) -> dict[str, Any]:
    """S22: Derive green/yellow/red from behavioral metrics."""
    checkin_repo = CheckinRepository(session)
    task_repo = WeeklyTaskRepository(session)
    profile_repo = StudentProfileRepository(session)
    risk_repo = RiskSignalRepository(session)

    active = await risk_repo.get_active_for_user(user_id)
    if active and active.level in ("high_risk", "red"):
        return {
            "level": "red" if active.level == "high_risk" else active.level,
            "rationale": active.rationale,
            "metrics": active.metrics or {},
        }

    current = await checkin_repo.get_current(tenant_id=tenant_id, user_id=user_id)
    tasks = await task_repo.list_for_user(tenant_id=tenant_id, user_id=user_id)
    profile = await profile_repo.get_by_user_id(user_id)

    completed = sum(1 for t in tasks if t.is_completed)
    total = len(tasks)
    completion_rate = (completed / total) if total else 1.0
    capacity = (
        float(profile.capacity_score)
        if profile and profile.capacity_score is not None
        else 70.0
    )
    missed_checkin = current is None or current.status == "pending"

    metrics = {
        "task_completion_rate": round(completion_rate, 2),
        "capacity_score": capacity,
        "missed_checkin": missed_checkin,
        "open_tasks": total - completed,
    }

    if missed_checkin and completion_rate < 0.3:
        level = "red"
        rationale = "Check-in kaçırıldı ve görev tamamlanma oranı düşük."
    elif capacity < 40 or completion_rate < 0.5:
        level = "yellow"
        rationale = "Kapasite düşük veya görevler yarım kaldı."
    else:
        level = "green"
        rationale = "Check-in ve görev metrikleri stabil."

    await risk_repo.create_signal(
        tenant_id=tenant_id,
        user_id=user_id,
        level=level,
        category="scoring",
        rationale=rationale,
        metrics=metrics,
    )
    return {"level": level, "rationale": rationale, "metrics": metrics}


async def compute_roi(
    session: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    revenue_per_student: float | None = None,
) -> dict[str, Any]:
    """S23/S24: Prevented dropouts + protected revenue."""
    from backend.db.models.tenant import Tenant

    user_repo = UserRepository(session)
    risk_repo = RiskSignalRepository(session)

    if revenue_per_student is None:
        t_result = await session.execute(select(Tenant).where(Tenant.id == tenant_id))
        tenant = t_result.scalar_one_or_none()
        revenue_per_student = (
            float(tenant.revenue_per_student)
            if tenant is not None and getattr(tenant, "revenue_per_student", None) is not None
            else 5000.0
        )

    students = [u for u in await user_repo.get_by_tenant(tenant_id) if u.role == "student"]
    active_signals = await risk_repo.list_for_tenant(tenant_id)

    result = await session.execute(
        select(RiskSignal).where(RiskSignal.tenant_id == tenant_id)
    )
    all_signals = list(result.scalars().all())

    # Prevented proxy: students who had high_risk/dropout signal but remain enrolled
    high_risk_user_ids = {
        s.user_id
        for s in all_signals
        if s.level in ("high_risk", "red") or s.category == "dropout"
    }
    still_active = {u.id for u in students}
    prevented = len(high_risk_user_ids & still_active)

    high_risk_active = sum(
        1 for s in active_signals if s.level in ("red", "high_risk")
    )

    return {
        "prevented_dropouts": prevented,
        "protected_revenue": round(prevented * float(revenue_per_student), 2),
        "revenue_per_student": float(revenue_per_student),
        "active_high_risk": high_risk_active,
        "total_students": len(students),
    }

"""
backend/services/risk_service.py
S17/S22/S25: Risk scoring and institution signals (no raw chat).
Daily window rules: missed days in last 7 + task completion + capacity.
"""

from __future__ import annotations

import logging
import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.risk import RiskSignal
from backend.repositories.checkin_repo import CheckinRepository, DailyTaskRepository
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


def derive_risk_level(
    *,
    missed_days_7: int,
    completion_rate: float,
    capacity: float,
    energy_avg: float | None = None,
    motivation_avg: float | None = None,
    signal_days: int = 0,
) -> tuple[str, str, dict[str, Any]]:
    """Pure function: map daily-window metrics → green/yellow/red."""
    metrics: dict[str, Any] = {
        "task_completion_rate": round(completion_rate, 2),
        "capacity_score": capacity,
        "missed_days_7": missed_days_7,
    }
    if energy_avg is not None:
        metrics["energy_avg"] = energy_avg
    if motivation_avg is not None:
        metrics["motivation_avg"] = motivation_avg
    if signal_days:
        metrics["signal_days"] = signal_days

    # Red: 5+ missed days in last 7 AND low completion
    if missed_days_7 >= 5 and completion_rate < 0.3:
        return (
            "red",
            "Son 7 günde check-in kaçırma yüksek ve görev tamamlanma oranı düşük.",
            metrics,
        )

    # Red from sustained low energy + motivation (need enough samples)
    if (
        signal_days >= 3
        and energy_avg is not None
        and motivation_avg is not None
        and energy_avg <= 3
        and motivation_avg <= 3
    ):
        return (
            "red",
            "Son günlerde enerji ve motivasyon sürekli düşük (check-in sinyalleri).",
            metrics,
        )

    # Yellow: 3+ missed OR low capacity OR mediocre completion
    if missed_days_7 >= 3 or capacity < 40 or completion_rate < 0.5:
        return (
            "yellow",
            "Check-in sürekliliği, kapasite veya görevler dikkat gerektiriyor.",
            metrics,
        )

    # Yellow from soft energy/motivation signals
    if signal_days >= 3 and (
        (energy_avg is not None and energy_avg <= 4)
        or (motivation_avg is not None and motivation_avg <= 4)
    ):
        return (
            "yellow",
            "Check-in sinyallerinde düşük enerji veya motivasyon eğilimi var.",
            metrics,
        )

    return "green", "Check-in ve görev metrikleri stabil.", metrics


async def compute_student_risk(
    session: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    user_id: uuid.UUID,
    persist: bool = False,
) -> dict[str, Any]:
    """
    Derive green/yellow/red from behavioral metrics + check-in signals.

    By default this is a pure read (no DB write). Pass persist=True to
    store a scoring signal (e.g. from a scheduled job).
    """
    checkin_repo = CheckinRepository(session)
    task_repo = DailyTaskRepository(session)
    profile_repo = StudentProfileRepository(session)
    risk_repo = RiskSignalRepository(session)

    active = await risk_repo.get_active_for_user(user_id)
    if active and active.level in ("high_risk", "red"):
        return {
            "level": "red" if active.level == "high_risk" else active.level,
            "rationale": active.rationale,
            "metrics": active.metrics or {},
        }

    missed_days_7 = await checkin_repo.count_missed_days(
        tenant_id=tenant_id, user_id=user_id, window_days=7
    )
    tasks = await task_repo.list_for_user(tenant_id=tenant_id, user_id=user_id)
    profile = await profile_repo.get_by_user_id(user_id)
    signal_avgs = await checkin_repo.avg_signals_last_days(
        tenant_id=tenant_id, user_id=user_id, window_days=7
    )

    completed = sum(1 for t in tasks if t.is_completed)
    total = len(tasks)
    completion_rate = (completed / total) if total else 1.0
    capacity = (
        float(profile.capacity_score)
        if profile and profile.capacity_score is not None
        else 70.0
    )

    level, rationale, metrics = derive_risk_level(
        missed_days_7=missed_days_7,
        completion_rate=completion_rate,
        capacity=capacity,
        energy_avg=signal_avgs.get("energy_avg"),
        motivation_avg=signal_avgs.get("motivation_avg"),
        signal_days=int(signal_avgs.get("signal_days") or 0),
    )
    metrics["open_tasks"] = total - completed

    if persist:
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

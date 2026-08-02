"""
backend/services/capacity_service.py
Orchestrates hybrid capacity recomputation and persistence.
"""

from __future__ import annotations

import logging
import uuid
from decimal import Decimal
from typing import Any, Mapping

from sqlalchemy.ext.asyncio import AsyncSession

from backend.repositories.capacity_repo import CapacitySnapshotRepository
from backend.repositories.checkin_repo import CheckinRepository, DailyTaskRepository
from backend.repositories.curriculum_repo import CurriculumRepository
from backend.repositories.user_repo import StudentProfileRepository
from backend.services.capacity import compute_capacity

logger = logging.getLogger(__name__)


async def _sum_curriculum_weekly_hours(
    db: AsyncSession, *, tenant_id: uuid.UUID
) -> float | None:
    curricula = await CurriculumRepository(db).list_by_tenant(tenant_id)
    hours = [
        int(c.weekly_hours)
        for c in curricula
        if getattr(c, "weekly_hours", None) is not None
    ]
    if not hours:
        return None
    return float(sum(hours))


async def recompute_for_user(
    db: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    user_id: uuid.UUID,
    state: Mapping[str, Any] | None = None,
    llm_delta: float = 0.0,
    source: str = "auto",
) -> dict[str, Any]:
    """
    Gather signals, run the pure capacity engine, persist score + snapshot.
    Returns {"score": float, "factors": dict, ...}.
    """
    profile_repo = StudentProfileRepository(db)
    checkin_repo = CheckinRepository(db)
    task_repo = DailyTaskRepository(db)
    snap_repo = CapacitySnapshotRepository(db)

    profile = await profile_repo.get_by_user_id(user_id)
    if profile is None:
        logger.warning("Capacity recompute skipped — no profile | user_id=%s", user_id)
        return {"score": None, "factors": {}}

    signal_avgs = await checkin_repo.avg_signals_last_days(
        tenant_id=tenant_id, user_id=user_id, window_days=7
    )
    missed = await checkin_repo.count_missed_days(
        tenant_id=tenant_id, user_id=user_id, window_days=7
    )
    tasks = await task_repo.list_for_user(tenant_id=tenant_id, user_id=user_id)
    curriculum_hours = await _sum_curriculum_weekly_hours(db, tenant_id=tenant_id)

    completed = sum(1 for t in tasks if t.is_completed)
    total = len(tasks)
    open_tasks = sum(
        1
        for t in tasks
        if not t.is_completed and getattr(t, "status", "active") != "suspended"
    )
    completion_rate = (completed / total) if total else None

    state = state or {}
    energy = state.get("enerji")
    if energy is None:
        energy = signal_avgs.get("energy_avg")
    motivation = state.get("motivasyon")
    if motivation is None:
        motivation = signal_avgs.get("motivation_avg")
    workload = state.get("yuk")

    # Prefer explicit llm_delta arg; fall back to state
    effective_delta = float(llm_delta or 0.0)
    if effective_delta == 0.0 and state.get("kapasite_delta") is not None:
        try:
            effective_delta = float(state["kapasite_delta"])
        except (TypeError, ValueError):
            effective_delta = 0.0

    previous = (
        float(profile.capacity_score) if profile.capacity_score is not None else None
    )

    result = compute_capacity(
        energy=float(energy) if energy is not None else None,
        motivation=float(motivation) if motivation is not None else None,
        workload=str(workload) if workload else None,
        completion_rate=completion_rate,
        missed_days_7=missed,
        open_tasks=open_tasks,
        signal_days=int(signal_avgs.get("signal_days") or 0),
        self_reported_stress=getattr(profile, "self_reported_stress", None),
        weekly_available_hours=(
            float(profile.weekly_available_hours)
            if getattr(profile, "weekly_available_hours", None) is not None
            else None
        ),
        curriculum_weekly_hours=curriculum_hours,
        competencies=profile.competencies if isinstance(profile.competencies, dict) else None,
        previous_score=previous,
        llm_delta=effective_delta,
    )

    score = Decimal(str(result["score"]))
    factors = result["factors"]
    if state.get("kapasite_neden"):
        factors = {**factors, "llm_neden": str(state["kapasite_neden"])[:200]}

    profile.capacity_score = score
    profile.capacity_source = source
    await db.flush()

    await snap_repo.record(
        tenant_id=tenant_id,
        user_id=user_id,
        score=score,
        source=source,
        factors=factors,
    )

    # Dominant factors for log (exclude meta keys)
    meta_keys = {"base", "w_behavior", "raw_score", "previous_score", "llm_neden"}
    ranked = sorted(
        ((k, v) for k, v in factors.items() if k not in meta_keys and isinstance(v, (int, float))),
        key=lambda kv: abs(float(kv[1])),
        reverse=True,
    )[:3]

    logger.info(
        "Capacity recomputed | user_id=%s score=%s source=%s top=%s",
        user_id,
        result["score"],
        source,
        ranked,
    )
    return result

"""
backend/services/institution_service.py
S20–S25: Institution dashboard data (batch queries, no N+1).
"""

from __future__ import annotations

import logging
import uuid
from collections import defaultdict
from datetime import date, timedelta
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.checkin import CheckinSession, DailyTask
from backend.db.models.risk import RiskSignal
from backend.db.models.tenant import Tenant
from backend.db.models.user import StudentProfile, User
from backend.domain.errors.app_error import AppError
from backend.services.risk_service import compute_roi, derive_risk_level

logger = logging.getLogger(__name__)

_RISK_ORDER = {"red": 0, "high_risk": 0, "yellow": 1, "green": 2}


async def list_students_with_risk(
    db: AsyncSession, *, tenant_id: uuid.UUID
) -> list[dict[str, Any]]:
    """Batch-load students, profiles, signals, check-ins, tasks — no N+1."""
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
        existing = active_by_user.get(sig.user_id)
        if existing is None or _RISK_ORDER.get(sig.level, 9) < _RISK_ORDER.get(
            existing.level, 9
        ):
            active_by_user[sig.user_id] = sig

    today = date.today()
    window_start = today - timedelta(days=6)

    checkins_result = await db.execute(
        select(CheckinSession.user_id, CheckinSession.checkin_date).where(
            CheckinSession.tenant_id == tenant_id,
            CheckinSession.user_id.in_(user_ids),
            CheckinSession.checkin_date >= window_start,
            CheckinSession.checkin_date <= today,
        )
    )
    checkin_dates_by_user: dict[uuid.UUID, set[date]] = defaultdict(set)
    for uid, cdate in checkins_result.all():
        checkin_dates_by_user[uid].add(cdate)

    tasks_result = await db.execute(
        select(DailyTask).where(
            DailyTask.tenant_id == tenant_id,
            DailyTask.user_id.in_(user_ids),
        )
    )
    tasks_by_user: dict[uuid.UUID, list[DailyTask]] = defaultdict(list)
    for task in tasks_result.scalars().all():
        tasks_by_user[task.user_id].append(task)

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
            present = checkin_dates_by_user.get(user.id, set())
            missed_days_7 = 7 - len(present)
            tasks = tasks_by_user.get(user.id, [])
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


async def get_student_detail(
    db: AsyncSession, *, tenant_id: uuid.UUID, user_id: uuid.UUID
) -> dict[str, Any]:
    """XAI detail for one student — metrics only, never raw chat."""
    user_result = await db.execute(
        select(User).where(
            User.id == user_id,
            User.tenant_id == tenant_id,
            User.role == "student",
        )
    )
    user = user_result.scalar_one_or_none()
    if user is None:
        raise AppError("Student not found", code="NOT_FOUND", status_code=404)

    rows = await list_students_with_risk(db, tenant_id=tenant_id)
    row = next((r for r in rows if r["user_id"] == str(user_id)), None)
    if row is None:
        raise AppError("Student not found", code="NOT_FOUND", status_code=404)

    # Extra aggregate metrics (no messages)
    today = date.today()
    hist = await db.execute(
        select(CheckinSession.checkin_date, CheckinSession.status, CheckinSession.mood_score)
        .where(
            CheckinSession.tenant_id == tenant_id,
            CheckinSession.user_id == user_id,
        )
        .order_by(CheckinSession.checkin_date.desc())
        .limit(30)
    )
    history = [
        {
            "checkin_date": r[0].isoformat(),
            "status": r[1],
            "mood_score": r[2],
        }
        for r in hist.all()
    ]

    task_stats = await db.execute(
        select(
            func.count(DailyTask.id),
            func.count(DailyTask.id).filter(DailyTask.is_completed.is_(True)),
        ).where(DailyTask.tenant_id == tenant_id, DailyTask.user_id == user_id)
    )
    total_tasks, completed_tasks = task_stats.one()

    return {
        **row,
        "checkin_history": history,
        "total_tasks": int(total_tasks or 0),
        "completed_tasks": int(completed_tasks or 0),
        "as_of": today.isoformat(),
    }


async def get_roi_metrics(
    db: AsyncSession, *, tenant_id: uuid.UUID
) -> dict[str, Any]:
    return await compute_roi(db, tenant_id=tenant_id)


async def get_overview(
    db: AsyncSession, *, tenant_id: uuid.UUID
) -> dict[str, Any]:
    """Tenant-wide dashboard: counts, completion rate, risk distribution, trend."""
    students = await list_students_with_risk(db, tenant_id=tenant_id)
    total = len(students)
    risk_dist = {"green": 0, "yellow": 0, "red": 0}
    capacity_sum = 0.0
    capacity_n = 0
    for s in students:
        level = "red" if s["risk_level"] == "high_risk" else s["risk_level"]
        if level in risk_dist:
            risk_dist[level] += 1
        if s.get("capacity_score") is not None:
            capacity_sum += float(s["capacity_score"])
            capacity_n += 1

    today = date.today()
    window_start = today - timedelta(days=6)
    checkin_count = await db.execute(
        select(func.count(func.distinct(CheckinSession.user_id))).where(
            CheckinSession.tenant_id == tenant_id,
            CheckinSession.checkin_date == today,
        )
    )
    checked_in_today = int(checkin_count.scalar_one() or 0)
    daily_completion_rate = (checked_in_today / total) if total else 0.0

    # 7-day trend: distinct students with a check-in per day
    trend_rows = await db.execute(
        select(CheckinSession.checkin_date, func.count(func.distinct(CheckinSession.user_id)))
        .where(
            CheckinSession.tenant_id == tenant_id,
            CheckinSession.checkin_date >= window_start,
            CheckinSession.checkin_date <= today,
        )
        .group_by(CheckinSession.checkin_date)
        .order_by(CheckinSession.checkin_date)
    )
    by_day = {r[0]: int(r[1]) for r in trend_rows.all()}
    trend = []
    for i in range(7):
        d = window_start + timedelta(days=i)
        trend.append(
            {
                "date": d.isoformat(),
                "checkins": by_day.get(d, 0),
                "rate": round((by_day.get(d, 0) / total), 2) if total else 0.0,
            }
        )

    roi = await compute_roi(db, tenant_id=tenant_id)

    logger.info("Institution overview | tenant_id=%s students=%s", tenant_id, total)
    return {
        "total_students": total,
        "checked_in_today": checked_in_today,
        "daily_checkin_rate": round(daily_completion_rate, 2),
        "avg_capacity": round(capacity_sum / capacity_n, 1) if capacity_n else None,
        "risk_distribution": risk_dist,
        "trend_7d": trend,
        "roi": roi,
    }


async def get_usage(
    db: AsyncSession, *, tenant_id: uuid.UUID
) -> dict[str, Any]:
    """Adoption metrics for the tenant."""
    student_count = await db.execute(
        select(func.count()).select_from(User).where(
            User.tenant_id == tenant_id, User.role == "student"
        )
    )
    total_students = int(student_count.scalar_one() or 0)

    today = date.today()
    week_ago = today - timedelta(days=6)
    active_week = await db.execute(
        select(func.count(func.distinct(CheckinSession.user_id))).where(
            CheckinSession.tenant_id == tenant_id,
            CheckinSession.checkin_date >= week_ago,
        )
    )
    active_7d = int(active_week.scalar_one() or 0)

    tasks_total = await db.execute(
        select(func.count()).select_from(DailyTask).where(DailyTask.tenant_id == tenant_id)
    )
    tasks_done = await db.execute(
        select(func.count())
        .select_from(DailyTask)
        .where(DailyTask.tenant_id == tenant_id, DailyTask.is_completed.is_(True))
    )
    total_t = int(tasks_total.scalar_one() or 0)
    done_t = int(tasks_done.scalar_one() or 0)

    return {
        "total_students": total_students,
        "active_students_7d": active_7d,
        "adoption_rate_7d": round(active_7d / total_students, 2) if total_students else 0.0,
        "total_tasks": total_t,
        "completed_tasks": done_t,
        "task_completion_rate": round(done_t / total_t, 2) if total_t else 0.0,
    }


async def get_staff_me(
    db: AsyncSession, *, tenant_id: uuid.UUID, user_id: uuid.UUID
) -> dict[str, Any]:
    user_result = await db.execute(
        select(User).where(User.id == user_id, User.tenant_id == tenant_id)
    )
    user = user_result.scalar_one_or_none()
    if user is None:
        raise AppError("User not found", code="NOT_FOUND", status_code=404)

    tenant_result = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
    tenant = tenant_result.scalar_one_or_none()
    if tenant is None:
        raise AppError("Tenant not found", code="NOT_FOUND", status_code=404)

    return {
        "id": str(user.id),
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role,
        "tenant": {
            "id": str(tenant.id),
            "name": tenant.name,
            "slug": tenant.slug,
            "revenue_per_student": float(tenant.revenue_per_student)
            if getattr(tenant, "revenue_per_student", None) is not None
            else None,
        },
    }


async def update_tenant_settings(
    db: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    revenue_per_student: float,
) -> dict[str, Any]:
    tenant_result = await db.execute(select(Tenant).where(Tenant.id == tenant_id))
    tenant = tenant_result.scalar_one_or_none()
    if tenant is None:
        raise AppError("Tenant not found", code="NOT_FOUND", status_code=404)
    tenant.revenue_per_student = revenue_per_student
    await db.flush()
    logger.info(
        "Tenant settings updated | tenant_id=%s revenue=%s",
        tenant_id,
        revenue_per_student,
    )
    return {
        "id": str(tenant.id),
        "name": tenant.name,
        "slug": tenant.slug,
        "revenue_per_student": float(tenant.revenue_per_student),
    }

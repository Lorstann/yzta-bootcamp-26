"""
backend/services/checkin_service.py
S07: Daily check-in session lifecycle.
"""

from __future__ import annotations

import logging
import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.domain.errors.app_error import AppError
from backend.repositories.checkin_repo import CheckinRepository, DailyTaskRepository
from backend.repositories.user_repo import StudentProfileRepository
from backend.services.task_balancing import limit_tasks, should_downscale

logger = logging.getLogger(__name__)


def serialize_session(session) -> dict[str, Any]:
    return {
        "id": str(session.id),
        "checkin_date": session.checkin_date.isoformat(),
        "status": session.status,
        "summary": session.summary,
        "mood_score": session.mood_score,
        "energy_level": getattr(session, "energy_level", None),
        "motivation_level": getattr(session, "motivation_level", None),
        "workload_level": getattr(session, "workload_level", None),
        "main_blocker": getattr(session, "main_blocker", None),
        "stage": getattr(session, "stage", None) or "opening",
        "turn_count": getattr(session, "turn_count", None) or 0,
        "messages": session.messages or [],
        "daily_tasks": [
            {
                "id": str(t.id),
                "title": t.title,
                "description": t.description,
                "is_completed": t.is_completed,
                "completed_at": t.completed_at.isoformat() if t.completed_at else None,
                "status": getattr(t, "status", None) or "active",
                "due_date": t.due_date.isoformat() if getattr(t, "due_date", None) else None,
                "created_at": t.created_at.isoformat() if getattr(t, "created_at", None) else None,
            }
            for t in (session.daily_tasks or [])
        ],
    }


async def get_or_start_checkin(
    db: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    user_id: uuid.UUID,
) -> dict[str, Any]:
    repo = CheckinRepository(db)
    current = await repo.get_current(tenant_id=tenant_id, user_id=user_id)
    if current and current.status in ("in_progress", "completed"):
        full = await repo.get_with_tasks(current.id)
        logger.info("Check-in resume | session_id=%s status=%s", current.id, current.status)
        return serialize_session(full or current)

    created = await repo.create_session(tenant_id=tenant_id, user_id=user_id)
    await repo.append_messages(
        created,
        [
            {
                "role": "assistant",
                "content": (
                    "Merhaba! Ben Equa. Bugün nasıl hissediyorsun? "
                    "Enerjin 1-10 arası nerede?"
                ),
            }
        ],
    )
    full = await repo.get_with_tasks(created.id)
    logger.info("Check-in started | session_id=%s", created.id)
    return serialize_session(full or created)


async def persist_turn_and_tasks(
    db: AsyncSession,
    *,
    session_id: uuid.UUID,
    tenant_id: uuid.UUID,
    user_id: uuid.UUID,
    user_message: str,
    assistant_message: str,
    daily_tasks: list[str] | None = None,
    weekly_tasks: list[str] | None = None,
    state: dict[str, Any] | None = None,
    stage: str | None = None,
    turn_count: int | None = None,
    checkin_completed: bool = False,
) -> None:
    """Persist chat turn + signals. Accepts daily_tasks (preferred) or weekly_tasks alias."""
    tasks = daily_tasks if daily_tasks is not None else weekly_tasks
    repo = CheckinRepository(db)
    task_repo = DailyTaskRepository(db)
    profile_repo = StudentProfileRepository(db)

    session = await repo.get_with_tasks(session_id)
    if session is None:
        raise AppError("Check-in session not found", code="NOT_FOUND", status_code=404)
    if session.user_id != user_id:
        raise AppError("Forbidden", code="FORBIDDEN", status_code=403)

    await repo.append_messages(
        session,
        [
            {"role": "user", "content": user_message},
            {"role": "assistant", "content": assistant_message},
        ],
    )

    if state is not None or stage is not None or turn_count is not None:
        await repo.update_signals(
            session,
            energy_level=(state or {}).get("enerji"),
            motivation_level=(state or {}).get("motivasyon"),
            workload_level=(state or {}).get("yuk"),
            main_blocker=(state or {}).get("engel"),
            stage=stage,
            turn_count=turn_count,
        )
        # Derive mood from energy when user hasn't set emoji mood
        if session.mood_score is None:
            from backend.services.checkin_flow import energy_to_mood

            derived = energy_to_mood((state or {}).get("enerji"))
            if derived is not None:
                await repo.set_mood(session, derived)

    profile = await profile_repo.get_by_user_id(user_id)
    capacity = profile.capacity_score if profile else None

    if should_downscale(capacity, user_message):
        suspended = await task_repo.suspend_incomplete(
            tenant_id=tenant_id, user_id=user_id
        )
        logger.info("Kapasite downscale | user_id=%s suspended=%s", user_id, suspended)

    if tasks:
        # Cap tasks further when energy is low
        energy = (state or {}).get("enerji")
        effective_capacity = capacity
        if energy is not None and int(energy) <= 4:
            effective_capacity = min(float(capacity) if capacity is not None else 40.0, 35.0)
        limited = limit_tasks(tasks, effective_capacity)
        await task_repo.replace_tasks(
            checkin_session_id=session_id,
            tenant_id=tenant_id,
            user_id=user_id,
            titles=limited,
        )
        await repo.complete(session, summary=assistant_message[:500])
        logger.info(
            "Check-in completed with tasks | session_id=%s count=%s",
            session_id,
            len(limited),
        )
    elif checkin_completed:
        await repo.complete(session, summary=assistant_message[:500])
        logger.info(
            "Check-in force-completed (max turns) | session_id=%s",
            session_id,
        )


async def list_task_history(
    db: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    user_id: uuid.UUID,
) -> list[dict[str, Any]]:
    task_repo = DailyTaskRepository(db)
    tasks = await task_repo.list_for_user(tenant_id=tenant_id, user_id=user_id)
    rows: list[dict[str, Any]] = []
    for t in tasks:
        session = getattr(t, "checkin_session", None)
        rows.append(
            {
                "id": str(t.id),
                "title": t.title,
                "description": t.description,
                "is_completed": t.is_completed,
                "completed_at": t.completed_at.isoformat() if t.completed_at else None,
                "status": getattr(t, "status", None) or "active",
                "due_date": t.due_date.isoformat() if getattr(t, "due_date", None) else None,
                "created_at": t.created_at.isoformat() if t.created_at else None,
                "checkin_date": session.checkin_date.isoformat() if session else None,
                "checkin_session_id": str(t.checkin_session_id),
            }
        )
    logger.info("Tasks listed | user_id=%s count=%s", user_id, len(rows))
    return rows


async def list_checkin_history(
    db: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    user_id: uuid.UUID,
    limit: int = 30,
) -> list[dict[str, Any]]:
    repo = CheckinRepository(db)
    sessions = await repo.list_history(
        tenant_id=tenant_id, user_id=user_id, limit=limit
    )
    rows = []
    for s in sessions:
        tasks = s.daily_tasks or []
        rows.append(
            {
                "id": str(s.id),
                "checkin_date": s.checkin_date.isoformat(),
                "status": s.status,
                "summary": s.summary,
                "mood_score": s.mood_score,
                "task_count": len(tasks),
                "completed_task_count": sum(1 for t in tasks if t.is_completed),
            }
        )
    logger.info("Check-in history | user_id=%s count=%s", user_id, len(rows))
    return rows


async def set_current_mood(
    db: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    user_id: uuid.UUID,
    mood_score: int,
) -> dict[str, Any]:
    if mood_score < 1 or mood_score > 5:
        raise AppError(
            "mood_score must be between 1 and 5",
            code="VALIDATION_ERROR",
            status_code=422,
        )
    data = await get_or_start_checkin(db, tenant_id=tenant_id, user_id=user_id)
    repo = CheckinRepository(db)
    session = await repo.get_with_tasks(uuid.UUID(data["id"]))
    if session is None:
        raise AppError("Check-in session not found", code="NOT_FOUND", status_code=404)
    await repo.set_mood(session, mood_score)
    full = await repo.get_with_tasks(session.id)
    logger.info("Mood updated | session_id=%s mood=%s", session.id, mood_score)
    return serialize_session(full or session)

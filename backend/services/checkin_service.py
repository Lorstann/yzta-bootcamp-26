"""
backend/services/checkin_service.py
S07: Weekly check-in session lifecycle.
"""

from __future__ import annotations

import logging
import uuid
from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from backend.domain.errors.app_error import AppError
from backend.repositories.checkin_repo import CheckinRepository, WeeklyTaskRepository
from backend.repositories.user_repo import StudentProfileRepository
from backend.services.task_balancing import limit_tasks, should_downscale

logger = logging.getLogger(__name__)


def serialize_session(session) -> dict[str, Any]:
    return {
        "id": str(session.id),
        "week_start": session.week_start.isoformat(),
        "status": session.status,
        "summary": session.summary,
        "messages": session.messages or [],
        "weekly_tasks": [
            {
                "id": str(t.id),
                "title": t.title,
                "description": t.description,
                "is_completed": t.is_completed,
                "completed_at": t.completed_at.isoformat() if t.completed_at else None,
            }
            for t in (session.weekly_tasks or [])
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
    # Welcome seed message
    await repo.append_messages(
        created,
        [
            {
                "role": "assistant",
                "content": "Merhaba! Ben Equa. Bu hafta nasıl hissediyorsun? Enerjin 1-10 arası nerede?",
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
    weekly_tasks: list[str] | None,
) -> None:
    repo = CheckinRepository(db)
    task_repo = WeeklyTaskRepository(db)
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

    profile = await profile_repo.get_by_user_id(user_id)
    capacity = profile.capacity_score if profile else None

    if should_downscale(capacity, user_message):
        suspended = await task_repo.suspend_incomplete(
            tenant_id=tenant_id, user_id=user_id
        )
        logger.info("Kapasite downscale | user_id=%s suspended=%s", user_id, suspended)

    if weekly_tasks:
        limited = limit_tasks(weekly_tasks, capacity)
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

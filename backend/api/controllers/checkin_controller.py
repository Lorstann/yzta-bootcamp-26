"""
backend/api/controllers/checkin_controller.py
"""

import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.dependencies.auth import CurrentUser
from backend.domain.errors.app_error import AppError
from backend.domain.schemas.checkin import TaskCompleteRequest
from backend.repositories.checkin_repo import WeeklyTaskRepository
from backend.services.checkin_service import get_or_start_checkin
from backend.utils.response import ok


async def get_current_checkin(db: AsyncSession, user: CurrentUser):
    data = await get_or_start_checkin(
        db, tenant_id=user.tenant_id, user_id=user.id
    )
    return ok(data=data)


async def complete_task(
    db: AsyncSession,
    user: CurrentUser,
    task_id: uuid.UUID,
    body: TaskCompleteRequest,
):
    repo = WeeklyTaskRepository(db)
    task = await repo.get_by_id(task_id)
    if task is None or task.user_id != user.id:
        raise AppError("Task not found", code="NOT_FOUND", status_code=404)
    updated = await repo.set_completed(task, body.is_completed)
    return ok(
        data={
            "id": str(updated.id),
            "title": updated.title,
            "is_completed": updated.is_completed,
            "completed_at": updated.completed_at.isoformat()
            if updated.completed_at
            else None,
        }
    )

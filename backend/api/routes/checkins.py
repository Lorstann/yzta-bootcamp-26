"""
backend/api/routes/checkins.py
"""

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.controllers import checkin_controller
from backend.api.dependencies.auth import CurrentUser, get_current_user, get_db_for_user
from backend.domain.schemas.checkin import TaskCompleteRequest

router = APIRouter(tags=["checkins"])


@router.post("/checkins")
@router.get("/checkins/current")
async def current_checkin(
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_for_user),
):
    return await checkin_controller.get_current_checkin(db, user)


@router.patch("/tasks/{task_id}")
async def patch_task(
    task_id: uuid.UUID,
    body: TaskCompleteRequest,
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_for_user),
):
    return await checkin_controller.complete_task(db, user, task_id, body)

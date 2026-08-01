"""
backend/api/routes/checkins.py
"""

import uuid

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.controllers import checkin_controller
from backend.api.dependencies.auth import CurrentUser, get_db_for_user, require_roles
from backend.domain.schemas.checkin import MoodUpdateRequest, TaskCompleteRequest

router = APIRouter(tags=["checkins"])

_student = require_roles("student")


@router.post("/checkins")
@router.get("/checkins/current")
async def current_checkin(
    user: CurrentUser = Depends(_student),
    db: AsyncSession = Depends(get_db_for_user),
):
    return await checkin_controller.get_current_checkin(db, user)


@router.get("/checkins/history")
async def checkin_history(
    limit: int = Query(default=30, ge=1, le=365),
    user: CurrentUser = Depends(_student),
    db: AsyncSession = Depends(get_db_for_user),
):
    return await checkin_controller.list_history(db, user, limit=limit)


@router.patch("/checkins/current/mood")
async def patch_mood(
    body: MoodUpdateRequest,
    user: CurrentUser = Depends(_student),
    db: AsyncSession = Depends(get_db_for_user),
):
    return await checkin_controller.update_mood(db, user, body)


@router.get("/tasks")
async def list_tasks(
    user: CurrentUser = Depends(_student),
    db: AsyncSession = Depends(get_db_for_user),
):
    return await checkin_controller.list_tasks(db, user)


@router.patch("/tasks/{task_id}")
async def patch_task(
    task_id: uuid.UUID,
    body: TaskCompleteRequest,
    user: CurrentUser = Depends(_student),
    db: AsyncSession = Depends(get_db_for_user),
):
    return await checkin_controller.complete_task(db, user, task_id, body)

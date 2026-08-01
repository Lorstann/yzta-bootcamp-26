"""
backend/api/routes/institution.py
"""

import uuid

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.controllers import institution_controller
from backend.api.dependencies.auth import CurrentUser, get_db_for_user, require_roles
from backend.domain.schemas.institution import (
    InstitutionAssistantRequest,
    TenantSettingsUpdate,
)

router = APIRouter(prefix="/institution", tags=["institution"])

_staff = require_roles("instructor", "admin")
_admin = require_roles("admin")


@router.get("/students")
async def institution_students(
    user: CurrentUser = Depends(_staff),
    db: AsyncSession = Depends(get_db_for_user),
):
    return await institution_controller.list_students(db, user)


@router.get("/students/{student_id}")
async def institution_student_detail(
    student_id: uuid.UUID,
    user: CurrentUser = Depends(_staff),
    db: AsyncSession = Depends(get_db_for_user),
):
    return await institution_controller.get_student(db, user, student_id)


@router.get("/roi")
async def institution_roi(
    user: CurrentUser = Depends(_staff),
    db: AsyncSession = Depends(get_db_for_user),
):
    return await institution_controller.get_roi(db, user)


@router.get("/overview")
async def institution_overview(
    user: CurrentUser = Depends(_staff),
    db: AsyncSession = Depends(get_db_for_user),
):
    return await institution_controller.get_overview(db, user)


@router.get("/usage")
async def institution_usage(
    user: CurrentUser = Depends(_staff),
    db: AsyncSession = Depends(get_db_for_user),
):
    return await institution_controller.get_usage(db, user)


@router.get("/me")
async def institution_me(
    user: CurrentUser = Depends(_staff),
    db: AsyncSession = Depends(get_db_for_user),
):
    return await institution_controller.get_me(db, user)


@router.patch("/settings")
async def institution_settings(
    body: TenantSettingsUpdate,
    user: CurrentUser = Depends(_admin),
    db: AsyncSession = Depends(get_db_for_user),
):
    return await institution_controller.patch_settings(db, user, body)


@router.post("/assistant/stream")
async def institution_assistant_stream(
    body: InstitutionAssistantRequest,
    user: CurrentUser = Depends(_staff),
    db: AsyncSession = Depends(get_db_for_user),
):
    return await institution_controller.assistant_stream(db, user, body)

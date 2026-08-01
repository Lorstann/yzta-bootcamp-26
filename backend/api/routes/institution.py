"""
backend/api/routes/institution.py
"""

import uuid

from fastapi import APIRouter, Depends, File, Form, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.controllers import institution_controller
from backend.api.dependencies.auth import CurrentUser, get_db_for_user, require_roles
from backend.domain.schemas.curriculum import CurriculumCreateText
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


@router.get("/curriculum")
async def institution_curriculum_list(
    user: CurrentUser = Depends(_staff),
    db: AsyncSession = Depends(get_db_for_user),
):
    return await institution_controller.list_curriculum(db, user)


@router.post("/curriculum")
async def institution_curriculum_upload(
    file: UploadFile = File(...),
    title: str | None = Form(default=None),
    user: CurrentUser = Depends(_admin),
    db: AsyncSession = Depends(get_db_for_user),
):
    return await institution_controller.upload_curriculum(db, user, file, title)


@router.post("/curriculum/text")
async def institution_curriculum_text(
    body: CurriculumCreateText,
    user: CurrentUser = Depends(_admin),
    db: AsyncSession = Depends(get_db_for_user),
):
    return await institution_controller.create_curriculum_text(db, user, body)


@router.delete("/curriculum/{curriculum_id}")
async def institution_curriculum_delete(
    curriculum_id: uuid.UUID,
    user: CurrentUser = Depends(_admin),
    db: AsyncSession = Depends(get_db_for_user),
):
    return await institution_controller.delete_curriculum(db, user, curriculum_id)

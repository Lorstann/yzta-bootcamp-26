"""
backend/api/routes/profiles.py
"""

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.controllers import profile_controller
from backend.api.dependencies.auth import CurrentUser, get_db_for_user, require_roles
from backend.domain.schemas.profile import OnboardingUpdateRequest

router = APIRouter(prefix="/profiles", tags=["profiles"])

_student = require_roles("student")


@router.get("/me")
async def profile_me(
    user: CurrentUser = Depends(_student),
    db: AsyncSession = Depends(get_db_for_user),
):
    return await profile_controller.get_me(db, user)


@router.get("/me/stats")
async def profile_stats(
    user: CurrentUser = Depends(_student),
    db: AsyncSession = Depends(get_db_for_user),
):
    return await profile_controller.get_stats(db, user)


@router.patch("/me/onboarding")
async def profile_onboarding(
    body: OnboardingUpdateRequest,
    user: CurrentUser = Depends(_student),
    db: AsyncSession = Depends(get_db_for_user),
):
    return await profile_controller.update_onboarding(db, user, body)


@router.post("/me/linkedin")
async def profile_linkedin(
    file: UploadFile = File(...),
    user: CurrentUser = Depends(_student),
    db: AsyncSession = Depends(get_db_for_user),
):
    return await profile_controller.upload_linkedin(db, user, file)

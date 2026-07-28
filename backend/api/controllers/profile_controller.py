"""
backend/api/controllers/profile_controller.py
"""

from fastapi import UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.dependencies.auth import CurrentUser
from backend.domain.schemas.profile import OnboardingUpdateRequest
from backend.services import profile_service
from backend.utils.response import ok


async def get_me(db: AsyncSession, user: CurrentUser):
    data = await profile_service.get_profile(db, user_id=user.id)
    return ok(data=data)


async def update_onboarding(
    db: AsyncSession, user: CurrentUser, body: OnboardingUpdateRequest
):
    data = await profile_service.update_onboarding(
        db,
        user_id=user.id,
        capacity_score=body.capacity_score,
        bio=body.bio,
        onboarding_completed=body.onboarding_completed,
    )
    return ok(data=data)


async def upload_linkedin(db: AsyncSession, user: CurrentUser, file: UploadFile):
    raw = await file.read()
    data = await profile_service.extract_linkedin_competencies(
        db,
        user_id=user.id,
        filename=file.filename or "upload.bin",
        data=raw,
    )
    return ok(data=data)

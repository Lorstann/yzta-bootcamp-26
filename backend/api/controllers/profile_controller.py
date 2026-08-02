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


async def get_stats(db: AsyncSession, user: CurrentUser):
    data = await profile_service.get_profile_stats(
        db, tenant_id=user.tenant_id, user_id=user.id
    )
    return ok(data=data)


async def update_onboarding(
    db: AsyncSession, user: CurrentUser, body: OnboardingUpdateRequest
):
    data = await profile_service.update_onboarding(
        db,
        user_id=user.id,
        bio=body.bio,
        onboarding_completed=body.onboarding_completed,
        city=body.city,
        district=body.district,
        program_track=body.program_track,
        interests=body.interests,
        self_reported_stress=body.self_reported_stress,
        weekly_available_hours=body.weekly_available_hours,
    )
    return ok(data=data)


async def upload_linkedin(db: AsyncSession, user: CurrentUser, file: UploadFile):
    filename = file.filename or "upload.bin"
    content_type = (file.content_type or "").lower()
    allowed = {
        "application/pdf",
        "text/plain",
        "application/octet-stream",
    }
    if content_type and content_type not in allowed:
        from backend.domain.errors.app_error import AppError

        raise AppError(
            "Sadece PDF veya metin dosyası yükleyebilirsin.",
            code="INVALID_FILE_TYPE",
            status_code=400,
        )

    raw = await file.read()
    max_bytes = 10 * 1024 * 1024
    if len(raw) > max_bytes:
        from backend.domain.errors.app_error import AppError

        raise AppError(
            "Dosya 10 MB sınırını aşıyor. Daha küçük bir PDF dene.",
            code="FILE_TOO_LARGE",
            status_code=400,
        )
    if not filename.lower().endswith((".pdf", ".txt")):
        from backend.domain.errors.app_error import AppError

        raise AppError(
            "Dosya uzantısı .pdf veya .txt olmalı.",
            code="INVALID_FILE_TYPE",
            status_code=400,
        )

    data = await profile_service.extract_linkedin_competencies(
        db,
        user_id=user.id,
        filename=filename,
        data=raw,
    )
    return ok(data=data)

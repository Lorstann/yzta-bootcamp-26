"""
backend/api/controllers/institution_controller.py
"""

from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.dependencies.auth import CurrentUser
from backend.domain.errors.app_error import AppError
from backend.services import institution_service
from backend.utils.response import ok


def _ensure_staff(user: CurrentUser) -> None:
    if user.role not in ("instructor", "admin"):
        raise AppError("Forbidden", code="FORBIDDEN", status_code=403)


async def list_students(db: AsyncSession, user: CurrentUser):
    _ensure_staff(user)
    rows = await institution_service.list_students_with_risk(
        db, tenant_id=user.tenant_id
    )
    return ok(data={"students": rows})


async def get_roi(db: AsyncSession, user: CurrentUser):
    _ensure_staff(user)
    metrics = await institution_service.get_roi_metrics(db, tenant_id=user.tenant_id)
    return ok(data=metrics)

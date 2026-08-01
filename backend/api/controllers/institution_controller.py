"""
backend/api/controllers/institution_controller.py
"""

from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.dependencies.auth import CurrentUser
from backend.services import institution_service
from backend.utils.response import ok


async def list_students(db: AsyncSession, user: CurrentUser):
    rows = await institution_service.list_students_with_risk(
        db, tenant_id=user.tenant_id
    )
    return ok(data={"students": rows})


async def get_roi(db: AsyncSession, user: CurrentUser):
    metrics = await institution_service.get_roi_metrics(db, tenant_id=user.tenant_id)
    return ok(data=metrics)

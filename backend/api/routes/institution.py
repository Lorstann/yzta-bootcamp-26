"""
backend/api/routes/institution.py
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.controllers import institution_controller
from backend.api.dependencies.auth import CurrentUser, get_db_for_user, require_roles

router = APIRouter(prefix="/institution", tags=["institution"])

_staff = require_roles("instructor", "admin")


@router.get("/students")
async def institution_students(
    user: CurrentUser = Depends(_staff),
    db: AsyncSession = Depends(get_db_for_user),
):
    return await institution_controller.list_students(db, user)


@router.get("/roi")
async def institution_roi(
    user: CurrentUser = Depends(_staff),
    db: AsyncSession = Depends(get_db_for_user),
):
    return await institution_controller.get_roi(db, user)

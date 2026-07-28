"""
backend/api/routes/institution.py
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.controllers import institution_controller
from backend.api.dependencies.auth import CurrentUser, get_current_user, get_db_for_user

router = APIRouter(prefix="/institution", tags=["institution"])


@router.get("/students")
async def institution_students(
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_for_user),
):
    return await institution_controller.list_students(db, user)


@router.get("/roi")
async def institution_roi(
    user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db_for_user),
):
    return await institution_controller.get_roi(db, user)

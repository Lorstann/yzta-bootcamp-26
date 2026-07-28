"""
backend/api/routes/auth.py
"""

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from backend.api.controllers import auth_controller
from backend.api.dependencies.db import get_db
from backend.domain.schemas.auth import LoginRequest, RegisterRequest

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", status_code=201)
async def register_endpoint(
    body: RegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    return await auth_controller.register(db, body)


@router.post("/login")
async def login_endpoint(
    body: LoginRequest,
    db: AsyncSession = Depends(get_db),
):
    return await auth_controller.login(db, body)

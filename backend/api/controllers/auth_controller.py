"""
backend/api/controllers/auth_controller.py
"""

from sqlalchemy.ext.asyncio import AsyncSession

from backend.domain.schemas.auth import LoginRequest, RegisterRequest
from backend.services.user_auth_flow import login_user, register_user
from backend.utils.response import ok


async def register(db: AsyncSession, body: RegisterRequest):
    data = await register_user(
        db,
        tenant_slug=body.tenant_slug,
        email=str(body.email),
        password=body.password,
        full_name=body.full_name,
        role=body.role,
    )
    return ok(data=data, meta={})


async def login(db: AsyncSession, body: LoginRequest):
    data = await login_user(
        db,
        tenant_slug=body.tenant_slug,
        email=str(body.email),
        password=body.password,
    )
    return ok(data=data, meta={})

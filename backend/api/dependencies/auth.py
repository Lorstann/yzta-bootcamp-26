"""
backend/api/dependencies/auth.py
JWT authentication + tenant-scoped DB session.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import AsyncGenerator, Literal

from fastapi import Depends, Header
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.session import AsyncSessionLocal
from backend.db.tenant_context import apply_tenant_context
from backend.domain.errors.app_error import AppError
from backend.services.auth_service import decode_access_token

_bearer = HTTPBearer(auto_error=False)


@dataclass(frozen=True)
class CurrentUser:
    id: uuid.UUID
    tenant_id: uuid.UUID
    role: str
    email: str


async def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(_bearer),
) -> CurrentUser:
    if credentials is None or not credentials.credentials:
        raise AppError("Authentication required", code="UNAUTHENTICATED", status_code=401)

    payload = decode_access_token(credentials.credentials)
    try:
        return CurrentUser(
            id=uuid.UUID(payload["sub"]),
            tenant_id=uuid.UUID(payload["tenant_id"]),
            role=str(payload.get("role", "student")),
            email=str(payload.get("email", "")),
        )
    except (KeyError, ValueError) as exc:
        raise AppError("Invalid token", code="INVALID_TOKEN", status_code=401) from exc


def require_roles(*roles: Literal["student", "instructor", "admin"]):
    async def _dep(user: CurrentUser = Depends(get_current_user)) -> CurrentUser:
        if user.role not in roles:
            raise AppError("Forbidden", code="FORBIDDEN", status_code=403)
        return user

    return _dep


async def get_db_for_user(
    user: CurrentUser = Depends(get_current_user),
) -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        try:
            await apply_tenant_context(session, user.tenant_id)
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise


async def get_optional_db(
    x_tenant_id: str | None = Header(default=None, alias="X-Tenant-Id"),
) -> AsyncGenerator[AsyncSession, None]:
    """DB session with optional tenant header (dev/chat fallback)."""
    async with AsyncSessionLocal() as session:
        try:
            if x_tenant_id:
                await apply_tenant_context(session, uuid.UUID(x_tenant_id))
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

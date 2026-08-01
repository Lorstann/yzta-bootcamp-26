"""
backend/services/user_auth_flow.py
Register/login orchestration (no FastAPI).
"""

from __future__ import annotations

import logging
import uuid
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.tenant import Tenant
from backend.db.models.user import StudentProfile, User
from backend.db.tenant_context import apply_tenant_context
from backend.domain.errors.app_error import AppError
from backend.repositories.user_repo import UserRepository
from backend.services.auth_service import (
    authenticate_credentials,
    create_access_token,
    hash_password,
)

logger = logging.getLogger(__name__)


def to_public_user(user: User, *, onboarding_completed: bool | None = None) -> dict[str, Any]:
    data: dict[str, Any] = {
        "id": str(user.id),
        "tenant_id": str(user.tenant_id),
        "email": user.email,
        "full_name": user.full_name,
        "role": user.role,
    }
    if onboarding_completed is not None:
        data["onboarding_completed"] = onboarding_completed
    return data


async def _get_tenant_by_slug(db: AsyncSession, slug: str) -> Tenant:
    result = await db.execute(select(Tenant).where(Tenant.slug == slug, Tenant.is_active.is_(True)))
    tenant = result.scalar_one_or_none()
    if tenant is None:
        raise AppError("Invalid credentials", code="INVALID_CREDENTIALS", status_code=401)
    return tenant


async def register_user(
    db: AsyncSession,
    *,
    tenant_slug: str,
    email: str,
    password: str,
    full_name: str,
    role: str = "student",
) -> dict[str, Any]:
    tenant = await _get_tenant_by_slug(db, tenant_slug)
    await apply_tenant_context(db, tenant.id)

    repo = UserRepository(db)
    existing = await repo.get_by_email(tenant.id, email.lower())
    if existing:
        raise AppError("Email already registered", code="CONFLICT", status_code=409)

    user = User(
        tenant_id=tenant.id,
        email=email.lower(),
        full_name=full_name,
        role=role,
        password_hash=hash_password(password),
        is_active=True,
    )
    await repo.create(user)

    if role == "student":
        profile = StudentProfile(
            user_id=user.id,
            tenant_id=tenant.id,
            onboarding_completed=False,
        )
        db.add(profile)
        await db.flush()

    token = create_access_token(
        user_id=user.id,
        tenant_id=tenant.id,
        role=user.role,
        email=user.email,
    )
    logger.info("User registered | user_id=%s tenant_id=%s", user.id, tenant.id)
    onboarded = None if role != "student" else False
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": to_public_user(user, onboarding_completed=onboarded),
    }


async def login_user(
    db: AsyncSession,
    *,
    tenant_slug: str,
    email: str,
    password: str,
) -> dict[str, Any]:
    tenant = await _get_tenant_by_slug(db, tenant_slug)
    await apply_tenant_context(db, tenant.id)

    repo = UserRepository(db)
    user = await repo.get_by_email(tenant.id, email.lower())
    if user is None or not user.is_active:
        raise AppError("Invalid credentials", code="INVALID_CREDENTIALS", status_code=401)

    authenticate_credentials(password=password, password_hash=user.password_hash)

    token = create_access_token(
        user_id=user.id,
        tenant_id=tenant.id,
        role=user.role,
        email=user.email,
    )
    logger.info("User login | user_id=%s", user.id)
    onboarded: bool | None = None
    if user.role == "student":
        from backend.repositories.user_repo import StudentProfileRepository

        profile = await StudentProfileRepository(db).get_by_user_id(user.id)
        onboarded = bool(profile.onboarding_completed) if profile else False
    return {
        "access_token": token,
        "token_type": "bearer",
        "user": to_public_user(user, onboarding_completed=onboarded),
    }

"""
backend/services/auth_service.py
JWT auth: register, login, token create/verify. No FastAPI imports.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
import jwt

from backend.config import settings
from backend.domain.errors.app_error import AppError


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))


def create_access_token(
    *,
    user_id: uuid.UUID,
    tenant_id: uuid.UUID,
    role: str,
    email: str,
) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": str(user_id),
        "tenant_id": str(tenant_id),
        "role": role,
        "email": email,
        "iat": now,
        "exp": now + timedelta(minutes=settings.jwt_expire_minutes),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict[str, Any]:
    try:
        return jwt.decode(
            token,
            settings.jwt_secret,
            algorithms=[settings.jwt_algorithm],
        )
    except jwt.ExpiredSignatureError as exc:
        raise AppError("Token expired", code="TOKEN_EXPIRED", status_code=401) from exc
    except jwt.InvalidTokenError as exc:
        raise AppError("Invalid token", code="INVALID_TOKEN", status_code=401) from exc


def authenticate_credentials(
    *,
    password: str,
    password_hash: str | None,
) -> None:
    if not password_hash or not verify_password(password, password_hash):
        raise AppError("Invalid credentials", code="INVALID_CREDENTIALS", status_code=401)

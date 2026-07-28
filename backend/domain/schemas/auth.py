"""
backend/domain/schemas/auth.py
"""

from __future__ import annotations

from typing import Literal, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, EmailStr, Field


class RegisterRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tenant_slug: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=8, max_length=128)
    full_name: str = Field(..., min_length=1, max_length=255)
    role: Literal["student", "instructor", "admin"] = "student"


class LoginRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    tenant_slug: str = Field(..., min_length=2, max_length=100)
    email: EmailStr
    password: str = Field(..., min_length=1, max_length=128)


class PublicUser(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID
    tenant_id: UUID
    email: str
    full_name: Optional[str] = None
    role: str


class AuthTokenData(BaseModel):
    model_config = ConfigDict(extra="forbid")

    access_token: str
    token_type: str = "bearer"
    user: PublicUser

"""
backend/domain/schemas/profile.py
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class ProfileOut(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_id: UUID
    capacity_score: Optional[Decimal] = None
    linkedin_url: Optional[str] = None
    bio: Optional[str] = None
    competencies: Optional[dict[str, Any]] = None
    onboarding_completed: bool


class OnboardingUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    capacity_score: Decimal = Field(..., ge=0, le=100)
    bio: Optional[str] = Field(default=None, max_length=2000)
    onboarding_completed: bool = True


class CompetencyExtractOut(BaseModel):
    model_config = ConfigDict(extra="forbid")

    competencies: dict[str, Any]
    source: str
    fallback_required: bool = False

"""
backend/domain/schemas/profile.py
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class InterestsPayload(BaseModel):
    model_config = ConfigDict(extra="forbid")

    hobbies: list[str] = Field(default_factory=list)
    recharge: list[str] = Field(default_factory=list)
    notes: list[str] = Field(default_factory=list)


class ProfileOut(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_id: UUID
    capacity_score: Optional[Decimal] = None
    capacity_source: Optional[str] = None
    capacity_factors: Optional[dict[str, Any]] = None
    capacity_updated_at: Optional[str] = None
    self_reported_stress: Optional[int] = None
    weekly_available_hours: Optional[int] = None
    linkedin_url: Optional[str] = None
    bio: Optional[str] = None
    competencies: Optional[dict[str, Any]] = None
    city: Optional[str] = None
    district: Optional[str] = None
    program_track: Optional[str] = None
    interests: Optional[dict[str, Any]] = None
    onboarding_completed: bool


class OnboardingUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    bio: Optional[str] = Field(default=None, max_length=2000)
    city: Optional[str] = Field(default=None, max_length=120)
    district: Optional[str] = Field(default=None, max_length=120)
    program_track: Optional[str] = Field(default=None, max_length=200)
    interests: Optional[InterestsPayload] = None
    self_reported_stress: Optional[int] = Field(default=None, ge=1, le=5)
    weekly_available_hours: Optional[int] = Field(default=None, ge=0, le=80)
    onboarding_completed: bool = True


class CompetencyExtractOut(BaseModel):
    model_config = ConfigDict(extra="forbid")

    competencies: dict[str, Any]
    source: str
    fallback_required: bool = False

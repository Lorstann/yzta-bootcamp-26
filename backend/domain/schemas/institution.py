"""
backend/domain/schemas/institution.py
"""

from __future__ import annotations

from typing import Any, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class StudentRiskRow(BaseModel):
    model_config = ConfigDict(extra="forbid")

    user_id: UUID
    full_name: Optional[str] = None
    email: str
    risk_level: str
    rationale: Optional[str] = None
    capacity_score: Optional[float] = None
    metrics: Optional[dict[str, Any]] = None
    updated_at: Optional[str] = None


class RoiMetrics(BaseModel):
    model_config = ConfigDict(extra="forbid")

    prevented_dropouts: int
    protected_revenue: float
    revenue_per_student: float
    active_high_risk: int
    total_students: int


class TenantSettingsUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    revenue_per_student: float = Field(gt=0, le=1_000_000)


class InstitutionAssistantRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    message: str = Field(min_length=1, max_length=2000)

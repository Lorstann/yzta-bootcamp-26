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
    risk_level: str = "green"
    rationale: Optional[str] = None
    metrics: Optional[dict[str, Any]] = None
    capacity_score: Optional[float] = None


class RoiMetrics(BaseModel):
    model_config = ConfigDict(extra="forbid")

    prevented_dropouts: int = 0
    protected_revenue: float = 0.0
    revenue_per_student: float = Field(default=5000.0)
    active_high_risk: int = 0
    total_students: int = 0

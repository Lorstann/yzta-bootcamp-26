"""
backend/domain/schemas/checkin.py
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Literal, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CheckinMessage(BaseModel):
    model_config = ConfigDict(extra="forbid")

    role: Literal["user", "assistant"]
    content: str


class WeeklyTaskOut(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID
    title: str
    description: Optional[str] = None
    is_completed: bool
    completed_at: Optional[datetime] = None


class CheckinSessionOut(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID
    week_start: date
    status: str
    summary: Optional[str] = None
    messages: list[dict[str, Any]] = Field(default_factory=list)
    weekly_tasks: list[WeeklyTaskOut] = Field(default_factory=list)


class TaskCompleteRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    is_completed: bool = True

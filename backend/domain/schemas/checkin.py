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
    status: Literal["active", "suspended"] = "active"
    due_date: Optional[date] = None
    created_at: Optional[datetime] = None
    week_start: Optional[date] = None
    checkin_session_id: Optional[UUID] = None


class CheckinSessionOut(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID
    week_start: date
    status: str
    summary: Optional[str] = None
    mood_score: Optional[int] = None
    messages: list[dict[str, Any]] = Field(default_factory=list)
    weekly_tasks: list[WeeklyTaskOut] = Field(default_factory=list)


class TaskCompleteRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    is_completed: bool = True


class MoodUpdateRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    mood_score: int = Field(ge=1, le=5)


class CheckinHistoryItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID
    week_start: date
    status: str
    summary: Optional[str] = None
    mood_score: Optional[int] = None
    task_count: int = 0
    completed_task_count: int = 0


class ProfileStatsOut(BaseModel):
    model_config = ConfigDict(extra="forbid")

    total_checkins: int
    streak_weeks: int
    completed_tasks: int
    open_tasks: int = 0
    capacity_history: list[dict[str, Any]] = Field(default_factory=list)

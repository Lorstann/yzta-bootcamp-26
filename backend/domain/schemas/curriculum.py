"""
backend/domain/schemas/curriculum.py
"""

from __future__ import annotations

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class CurriculumCreateText(BaseModel):
    model_config = ConfigDict(extra="forbid")

    title: str = Field(..., min_length=1, max_length=500)
    text: str = Field(..., min_length=1, max_length=500_000)
    description: Optional[str] = Field(default=None, max_length=2000)


class CurriculumOut(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: UUID
    title: str
    description: Optional[str] = None
    source_type: str
    file_name: Optional[str] = None
    chunk_count: Optional[int] = None
    is_active: bool
    created_at: datetime

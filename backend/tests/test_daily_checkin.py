"""Tests for daily check-in service serialization and mood bounds."""

from __future__ import annotations

import uuid
from datetime import date
from types import SimpleNamespace

import pytest

from backend.domain.errors.app_error import AppError
from backend.services.checkin_service import serialize_session, set_current_mood


def test_serialize_session_uses_daily_fields():
    task = SimpleNamespace(
        id=uuid.uuid4(),
        title="Okuma",
        description=None,
        is_completed=False,
        completed_at=None,
        status="active",
        due_date=date.today(),
        created_at=None,
    )
    session = SimpleNamespace(
        id=uuid.uuid4(),
        checkin_date=date.today(),
        status="in_progress",
        summary=None,
        mood_score=3,
        messages=[{"role": "assistant", "content": "Merhaba"}],
        daily_tasks=[task],
    )
    data = serialize_session(session)
    assert "checkin_date" in data
    assert "daily_tasks" in data
    assert "week_start" not in data
    assert "weekly_tasks" not in data
    assert data["daily_tasks"][0]["title"] == "Okuma"


@pytest.mark.asyncio
@pytest.mark.parametrize("bad", [0, 6, -1, 99])
async def test_mood_out_of_range(bad):
    with pytest.raises(AppError) as exc:
        await set_current_mood(
            db=None,  # type: ignore[arg-type]
            tenant_id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            mood_score=bad,
        )
    assert exc.value.status_code == 422

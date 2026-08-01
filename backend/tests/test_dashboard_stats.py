"""Tests for dashboard/stats helpers and mood validation."""

from datetime import date, timedelta

import pytest

from backend.services.profile_service import _compute_streak


def test_compute_streak_consecutive_days():
    d0 = date(2026, 7, 27)
    d1 = d0 - timedelta(days=1)
    d2 = d1 - timedelta(days=1)
    assert _compute_streak([d0, d1, d2]) == 3


def test_compute_streak_broken():
    d0 = date(2026, 7, 27)
    d1 = d0 - timedelta(days=1)
    d3 = d0 - timedelta(days=3)
    assert _compute_streak([d0, d1, d3]) == 2


def test_compute_streak_empty():
    assert _compute_streak([]) == 0


@pytest.mark.asyncio
async def test_mood_validation_rejects_out_of_range():
    from backend.domain.errors.app_error import AppError
    from backend.services import checkin_service
    import uuid

    with pytest.raises(AppError) as exc:
        await checkin_service.set_current_mood(
            db=None,  # type: ignore[arg-type]
            tenant_id=uuid.uuid4(),
            user_id=uuid.uuid4(),
            mood_score=9,
        )
    assert exc.value.status_code == 422


def test_capacity_snapshot_model_importable():
    from backend.db.models import CapacitySnapshot

    assert CapacitySnapshot.__tablename__ == "capacity_snapshots"
    assert hasattr(CapacitySnapshot, "score")


def test_daily_task_model_tablename():
    from backend.db.models import DailyTask

    assert DailyTask.__tablename__ == "daily_tasks"

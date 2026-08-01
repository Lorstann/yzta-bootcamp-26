"""Tests for dashboard/stats helpers and mood validation."""

from datetime import date, timedelta

import pytest

from backend.services.profile_service import _compute_streak


def test_compute_streak_consecutive_weeks():
    w0 = date(2026, 7, 27)
    w1 = w0 - timedelta(days=7)
    w2 = w1 - timedelta(days=7)
    assert _compute_streak([w0, w1, w2]) == 3


def test_compute_streak_broken():
    w0 = date(2026, 7, 27)
    w1 = w0 - timedelta(days=7)
    w3 = w0 - timedelta(days=21)
    assert _compute_streak([w0, w1, w3]) == 2


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

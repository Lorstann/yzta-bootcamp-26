"""Tests for daily streak computation."""

from datetime import date, timedelta

from backend.services.profile_service import _compute_streak


def test_streak_consecutive_days():
    d0 = date(2026, 8, 1)
    d1 = d0 - timedelta(days=1)
    d2 = d1 - timedelta(days=1)
    assert _compute_streak([d0, d1, d2]) == 3


def test_streak_broken_gap():
    d0 = date(2026, 8, 1)
    d1 = d0 - timedelta(days=1)
    d3 = d0 - timedelta(days=3)
    assert _compute_streak([d0, d1, d3]) == 2


def test_streak_empty():
    assert _compute_streak([]) == 0


def test_streak_single_day():
    assert _compute_streak([date(2026, 8, 1)]) == 1


def test_streak_duplicates_ignored():
    d0 = date(2026, 8, 1)
    d1 = d0 - timedelta(days=1)
    assert _compute_streak([d0, d0, d1, d1]) == 2


def test_streak_month_boundary():
    d0 = date(2026, 8, 1)
    d1 = date(2026, 7, 31)
    d2 = date(2026, 7, 30)
    assert _compute_streak([d0, d1, d2]) == 3


def test_streak_unordered_input():
    days = [date(2026, 7, 30), date(2026, 8, 1), date(2026, 7, 31)]
    assert _compute_streak(days) == 3

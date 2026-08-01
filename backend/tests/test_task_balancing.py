"""
backend/tests/test_task_balancing.py
S15: Capacity-based max tasks + downscale triggers.
"""

from decimal import Decimal

from backend.services.task_balancing import (
    limit_tasks,
    max_tasks_for_capacity,
    should_downscale,
)


def test_max_tasks_high_capacity():
    assert max_tasks_for_capacity(80) == 3
    assert max_tasks_for_capacity(None) == 3


def test_max_tasks_medium_capacity():
    assert max_tasks_for_capacity(50) == 2


def test_max_tasks_low_capacity():
    assert max_tasks_for_capacity(30) == 1
    assert max_tasks_for_capacity(Decimal("3")) == 1


def test_limit_tasks_caps_at_capacity():
    tasks = ["a", "b", "c", "d"]
    assert limit_tasks(tasks, 20) == ["a"]
    assert limit_tasks(tasks, 55) == ["a", "b"]
    assert limit_tasks(tasks, 90) == ["a", "b", "c"]


def test_should_downscale_on_fatigue_keyword():
    assert should_downscale(70, "Bu hafta çok yorgun hissediyorum") is True


def test_should_downscale_on_low_capacity():
    assert should_downscale(20, "Normal bir mesaj") is True


def test_should_not_downscale_when_healthy():
    assert should_downscale(80, "Enerjim yüksek, devam") is False

"""Task balancing unit tests."""

from backend.services.task_balancing import limit_tasks


def test_limit_tasks_max_three():
    titles = [f"t{i}" for i in range(10)]
    assert len(limit_tasks(titles, 100)) <= 3


def test_limit_tasks_empty():
    assert limit_tasks([], 80) == []


def test_limit_tasks_low_capacity_fewer():
    titles = ["a", "b", "c"]
    limited = limit_tasks(titles, 20)
    assert 1 <= len(limited) <= 3

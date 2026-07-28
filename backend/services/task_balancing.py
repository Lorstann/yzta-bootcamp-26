"""
backend/services/task_balancing.py
S15: Capacity-based max-3 tasks and downscale.
"""

from __future__ import annotations

from decimal import Decimal


def max_tasks_for_capacity(capacity_score: Decimal | float | None) -> int:
    if capacity_score is None:
        return 3
    score = float(capacity_score)
    if score < 40:
        return 1
    if score < 70:
        return 2
    return 3


def should_downscale(capacity_score: Decimal | float | None, message: str) -> bool:
    lowered = message.lower()
    fatigue_keywords = (
        "yorgun",
        "tüken",
        "kapasite",
        "aşırı yük",
        "burnout",
        "çok yoğun",
        "yetişemiyorum",
    )
    if any(k in lowered for k in fatigue_keywords):
        return True
    if capacity_score is not None and float(capacity_score) < 35:
        return True
    return False


def limit_tasks(tasks: list[str], capacity_score: Decimal | float | None) -> list[str]:
    limit = max_tasks_for_capacity(capacity_score)
    cleaned = [t.strip() for t in tasks if t and t.strip()]
    return cleaned[:limit]

"""
backend/services/task_balancing.py
S15: Capacity-based max-3 tasks and downscale.
"""

from __future__ import annotations

from decimal import Decimal
from typing import Any


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


def _normalize_task_item(task: str | dict[str, Any]) -> dict[str, str] | None:
    if isinstance(task, dict):
        title = str(task.get("title") or "").strip()
        if not title:
            return None
        return {
            "title": title,
            "description": str(task.get("description") or "").strip(),
        }
    cleaned = (task or "").strip()
    if not cleaned:
        return None
    return {"title": cleaned, "description": ""}


def limit_tasks(
    tasks: list[str] | list[dict[str, Any]],
    capacity_score: Decimal | float | None,
) -> list[str] | list[dict[str, str]]:
    """
    Cap task count by capacity. Preserves dict shape when input items are dicts;
    returns list[str] when all inputs are plain strings (backward compatible).
    """
    limit = max_tasks_for_capacity(capacity_score)
    if not tasks:
        return []

    all_str = all(isinstance(t, str) for t in tasks)
    normalized: list[dict[str, str]] = []
    for t in tasks:
        item = _normalize_task_item(t)
        if item:
            normalized.append(item)
    capped = normalized[:limit]
    if all_str:
        return [t["title"] for t in capped]
    return capped

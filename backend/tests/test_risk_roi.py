"""
backend/tests/test_risk_roi.py
S22/S23/S24: Pure scoring helpers where possible.
"""

from backend.services.task_balancing import max_tasks_for_capacity


def test_capacity_bands_align_with_risk_inputs():
    """Low capacity feeds yellow/red paths in risk scoring."""
    assert max_tasks_for_capacity(35) == 1
    assert max_tasks_for_capacity(45) == 2
    assert max_tasks_for_capacity(75) == 3

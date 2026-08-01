"""Pure risk derivation tests for daily windows (no DB writes)."""

from backend.services.risk_service import derive_risk_level


def test_green_stable():
    level, _, metrics = derive_risk_level(
        missed_days_7=0, completion_rate=0.9, capacity=75
    )
    assert level == "green"
    assert metrics["missed_days_7"] == 0


def test_yellow_missed_days():
    level, _, _ = derive_risk_level(
        missed_days_7=3, completion_rate=0.8, capacity=70
    )
    assert level == "yellow"


def test_yellow_low_capacity():
    level, _, _ = derive_risk_level(
        missed_days_7=0, completion_rate=0.9, capacity=30
    )
    assert level == "yellow"


def test_red_high_miss_and_low_completion():
    level, rationale, metrics = derive_risk_level(
        missed_days_7=5, completion_rate=0.2, capacity=50
    )
    assert level == "red"
    assert "kaçırma" in rationale.lower() or "check-in" in rationale.lower()
    assert metrics["task_completion_rate"] == 0.2


def test_not_red_if_completion_ok():
    """5 missed days but high completion → yellow, not red."""
    level, _, _ = derive_risk_level(
        missed_days_7=5, completion_rate=0.8, capacity=70
    )
    assert level == "yellow"


def test_red_from_low_energy_and_motivation():
    level, rationale, metrics = derive_risk_level(
        missed_days_7=0,
        completion_rate=0.9,
        capacity=70,
        energy_avg=2.5,
        motivation_avg=2.0,
        signal_days=3,
    )
    assert level == "red"
    assert "enerji" in rationale.lower() or "motivasyon" in rationale.lower()
    assert metrics["energy_avg"] == 2.5


def test_yellow_from_soft_energy():
    level, _, metrics = derive_risk_level(
        missed_days_7=0,
        completion_rate=0.9,
        capacity=70,
        energy_avg=3.5,
        motivation_avg=6.0,
        signal_days=3,
    )
    assert level == "yellow"
    assert metrics["energy_avg"] == 3.5


def test_energy_ignored_with_few_samples():
    """Fewer than 3 signal days → energy alone does not raise risk."""
    level, _, _ = derive_risk_level(
        missed_days_7=0,
        completion_rate=0.9,
        capacity=70,
        energy_avg=2.0,
        motivation_avg=2.0,
        signal_days=1,
    )
    assert level == "green"


def test_optional_energy_defaults_preserve_green():
    level, _, metrics = derive_risk_level(
        missed_days_7=0, completion_rate=0.9, capacity=75
    )
    assert level == "green"
    assert "energy_avg" not in metrics

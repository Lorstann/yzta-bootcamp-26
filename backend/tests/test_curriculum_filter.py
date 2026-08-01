"""
backend/tests/test_curriculum_filter.py
S14/AC2: curriculum-only task filter heuristics.
"""

from backend.services.chat_service import (
    _filter_tasks_to_curriculum,
    is_likely_off_curriculum,
)


def test_filter_keeps_in_curriculum_tasks():
    ctx = "React hooks useState useEffect Node.js Express"
    tasks = ["React useState çalış", "Solidity contract yaz", "Express route ekle"]
    kept = _filter_tasks_to_curriculum(tasks, ctx)
    assert any("React" in t or "Express" in t for t in kept)
    assert all("Solidity" not in t for t in kept)


def test_off_curriculum_heuristic():
    assert is_likely_off_curriculum(
        "Solidity öğrenmek istiyorum", "React Node.js SQL"
    )
    assert not is_likely_off_curriculum(
        "React hooks tekrar edeyim", "React hooks useState"
    )

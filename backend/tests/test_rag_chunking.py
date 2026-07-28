"""
backend/tests/test_rag_chunking.py
Unit tests for chunking (no DB required).
"""

from backend.services.rag.chunking import chunk_text
from backend.services.task_balancing import limit_tasks, max_tasks_for_capacity


def test_chunk_text_splits_long_content():
    text = "kelime " * 300
    chunks = chunk_text(text, chunk_size=100, overlap=20)
    assert len(chunks) > 1
    assert all(len(c) <= 120 for c in chunks)


def test_chunk_text_empty():
    assert chunk_text("   ") == []


def test_capacity_limits_tasks():
    assert max_tasks_for_capacity(30) == 1
    assert max_tasks_for_capacity(50) == 2
    assert max_tasks_for_capacity(80) == 3
    assert len(limit_tasks(["a", "b", "c", "d"], 30)) == 1

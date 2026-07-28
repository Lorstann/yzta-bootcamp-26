"""
backend/services/rag/__init__.py
"""

from backend.services.rag.ingest import ingest_curriculum_text
from backend.services.rag.retrieve import retrieve_curriculum_context

__all__ = ["ingest_curriculum_text", "retrieve_curriculum_context"]

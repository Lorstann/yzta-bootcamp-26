"""
backend/services/rag/retrieve.py
A5/A7: Top-k retrieve and format for prompt injection.
"""

from __future__ import annotations

import logging
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from backend.repositories.curriculum_repo import CurriculumRepository
from backend.services.rag.embeddings import embed_query

logger = logging.getLogger(__name__)


async def retrieve_curriculum_context(
    session: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    query: str,
    top_k: int = 4,
) -> str:
    embedding = await embed_query(query)
    repo = CurriculumRepository(session)
    chunks = await repo.similarity_search(
        tenant_id=tenant_id,
        query_embedding=embedding,
        top_k=top_k,
    )
    if not chunks:
        logger.info("RAG retrieve boş | tenant_id=%s", tenant_id)
        return ""

    parts = [f"[{i + 1}] {c.content}" for i, c in enumerate(chunks)]
    context = "\n\n".join(parts)
    logger.info("RAG retrieve | tenant_id=%s hits=%s", tenant_id, len(chunks))
    return context

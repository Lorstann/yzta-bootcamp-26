"""
backend/services/rag/ingest.py
A4: Chunk + embed + store curriculum.
"""

from __future__ import annotations

import logging
import uuid

from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.curriculum import Curriculum
from backend.repositories.curriculum_repo import CurriculumRepository
from backend.services.rag.chunking import chunk_text
from backend.services.rag.embeddings import embed_texts

logger = logging.getLogger(__name__)


async def ingest_curriculum_text(
    session: AsyncSession,
    *,
    tenant_id: uuid.UUID,
    title: str,
    text: str,
    description: str | None = None,
    source_type: str = "manual",
    file_name: str | None = None,
    file_uri: str | None = None,
    uploaded_by: uuid.UUID | None = None,
) -> Curriculum:
    chunks = chunk_text(text)
    if not chunks:
        raise ValueError("Müfredat metni boş — chunk üretilemedi")

    embeddings = await embed_texts(chunks)
    repo = CurriculumRepository(session)
    curriculum = await repo.create_curriculum(
        tenant_id=tenant_id,
        title=title,
        description=description,
        source_type=source_type,
        file_name=file_name,
        file_uri=file_uri,
        chunk_count=len(chunks),
        uploaded_by=uploaded_by,
    )
    await repo.add_chunks(
        curriculum_id=curriculum.id,
        tenant_id=tenant_id,
        contents=chunks,
        embeddings=embeddings,
    )
    logger.info(
        "Müfredat indekslendi | curriculum_id=%s chunks=%s",
        curriculum.id,
        len(chunks),
    )
    return curriculum

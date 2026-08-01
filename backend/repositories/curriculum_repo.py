"""
backend/repositories/curriculum_repo.py
Curriculum + chunk persistence and pgvector similarity search.
"""

from __future__ import annotations

import uuid
from typing import Sequence

from sqlalchemy import select, text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.curriculum import Curriculum, CurriculumChunk
from backend.repositories.base import BaseRepository


class CurriculumRepository(BaseRepository[Curriculum]):
    model = Curriculum

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def create_curriculum(
        self,
        *,
        tenant_id: uuid.UUID,
        title: str,
        description: str | None = None,
        source_type: str = "manual",
        file_name: str | None = None,
        file_uri: str | None = None,
        chunk_count: int | None = None,
        uploaded_by: uuid.UUID | None = None,
    ) -> Curriculum:
        row = Curriculum(
            tenant_id=tenant_id,
            title=title,
            description=description,
            source_type=source_type,
            file_name=file_name,
            file_uri=file_uri,
            chunk_count=chunk_count,
            uploaded_by=uploaded_by,
            is_active=True,
        )
        self.session.add(row)
        await self.session.flush()
        return row

    async def soft_delete(
        self, curriculum_id: uuid.UUID, *, tenant_id: uuid.UUID
    ) -> Curriculum | None:
        result = await self.session.execute(
            select(Curriculum).where(
                Curriculum.id == curriculum_id,
                Curriculum.tenant_id == tenant_id,
            )
        )
        row = result.scalar_one_or_none()
        if row is None:
            return None
        row.is_active = False
        await self.session.flush()
        return row

    async def get_for_tenant(
        self, curriculum_id: uuid.UUID, *, tenant_id: uuid.UUID
    ) -> Curriculum | None:
        result = await self.session.execute(
            select(Curriculum).where(
                Curriculum.id == curriculum_id,
                Curriculum.tenant_id == tenant_id,
            )
        )
        return result.scalar_one_or_none()

    async def add_chunks(
        self,
        *,
        curriculum_id: uuid.UUID,
        tenant_id: uuid.UUID,
        contents: Sequence[str],
        embeddings: Sequence[list[float]],
    ) -> list[CurriculumChunk]:
        rows: list[CurriculumChunk] = []
        for idx, (content, embedding) in enumerate(zip(contents, embeddings)):
            row = CurriculumChunk(
                curriculum_id=curriculum_id,
                tenant_id=tenant_id,
                content=content,
                chunk_index=idx,
                embedding=embedding,
            )
            self.session.add(row)
            rows.append(row)
        await self.session.flush()
        return rows

    async def similarity_search(
        self,
        *,
        tenant_id: uuid.UUID,
        query_embedding: list[float],
        top_k: int = 5,
    ) -> list[CurriculumChunk]:
        # Cosine distance via pgvector <=> operator
        vector_literal = "[" + ",".join(str(float(x)) for x in query_embedding) + "]"
        result = await self.session.execute(
            text(
                """
                SELECT id, curriculum_id, tenant_id, content, chunk_index
                FROM curriculum_chunks
                WHERE tenant_id = :tenant_id
                  AND embedding IS NOT NULL
                ORDER BY embedding <=> CAST(:embedding AS vector)
                LIMIT :top_k
                """
            ),
            {
                "tenant_id": str(tenant_id),
                "embedding": vector_literal,
                "top_k": top_k,
            },
        )
        rows = result.fetchall()
        chunks: list[CurriculumChunk] = []
        for row in rows:
            chunk = CurriculumChunk(
                id=row.id,
                curriculum_id=row.curriculum_id,
                tenant_id=row.tenant_id,
                content=row.content,
                chunk_index=row.chunk_index,
            )
            chunks.append(chunk)
        return chunks

    async def list_by_tenant(self, tenant_id: uuid.UUID) -> list[Curriculum]:
        result = await self.session.execute(
            select(Curriculum).where(
                Curriculum.tenant_id == tenant_id,
                Curriculum.is_active.is_(True),
            )
        )
        return list(result.scalars().all())

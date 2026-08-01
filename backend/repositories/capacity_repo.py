"""
backend/repositories/capacity_repo.py
"""

from __future__ import annotations

import uuid
from decimal import Decimal
from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.capacity import CapacitySnapshot
from backend.repositories.base import BaseRepository


class CapacitySnapshotRepository(BaseRepository[CapacitySnapshot]):
    model = CapacitySnapshot

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def record(
        self,
        *,
        tenant_id: uuid.UUID,
        user_id: uuid.UUID,
        score: Decimal,
    ) -> CapacitySnapshot:
        row = CapacitySnapshot(
            tenant_id=tenant_id,
            user_id=user_id,
            score=score,
        )
        return await self.create(row)

    async def list_for_user(
        self,
        *,
        tenant_id: uuid.UUID,
        user_id: uuid.UUID,
        limit: int = 26,
    ) -> list[CapacitySnapshot]:
        stmt = (
            select(CapacitySnapshot)
            .where(
                CapacitySnapshot.tenant_id == tenant_id,
                CapacitySnapshot.user_id == user_id,
            )
            .order_by(CapacitySnapshot.recorded_at.asc())
            .limit(limit)
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

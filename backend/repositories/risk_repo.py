"""
backend/repositories/risk_repo.py
"""

from __future__ import annotations

import uuid
from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.risk import RiskSignal
from backend.repositories.base import BaseRepository


class RiskSignalRepository(BaseRepository[RiskSignal]):
    model = RiskSignal

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def create_signal(
        self,
        *,
        tenant_id: uuid.UUID,
        user_id: uuid.UUID,
        level: str,
        category: str | None = None,
        rationale: str | None = None,
        metrics: dict[str, Any] | None = None,
    ) -> RiskSignal:
        # Deactivate prior active signals for user
        existing = await self.session.execute(
            select(RiskSignal).where(
                RiskSignal.user_id == user_id,
                RiskSignal.is_active.is_(True),
            )
        )
        for row in existing.scalars().all():
            row.is_active = False

        signal = RiskSignal(
            tenant_id=tenant_id,
            user_id=user_id,
            level=level,
            category=category,
            rationale=rationale,
            metrics=metrics,
            is_active=True,
        )
        return await self.create(signal)

    async def get_active_for_user(
        self, user_id: uuid.UUID
    ) -> Optional[RiskSignal]:
        stmt = (
            select(RiskSignal)
            .where(RiskSignal.user_id == user_id, RiskSignal.is_active.is_(True))
            .order_by(RiskSignal.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def list_for_tenant(self, tenant_id: uuid.UUID) -> list[RiskSignal]:
        stmt = (
            select(RiskSignal)
            .where(
                RiskSignal.tenant_id == tenant_id,
                RiskSignal.is_active.is_(True),
            )
            .order_by(RiskSignal.created_at.desc())
        )
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

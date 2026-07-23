"""
backend/repositories/tenant_repo.py
B8: Tenant'a özel repository.
"""

from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.models.tenant import Tenant
from backend.repositories.base import BaseRepository


class TenantRepository(BaseRepository[Tenant]):
    model = Tenant

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_slug(self, slug: str) -> Optional[Tenant]:
        """Slug ile tenant getirir."""
        stmt = select(Tenant).where(Tenant.slug == slug)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_active(self) -> list[Tenant]:
        """Sadece aktif tenant'ları getirir."""
        stmt = select(Tenant).where(Tenant.is_active.is_(True))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

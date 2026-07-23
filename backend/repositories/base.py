"""
backend/repositories/base.py
B8: Generic async repository — temel CRUD işlemleri.

Tüm spesifik repository sınıfları buradan türer.
Tip parametresi sayesinde mypy/IDE her modele özel otomatik tamamlama sağlar.
"""

from typing import Generic, TypeVar, Type, Optional, Sequence
from uuid import UUID
import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from backend.db.base import Base

logger = logging.getLogger(__name__)

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    """
    Async SQLAlchemy repository temel sınıfı.

    Kullanım:
        class TenantRepository(BaseRepository[Tenant]):
            model = Tenant
    """

    model: Type[ModelT]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_id(self, record_id: UUID) -> Optional[ModelT]:
        """ID ile tek kayıt getirir. Bulunamazsa None döner."""
        result = await self.session.get(self.model, record_id)
        return result

    async def get_all(self, limit: int = 100, offset: int = 0) -> Sequence[ModelT]:
        """Tüm kayıtları sayfalı olarak getirir."""
        stmt = select(self.model).limit(limit).offset(offset)
        result = await self.session.execute(stmt)
        return result.scalars().all()

    async def create(self, obj: ModelT) -> ModelT:
        """Yeni kayıt ekler ve flush eder (ID üretilir ama commit olmaz)."""
        self.session.add(obj)
        await self.session.flush()
        await self.session.refresh(obj)
        logger.debug("Created %s id=%s", self.model.__tablename__, obj.id)  # type: ignore[attr-defined]
        return obj

    async def delete(self, obj: ModelT) -> None:
        """Kaydı siler."""
        await self.session.delete(obj)
        await self.session.flush()
        logger.debug("Deleted %s id=%s", self.model.__tablename__, obj.id)  # type: ignore[attr-defined]

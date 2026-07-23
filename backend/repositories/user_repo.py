"""
backend/repositories/user_repo.py
B8: User ve StudentProfile'a özel repository.
"""

from typing import Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from backend.db.models.user import User, StudentProfile
from backend.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    model = User

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_email(self, tenant_id: UUID, email: str) -> Optional[User]:
        """Tenant içinde email ile kullanıcı getirir."""
        stmt = select(User).where(
            User.tenant_id == tenant_id,
            User.email == email,
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_with_profile(self, user_id: UUID) -> Optional[User]:
        """Kullanıcıyı student_profile ilişkisiyle birlikte getirir."""
        stmt = (
            select(User)
            .options(selectinload(User.student_profile))
            .where(User.id == user_id)
        )
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

    async def get_by_tenant(self, tenant_id: UUID) -> list[User]:
        """Bir tenant'ın tüm kullanıcılarını getirir."""
        stmt = select(User).where(User.tenant_id == tenant_id, User.is_active.is_(True))
        result = await self.session.execute(stmt)
        return list(result.scalars().all())


class StudentProfileRepository(BaseRepository[StudentProfile]):
    model = StudentProfile

    def __init__(self, session: AsyncSession) -> None:
        super().__init__(session)

    async def get_by_user_id(self, user_id: UUID) -> Optional[StudentProfile]:
        """User ID ile öğrenci profilini getirir."""
        stmt = select(StudentProfile).where(StudentProfile.user_id == user_id)
        result = await self.session.execute(stmt)
        return result.scalar_one_or_none()

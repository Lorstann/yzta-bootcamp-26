"""
backend/api/dependencies/db.py
B8: FastAPI DB session dependency.

Endpoint'lerde kullanım:
    from backend.api.dependencies.db import get_db
    from sqlalchemy.ext.asyncio import AsyncSession

    @router.get("/example")
    async def example(db: AsyncSession = Depends(get_db)):
        ...
"""

from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession
from backend.db.session import AsyncSessionLocal


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    FastAPI Depends() ile kullanılacak async DB session.
    Her istek için yeni session açar, biter bitmez kapatır.
    Hata olursa rollback yapar.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

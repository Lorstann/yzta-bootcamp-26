"""
backend/db/session.py
D3: Async SQLAlchemy engine ve session factory.

Kullanım (endpoint'lerde):
    from backend.db.session import get_db
    # FastAPI dependency injection ile kullanılır (B8'de eklenir)
"""

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from backend.config import settings

# Async engine — asyncpg driver'ı ile PostgreSQL'e bağlanır
engine = create_async_engine(
    settings.database_url,
    echo=settings.log_level == "debug",  # debug modda SQL sorgularını logla
    pool_pre_ping=True,                  # bağlantı kopmuşsa otomatik yenile
    pool_size=10,
    max_overflow=20,
)

# Session factory
AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)


async def get_db() -> AsyncSession:
    """
    FastAPI dependency olarak kullanılacak DB session.
    B8 (repository katmanı) kurulunca endpoint'lere inject edilir.
    """
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise

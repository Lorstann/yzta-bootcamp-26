"""
backend/tests/conftest.py
Plan 1B: Postgres test fixtures for RLS isolation suite.
"""

from __future__ import annotations

import os
import uuid

import pytest
import pytest_asyncio
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from backend.config import settings

TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL", settings.database_url)


@pytest_asyncio.fixture
async def db_session() -> AsyncSession:
    """Per-test session: truncate tenant data, yield session, cleanup."""
    eng = create_async_engine(TEST_DATABASE_URL, echo=False, pool_pre_ping=True)

    async with eng.begin() as conn:
        await conn.execute(
            text(
                """
                DO $$
                BEGIN
                  IF NOT EXISTS (SELECT FROM pg_roles WHERE rolname = 'equa_app') THEN
                    CREATE ROLE equa_app NOINHERIT LOGIN PASSWORD 'equa_app_dev';
                  END IF;
                END
                $$;
                """
            )
        )
        await conn.execute(text("GRANT USAGE ON SCHEMA public TO equa_app"))
        await conn.execute(
            text(
                "GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO equa_app"
            )
        )
        await conn.execute(
            text(
                "GRANT USAGE, SELECT ON ALL SEQUENCES IN SCHEMA public TO equa_app"
            )
        )

    session_factory = async_sessionmaker(
        bind=eng, class_=AsyncSession, expire_on_commit=False
    )

    async with session_factory() as session:
        await session.execute(
            text(
                """
                TRUNCATE TABLE
                  daily_tasks,
                  capacity_snapshots,
                  checkin_sessions,
                  curriculum_chunks,
                  curricula,
                  student_profiles,
                  risk_signals,
                  users,
                  tenants
                RESTART IDENTITY CASCADE
                """
            )
        )
        await session.commit()

        try:
            yield session
        finally:
            await session.rollback()
            try:
                await session.execute(
                    text(
                        """
                        TRUNCATE TABLE
                          daily_tasks,
                          capacity_snapshots,
                          checkin_sessions,
                          curriculum_chunks,
                          curricula,
                          student_profiles,
                          risk_signals,
                          users,
                          tenants
                        RESTART IDENTITY CASCADE
                        """
                    )
                )
                await session.commit()
            except Exception:
                await session.rollback()
            await eng.dispose()


async def set_tenant_context(session: AsyncSession, tenant_id: uuid.UUID) -> None:
    """Apply RLS tenant context under equa_app role."""
    await session.execute(text("SET LOCAL ROLE equa_app"))
    await session.execute(
        text("SELECT set_config('app.current_tenant_id', :tid, true)"),
        {"tid": str(tenant_id)},
    )

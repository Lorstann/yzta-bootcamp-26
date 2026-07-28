"""
backend/db/seeds/dev_seed.py
D9: Local geliştirme için örnek veri.
"""

import asyncio
import uuid

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from backend.config import settings
from backend.services.auth_service import hash_password

TENANT_ALPHA_ID = uuid.UUID("11111111-1111-1111-1111-111111111111")
TENANT_BETA_ID = uuid.UUID("22222222-2222-2222-2222-222222222222")
USER_ALPHA_ID = uuid.UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
USER_BETA_ID = uuid.UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")
USER_ALPHA_ADMIN_ID = uuid.UUID("cccccccc-cccc-cccc-cccc-cccccccccccc")

# Dev password for all seed users
DEV_PASSWORD = "password123"


async def seed(session: AsyncSession) -> None:
    print("Seed basliyor...")
    pw = hash_password(DEV_PASSWORD)

    await session.execute(
        text(
            """
        INSERT INTO tenants (id, name, slug, is_active)
        VALUES
            (:id1, 'Bootcamp Alpha', 'bootcamp-alpha', true),
            (:id2, 'Bootcamp Beta',  'bootcamp-beta',  true)
        ON CONFLICT (slug) DO NOTHING
    """
        ),
        {"id1": str(TENANT_ALPHA_ID), "id2": str(TENANT_BETA_ID)},
    )
    print("  Tenants eklendi")

    await session.execute(
        text(
            """
        INSERT INTO users (id, tenant_id, email, full_name, role, password_hash)
        VALUES
            (:uid1, :tid1, 'test_student_alpha@equa.dev', 'Alpha Test Ogrencisi', 'student', :pw),
            (:uid2, :tid2, 'test_student_beta@equa.dev',  'Beta Test Ogrencisi',  'student', :pw),
            (:uid3, :tid1, 'coordinator_alpha@equa.dev', 'Alpha Koordinator', 'instructor', :pw)
        ON CONFLICT (tenant_id, email) DO UPDATE
          SET password_hash = EXCLUDED.password_hash
    """
        ),
        {
            "uid1": str(USER_ALPHA_ID),
            "tid1": str(TENANT_ALPHA_ID),
            "uid2": str(USER_BETA_ID),
            "tid2": str(TENANT_BETA_ID),
            "uid3": str(USER_ALPHA_ADMIN_ID),
            "pw": pw,
        },
    )
    print("  Users eklendi (password: password123)")

    await session.execute(
        text(
            """
        INSERT INTO student_profiles (user_id, tenant_id, capacity_score, onboarding_completed)
        VALUES
            (:uid1, :tid1, 75.00, true),
            (:uid2, :tid2, 60.00, false)
        ON CONFLICT (user_id) DO NOTHING
    """
        ),
        {
            "uid1": str(USER_ALPHA_ID),
            "tid1": str(TENANT_ALPHA_ID),
            "uid2": str(USER_BETA_ID),
            "tid2": str(TENANT_BETA_ID),
        },
    )
    print("  Student profiles eklendi")
    await session.commit()
    print("Seed tamamlandi!")


async def main() -> None:
    engine = create_async_engine(settings.database_url, echo=False)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        await seed(session)
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())

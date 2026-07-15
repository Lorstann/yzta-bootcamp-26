"""
backend/db/seeds/dev_seed.py
D9: Local geliştirme için örnek veri.

2 tenant + 2 öğrenci kullanıcısı + 2 student_profile oluşturur.
D10 cross-tenant izolasyon testleri bu veriye dayanır.
"""

import asyncio
import uuid
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy import text

from backend.config import settings

# Sabit UUID'ler — testlerde her zaman aynı veriye erişebilmek için
TENANT_ALPHA_ID = uuid.UUID("11111111-1111-1111-1111-111111111111")
TENANT_BETA_ID  = uuid.UUID("22222222-2222-2222-2222-222222222222")
USER_ALPHA_ID   = uuid.UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
USER_BETA_ID    = uuid.UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")


async def seed(session: AsyncSession) -> None:
    """Seed verisini ekler. Zaten varsa atlar (idempotent)."""

    print("🌱 Seed başlıyor...")

    # --- Tenant'lar ---
    await session.execute(text("""
        INSERT INTO tenants (id, name, slug, is_active)
        VALUES
            (:id1, 'Bootcamp Alpha', 'bootcamp-alpha', true),
            (:id2, 'Bootcamp Beta',  'bootcamp-beta',  true)
        ON CONFLICT (slug) DO NOTHING
    """), {"id1": str(TENANT_ALPHA_ID), "id2": str(TENANT_BETA_ID)})
    print("  ✅ Tenants eklendi")

    # --- Kullanıcılar ---
    await session.execute(text("""
        INSERT INTO users (id, tenant_id, email, full_name, role)
        VALUES
            (:uid1, :tid1, 'test_student_alpha@equa.dev', 'Alpha Test Öğrencisi', 'student'),
            (:uid2, :tid2, 'test_student_beta@equa.dev',  'Beta Test Öğrencisi',  'student')
        ON CONFLICT (tenant_id, email) DO NOTHING
    """), {
        "uid1": str(USER_ALPHA_ID), "tid1": str(TENANT_ALPHA_ID),
        "uid2": str(USER_BETA_ID),  "tid2": str(TENANT_BETA_ID),
    })
    print("  ✅ Users eklendi")

    # --- Student Profiles ---
    await session.execute(text("""
        INSERT INTO student_profiles (user_id, tenant_id, capacity_score, onboarding_completed)
        VALUES
            (:uid1, :tid1, 75.00, true),
            (:uid2, :tid2, 60.00, false)
        ON CONFLICT (user_id) DO NOTHING
    """), {
        "uid1": str(USER_ALPHA_ID), "tid1": str(TENANT_ALPHA_ID),
        "uid2": str(USER_BETA_ID),  "tid2": str(TENANT_BETA_ID),
    })
    print("  ✅ Student profiles eklendi")

    await session.commit()
    print("🎉 Seed tamamlandı!")


async def main() -> None:
    engine = create_async_engine(settings.database_url, echo=False)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)

    async with session_factory() as session:
        await seed(session)

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())

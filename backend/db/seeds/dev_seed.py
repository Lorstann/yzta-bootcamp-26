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
            (:uid3, :tid1, 'coordinator_alpha@equa.dev', 'Alpha Kurum Admin', 'admin', :pw)
        ON CONFLICT (tenant_id, email) DO UPDATE
          SET password_hash = EXCLUDED.password_hash,
              role = EXCLUDED.role,
              full_name = EXCLUDED.full_name
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
        INSERT INTO student_profiles (
            user_id, tenant_id, capacity_score, onboarding_completed,
            city, district, program_track, interests,
            self_reported_stress, weekly_available_hours, capacity_source
        )
        VALUES
            (
                :uid1, :tid1, 75.00, true,
                'İzmir', 'Bornova', 'Veri Bilimi',
                CAST(:interests1 AS jsonb),
                3, 15, 'onboarding'
            ),
            (
                :uid2, :tid2, 60.00, false,
                NULL, NULL, NULL, NULL,
                NULL, NULL, 'auto'
            )
        ON CONFLICT (user_id) DO UPDATE SET
            capacity_score = EXCLUDED.capacity_score,
            onboarding_completed = EXCLUDED.onboarding_completed,
            city = COALESCE(student_profiles.city, EXCLUDED.city),
            district = COALESCE(student_profiles.district, EXCLUDED.district),
            program_track = COALESCE(student_profiles.program_track, EXCLUDED.program_track),
            interests = COALESCE(student_profiles.interests, EXCLUDED.interests),
            self_reported_stress = COALESCE(
                student_profiles.self_reported_stress, EXCLUDED.self_reported_stress
            ),
            weekly_available_hours = COALESCE(
                student_profiles.weekly_available_hours, EXCLUDED.weekly_available_hours
            ),
            capacity_source = EXCLUDED.capacity_source
    """
        ),
        {
            "uid1": str(USER_ALPHA_ID),
            "tid1": str(TENANT_ALPHA_ID),
            "uid2": str(USER_BETA_ID),
            "tid2": str(TENANT_BETA_ID),
            "interests1": '{"hobbies":["Yürüyüş","Kitap","Kahve"],"recharge":["Doğada olmak"],"notes":[]}',
        },
    )
    print("  Student profiles eklendi (Alpha: Izmir/Veri Bilimi + hobiler)")
    await session.commit()
    print("Seed tamamlandi!")
    print("")
    print("Giris bilgileri (tenant slug + email + sifre):")
    print("  Ogrenci Alpha : bootcamp-alpha / test_student_alpha@equa.dev / password123")
    print("  Ogrenci Beta  : bootcamp-beta  / test_student_beta@equa.dev  / password123")
    print("  Kurum Admin   : bootcamp-alpha / coordinator_alpha@equa.dev / password123  (role=admin)")


async def main() -> None:
    engine = create_async_engine(settings.database_url, echo=False)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        await seed(session)
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())

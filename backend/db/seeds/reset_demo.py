"""
Reset seed users' app data for first-login demos.
Keeps tenants + users (email/password). Clears activity + onboarding.
"""

from __future__ import annotations

import asyncio
import uuid

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from backend.config import settings

TENANT_ALPHA_ID = uuid.UUID("11111111-1111-1111-1111-111111111111")
TENANT_BETA_ID = uuid.UUID("22222222-2222-2222-2222-222222222222")
USER_ALPHA_ID = uuid.UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa")
USER_BETA_ID = uuid.UUID("bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb")
USER_ALPHA_ADMIN_ID = uuid.UUID("cccccccc-cccc-cccc-cccc-cccccccccccc")

SEED_USER_IDS = (USER_ALPHA_ID, USER_BETA_ID, USER_ALPHA_ADMIN_ID)
SEED_TENANT_IDS = (TENANT_ALPHA_ID, TENANT_BETA_ID)


async def reset_for_demo(session: AsyncSession) -> None:
    user_ids = [str(u) for u in SEED_USER_IDS]
    tenant_ids = [str(t) for t in SEED_TENANT_IDS]

    print("Demo reset basliyor (login bilgileri korunur)...")

    # Order: children before parents where needed
    await session.execute(
        text(
            """
            DELETE FROM daily_tasks
            WHERE user_id = ANY(CAST(:uids AS uuid[]))
              AND tenant_id = ANY(CAST(:tids AS uuid[]))
            """
        ),
        {"uids": user_ids, "tids": tenant_ids},
    )
    print("  daily_tasks temizlendi")

    await session.execute(
        text(
            """
            DELETE FROM checkin_sessions
            WHERE user_id = ANY(CAST(:uids AS uuid[]))
              AND tenant_id = ANY(CAST(:tids AS uuid[]))
            """
        ),
        {"uids": user_ids, "tids": tenant_ids},
    )
    print("  checkin_sessions (chat) temizlendi")

    await session.execute(
        text(
            """
            DELETE FROM capacity_snapshots
            WHERE user_id = ANY(CAST(:uids AS uuid[]))
              AND tenant_id = ANY(CAST(:tids AS uuid[]))
            """
        ),
        {"uids": user_ids, "tids": tenant_ids},
    )
    print("  capacity_snapshots temizlendi")

    await session.execute(
        text(
            """
            DELETE FROM risk_signals
            WHERE user_id = ANY(CAST(:uids AS uuid[]))
              AND tenant_id = ANY(CAST(:tids AS uuid[]))
            """
        ),
        {"uids": user_ids, "tids": tenant_ids},
    )
    print("  risk_signals temizlendi")

    # Fresh first-login profiles for both students (admin may have no profile)
    await session.execute(
        text(
            """
            INSERT INTO student_profiles (
                user_id, tenant_id, onboarding_completed, capacity_source
            )
            VALUES
                (:uid1, :tid1, false, 'auto'),
                (:uid2, :tid2, false, 'auto')
            ON CONFLICT (user_id) DO UPDATE SET
                onboarding_completed = false,
                capacity_score = NULL,
                capacity_source = 'auto',
                self_reported_stress = NULL,
                weekly_available_hours = NULL,
                linkedin_url = NULL,
                bio = NULL,
                competencies = NULL,
                city = NULL,
                district = NULL,
                program_track = NULL,
                interests = NULL,
                updated_at = now()
            """
        ),
        {
            "uid1": str(USER_ALPHA_ID),
            "tid1": str(TENANT_ALPHA_ID),
            "uid2": str(USER_BETA_ID),
            "tid2": str(TENANT_BETA_ID),
        },
    )
    print("  student_profiles sifirlandi (onboarding_completed=false)")

    await session.commit()
    print("Demo reset tamamlandi!")
    print("")
    print("Giris (ilk kez gibi):")
    print("  Ogrenci Alpha : bootcamp-alpha / test_student_alpha@equa.dev / password123")
    print("  Ogrenci Beta  : bootcamp-beta  / test_student_beta@equa.dev  / password123")
    print("  Kurum Admin   : bootcamp-alpha / coordinator_alpha@equa.dev / password123")
    print("Not: Tarayicida localStorage/eski JWT varsa cikis yap veya gizli pencere kullan.")


async def main() -> None:
    engine = create_async_engine(settings.database_url, echo=False)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    async with session_factory() as session:
        await reset_for_demo(session)
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())

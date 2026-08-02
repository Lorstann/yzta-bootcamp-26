"""
backend/db/seeds/video_seed.py

3 dakikalık demo videosu için Bootcamp Alpha verisini hazırlar.
- Temel hesaplar için dev_seed çalıştırır
- Ayşe (öğrenci demo) + kırmızı riskli ikinci öğrenci + yeşil kontrast öğrencisi
- ROI / revenue / risk_signals
- Ayşe'nin bugünkü check-in'ini temizler (canlı chat için)
- Opsiyonel müfredat ingest (RAG)

Kullanım (repo kökünden, venv aktif):
    python -m backend.db.seeds.video_seed
    python -m backend.db.seeds.video_seed --skip-curriculum
    python backend/scripts/seed_video.py
"""

from __future__ import annotations

import argparse
import asyncio
import json
import uuid

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from backend.config import settings
from backend.db.seeds.dev_seed import (
    DEV_PASSWORD,
    TENANT_ALPHA_ID,
    USER_ALPHA_ADMIN_ID,
    USER_ALPHA_ID,
    seed as base_seed,
)
from backend.db.tenant_context import apply_tenant_context
from backend.services.auth_service import hash_password

# Sabit ID'ler — video senaryosu / SQL ile uyumlu
USER_AYSE_ID = USER_ALPHA_ID  # narrasyon: Ayşe Yılmaz
USER_CAN_ID = uuid.UUID("dddddddd-dddd-dddd-dddd-dddddddddddd")  # kırmızı risk
USER_ELIF_ID = uuid.UUID("eeeeeeee-eeee-eeee-eeee-eeeeeeeeeeee")  # yeşil kontrast

VIDEO_CURRICULUM_TITLE = "Bootcamp React Müfredatı (Video Demo)"
REVENUE_PER_STUDENT = 25000


async def _set_alpha_context(session: AsyncSession) -> None:
    await apply_tenant_context(session, TENANT_ALPHA_ID)


async def seed_video_overlay(session: AsyncSession) -> None:
    """dev_seed üstüne video-specific veriyi yazar (idempotent)."""
    await _set_alpha_context(session)
    pw = hash_password(DEV_PASSWORD)

    print("Video overlay basliyor (Bootcamp Alpha)...")

    # --- Tenant ROI ---
    await session.execute(
        text(
            """
            UPDATE tenants
            SET revenue_per_student = :rev,
                updated_at = now()
            WHERE id = :tid
            """
        ),
        {"rev": REVENUE_PER_STUDENT, "tid": str(TENANT_ALPHA_ID)},
    )
    print(f"  revenue_per_student = {REVENUE_PER_STUDENT}")

    # --- Ayşe (mevcut alpha student) ---
    await session.execute(
        text(
            """
            UPDATE users
            SET full_name = 'Ayşe Yılmaz',
                password_hash = :pw,
                role = 'student'
            WHERE id = :uid AND tenant_id = :tid
            """
        ),
        {"pw": pw, "uid": str(USER_AYSE_ID), "tid": str(TENANT_ALPHA_ID)},
    )
    await session.execute(
        text(
            """
            UPDATE student_profiles
            SET capacity_score = 48.00,
                onboarding_completed = true,
                program_track = 'Full-Stack',
                city = 'İzmir',
                district = 'Bornova',
                self_reported_stress = 4,
                weekly_available_hours = 12,
                capacity_source = 'onboarding',
                interests = CAST(:interests AS jsonb)
            WHERE user_id = :uid AND tenant_id = :tid
            """
        ),
        {
            "uid": str(USER_AYSE_ID),
            "tid": str(TENANT_ALPHA_ID),
            "interests": json.dumps(
                {
                    "hobbies": ["Yürüyüş", "Kitap"],
                    "recharge": ["Doğada olmak"],
                    "notes": ["Video demo — Ayşe"],
                },
                ensure_ascii=False,
            ),
        },
    )
    print("  Ayşe Yılmaz hazir (capacity=48, onboarding=true)")

    # --- İkinci + üçüncü öğrenci (Can kırmızı, Elif yeşil) ---
    await session.execute(
        text(
            """
            INSERT INTO users (id, tenant_id, email, full_name, role, password_hash)
            VALUES
                (:uid_can, :tid, 'can.risk@equa.dev', 'Can Demir', 'student', :pw),
                (:uid_elif, :tid, 'elif.stable@equa.dev', 'Elif Kara', 'student', :pw)
            ON CONFLICT (tenant_id, email) DO UPDATE
              SET password_hash = EXCLUDED.password_hash,
                  role = EXCLUDED.role,
                  full_name = EXCLUDED.full_name
            """
        ),
        {
            "uid_can": str(USER_CAN_ID),
            "uid_elif": str(USER_ELIF_ID),
            "tid": str(TENANT_ALPHA_ID),
            "pw": pw,
        },
    )
    await session.execute(
        text(
            """
            INSERT INTO student_profiles (
                user_id, tenant_id, capacity_score, onboarding_completed,
                city, program_track, self_reported_stress, weekly_available_hours,
                capacity_source
            )
            VALUES
                (
                    :uid_can, :tid, 32.00, true,
                    'İstanbul', 'Full-Stack', 5, 6, 'onboarding'
                ),
                (
                    :uid_elif, :tid, 82.00, true,
                    'Ankara', 'Full-Stack', 2, 20, 'onboarding'
                )
            ON CONFLICT (user_id) DO UPDATE SET
                capacity_score = EXCLUDED.capacity_score,
                onboarding_completed = EXCLUDED.onboarding_completed,
                city = EXCLUDED.city,
                program_track = EXCLUDED.program_track,
                self_reported_stress = EXCLUDED.self_reported_stress,
                weekly_available_hours = EXCLUDED.weekly_available_hours,
                capacity_source = EXCLUDED.capacity_source
            """
        ),
        {
            "uid_can": str(USER_CAN_ID),
            "uid_elif": str(USER_ELIF_ID),
            "tid": str(TENANT_ALPHA_ID),
        },
    )
    print("  Can Demir (risk) + Elif Kara (stabil) eklendi")

    # --- Video risk sinyalleri: eski video_demo satırlarını kapat, yenilerini yaz ---
    await session.execute(
        text(
            """
            UPDATE risk_signals
            SET is_active = false
            WHERE tenant_id = :tid
              AND category = 'video_demo'
              AND is_active = true
            """
        ),
        {"tid": str(TENANT_ALPHA_ID)},
    )

    await session.execute(
        text(
            """
            INSERT INTO risk_signals (
                id, tenant_id, user_id, level, category, rationale, metrics, is_active
            )
            VALUES
                (
                    :sid_ayse, :tid, :uid_ayse, 'yellow', 'video_demo',
                    'Kapasite düşük ve görev temposu düşüyor; mentör check-in önerilir.',
                    CAST(:m_ayse AS jsonb), true
                ),
                (
                    :sid_can, :tid, :uid_can, 'high_risk', 'video_demo',
                    'Son 7 günde check-in kaçırma yüksek ve görev tamamlanma oranı düşük.',
                    CAST(:m_can AS jsonb), true
                ),
                (
                    :sid_elif, :tid, :uid_elif, 'green', 'video_demo',
                    'Check-in ve görev metrikleri stabil.',
                    CAST(:m_elif AS jsonb), true
                )
            """
        ),
        {
            "sid_ayse": str(uuid.uuid4()),
            "sid_can": str(uuid.uuid4()),
            "sid_elif": str(uuid.uuid4()),
            "tid": str(TENANT_ALPHA_ID),
            "uid_ayse": str(USER_AYSE_ID),
            "uid_can": str(USER_CAN_ID),
            "uid_elif": str(USER_ELIF_ID),
            "m_ayse": json.dumps(
                {
                    "capacity_score": 48,
                    "task_completion_rate": 0.33,
                    "missed_days_7": 3,
                    "open_tasks": 2,
                    "source": "video_seed",
                }
            ),
            "m_can": json.dumps(
                {
                    "capacity_score": 32,
                    "task_completion_rate": 0.15,
                    "missed_days_7": 5,
                    "open_tasks": 4,
                    "source": "video_seed",
                }
            ),
            "m_elif": json.dumps(
                {
                    "capacity_score": 82,
                    "task_completion_rate": 0.9,
                    "missed_days_7": 0,
                    "open_tasks": 0,
                    "source": "video_seed",
                }
            ),
        },
    )
    print("  risk_signals: Ayşe=yellow, Can=high_risk, Elif=green")

    # --- Ayşe bugünkü check-in temiz (canlı demo) ---
    await session.execute(
        text(
            """
            DELETE FROM daily_tasks
            WHERE user_id = :uid
              AND tenant_id = :tid
              AND checkin_session_id IN (
                  SELECT id FROM checkin_sessions
                  WHERE user_id = :uid
                    AND tenant_id = :tid
                    AND checkin_date = CURRENT_DATE
              )
            """
        ),
        {"uid": str(USER_AYSE_ID), "tid": str(TENANT_ALPHA_ID)},
    )
    await session.execute(
        text(
            """
            DELETE FROM checkin_sessions
            WHERE user_id = :uid
              AND tenant_id = :tid
              AND checkin_date = CURRENT_DATE
            """
        ),
        {"uid": str(USER_AYSE_ID), "tid": str(TENANT_ALPHA_ID)},
    )
    print("  Ayşe bugunku check-in temizlendi")

    await session.commit()
    print("Video overlay commit edildi")


async def seed_curriculum_if_needed(session: AsyncSession) -> None:
    """RAG için örnek müfredat; aynı başlık varsa atlar."""
    from backend.scripts.ingest_curriculum import SAMPLE_CURRICULUM
    from backend.services.rag.ingest import ingest_curriculum_text

    await _set_alpha_context(session)
    existing = await session.execute(
        text(
            """
            SELECT id FROM curricula
            WHERE tenant_id = :tid AND title = :title
            LIMIT 1
            """
        ),
        {"tid": str(TENANT_ALPHA_ID), "title": VIDEO_CURRICULUM_TITLE},
    )
    if existing.first() is not None:
        print("  Mufredat zaten var — ingest atlandi")
        return

    print("  Mufredat ingest basliyor...")
    curriculum = await ingest_curriculum_text(
        session,
        tenant_id=TENANT_ALPHA_ID,
        title=VIDEO_CURRICULUM_TITLE,
        text=SAMPLE_CURRICULUM,
        description="Video demo icin ornek React bootcamp mufredati",
        source_type="manual",
        uploaded_by=USER_ALPHA_ADMIN_ID,
    )
    await session.commit()
    print(f"  Mufredat hazir: {curriculum.id}")


def _print_logins() -> None:
    print("")
    print("=== Video demo girisleri (tenant slug + email + sifre) ===")
    print("  Ogrenci Ayşe : bootcamp-alpha / test_student_alpha@equa.dev / password123")
    print("  Ogrenci Can  : bootcamp-alpha / can.risk@equa.dev / password123  (kirmizi)")
    print("  Ogrenci Elif : bootcamp-alpha / elif.stable@equa.dev / password123  (yesil)")
    print("  Kurum Admin  : bootcamp-alpha / coordinator_alpha@equa.dev / password123")
    print("")
    print("Demo sirasi: Ayşe ile /chat → Can ile kurumda kirmizi satira tikla")


async def run(*, skip_base: bool = False, skip_curriculum: bool = False) -> None:
    engine = create_async_engine(settings.database_url, echo=False)
    session_factory = async_sessionmaker(engine, expire_on_commit=False)
    try:
        async with session_factory() as session:
            if not skip_base:
                await base_seed(session)
            else:
                print("Temel dev_seed atlandi (--skip-base)")

        async with session_factory() as session:
            await seed_video_overlay(session)

        if not skip_curriculum:
            async with session_factory() as session:
                try:
                    await seed_curriculum_if_needed(session)
                except Exception as exc:  # noqa: BLE001 — seed UX: soft-fail curriculum
                    await session.rollback()
                    print(f"  Mufredat ingest basarisiz (devam): {exc}")
        else:
            print("Mufredat atlandi (--skip-curriculum)")

        _print_logins()
    finally:
        await engine.dispose()


def main() -> None:
    parser = argparse.ArgumentParser(description="Equa video demo seed")
    parser.add_argument(
        "--skip-base",
        action="store_true",
        help="dev_seed calistirma (sadece video overlay)",
    )
    parser.add_argument(
        "--skip-curriculum",
        action="store_true",
        help="RAG mufredat ingest atla",
    )
    args = parser.parse_args()
    asyncio.run(run(skip_base=args.skip_base, skip_curriculum=args.skip_curriculum))


if __name__ == "__main__":
    main()

"""
backend/scripts/ingest_curriculum.py
A4/A5: Ingest sample or file-based curriculum into pgvector.
"""

from __future__ import annotations

import argparse
import asyncio
import uuid
from pathlib import Path

from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from backend.config import settings
from backend.db.tenant_context import apply_tenant_context
from backend.services.rag.ingest import ingest_curriculum_text

SAMPLE_CURRICULUM = """
Hafta 1 — React Temelleri
JSX, bileşenler, props ve state kavramları. useState ile yerel durum yönetimi.

Hafta 2 — React Hooks
useEffect, useRef ve custom hook yazımı. Side effect temizliği ve dependency array.

Hafta 3 — Routing ve Formlar
React Router ile sayfa geçişleri. Kontrollü formlar ve temel validasyon.

Hafta 4 — Veri Çekme
Fetch API, loading/error/empty state kalıpları. Basit SSE ile canlı güncelleme.

Hafta 5 — Test
Vitest ve React Testing Library ile bileşen testleri. getByRole erişilebilir sorgular.

Hafta 6 — PWA
Service worker, manifest ve offline kabuk. Mobil-first layout.
"""

# Seed tenant alpha
DEFAULT_TENANT = uuid.UUID("11111111-1111-1111-1111-111111111111")


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--tenant-id", default=str(DEFAULT_TENANT))
    parser.add_argument("--title", default="Bootcamp React Müfredatı")
    parser.add_argument("--file", default="")
    args = parser.parse_args()

    tenant_id = uuid.UUID(args.tenant_id)
    if args.file:
        text = Path(args.file).read_text(encoding="utf-8")
    else:
        text = SAMPLE_CURRICULUM

    engine = create_async_engine(settings.database_url, echo=False)
    factory = async_sessionmaker(engine, expire_on_commit=False)

    async with factory() as session:
        await apply_tenant_context(session, tenant_id)
        curriculum = await ingest_curriculum_text(
            session,
            tenant_id=tenant_id,
            title=args.title,
            text=text,
        )
        await session.commit()
        print(f"Ingested curriculum {curriculum.id}")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())

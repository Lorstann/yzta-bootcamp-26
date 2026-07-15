"""
backend/alembic/env.py
D3: Alembic migration ortamı.

- Async engine kullanır (asyncio modunda çalışır)
- DATABASE_URL'i backend/config.py üzerinden okur (.env'den)
- Tüm modeller Base'den türediği için otomatik keşfedilir
"""

import sys
import os

# Proje kökünü Python path'e ekle (backend modülü bulunabilsin)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# Alembic Config nesnesi — alembic.ini'yi temsil eder
config = context.config

# Python logging konfigürasyonu
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Model metadata — autogenerate için gerekli
from backend.db.base import Base  # noqa: E402
from backend.config import settings  # noqa: E402

# .env'deki DATABASE_URL'i alembic.ini'nin üzerine yaz
config.set_main_option("sqlalchemy.url", settings.database_url)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Offline modda migration çalıştır (DB bağlantısı olmadan SQL üretir)."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection: Connection) -> None:
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Async engine ile online migration çalıştır."""
    connectable = async_engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

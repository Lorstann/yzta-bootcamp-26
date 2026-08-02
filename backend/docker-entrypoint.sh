#!/bin/sh
set -eu

: "${DB_HOST:?DB_HOST is required}"
: "${DB_PORT:=5432}"
: "${DB_NAME:=equa}"
: "${DB_USER:?DB_USER is required}"
: "${DB_PASSWORD:?DB_PASSWORD is required}"

export DATABASE_URL="$(
  python - <<'PY'
import os
import urllib.parse

user = urllib.parse.quote(os.environ["DB_USER"], safe="")
password = urllib.parse.quote(os.environ["DB_PASSWORD"], safe="")
host = os.environ["DB_HOST"]
port = os.environ.get("DB_PORT", "5432")
name = os.environ.get("DB_NAME", "equa")
print(f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{name}")
PY
)"

# One-off commands (e.g. seed): docker-entrypoint.sh python -m backend.db.seeds.dev_seed
if [ "$#" -gt 0 ]; then
  exec "$@"
fi

echo "Ensuring Postgres extensions..."
python - <<'PY'
import asyncio
import os
import asyncpg

async def main() -> None:
    dsn = os.environ["DATABASE_URL"].replace("postgresql+asyncpg://", "postgresql://", 1)
    conn = await asyncpg.connect(dsn)
    try:
        await conn.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
        await conn.execute("CREATE EXTENSION IF NOT EXISTS vector")
    finally:
        await conn.close()

asyncio.run(main())
PY

echo "Running Alembic migrations..."
alembic upgrade head

echo "Starting Equa API on ${APP_HOST:-0.0.0.0}:${APP_PORT:-8000}"
exec uvicorn backend.main:app \
  --host "${APP_HOST:-0.0.0.0}" \
  --port "${APP_PORT:-8000}" \
  --proxy-headers \
  --forwarded-allow-ips='*'

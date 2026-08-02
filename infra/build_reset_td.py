import json
from pathlib import Path

td_path = Path("infra/td.json")
td = json.loads(td_path.read_text(encoding="utf-8"))
for key in (
    "taskDefinitionArn",
    "revision",
    "status",
    "requiresAttributes",
    "compatibilities",
    "registeredAt",
    "registeredBy",
):
    td.pop(key, None)

# Keep reset payload as a single shell string; avoid nested """ inside.
reset_py = r'''
import asyncio
import os
import urllib.parse

user = urllib.parse.quote(os.environ["DB_USER"], safe="")
password = urllib.parse.quote(os.environ["DB_PASSWORD"], safe="")
host = os.environ["DB_HOST"]
port = os.environ.get("DB_PORT", "5432")
name = os.environ.get("DB_NAME", "equa")
os.environ["DATABASE_URL"] = f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{name}"

from sqlalchemy import text
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

ALPHA_U = "aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaaaaaa"
BETA_U = "bbbbbbbb-bbbb-bbbb-bbbb-bbbbbbbbbbbb"
ADMIN_U = "cccccccc-cccc-cccc-cccc-cccccccccccc"
ALPHA_T = "11111111-1111-1111-1111-111111111111"
BETA_T = "22222222-2222-2222-2222-222222222222"

STATEMENTS = [
    "DELETE FROM daily_tasks WHERE user_id IN (:u1, :u2, :u3)",
    "DELETE FROM checkin_sessions WHERE user_id IN (:u1, :u2, :u3)",
    "DELETE FROM capacity_snapshots WHERE user_id IN (:u1, :u2, :u3)",
    "DELETE FROM risk_signals WHERE user_id IN (:u1, :u2, :u3)",
    """
    INSERT INTO student_profiles (user_id, tenant_id, onboarding_completed, capacity_source)
    VALUES
      (:alpha_u, :alpha_t, false, 'auto'),
      (:beta_u, :beta_t, false, 'auto')
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
    """,
]


async def main() -> None:
    engine = create_async_engine(os.environ["DATABASE_URL"], echo=False)
    factory = async_sessionmaker(engine, expire_on_commit=False)
    params = {
        "u1": ALPHA_U,
        "u2": BETA_U,
        "u3": ADMIN_U,
        "alpha_u": ALPHA_U,
        "alpha_t": ALPHA_T,
        "beta_u": BETA_U,
        "beta_t": BETA_T,
    }
    async with factory() as session:
        for stmt in STATEMENTS:
            await session.execute(text(stmt), params)
        await session.commit()
    await engine.dispose()
    print("Demo reset OK")
    print("Alpha: bootcamp-alpha / test_student_alpha@equa.dev / password123")
    print("Beta:  bootcamp-beta  / test_student_beta@equa.dev  / password123")
    print("Admin: bootcamp-alpha / coordinator_alpha@equa.dev / password123")
    print("Use a private window or log out so JWT/localStorage is cleared.")


asyncio.run(main())
'''.lstrip()

# heredoc wrapper for container entrypoint
reset_cmd = "python - <<'PY'\n" + reset_py + "\nPY"

container = td["containerDefinitions"][0]
container["entryPoint"] = ["sh", "-c"]
container["command"] = [reset_cmd]
container.pop("healthCheck", None)

out = Path("infra/td-reset.json")
out.write_text(json.dumps(td), encoding="utf-8")
print(f"wrote {out}")

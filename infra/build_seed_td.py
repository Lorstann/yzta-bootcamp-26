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

seed_cmd = r"""
python - <<'PY'
import asyncio
import os
import urllib.parse

user = urllib.parse.quote(os.environ["DB_USER"], safe="")
password = urllib.parse.quote(os.environ["DB_PASSWORD"], safe="")
host = os.environ["DB_HOST"]
port = os.environ.get("DB_PORT", "5432")
name = os.environ.get("DB_NAME", "equa")
os.environ["DATABASE_URL"] = f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{name}"

from backend.db.seeds.video_seed import run

asyncio.run(run())
PY
""".strip()

container = td["containerDefinitions"][0]
container["entryPoint"] = ["sh", "-c"]
container["command"] = [seed_cmd]
# One-off: don't need healthcheck blocking
container.pop("healthCheck", None)

out = Path("infra/td-seed.json")
out.write_text(json.dumps(td), encoding="utf-8")
print(f"wrote {out}")

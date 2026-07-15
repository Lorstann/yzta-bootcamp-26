"""
backend/scripts/seed.py
D9: Seed script çalıştırıcı.

Kullanım:
    source .venv/bin/activate
    python backend/scripts/seed.py
"""

import sys
import os

# Proje kökünü path'e ekle
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from backend.db.seeds.dev_seed import main
import asyncio

if __name__ == "__main__":
    asyncio.run(main())

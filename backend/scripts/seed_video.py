"""
backend/scripts/seed_video.py

Video demo seed çalıştırıcı.

Kullanım:
    python backend/scripts/seed_video.py
    python backend/scripts/seed_video.py --skip-curriculum
    python -m backend.db.seeds.video_seed
"""

from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from backend.db.seeds.video_seed import main

if __name__ == "__main__":
    main()

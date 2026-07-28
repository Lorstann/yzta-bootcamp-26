"""
backend/db/models/__init__.py
B8: Tüm ORM modellerini tek yerden dışarıya sunar.
Alembic env.py ve diğer modüller buradan import eder.
"""

from backend.db.models.tenant import Tenant
from backend.db.models.user import User, StudentProfile
from backend.db.models.curriculum import Curriculum, CurriculumChunk
from backend.db.models.checkin import CheckinSession, WeeklyTask
from backend.db.models.risk import RiskSignal

__all__ = [
    "Tenant",
    "User",
    "StudentProfile",
    "Curriculum",
    "CurriculumChunk",
    "CheckinSession",
    "WeeklyTask",
    "RiskSignal",
]

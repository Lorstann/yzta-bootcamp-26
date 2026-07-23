"""
backend/repositories/__init__.py
B8: Repository katmanı dışa aktarımı.
"""

from backend.repositories.base import BaseRepository
from backend.repositories.tenant_repo import TenantRepository
from backend.repositories.user_repo import UserRepository, StudentProfileRepository

__all__ = [
    "BaseRepository",
    "TenantRepository",
    "UserRepository",
    "StudentProfileRepository",
]

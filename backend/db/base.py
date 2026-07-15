"""
backend/db/base.py
D3: SQLAlchemy declarative base — tüm ORM modelleri buradan türer.
"""

from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    """Tüm veritabanı modellerinin temel sınıfı."""
    pass

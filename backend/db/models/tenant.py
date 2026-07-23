"""
backend/db/models/tenant.py
B8: Tenant ORM modeli — tenants tablosunun Python karşılığı.
"""

import uuid
from datetime import datetime
from sqlalchemy import Boolean, String, TIMESTAMP, text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from backend.db.base import Base


class Tenant(Base):
    __tablename__ = "tenants"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        server_default=text("uuid_generate_v4()"),
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    is_active: Mapped[bool] = mapped_column(Boolean, server_default=text("true"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=text("now()"), nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), server_default=text("now()"), nullable=False
    )

    # İlişkiler
    users: Mapped[list["User"]] = relationship("User", back_populates="tenant")  # type: ignore[name-defined]

    def __repr__(self) -> str:
        return f"<Tenant id={self.id} slug={self.slug!r}>"

"""D4: tenants ve users tablolarını oluştur

Revision ID: 001
Revises:
Create Date: 2026-07-16

Tablolar:
- tenants: Her bootcamp/kurum bir tenant. Tüm veriler tenant'a göre ayrılır.
- users: Sisteme kayıtlı kullanıcılar (öğrenci, eğitmen, admin).
         Her user bir tenant'a aittir (tenant_id FK).
"""

from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- tenants tablosu ---
    op.create_table(
        "tenants",
        sa.Column("id", sa.UUID(), server_default=sa.text("uuid_generate_v4()"), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False, comment="Kurumun tam adı"),
        sa.Column("slug", sa.String(length=100), nullable=False, comment="URL dostu kısa isim (benzersiz)"),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("slug", name="uq_tenants_slug"),
    )
    op.create_index("ix_tenants_slug", "tenants", ["slug"])

    # --- users tablosu ---
    op.create_table(
        "users",
        sa.Column("id", sa.UUID(), server_default=sa.text("uuid_generate_v4()"), nullable=False),
        sa.Column("tenant_id", sa.UUID(), nullable=False, comment="Hangi kuruma ait"),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=True),
        sa.Column("role", sa.String(length=50), server_default=sa.text("'student'"), nullable=False,
                  comment="student | instructor | admin"),
        sa.Column("is_active", sa.Boolean(), server_default=sa.text("true"), nullable=False),
        sa.Column("created_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.TIMESTAMP(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["tenant_id"], ["tenants.id"], ondelete="CASCADE", name="fk_users_tenant_id"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("tenant_id", "email", name="uq_users_tenant_email"),
    )
    op.create_index("ix_users_tenant_id", "users", ["tenant_id"])
    op.create_index("ix_users_email", "users", ["email"])


def downgrade() -> None:
    # Tabloları ters sırayla sil (FK bağımlılığı nedeniyle önce users)
    op.drop_table("users")
    op.drop_table("tenants")

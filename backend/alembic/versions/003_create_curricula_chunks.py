"""D6: curricula ve curriculum_chunks tablolarını oluştur

Revision ID: 003
Revises: 002
Create Date: 2026-07-16

Tablolar:
- curricula: Tenant'a ait müfredat belgesi (ders/bootcamp içeriği).
- curriculum_chunks: Müfredatın AI için parçalanmış bölümleri.
  Her chunk'ın bir pgvector embedding'i var — similarity search için.
"""

from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector

revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- curricula tablosu ---
    op.create_table(
        "curricula",
        sa.Column(
            "id",
            sa.UUID(),
            server_default=sa.text("uuid_generate_v4()"),
            nullable=False,
        ),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column(
            "title",
            sa.String(length=500),
            nullable=False,
            comment="Müfredatın başlığı (ör: Python Temelleri)",
        ),
        sa.Column(
            "description",
            sa.Text(),
            nullable=True,
            comment="Kısa açıklama",
        ),
        sa.Column(
            "source_type",
            sa.String(length=50),
            server_default=sa.text("'manual'"),
            nullable=False,
            comment="manual | pdf | url",
        ),
        sa.Column(
            "is_active",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"], ["tenants.id"],
            ondelete="CASCADE",
            name="fk_curricula_tenant_id",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_curricula_tenant_id", "curricula", ["tenant_id"])

    # --- curriculum_chunks tablosu ---
    op.create_table(
        "curriculum_chunks",
        sa.Column(
            "id",
            sa.UUID(),
            server_default=sa.text("uuid_generate_v4()"),
            nullable=False,
        ),
        sa.Column("curriculum_id", sa.UUID(), nullable=False),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column(
            "content",
            sa.Text(),
            nullable=False,
            comment="Ham metin içeriği",
        ),
        sa.Column(
            "chunk_index",
            sa.Integer(),
            nullable=False,
            comment="Müfredat içindeki sıra numarası",
        ),
        sa.Column(
            "embedding",
            Vector(1536),
            nullable=True,
            comment="OpenAI text-embedding-3-small vektörü (AI ekibi doldurur)",
        ),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["curriculum_id"], ["curricula.id"],
            ondelete="CASCADE",
            name="fk_curriculum_chunks_curriculum_id",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"], ["tenants.id"],
            ondelete="CASCADE",
            name="fk_curriculum_chunks_tenant_id",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_curriculum_chunks_curriculum_id", "curriculum_chunks", ["curriculum_id"])
    op.create_index("ix_curriculum_chunks_tenant_id", "curriculum_chunks", ["tenant_id"])


def downgrade() -> None:
    op.drop_table("curriculum_chunks")
    op.drop_table("curricula")

"""D5: student_profiles tablosunu oluştur

Revision ID: 002
Revises: 001
Create Date: 2026-07-16

Tablo:
- student_profiles: Öğrenciye özgü profil bilgileri.
  users tablosuyla 1:1 ilişki. Kapasite skoru, LinkedIn, biyografi gibi
  öğrenci özelindeki verileri tutar.
"""

from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op

revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "student_profiles",
        sa.Column(
            "id",
            sa.UUID(),
            server_default=sa.text("uuid_generate_v4()"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            sa.UUID(),
            nullable=False,
            comment="users tablosuna 1:1 bağlı",
        ),
        sa.Column(
            "tenant_id",
            sa.UUID(),
            nullable=False,
            comment="Hızlı sorgular için tenant referansı",
        ),
        sa.Column(
            "capacity_score",
            sa.Numeric(precision=5, scale=2),
            nullable=True,
            comment="AI check-in'de hesaplanan haftalık kapasite (0-100)",
        ),
        sa.Column(
            "linkedin_url",
            sa.String(length=500),
            nullable=True,
        ),
        sa.Column(
            "bio",
            sa.Text(),
            nullable=True,
            comment="Öğrencinin kısa biyografisi / tanıtımı",
        ),
        sa.Column(
            "onboarding_completed",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
            comment="Tanışma anketi tamamlandı mı?",
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
            ["user_id"], ["users.id"],
            ondelete="CASCADE",
            name="fk_student_profiles_user_id",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"], ["tenants.id"],
            ondelete="CASCADE",
            name="fk_student_profiles_tenant_id",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", name="uq_student_profiles_user_id"),
    )
    op.create_index("ix_student_profiles_user_id", "student_profiles", ["user_id"])
    op.create_index("ix_student_profiles_tenant_id", "student_profiles", ["tenant_id"])


def downgrade() -> None:
    op.drop_table("student_profiles")

"""D7: checkin_sessions ve weekly_tasks tablolarını oluştur

Revision ID: 004
Revises: 003
Create Date: 2026-07-16

Tablolar:
- checkin_sessions: Öğrencinin haftalık AI check-in görüşmesi.
  Nasıl hissetttiği, genel durumu, AI konuşma özeti burada tutulur.
- weekly_tasks: Check-in sırasında belirlenen haftalık görevler.
  Her görevin tamamlanma durumu takip edilir.
"""

from typing import Sequence, Union
import sqlalchemy as sa
from alembic import op

revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # --- checkin_sessions tablosu ---
    op.create_table(
        "checkin_sessions",
        sa.Column(
            "id",
            sa.UUID(),
            server_default=sa.text("uuid_generate_v4()"),
            nullable=False,
        ),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column(
            "week_start",
            sa.Date(),
            nullable=False,
            comment="Check-in'in ait olduğu haftanın başlangıcı (Pazartesi)",
        ),
        sa.Column(
            "mood_score",
            sa.Integer(),
            nullable=True,
            comment="Öğrencinin kendini nasıl hissettiği (1-5)",
        ),
        sa.Column(
            "summary",
            sa.Text(),
            nullable=True,
            comment="AI'nin oluşturduğu görüşme özeti",
        ),
        sa.Column(
            "status",
            sa.String(length=50),
            server_default=sa.text("'pending'"),
            nullable=False,
            comment="pending | in_progress | completed",
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
            name="fk_checkin_sessions_user_id",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"], ["tenants.id"],
            ondelete="CASCADE",
            name="fk_checkin_sessions_tenant_id",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "week_start", name="uq_checkin_user_week"),
    )
    op.create_index("ix_checkin_sessions_user_id", "checkin_sessions", ["user_id"])
    op.create_index("ix_checkin_sessions_tenant_id", "checkin_sessions", ["tenant_id"])
    op.create_index("ix_checkin_sessions_week_start", "checkin_sessions", ["week_start"])

    # --- weekly_tasks tablosu ---
    op.create_table(
        "weekly_tasks",
        sa.Column(
            "id",
            sa.UUID(),
            server_default=sa.text("uuid_generate_v4()"),
            nullable=False,
        ),
        sa.Column("checkin_session_id", sa.UUID(), nullable=False),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column(
            "title",
            sa.String(length=500),
            nullable=False,
            comment="Görev başlığı",
        ),
        sa.Column(
            "description",
            sa.Text(),
            nullable=True,
            comment="Görevin detayı",
        ),
        sa.Column(
            "is_completed",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
        ),
        sa.Column(
            "completed_at",
            sa.TIMESTAMP(timezone=True),
            nullable=True,
        ),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["checkin_session_id"], ["checkin_sessions.id"],
            ondelete="CASCADE",
            name="fk_weekly_tasks_checkin_session_id",
        ),
        sa.ForeignKeyConstraint(
            ["tenant_id"], ["tenants.id"],
            ondelete="CASCADE",
            name="fk_weekly_tasks_tenant_id",
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"],
            ondelete="CASCADE",
            name="fk_weekly_tasks_user_id",
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_weekly_tasks_checkin_session_id", "weekly_tasks", ["checkin_session_id"])
    op.create_index("ix_weekly_tasks_user_id", "weekly_tasks", ["user_id"])


def downgrade() -> None:
    op.drop_table("weekly_tasks")
    op.drop_table("checkin_sessions")

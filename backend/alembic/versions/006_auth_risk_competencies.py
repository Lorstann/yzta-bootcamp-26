"""Plan 2–5: auth, competencies, risk signals, check-in messages

Revision ID: 006
Revises: 005
Create Date: 2026-07-28
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "006"
down_revision: Union[str, None] = "005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column("password_hash", sa.String(length=255), nullable=True),
    )

    op.add_column(
        "student_profiles",
        sa.Column(
            "competencies",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            comment="LinkedIn/OCR yetkinlik JSON",
        ),
    )

    op.add_column(
        "checkin_sessions",
        sa.Column(
            "messages",
            postgresql.JSONB(astext_type=sa.Text()),
            server_default=sa.text("'[]'::jsonb"),
            nullable=False,
            comment="Check-in sohbet mesajları [{role, content}]",
        ),
    )

    op.create_table(
        "risk_signals",
        sa.Column(
            "id",
            sa.UUID(),
            server_default=sa.text("uuid_generate_v4()"),
            nullable=False,
        ),
        sa.Column("tenant_id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column(
            "level",
            sa.String(length=20),
            nullable=False,
            comment="green | yellow | red | high_risk",
        ),
        sa.Column(
            "category",
            sa.String(length=50),
            nullable=True,
            comment="guardrail category or scoring reason key",
        ),
        sa.Column(
            "rationale",
            sa.Text(),
            nullable=True,
            comment="XAI gerekçe — ham chat yok",
        ),
        sa.Column(
            "metrics",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
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
        sa.ForeignKeyConstraint(
            ["tenant_id"], ["tenants.id"], ondelete="CASCADE", name="fk_risk_signals_tenant"
        ),
        sa.ForeignKeyConstraint(
            ["user_id"], ["users.id"], ondelete="CASCADE", name="fk_risk_signals_user"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_risk_signals_tenant_id", "risk_signals", ["tenant_id"])
    op.create_index("ix_risk_signals_user_id", "risk_signals", ["user_id"])

    op.execute("ALTER TABLE risk_signals ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE risk_signals FORCE ROW LEVEL SECURITY;")
    op.execute(
        """
        CREATE POLICY tenant_isolation_policy ON risk_signals
        AS PERMISSIVE FOR ALL
        TO PUBLIC
        USING (tenant_id = current_setting('app.current_tenant_id', true)::uuid)
        WITH CHECK (tenant_id = current_setting('app.current_tenant_id', true)::uuid);
        """
    )


def downgrade() -> None:
    op.execute("DROP POLICY IF EXISTS tenant_isolation_policy ON risk_signals;")
    op.execute("ALTER TABLE risk_signals NO FORCE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE risk_signals DISABLE ROW LEVEL SECURITY;")
    op.drop_table("risk_signals")
    op.drop_column("checkin_sessions", "messages")
    op.drop_column("student_profiles", "competencies")
    op.drop_column("users", "password_hash")

"""008: capacity_snapshots + weekly_tasks.due_date

Revision ID: 008
Revises: 007
Create Date: 2026-08-01
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "008"
down_revision: Union[str, None] = "007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "capacity_snapshots",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            server_default=sa.text("uuid_generate_v4()"),
            primary_key=True,
        ),
        sa.Column(
            "tenant_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("tenants.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "user_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("users.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("score", sa.Numeric(5, 2), nullable=False),
        sa.Column(
            "recorded_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
    )
    op.create_index(
        "ix_capacity_snapshots_user_recorded",
        "capacity_snapshots",
        ["user_id", "recorded_at"],
    )
    op.execute("ALTER TABLE capacity_snapshots ENABLE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE capacity_snapshots FORCE ROW LEVEL SECURITY;")
    op.execute(
        """
        CREATE POLICY tenant_isolation_policy ON capacity_snapshots
        AS PERMISSIVE FOR ALL
        TO PUBLIC
        USING (tenant_id = current_setting('app.current_tenant_id', true)::uuid)
        WITH CHECK (tenant_id = current_setting('app.current_tenant_id', true)::uuid);
        """
    )
    op.add_column(
        "weekly_tasks",
        sa.Column("due_date", sa.Date(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("weekly_tasks", "due_date")
    op.execute("DROP POLICY IF EXISTS tenant_isolation_policy ON capacity_snapshots;")
    op.execute("ALTER TABLE capacity_snapshots NO FORCE ROW LEVEL SECURITY;")
    op.execute("ALTER TABLE capacity_snapshots DISABLE ROW LEVEL SECURITY;")
    op.drop_index("ix_capacity_snapshots_user_recorded", table_name="capacity_snapshots")
    op.drop_table("capacity_snapshots")

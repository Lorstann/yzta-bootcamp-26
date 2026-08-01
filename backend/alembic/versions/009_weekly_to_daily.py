"""009: weekly check-in → daily check-in

Rename checkin_sessions.week_start → checkin_date,
rename weekly_tasks → daily_tasks (RLS policy moves with the table),
add unique (tenant_id, user_id, checkin_date).

Revision ID: 009
Revises: 008
Create Date: 2026-08-01
"""

from typing import Sequence, Union

from alembic import op

revision: str = "009"
down_revision: Union[str, None] = "008"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column("checkin_sessions", "week_start", new_column_name="checkin_date")

    # Rename table; Postgres moves indexes/constraints/RLS policies with it.
    op.rename_table("weekly_tasks", "daily_tasks")

    # Deduplicate same-day sessions before unique index (keep newest).
    op.execute(
        """
        DELETE FROM checkin_sessions a
        USING checkin_sessions b
        WHERE a.tenant_id = b.tenant_id
          AND a.user_id = b.user_id
          AND a.checkin_date = b.checkin_date
          AND a.created_at < b.created_at;
        """
    )

    op.create_index(
        "ux_checkin_user_date",
        "checkin_sessions",
        ["tenant_id", "user_id", "checkin_date"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("ux_checkin_user_date", table_name="checkin_sessions")
    op.rename_table("daily_tasks", "weekly_tasks")
    op.alter_column("checkin_sessions", "checkin_date", new_column_name="week_start")

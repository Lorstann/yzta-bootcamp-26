"""P1: task status + tenant revenue_per_student

Revision ID: 007
Revises: 006
Create Date: 2026-07-31
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "007"
down_revision: Union[str, None] = "006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "weekly_tasks",
        sa.Column(
            "status",
            sa.String(length=32),
            server_default=sa.text("'active'"),
            nullable=False,
        ),
    )
    # Migrate existing [ASKIDA] titles into status=suspended
    op.execute(
        """
        UPDATE weekly_tasks
        SET status = 'suspended',
            title = CASE
              WHEN title LIKE '[ASKIDA] %' THEN substring(title from 10)
              ELSE title
            END
        WHERE title LIKE '[ASKIDA] %'
        """
    )
    op.add_column(
        "tenants",
        sa.Column(
            "revenue_per_student",
            sa.Numeric(12, 2),
            server_default=sa.text("5000"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("tenants", "revenue_per_student")
    op.execute(
        """
        UPDATE weekly_tasks
        SET title = '[ASKIDA] ' || title
        WHERE status = 'suspended' AND title NOT LIKE '[ASKIDA] %'
        """
    )
    op.drop_column("weekly_tasks", "status")

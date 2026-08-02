"""013: auto capacity scoring fields

Adds self-reported stress / weekly hours / capacity_source to profiles,
source + factors to capacity_snapshots, weekly_hours to curricula.

Revision ID: 013
Revises: 012
Create Date: 2026-08-02
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "013"
down_revision: Union[str, None] = "012"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "student_profiles",
        sa.Column("self_reported_stress", sa.SmallInteger(), nullable=True),
    )
    op.add_column(
        "student_profiles",
        sa.Column("weekly_available_hours", sa.SmallInteger(), nullable=True),
    )
    op.add_column(
        "student_profiles",
        sa.Column(
            "capacity_source",
            sa.String(length=20),
            server_default=sa.text("'auto'"),
            nullable=False,
        ),
    )

    op.add_column(
        "capacity_snapshots",
        sa.Column(
            "source",
            sa.String(length=20),
            server_default=sa.text("'manual'"),
            nullable=False,
        ),
    )
    op.add_column(
        "capacity_snapshots",
        sa.Column(
            "factors",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
        ),
    )

    op.add_column(
        "curricula",
        sa.Column("weekly_hours", sa.SmallInteger(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("curricula", "weekly_hours")
    op.drop_column("capacity_snapshots", "factors")
    op.drop_column("capacity_snapshots", "source")
    op.drop_column("student_profiles", "capacity_source")
    op.drop_column("student_profiles", "weekly_available_hours")
    op.drop_column("student_profiles", "self_reported_stress")

"""010: check-in structured signals + stage machine columns

Adds energy_level, motivation_level, workload_level, main_blocker,
stage, turn_count to checkin_sessions for measurable daily check-ins.

Revision ID: 010
Revises: 009
Create Date: 2026-08-01
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "010"
down_revision: Union[str, None] = "009"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "checkin_sessions",
        sa.Column("energy_level", sa.SmallInteger(), nullable=True),
    )
    op.add_column(
        "checkin_sessions",
        sa.Column("motivation_level", sa.SmallInteger(), nullable=True),
    )
    op.add_column(
        "checkin_sessions",
        sa.Column("workload_level", sa.String(length=16), nullable=True),
    )
    op.add_column(
        "checkin_sessions",
        sa.Column("main_blocker", sa.Text(), nullable=True),
    )
    op.add_column(
        "checkin_sessions",
        sa.Column(
            "stage",
            sa.String(length=32),
            server_default="opening",
            nullable=False,
        ),
    )
    op.add_column(
        "checkin_sessions",
        sa.Column(
            "turn_count",
            sa.Integer(),
            server_default="0",
            nullable=False,
        ),
    )


def downgrade() -> None:
    op.drop_column("checkin_sessions", "turn_count")
    op.drop_column("checkin_sessions", "stage")
    op.drop_column("checkin_sessions", "main_blocker")
    op.drop_column("checkin_sessions", "workload_level")
    op.drop_column("checkin_sessions", "motivation_level")
    op.drop_column("checkin_sessions", "energy_level")

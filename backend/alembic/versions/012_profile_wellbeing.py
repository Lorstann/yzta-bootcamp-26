"""012: student profile wellbeing fields

Adds city, district, program_track, interests to student_profiles
for personalized burnout-prevention coaching.

Revision ID: 012
Revises: 011
Create Date: 2026-08-01
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "012"
down_revision: Union[str, None] = "011"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "student_profiles",
        sa.Column("city", sa.String(length=120), nullable=True),
    )
    op.add_column(
        "student_profiles",
        sa.Column("district", sa.String(length=120), nullable=True),
    )
    op.add_column(
        "student_profiles",
        sa.Column("program_track", sa.String(length=200), nullable=True),
    )
    op.add_column(
        "student_profiles",
        sa.Column(
            "interests",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=True,
            comment='{"hobbies":[],"recharge":[],"notes":[]}',
        ),
    )


def downgrade() -> None:
    op.drop_column("student_profiles", "interests")
    op.drop_column("student_profiles", "program_track")
    op.drop_column("student_profiles", "district")
    op.drop_column("student_profiles", "city")

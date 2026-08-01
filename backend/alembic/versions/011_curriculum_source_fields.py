"""011: curriculum source metadata for institution uploads

Adds file_name, file_uri, chunk_count, uploaded_by to curricula.

Revision ID: 011
Revises: 010
Create Date: 2026-08-01
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "011"
down_revision: Union[str, None] = "010"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "curricula",
        sa.Column("file_name", sa.String(length=500), nullable=True),
    )
    op.add_column(
        "curricula",
        sa.Column("file_uri", sa.Text(), nullable=True),
    )
    op.add_column(
        "curricula",
        sa.Column("chunk_count", sa.Integer(), nullable=True),
    )
    op.add_column(
        "curricula",
        sa.Column("uploaded_by", sa.UUID(), nullable=True),
    )
    op.create_foreign_key(
        "fk_curricula_uploaded_by_users",
        "curricula",
        "users",
        ["uploaded_by"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint(
        "fk_curricula_uploaded_by_users", "curricula", type_="foreignkey"
    )
    op.drop_column("curricula", "uploaded_by")
    op.drop_column("curricula", "chunk_count")
    op.drop_column("curricula", "file_uri")
    op.drop_column("curricula", "file_name")

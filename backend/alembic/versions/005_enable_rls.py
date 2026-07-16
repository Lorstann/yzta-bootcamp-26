"""D8: Tüm tenant-scoped tablolara RLS (Row-Level Security) ekle

Revision ID: 005
Revises: 004
Create Date: 2026-07-16

"""

from typing import Sequence, Union
from alembic import op

revision: str = "005"
down_revision: Union[str, None] = "004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

tenant_scoped_tables = [
    "users",
    "student_profiles",
    "curricula",
    "curriculum_chunks",
    "checkin_sessions",
    "weekly_tasks"
]

def upgrade() -> None:
    for table in tenant_scoped_tables:
        op.execute(f"ALTER TABLE {table} ENABLE ROW LEVEL SECURITY;")
        op.execute(f"ALTER TABLE {table} FORCE ROW LEVEL SECURITY;")
        
        policy_sql = f"""
        CREATE POLICY tenant_isolation_policy ON {table}
        AS PERMISSIVE FOR ALL
        TO PUBLIC
        USING (tenant_id = current_setting('app.current_tenant_id', true)::uuid)
        WITH CHECK (tenant_id = current_setting('app.current_tenant_id', true)::uuid);
        """
        op.execute(policy_sql)


def downgrade() -> None:
    for table in reversed(tenant_scoped_tables):
        op.execute(f"DROP POLICY IF EXISTS tenant_isolation_policy ON {table};")
        op.execute(f"ALTER TABLE {table} NO FORCE ROW LEVEL SECURITY;")
        op.execute(f"ALTER TABLE {table} DISABLE ROW LEVEL SECURITY;")

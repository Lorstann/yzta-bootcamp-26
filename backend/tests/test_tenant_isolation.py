"""
S19 - Tenant İzolasyonu Doğrulama (AC4) Test Senaryoları
"""

import uuid

import pytest
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from backend.tests.conftest import set_tenant_context

pytestmark = pytest.mark.asyncio


@pytest.fixture
async def seed_tenants(db_session: AsyncSession):
    """Test için iki farklı tenant ve seed verisi oluşturur."""
    tenant_a_id = uuid.uuid4()
    tenant_b_id = uuid.uuid4()

    await db_session.execute(
        text("INSERT INTO tenants (id, name, slug) VALUES (:id, :name, :slug)"),
        [
            {"id": tenant_a_id, "name": "Tenant A", "slug": f"tenant-a-{tenant_a_id.hex[:8]}"},
            {"id": tenant_b_id, "name": "Tenant B", "slug": f"tenant-b-{tenant_b_id.hex[:8]}"},
        ],
    )

    user_a_id = uuid.uuid4()
    user_b_id = uuid.uuid4()
    curriculum_a_id = uuid.uuid4()
    curriculum_b_id = uuid.uuid4()

    # Inserts as superuser (bypasses RLS); queries under equa_app enforce it
    await db_session.execute(
        text(
            "INSERT INTO users (id, tenant_id, email) VALUES (:id, :t_id, :email)"
        ),
        [
            {"id": user_a_id, "t_id": tenant_a_id, "email": "studentA@tenantA.com"},
            {"id": user_b_id, "t_id": tenant_b_id, "email": "studentB@tenantB.com"},
        ],
    )
    await db_session.execute(
        text(
            "INSERT INTO curricula (id, tenant_id, title) VALUES (:id, :t_id, :title)"
        ),
        [
            {"id": curriculum_a_id, "t_id": tenant_a_id, "title": "Tenant A Python Course"},
            {"id": curriculum_b_id, "t_id": tenant_b_id, "title": "Tenant B AI Course"},
        ],
    )
    await db_session.commit()

    return {
        "tenant_a_id": tenant_a_id,
        "tenant_b_id": tenant_b_id,
        "user_a_id": user_a_id,
        "user_b_id": user_b_id,
        "curriculum_b_id": curriculum_b_id,
    }


async def test_tenant_a_cannot_see_tenant_b_data(
    db_session: AsyncSession, seed_tenants: dict
):
    tenant_a_id = seed_tenants["tenant_a_id"]

    await set_tenant_context(db_session, tenant_a_id)

    result = await db_session.execute(text("SELECT id, email FROM users"))
    users = result.fetchall()

    assert len(users) == 1
    assert users[0].id == seed_tenants["user_a_id"]
    assert "studentB@tenantB.com" not in [u.email for u in users]


async def test_tenant_a_cannot_access_tenant_b_curriculum_by_id(
    db_session: AsyncSession, seed_tenants: dict
):
    tenant_a_id = seed_tenants["tenant_a_id"]
    curriculum_b_id = seed_tenants["curriculum_b_id"]

    await set_tenant_context(db_session, tenant_a_id)

    result = await db_session.execute(
        text("SELECT id FROM curricula WHERE id = :c_id"),
        {"c_id": curriculum_b_id},
    )
    curriculum = result.fetchone()
    assert curriculum is None


async def test_rls_bypass_prevention(db_session: AsyncSession, seed_tenants: dict):
    # equa_app with unknown tenant context → no rows (cannot bypass via missing/wrong id)
    await db_session.execute(text("SET LOCAL ROLE equa_app"))
    await db_session.execute(
        text("SELECT set_config('app.current_tenant_id', :tid, true)"),
        {"tid": str(uuid.uuid4())},
    )

    result = await db_session.execute(text("SELECT id FROM users"))
    users = result.fetchall()
    assert len(users) == 0

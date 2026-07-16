"""
S19 - Tenant İzolasyonu Doğrulama (AC4) Test Senaryoları
Bu testler, PostgreSQL seviyesindeki Row-Level Security (RLS) politikalarının
doğru çalışıp çalışmadığını doğrular.

Not: Bu testler veritabanı bağlantısı (db_session fixture) ve seed verisi gerektirir.
(Altyapı (B8) tamamlandığında doğrudan CI üzerinde çalıştırılacak şekilde tasarlanmıştır.)
"""

import pytest
import uuid
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

pytestmark = pytest.mark.asyncio

@pytest.fixture
async def seed_tenants(db_session: AsyncSession):
    """Test için iki farklı tenant ve seed verisi oluşturur."""
    tenant_a_id = uuid.uuid4()
    tenant_b_id = uuid.uuid4()
    
    # 1. Tenant'ları oluştur
    await db_session.execute(
        text("INSERT INTO tenants (id, name, slug) VALUES (:id, :name, :slug)"),
        [
            {"id": tenant_a_id, "name": "Tenant A", "slug": "tenant-a"},
            {"id": tenant_b_id, "name": "Tenant B", "slug": "tenant-b"},
        ]
    )
    
    # 2. Tenant A için users ve curricula verisi
    user_a_id = uuid.uuid4()
    await db_session.execute(
        text("INSERT INTO users (id, tenant_id, email) VALUES (:id, :t_id, :email)"),
        {"id": user_a_id, "t_id": tenant_a_id, "email": "studentA@tenantA.com"}
    )
    curriculum_a_id = uuid.uuid4()
    await db_session.execute(
        text("INSERT INTO curricula (id, tenant_id, title) VALUES (:id, :t_id, :title)"),
        {"id": curriculum_a_id, "t_id": tenant_a_id, "title": "Tenant A Python Course"}
    )
    
    # 3. Tenant B için users ve curricula verisi
    user_b_id = uuid.uuid4()
    await db_session.execute(
        text("INSERT INTO users (id, tenant_id, email) VALUES (:id, :t_id, :email)"),
        {"id": user_b_id, "t_id": tenant_b_id, "email": "studentB@tenantB.com"}
    )
    curriculum_b_id = uuid.uuid4()
    await db_session.execute(
        text("INSERT INTO curricula (id, tenant_id, title) VALUES (:id, :t_id, :title)"),
        {"id": curriculum_b_id, "t_id": tenant_b_id, "title": "Tenant B AI Course"}
    )
    
    await db_session.commit()
    
    return {
        "tenant_a_id": tenant_a_id, 
        "tenant_b_id": tenant_b_id, 
        "user_a_id": user_a_id, 
        "user_b_id": user_b_id,
        "curriculum_b_id": curriculum_b_id
    }


async def test_tenant_a_cannot_see_tenant_b_data(db_session: AsyncSession, seed_tenants: dict):
    """
    Senaryo 1: Tenant A context'i ile Tenant B verisi görünmez.
    Given Tenant A ve Tenant B seed verisi mevcut
    When Tenant A context'i ile user listesi istenir
    Then Sadece Tenant A verisi döner; Tenant B verisi görünmez.
    """
    tenant_a_id = seed_tenants["tenant_a_id"]
    
    # Session için tenant_id'yi Tenant A olarak ayarla
    await db_session.execute(
        text("SET LOCAL app.current_tenant_id = :tenant_id"),
        {"tenant_id": str(tenant_a_id)}
    )
    
    # Users tablosundan veri çek
    result = await db_session.execute(text("SELECT id, email FROM users"))
    users = result.fetchall()
    
    # Sadece Tenant A kullanıcısı gelmeli
    assert len(users) == 1
    assert users[0].id == seed_tenants["user_a_id"]
    assert "studentB@tenantB.com" not in [u.email for u in users]


async def test_tenant_a_cannot_access_tenant_b_curriculum_by_id(db_session: AsyncSession, seed_tenants: dict):
    """
    Senaryo 2: Tenant A koordinatörü, ID ile Tenant B müfredatına erişmeye çalışır.
    Given Tenant A context'i aktif
    When Tenant B'nin müfredat ID'si ile sorgu yapılır
    Then Kayıt bulunamaz (API'da 404 döner).
    """
    tenant_a_id = seed_tenants["tenant_a_id"]
    curriculum_b_id = seed_tenants["curriculum_b_id"]
    
    # Session için tenant_id'yi Tenant A olarak ayarla
    await db_session.execute(
        text("SET LOCAL app.current_tenant_id = :tenant_id"),
        {"tenant_id": str(tenant_a_id)}
    )
    
    # ID ile direkt Tenant B'nin curriculum'una erişmeye çalış
    result = await db_session.execute(
        text("SELECT id FROM curricula WHERE id = :c_id"),
        {"c_id": curriculum_b_id}
    )
    curriculum = result.fetchone()
    
    # Sonuç boş dönmeli
    assert curriculum is None


async def test_rls_bypass_prevention(db_session: AsyncSession, seed_tenants: dict):
    """
    Senaryo 4: Tenant_id manipülasyonu veya context olmadan erişim engellenir.
    Given Tenant_id eksik veya geçersiz (örn. SQL Injection / Context drop)
    When İstek yapılır
    Then RLS bypass edilemez, sonuç boş döner.
    """
    # Context içinde current_tenant_id ayarlanmadı/resetlendi
    await db_session.execute(text("RESET app.current_tenant_id"))
    
    # Users tablosundan veri çek (FORCE RLS devrede olduğu için boş dönmeli)
    result = await db_session.execute(text("SELECT id FROM users"))
    users = result.fetchall()
    
    assert len(users) == 0

# S19 — Tenant İzolasyonu Doğrulama (AC4)

**Epic:** [E08](../epics/E08-multi-tenant-security.md) | **Sprint:** 2 | **Priority:** P1  
**Persona:** Developer / QA  
**PRD:** AC4

## User Story

As a **QA mühendisi**, I want **tenant izolasyonunun otomatik testlerle doğrulanması**, so that **A Kurumu B Kurumunun verisini asla göremesin garantisi olsun**.

## Independent Test

AC4 test suite: iki tenant seed verisi; cross-tenant API çağrıları; tüm endpoint'lerde veri sızıntısı = 0.

## Acceptance Scenarios

1. **Given** Tenant A ve Tenant B seed verisi mevcut, **When** Tenant A token'ı ile Tenant B öğrenci listesi istenir, **Then** boş liste veya 403 döner; Tenant B verisi görünmez.
2. **Given** Tenant A koordinatörü, **When** Tenant B müfredat ID'si ile erişmeye çalışır, **Then** 404 döner.
3. **Given** AC4 integration test suite, **When** CI'da çalışır, **Then** tüm cross-tenant senaryolar geçer.
4. **Given** SQL injection veya tenant_id manipülasyonu denemesi, **When** istek yapılır, **Then** RLS bypass edilemez.

## Dependencies

- [S18](S18-postgresql-rls-multitenant.md)

## Out of Scope

- Penetration testing (manuel red team — launch öncesi opsiyonel)

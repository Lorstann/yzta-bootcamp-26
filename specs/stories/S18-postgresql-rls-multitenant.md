# S18 — PostgreSQL Multi-Tenant Şema + Row-Level Security

**Epic:** [E08](../epics/E08-multi-tenant-security.md) | **Sprint:** 2 | **Priority:** P1  
**Persona:** Kör Uçuşundaki Zeynep  
**PRD:** Section 8 Tenant Isolation, AC4

## User Story

As a **kurum koordinatörü**, I want **verilerimin diğer kurumlardan tamamen izole olması**, so that **öğrenci ve müfredat verilerimiz güvende olsun**.

## Independent Test

Tüm tablolarda `tenant_id` kolonu ve RLS politikaları aktif; JWT'den gelen tenant context ile sorgular otomatik filtrelenir.

## Acceptance Scenarios

1. **Given** PostgreSQL şeması oluşturuldu, **When** tablolar incelenir, **Then** users, profiles, curricula, tasks, risk_signals tablolarında `tenant_id` mevcuttur.
2. **Given** RLS politikaları aktif, **When** tenant A context'i ile sorgu yapılır, **Then** yalnızca tenant A kayıtları döner.
3. **Given** tenant A kullanıcısı, **When** tenant B kaydına ID ile erişmeye çalışır, **Then** 404 veya boş sonuç döner (veri sızıntısı yok).
4. **Given** S3 object key'leri, **When** incelenir, **Then** `{tenant_id}/` prefix yapısı kullanılır.

## Dependencies

- [S03](S03-api-contract-lock.md) — tenant header/context tanımı

## Out of Scope

- Cross-tenant aggregate analytics
- Multi-region deployment

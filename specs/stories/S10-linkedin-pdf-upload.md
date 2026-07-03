# S10 — LinkedIn PDF Yükleme (S3)

**Epic:** [E03](../epics/E03-data-ingestion-profile.md) | **Sprint:** 2 | **Priority:** P1  
**Persona:** Bunalmış Can  
**PRD:** FR3

## User Story

As a **bootcamp öğrencisi**, I want **LinkedIn profil PDF'imi yükleyebilmek**, so that **yetkinliklerim otomatik olarak sisteme aktarılsın**.

## Independent Test

Öğrenci PDF seçer/yükler; dosya S3'e tenant-scoped key ile kaydedilir; upload progress gösterilir; max dosya boyutu ve format validasyonu çalışır.

## Acceptance Scenarios

1. **Given** öğrenci onboarding veya profil ekranında, **When** geçerli PDF yükler, **Then** dosya S3'e kaydedilir ve upload ID döner.
2. **Given** dosya 10 MB'dan büyük, **When** yükleme denenir, **Then** 400 hata ve anlaşılır mesaj gösterilir.
3. **Given** PDF dışı format yüklenir, **When** validation çalışır, **Then** yükleme reddedilir.
4. **Given** upload tamamlandı, **When** S11 pipeline tetiklenir, **Then** async iş kuyruğuna alınır.

## Dependencies

- [S08](S08-diagnostic-onboarding.md) — onboarding akışına entegre
- [S18](S18-postgresql-rls-multitenant.md) — tenant-scoped S3 prefix

## Out of Scope

- OCR/LLM parsing (S11)
- Fallback chat (S12)

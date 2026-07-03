# S17 — Kuruma "Yüksek Risk" Sinyali (Ham Sohbet Yok)

**Epic:** [E07](../epics/E07-ai-guardrails.md) | **Sprint:** 2 | **Priority:** P1  
**Persona:** Kör Uçuşundaki Zeynep  
**PRD:** Section 7 Guardrails

## User Story

As a **kurum koordinatörü**, I want **yüksek riskli öğrenciler için "Mentör Görüşmesi Bekliyor" sinyali almak**, so that **ham sohbet içeriğini görmeden proaktif müdahale edebileyim**.

## Independent Test

S16 guardrail tetiklendiğinde kurum dashboard'una metadata-only sinyal gider; sinyalde öğrenci ID, risk seviyesi, timestamp var; ham sohbet metni yok.

## Acceptance Scenarios

1. **Given** S16 guardrail tetiklendi, **When** sinyal oluşturulur, **Then** kurum dashboard'unda "Yüksek Risk - Mentör Görüşmesi Bekliyor" görünür.
2. **Given** sinyal kuruma iletildi, **When** koordinatör detaya bakar, **Then** yalnızca metadata (öğrenci adı, risk seviyesi, tarih) görünür; sohbet transcript'i görünmez.
3. **Given** sinyal oluşturuldu, **When** audit log kontrol edilir, **Then** ham mesaj içeriği kurum API yanıtlarında yer almaz.
4. **Given** koordinatör müdahale kaydeder, **When** sinyal kapatılır, **Then** dashboard'da durum güncellenir.

## Dependencies

- [S16](S16-guardrails-keyword-redirect.md)
- [S20](S20-institution-dashboard-skeleton.md) — dashboard görüntüleme
- [S18](S18-postgresql-rls-multitenant.md) — tenant-scoped sinyal

## Out of Scope

- Ham sohbet paylaşımı (asla)
- Otomatik mentör ataması

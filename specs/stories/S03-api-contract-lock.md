# S03 — OpenAPI/JSON API Kontratlarının Kilitlenmesi

**Epic:** [E01](../epics/E01-platform-foundation.md) | **Sprint:** 1 | **Priority:** P1  
**Persona:** Developer (takım)  
**PRD:** Roadmap Sprint 1

## User Story

As a **geliştirici**, I want **kilitlenmiş OpenAPI/JSON API kontratları**, so that **frontend ve backend ekipleri mock-API ile paralel geliştirme yapabilsin**.

## Independent Test

OpenAPI spec dosyası repo'da mevcut; mock server kontrata uygun yanıt döner; frontend mock ile chat endpoint'ini çağırabilir.

## Acceptance Scenarios

1. **Given** OpenAPI spec repo'da yayınlanmış, **When** frontend geliştirici mock server başlatır, **Then** tüm tanımlı endpoint'ler kontrata uygun mock yanıt döner.
2. **Given** API kontratı v1 kilitlenmiş, **When** breaking change gerekiyorsa, **Then** yeni versiyon (`/api/v1` → `/api/v2`) açılır; mevcut kontrat değiştirilmez.
3. **Given** chat streaming endpoint kontratta tanımlı, **When** mock çağrılır, **Then** SSE/streaming formatı spec'e uygun chunk'lar döner.

## Dependencies

- Yok

## Out of Scope

- Backend implementasyonu (S04)
- Authentication endpoint'leri (Sprint 2)

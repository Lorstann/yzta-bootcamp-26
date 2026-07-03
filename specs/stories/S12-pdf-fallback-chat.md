# S12 — PDF Okunamazsa Chat Fallback Akışı

**Epic:** [E03](../epics/E03-data-ingestion-profile.md) | **Sprint:** 2 | **Priority:** P1  
**Persona:** Bunalmış Can  
**PRD:** FR4

## User Story

As a **bootcamp öğrencisi**, I want **PDF okunamadığında AI'ın eksik bilgileri chat ile sorması**, so that **profilim yine de tamamlanabilsin**.

## Independent Test

Parse başarısız PDF yüklendiğinde chat fallback başlar; AI eksik alanları sorar; yanıtlar profil JSON'una yazılır.

## Acceptance Scenarios

1. **Given** PDF parse başarısız, **When** fallback tetiklenir, **Then** AI "Bazı bilgileri okuyamadım, birkaç soru soracağım" mesajı gösterir.
2. **Given** fallback aktif, **When** AI eksik alan sorar (örn. "Son iş deneyiminiz?"), **Then** öğrenci chat ile yanıtlar.
3. **Given** tüm zorunlu alanlar dolduruldu, **When** fallback tamamlanır, **Then** profil S09 formatında kaydedilir.
4. **Given** öğrenci fallback'i yarıda bırakır, **When** tekrar girer, **Then** kaldığı sorudan devam eder.

## Dependencies

- [S10](S10-linkedin-pdf-upload.md), [S11](S11-ocr-llm-competency-json.md)
- [S05](S05-react-chat-ui-mock-api.md) — chat UI

## Out of Scope

- PDF parse iyileştirme (S11 kapsamında)

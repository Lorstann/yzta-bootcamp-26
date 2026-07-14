# S04 — FastAPI İskeleti + Streaming Chat Endpoint

**Epic:** [E04](../epics/E04-ai-checkin-memory.md) | **Sprint:** 1 | **Priority:** P1  
**Persona:** Bunalmış Can  
**PRD:** FR5, Roadmap Sprint 1

## User Story

As a **bootcamp öğrencisi**, I want **AI yanıtlarını gerçek zamanlı streaming olarak görmek**, so that **2 dakikalık check-in sırasında beklemeden etkileşim kurabileyim**.

## Independent Test

`POST /api/v1/chat/stream` endpoint'i FastAPI üzerinde çalışır; Bedrock/LLM'den gelen yanıt SSE veya chunked streaming ile client'a iletilir.

## Acceptance Scenarios

1. **Given** FastAPI sunucusu çalışıyor, **When** client chat mesajı gönderir, **Then** endpoint 200 OK ile streaming yanıt başlatır.
2. **Given** LLM yanıt üretiyor, **When** token'lar gelir, **Then** client her chunk'ı anında render eder (toplam ilk token ≤ 2 sn).
3. **Given** LLM servisi geçici olarak erişilemez, **When** istek yapılır, **Then** standart hata envelope'u döner: `{ success: false, error: { code, message } }`.
4. **Given** boş veya geçersiz mesaj gönderilir, **When** validation çalışır, **Then** 422 validation error döner.

## Dependencies

- [S03](S03-api-contract-lock.md) — API kontratı

## Out of Scope

- RAG hafıza entegrasyonu (S06, S13)
- Guardrails (S16)

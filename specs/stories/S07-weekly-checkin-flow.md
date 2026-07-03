# S07 — Haftalık 2 Dk Check-in Sohbet Akışı (Temel)

**Epic:** [E04](../epics/E04-ai-checkin-memory.md) | **Sprint:** 1 | **Priority:** P1  
**Persona:** Bunalmış Can  
**PRD:** FR5, Roadmap Sprint 1

## User Story

As a **bootcamp öğrencisi**, I want **haftada bir 2 dakikalık AI check-in yapabilmek**, so that **kapasiteme uygun haftalık hedefler alabileyim**.

## Independent Test

Check-in akışı başlatılır; AI 3–5 kısa soru sorar; akış ≤ 2 dk tamamlanır; haftalık görev özeti sunulur.

## Acceptance Scenarios

1. **Given** yeni hafta başladı, **When** öğrenci check-in başlatır, **Then** AI hoş geldin mesajı ve ilk soruyu sorar.
2. **Given** öğrenci check-in sorularını yanıtlar, **When** akış tamamlanır, **Then** süre ≤ 2 dakika olmalı (ortalama).
3. **Given** check-in tamamlandı, **When** özet gösterilir, **Then** öğrenci haftalık görev listesini görür (max 3 görev — S15'te enforce).
4. **Given** öğrenci check-in'i yarıda bırakır, **When** tekrar girer, **Then** kaldığı yerden devam edebilir.

## Dependencies

- [S04](S04-fastapi-streaming-chat.md), [S05](S05-react-chat-ui-mock-api.md)

## Out of Scope

- RAG hafıza (geçmiş haftalar — S13)
- Kapasite downscale (S15)

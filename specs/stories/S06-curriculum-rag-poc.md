# S06 — Manuel Müfredat Yükleme + Vektörel RAG POC

**Epic:** [E04](../epics/E04-ai-checkin-memory.md) | **Sprint:** 1 | **Priority:** P1  
**Persona:** Developer / Kurum admin  
**PRD:** FR6, Section 7 RAG, Roadmap Sprint 1

## User Story

As a **sistem yöneticisi**, I want **kurum müfredatını (PDF/Docx) yükleyip vektörel indekslemek**, so that **AI sadece müfredat bağlamında görev önerebilsin**.

## Independent Test

Manuel yüklenen bir müfredat dokümanı chunk'lanır, embed edilir, pgvector'a kaydedilir; test sorgusu ilgili chunk'ları retrieve eder.

## Acceptance Scenarios

1. **Given** admin bir müfredat PDF'i yükler, **When** ingestion pipeline çalışır, **Then** doküman chunk'lara bölünür ve vektör store'a yazılır.
2. **Given** müfredat indekslenmiş, **When** "React hooks" ile ilgili sorgu yapılır, **Then** müfredattaki ilgili bölümler top-k sonuç olarak döner.
3. **Given** müfredat dışı bir konu sorgulanır (örn. "Solidity"), **When** RAG retrieve eder, **Then** müfredat chunk'ı dönmez veya relevance skoru düşüktür.

## Dependencies

- [S04](S04-fastapi-streaming-chat.md) — backend iskelet

## Out of Scope

- Otomatik müfredat sync (MVP'de manuel)
- Müfredat dışı öneri engeli kural motoru (S14)

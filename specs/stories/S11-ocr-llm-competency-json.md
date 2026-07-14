# S11 — OCR/LLM ile Yetkinlik JSON Çıkarma

**Epic:** [E03](../epics/E03-data-ingestion-profile.md) | **Sprint:** 2 | **Priority:** P1  
**Persona:** Bunalmış Can  
**PRD:** FR3

## User Story

As a **bootcamp öğrencisi**, I want **yüklediğim LinkedIn PDF'inden yetkinliklerimin otomatik çıkarılması**, so that **manuel veri girişi yapmadan profilim zenginleşsin**.

## Independent Test

S3'teki PDF Textract/LlamaParse ile parse edilir; LLM yapılandırılmış yetkinlik JSON'u üretir; JSON öğrenci profiline bağlanır.

## Acceptance Scenarios

1. **Given** geçerli LinkedIn PDF S3'te, **When** ingestion pipeline çalışır, **Then** yetkinlik JSON'u `{ skills: [], experience: [], education: [] }` formatında üretilir.
2. **Given** PDF başarıyla parse edildi, **When** JSON profille birleştirilir, **Then** öğrenci profilinde yetkinlikler görünür.
3. **Given** PDF kısmen okunabilir, **When** LLM eksik alan tespit eder, **Then** S12 fallback akışı tetiklenir.
4. **Given** pipeline hata verir, **When** retry limiti aşılır, **Then** S12 fallback otomatik başlar.

## Dependencies

- [S10](S10-linkedin-pdf-upload.md)

## Out of Scope

- Fallback chat UI (S12)
- GitHub repo analizi (FR10)

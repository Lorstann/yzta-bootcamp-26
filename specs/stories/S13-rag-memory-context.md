# S13 — RAG Hafıza — Geçmiş Beyanlar + Müfredat Bağlamı

**Epic:** [E04](../epics/E04-ai-checkin-memory.md) | **Sprint:** 2 | **Priority:** P1  
**Persona:** Bunalmış Can  
**PRD:** FR5, FR6, Section 7 RAG

## User Story

As a **bootcamp öğrencisi**, I want **AI'ın geçmiş hafta beyanlarımı ve müfredatı hatırlaması**, so that **her check-in kişisel ve bağlama uygun olsun**.

## Independent Test

Öğrenci 2+ hafta check-in yaptıktan sonra AI, önceki hafta beyanlarını (enerji, stres) ve müfredat chunk'larını retrieve ederek yanıt verir.

## Acceptance Scenarios

1. **Given** öğrenci geçen hafta "çok yorgunum" dedi, **When** bu hafta check-in başlar, **Then** AI geçen haftaki beyanı referans alır.
2. **Given** müfredat indekslenmiş, **When** AI görev önerir, **Then** yalnızca retrieve edilen müfredat chunk'larına dayalı öneri sunar.
3. **Given** öğrenci PDF yetkinlikleri yüklü, **When** gap analysis yapılır, **Then** RAG hem müfredat hem yetkinlik verisini kullanır.
4. **Given** vektör store'da ilgili kayıt yok, **When** sorgu yapılır, **Then** AI genel yanıt verir, hallucination minimize edilir.

## Dependencies

- [S06](S06-curriculum-rag-poc.md), [S07](S07-weekly-checkin-flow.md)
- [S11](S11-ocr-llm-competency-json.md) — yetkinlik verisi (opsiyonel zenginleştirme)

## Out of Scope

- Müfredat dışı öneri engeli kural motoru (S14)

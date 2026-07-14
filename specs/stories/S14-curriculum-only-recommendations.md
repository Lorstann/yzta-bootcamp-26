# S14 — Müfredat Dışı Öneri Engeli (FR6/AC2)

**Epic:** [E04](../epics/E04-ai-checkin-memory.md) | **Sprint:** 2 | **Priority:** P1  
**Persona:** Bunalmış Can  
**PRD:** FR6, AC2

## User Story

As a **bootcamp öğrencisi**, I want **AI'ın yalnızca kurum müfredatındaki konuları önermesi**, so that **program dışı dikkat dağıtıcı hedefler almayayım**.

## Independent Test

Müfredat dışı bir framework (örn. kurum müfredatında olmayan "Solidity") için AI "bu hafta bunu öğrenmelisin" önerisi yapmaz; AC2 test suite geçer.

## Acceptance Scenarios

1. **Given** müfredat "React, Node.js" içerir, **When** AI haftalık görev önerir, **Then** yalnızca bu konularda öneri sunar.
2. **Given** öğrenci "Solidity öğrenmek istiyorum" der, **When** Solidity müfredatta yok, **Then** AI müfredat dışı öğrenme önermez; mevcut müfredat kapsamına yönlendirir.
3. **Given** RAG retrieve sonucu boş, **When** AI yanıt üretir, **Then** görev önerisi yapılmaz; "Müfredat bilgisi bulunamadı" mesajı gösterilir.
4. **Given** AC2 test suite çalışır, **When** 100 müfredat dışı senaryo test edilir, **Then** false positive oranı = 0.

## Dependencies

- [S06](S06-curriculum-rag-poc.md), [S13](S13-rag-memory-context.md)

## Out of Scope

- Müfredat otomatik güncelleme

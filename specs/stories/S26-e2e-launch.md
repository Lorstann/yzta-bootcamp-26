# S26 — E2E Testler + 2 Pilot Bootcamp Canlıya Çıkış

**Epic:** [E01](../epics/E01-platform-foundation.md), [E04](../epics/E04-ai-checkin-memory.md) | **Sprint:** 3 | **Priority:** P1  
**Persona:** Bunalmış Can, Kör Uçuşundaki Zeynep  
**PRD:** AC1, Roadmap Sprint 3

## User Story

As a **Equa takımı**, I want **uçtan uca testler geçmiş ve 2 pilot bootcamp canlıya alınmış olması**, so that **MVP gerçek kullanıcılarla doğrulanabilsin**.

## Independent Test

Playwright E2E suite geçer; 2 pilot bootcamp öğrenci listeleri yüklenmiş; PWA linki öğrencilere dağıtılmış; production ortamında temel akışlar çalışır.

## Acceptance Scenarios

1. **Given** E2E test suite, **When** CI'da çalışır, **Then** onboarding → check-in → dashboard akışları geçer.
2. **Given** 2 pilot bootcamp tenant'ları oluşturuldu, **When** öğrenci listeleri import edilir, **Then** her tenant kendi öğrencilerini görür (AC4).
3. **Given** production deploy tamamlandı, **When** öğrenci mobil tarayıcıdan PWA linkine tıklar, **Then** uygulama mağazası indirmeden açılır (AC1).
4. **Given** edge case testleri (guardrails, tenant isolation, curriculum-only), **When** manuel/automated test çalışır, **Then** kritik senaryolar geçer.
5. **Given** launch tamamlandı, **When** ilk hafta metrikleri toplanır, **Then** `ai_checkin_completion_rate` ölçülmeye başlanır.

## Dependencies

- Tüm P1 story'ler (S01–S25)

## Out of Scope

- Ölçeklenmiş production altyapısı (MVP pilot scope)
- 2'den fazla pilot kurum

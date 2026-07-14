# S01 — PWA Duyarlı Kabuk ve Mobil-First Layout

**Epic:** [E01](../epics/E01-platform-foundation.md) | **Sprint:** 1 | **Priority:** P1  
**Persona:** Bunalmış Can  
**PRD:** FR1, AC1

## User Story

As a **bootcamp öğrencisi**, I want **mobil tarayıcıdan duyarlı bir arayüzle Equa'ya erişmek**, so that **herhangi bir uygulama indirmeden hızlıca check-in yapabileyim**.

## Independent Test

Mobil tarayıcıda (375px genişlik) uygulama açıldığında tüm temel navigasyon ve chat alanı görünür ve kullanılabilir olmalı; desktop'ta (≥1024px) layout genişletilmiş görünüm sunmalı.

## Acceptance Scenarios

1. **Given** öğrenci mobil tarayıcıdan Equa URL'sine gider, **When** sayfa yüklenir, **Then** chat alanı ve navigasyon 375px genişlikte taşma olmadan görüntülenir.
2. **Given** öğrenci tablet veya desktop tarayıcı kullanır, **When** viewport genişler, **Then** layout responsive breakpoint'lere göre uyum sağlar.
3. **Given** öğrenci portrait/landscape mod arasında geçiş yapar, **When** ekran yönü değişir, **Then** layout bozulmadan yeniden düzenlenir.

## Dependencies

- Yok (Sprint 1 başlangıç story'si)

## Out of Scope

- Service worker / offline davranış (S02)
- Kurum dashboard layout'u (S20)

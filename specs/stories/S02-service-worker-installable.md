# S02 — Service Worker + Installable Web App

**Epic:** [E01](../epics/E01-platform-foundation.md) | **Sprint:** 1 | **Priority:** P1  
**Persona:** Bunalmış Can  
**PRD:** FR1, AC1

## User Story

As a **bootcamp öğrencisi**, I want **Equa'yı ana ekranıma ekleyebilmek**, so that **uygulama mağazası indirmeden native app benzeri deneyim yaşayabileyim**.

## Independent Test

Chrome/Edge mobil tarayıcıda "Ana ekrana ekle" seçeneği görünür ve eklendikten sonra standalone modda açılır; temel statik asset'ler cache'lenir.

## Acceptance Scenarios

1. **Given** öğrenci desteklenen mobil tarayıcıda Equa'yı açar, **When** PWA kriterleri karşılanır, **Then** "Ana ekrana ekle" / install prompt görünür.
2. **Given** öğrenci PWA'yı ana ekrana ekler, **When** ikondan açar, **Then** uygulama standalone modda (adres çubuğu olmadan) başlar.
3. **Given** ağ bağlantısı geçici kesilir, **When** öğrenci cache'lenmiş sayfayı açar, **Then** temel kabuk ve offline fallback mesajı gösterilir.

## Dependencies

- [S01](S01-pwa-responsive-shell.md) — responsive layout

## Out of Scope

- Tam offline chat (Sprint 1'de sadece kabuk cache)
- Push notification

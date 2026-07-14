# E01 — Platform Foundation & PWA

**Epic ID:** E01  
**Durum:** Draft  
**Hedef Sprint:** Sprint 1  
**PRD Referansları:** FR1, Roadmap Sprint 1, AC1

## Özet

Equa'nın mobile-first PWA olarak çalışmasını sağlayan temel platform katmanı. Öğrenciler uygulama mağazası indirmeden mobil tarayıcıdan erişebilmeli; frontend ve backend ekipleri mock-API ile paralel geliştirme yapabilmeli.

## Hedef Persona

- **Bunalmış Can** — mobil tarayıcıdan hızlı erişim
- **Kör Uçuşundaki Zeynep** — desktop dashboard için responsive layout

## PRD Functional Requirements

| ID | Gereksinim | Öncelik |
|----|------------|---------|
| FR1 | PWA destekli duyarlı Web App | Must |

## MVP Kapsamı

- Duyarlı (responsive) mobil-first layout
- Service worker ve installable Web App davranışı
- OpenAPI/JSON API kontratlarının kilitlenmesi (contract-first geliştirme)
- E2E testler ve pilot launch altyapısı (Sprint 3, S26)

## Başarı Metrikleri

- Öğrenciler mobil tarayıcıdan uygulama mağazası indirmeden giriş yapabilmeli (AC1)
- Frontend ve backend ekipleri API kontratına göre bağımsız geliştirme yapabilmeli
- PWA Lighthouse skoru ≥ 80 (Performance, PWA kategorileri)

## Story'ler

| ID | Başlık | Sprint | Priority |
|----|--------|--------|----------|
| [S01](../stories/S01-pwa-responsive-shell.md) | PWA duyarlı kabuk ve mobil-first layout | 1 | P1 |
| [S02](../stories/S02-service-worker-installable.md) | Service worker + installable Web App | 1 | P1 |
| [S03](../stories/S03-api-contract-lock.md) | OpenAPI/JSON API kontratlarının kilitlenmesi | 1 | P1 |
| [S26](../stories/S26-e2e-launch.md) | E2E testler + 2 pilot bootcamp canlıya çıkış | 3 | P1 |

## Bağımlılıklar

- Yok (temel epic; diğer epic'lerin ön koşulu)

## Non-Goals

- Native iOS/Android uygulama
- WhatsApp/Telegram bot arayüzü

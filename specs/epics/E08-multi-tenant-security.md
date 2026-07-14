# E08 — Multi-Tenant Güvenlik & Veri İzolasyonu

**Epic ID:** E08  
**Durum:** Draft  
**Hedef Sprint:** Sprint 2  
**PRD Referansları:** Section 8 Tenant Isolation, AC4, Roadmap Sprint 2

## Özet

B2B müşterilerinin (bootcamp/akademi) verilerinin Row-Level Security (RLS) ile donanımsal ve yazılımsal izolasyonu. A Kurumu, B Kurumuna ait hiçbir öğrenci verisini veya müfredatını görememeli.

## Hedef Persona

- **Kör Uçuşundaki Zeynep** — sadece kendi kurumunun verilerini görmek
- **Bunalmış Can** — verilerinin kurumu dışında paylaşılmaması

## PRD Technical Requirements

- Amazon RDS PostgreSQL + tenant_id
- Row-Level Security (RLS) politikaları
- S3 bucket prefix veya tenant-scoped object keys

## PRD Acceptance Criteria

- **AC4:** B2B müşterisi (A Kurumu), B Kurumuna ait hiçbir öğrenci verisini veya müfredatını sistemde kesinlikle görememelidir.

## MVP Kapsamı

- PostgreSQL multi-tenant şema (tenant_id tüm tablolarda)
- RLS politikaları (SELECT, INSERT, UPDATE, DELETE)
- Tenant izolasyonu integration testleri
- JWT/auth ile tenant context propagation

## Başarı Metrikleri

- Cross-tenant veri sızıntısı = 0 (AC4 test suite)
- Tüm API endpoint'leri tenant context doğrulaması yapmalı
- RLS bypass denemeleri reddedilmeli

## Story'ler

| ID | Başlık | Sprint | Priority |
|----|--------|--------|----------|
| [S18](../stories/S18-postgresql-rls-multitenant.md) | PostgreSQL multi-tenant şema + RLS | 2 | P1 |
| [S19](../stories/S19-tenant-isolation-validation.md) | Tenant izolasyonu doğrulama (AC4) | 2 | P1 |

## Bağımlılıklar

- **E01** — API kontratları (tenant header/context tanımı)

## Non-Goals

- Cross-tenant analytics (aggregate, anonymized — MVP dışı)
- Multi-region data residency

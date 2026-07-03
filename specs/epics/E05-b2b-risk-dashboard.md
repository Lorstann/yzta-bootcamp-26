# E05 — Kurum Risk Dashboard'u

**Epic ID:** E05  
**Durum:** Draft  
**Hedef Sprint:** Sprint 2–3  
**PRD Referansları:** FR8, Roadmap Sprint 2–3

## Özet

Kurum koordinatörlerine öğrenci risk sinyallerini (Yeşil, Sarı, Kırmızı) gösteren B2B dashboard arayüzü ve backend risk skorlaması.

## Hedef Persona

- **Kör Uçuşundaki Zeynep** — 100+ öğrencinin risk metriklerini tek ekranda görmek

## PRD Functional Requirements

| ID | Gereksinim | Öncelik |
|----|------------|---------|
| FR8 | Yeşil/Sarı/Kırmızı risk sinyalleri gösteren kurum arayüzü | Must |

## MVP Kapsamı

**Sprint 2 (İskelet):**
- Kurum dashboard iskeleti + öğrenci listesi
- Risk sinyali renk kodlu görünüm (mock veya basit kural tabanlı)

**Sprint 3 (Entegrasyon):**
- Backend risk skorlaması entegrasyonu
- Gerçek zamanlı risk güncellemeleri

## Başarı Metrikleri

- Risk tespitinden mentör müdahalesine süre: 14 günden 2 güne (PRD Goal)
- Dashboard üzerinden tetiklenen başarılı mentör müdahalesi sayısı
- Kurum koordinatörü tek ekranda tüm öğrenci risklerini görebilmeli

## Story'ler

| ID | Başlık | Sprint | Priority |
|----|--------|--------|----------|
| [S20](../stories/S20-institution-dashboard-skeleton.md) | Kurum dashboard iskeleti + öğrenci listesi | 2 | P2 |
| [S21](../stories/S21-risk-signal-display.md) | Yeşil/Sarı/Kırmızı risk sinyali görünümü | 2 | P2 |
| [S22](../stories/S22-risk-scoring-backend.md) | Risk skorlaması backend entegrasyonu | 3 | P1 |

## Bağımlılıklar

- **E08** — Multi-Tenant (kurum sadece kendi öğrencilerini görmeli, AC4)
- **E04** — Öğrenci davranış metrikleri (görev tamamlama, check-in)
- **E07** — Yüksek risk sinyalleri (guardrails tetiklemeleri)

## Non-Goals

- Ham sohbet verisinin kuruma gösterilmesi
- Manuel görev yönetimi arayüzü

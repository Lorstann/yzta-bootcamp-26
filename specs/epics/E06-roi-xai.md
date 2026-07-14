# E06 — ROI Tracker & Explainable AI

**Epic ID:** E06  
**Durum:** Draft  
**Hedef Sprint:** Sprint 3  
**PRD Referansları:** FR9, Section 7 XAI, Roadmap Sprint 3

## Özet

Kurum dashboard'unda "Önlenen Dropout Sayısı / Korunan Gelir" metriklerinin gösterimi ve kırmızı risk bayraklarının yapay zeka gerekçelerinin (XAI) loglanması.

## Hedef Persona

- **Kör Uçuşundaki Zeynep** — Equa'nın kurtardığı öğrenci sayısını ve ROI'yi görmek

## PRD Functional Requirements

| ID | Gereksinim | Öncelik |
|----|------------|---------|
| FR9 | Önlenen Dropout / Korunan Gelir metriği | Must |

## PRD AI Requirements

- **Explainable AI (XAI):** Kırmızı risk bayrağının yanında davranışsal metrik gerekçeleri loglanmalı (örn: 3 haftadır görev yapılmıyor, düşük enerji beyanı)

## MVP Kapsamı

- Önlenen dropout sayısı hesaplama ve gösterim
- Korunan gelir (ROI) metriği
- XAI gerekçe logları dashboard'da görüntüleme

## Başarı Metrikleri

- B2B pilot müşterilerinde dropout oranında %20 azalma
- ROI metrikleri kurum dashboard'unda anlık görüntülenebilmeli
- Her kırmızı bayrak en az bir XAI gerekçe kaydına sahip olmalı

## Story'ler

| ID | Başlık | Sprint | Priority |
|----|--------|--------|----------|
| [S23](../stories/S23-prevented-dropout-metric.md) | Önlenen dropout sayısı metriği | 3 | P1 |
| [S24](../stories/S24-protected-revenue-roi.md) | Korunan gelir (ROI) hesaplama ve gösterim | 3 | P1 |
| [S25](../stories/S25-xai-risk-rationale-logs.md) | XAI — kırmızı bayrak gerekçe logları | 3 | P1 |

## Bağımlılıklar

- **E05** — Risk dashboard (ROI metrikleri dashboard'a entegre)
- **E04** — Öğrenci davranış verileri (dropout tahmin modeli girdisi)
- **E08** — Tenant izolasyonu (ROI kurum bazlı)

## Non-Goals

- Finansal muhasebe entegrasyonu
- Detaylı ML model eğitimi (MVP'de kural tabanlı + basit metrikler)

# S24 — Korunan Gelir (ROI) Hesaplama ve Gösterim

**Epic:** [E06](../epics/E06-roi-xai.md) | **Sprint:** 3 | **Priority:** P1  
**Persona:** Kör Uçuşundaki Zeynep  
**PRD:** FR9, Roadmap Sprint 3

## User Story

As a **kurum koordinatörü**, I want **Equa'nın koruduğu eğitim gelirini (ROI) görmek**, so that **platform yatırımının geri dönüşünü kanıtlayabileyim**.

## Independent Test

Dashboard'da "Korunan Gelir" metriği görünür; hesaplama: önlenen dropout × öğrenci başına eğitim ücreti (kurum config).

## Acceptance Scenarios

1. **Given** koordinatör ROI dashboard'una bakar, **When** sayfa yüklenir, **Then** "Korunan Gelir" metriği para birimi ile gösterilir.
2. **Given** kurum öğrenci başına ücreti 50.000 TL config'de tanımlı, **When** 2 dropout önlendi, **Then** korunan gelir = 100.000 TL gösterilir.
3. **Given** önlenen dropout sayısı 0, **When** metrik hesaplanır, **Then** korunan gelir = 0 gösterilir.
4. **Given** tenant bazlı config, **When** farklı kurumlar, **Then** her kurum kendi ücret config'ini kullanır.

## Dependencies

- [S23](S23-prevented-dropout-metric.md)
- [S20](S20-institution-dashboard-skeleton.md)

## Out of Scope

- Muhasebe/fatura entegrasyonu
- Çok para birimi desteği (MVP'de tek para birimi)

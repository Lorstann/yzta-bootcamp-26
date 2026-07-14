# S23 — Önlenen Dropout Sayısı Metriği

**Epic:** [E06](../epics/E06-roi-xai.md) | **Sprint:** 3 | **Priority:** P1  
**Persona:** Kör Uçuşundaki Zeynep  
**PRD:** FR9, Roadmap Sprint 3

## User Story

As a **kurum koordinatörü**, I want **Equa'nın önlediği dropout sayısını görmek**, so that **platformun değerini somut olarak ölçebileyim**.

## Independent Test

Dashboard'da "Önlenen Dropout Sayısı" metriği görünür; hesaplama kuralı dokümante (örn: Kırmızı → müdahale → programda kalan öğrenci sayısı).

## Acceptance Scenarios

1. **Given** koordinatör dashboard ROI bölümüne bakar, **When** sayfa yüklenir, **Then** "Önlenen Dropout Sayısı" metriği görünür.
2. **Given** 3 öğrenci Kırmızı risk aldı ve mentör müdahalesi sonrası programda kaldı, **When** metrik hesaplanır, **Then** sayaç en az 3 gösterir (kural tanımına göre).
3. **Given** pilot öncesi/sonrası karşılaştırma, **When** rapor oluşturulur, **Then** dropout oranı farkı gösterilir.
4. **Given** tenant A koordinatörü, **When** metriğe bakar, **Then** yalnızca tenant A verisi kullanılır.

## Dependencies

- [S22](S22-risk-scoring-backend.md)
- [S20](S20-institution-dashboard-skeleton.md)

## Out of Scope

- Harici BI entegrasyonu

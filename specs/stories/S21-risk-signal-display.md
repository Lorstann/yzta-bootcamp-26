# S21 — Yeşil/Sarı/Kırmızı Risk Sinyali Görünümü

**Epic:** [E05](../epics/E05-b2b-risk-dashboard.md) | **Sprint:** 2 | **Priority:** P2  
**Persona:** Kör Uçuşundaki Zeynep  
**PRD:** FR8

## User Story

As a **kurum koordinatörü**, I want **öğrencilerin risk seviyelerini renk kodlu görmek**, so that **öncelikli müdahale gerektiren öğrencileri hızla tespit edebileyim**.

## Independent Test

Dashboard tablosunda her öğrenci Yeşil/Sarı/Kırmızı badge ile gösterilir; renkler basit kural tabanlı veya mock skor ile belirlenir.

## Acceptance Scenarios

1. **Given** öğrenci düşük risk (son 2 hafta check-in tamamladı, görevler devam ediyor), **When** listelenir, **Then** Yeşil badge gösterilir.
2. **Given** öğrenci orta risk (1 hafta check-in atlandı), **When** listelenir, **Then** Sarı badge gösterilir.
3. **Given** öğrenci yüksek risk (3 hafta görev yok veya S17 sinyali), **When** listelenir, **Then** Kırmızı badge gösterilir.
4. **Given** koordinatör renge göre filtreler, **When** "Kırmızı" seçer, **Then** yalnızca yüksek riskli öğrenciler listelenir.

## Dependencies

- [S20](S20-institution-dashboard-skeleton.md)

## Out of Scope

- Backend risk skorlama algoritması (S22)
- XAI gerekçe logları (S25)

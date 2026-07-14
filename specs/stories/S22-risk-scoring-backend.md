# S22 — Risk Skorlaması Backend Entegrasyonu

**Epic:** [E05](../epics/E05-b2b-risk-dashboard.md) | **Sprint:** 3 | **Priority:** P1  
**Persona:** Kör Uçuşundaki Zeynep  
**PRD:** FR8, Roadmap Sprint 3

## User Story

As a **kurum koordinatörü**, I want **gerçek zamanlı risk skorlarının dashboard'a yansıması**, so that **mock veri yerine güncel öğrenci durumunu görebileyim**.

## Independent Test

Backend risk scoring servisi check-in, görev tamamlama ve guardrail sinyallerinden skor üretir; dashboard API'den gerçek skorları çeker.

## Acceptance Scenarios

1. **Given** öğrenci 3 haftadır görev tamamlamadı, **When** risk skoru hesaplanır, **Then** skor Kırmızı eşiğine düşer.
2. **Given** öğrenci check-in tamamladı ve görevler devam ediyor, **When** skor güncellenir, **Then** Yeşil veya Sarı döner.
3. **Given** S17 yüksek risk sinyali tetiklendi, **When** skor hesaplanır, **Then** otomatik Kırmızı atanır.
4. **Given** koordinatör dashboard'u yeniler, **When** API çağrılır, **Then** skorlar ≤ 5 sn gecikmeyle güncellenir.

## Dependencies

- [S21](S21-risk-signal-display.md)
- [S15](S15-load-balancing-tasks.md) — görev metrikleri
- [S17](S17-high-risk-institution-signal.md) — guardrail sinyalleri

## Out of Scope

- ML tabanlı dropout tahmin modeli (MVP'de kural tabanlı)

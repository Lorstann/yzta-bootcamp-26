# S25 — XAI — Kırmızı Bayrak Gerekçe Logları

**Epic:** [E06](../epics/E06-roi-xai.md) | **Sprint:** 3 | **Priority:** P1  
**Persona:** Kör Uçuşundaki Zeynep  
**PRD:** Section 7 XAI, FR8

## User Story

As a **kurum koordinatörü**, I want **kırmızı risk bayrağının hangi davranışsal metriklere dayandığını görmek**, so that **müdahale kararımı veriye dayalı alabileyim**.

## Independent Test

Kırmızı badge yanında "Gerekçe" linki/modalı; gerekçe logları davranışsal metrikleri listeler (örn: "3 haftadır görev yapılmıyor", "düşük enerji beyanı"); ham sohbet içermez.

## Acceptance Scenarios

1. **Given** öğrenci Kırmızı risk badge'ine sahip, **When** koordinatör gerekçeye tıklar, **Then** davranışsal metrik listesi görünür.
2. **Given** gerekçe logu, **When** incelenir, **Then** en az bir metrik içerir (check-in atlama, görev tamamlama, guardrail sinyali vb.).
3. **Given** gerekçe logu, **When** incelenir, **Then** ham sohbet transcript'i veya mesaj içeriği içermez.
4. **Given** risk skoru güncellendi, **When** yeni gerekçe oluşur, **Then** timestamp ile loglanır ve dashboard'da görünür.

## Dependencies

- [S22](S22-risk-scoring-backend.md)
- [S21](S21-risk-signal-display.md)

## Out of Scope

- ML model explainability (SHAP/LIME — MVP'de kural tabanlı gerekçe)

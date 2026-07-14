# S05 — Mock-API ile React Chat UI (SSE/Streaming)

**Epic:** [E04](../epics/E04-ai-checkin-memory.md) | **Sprint:** 1 | **Priority:** P1  
**Persona:** Bunalmış Can  
**PRD:** FR5, Roadmap Sprint 1

## User Story

As a **bootcamp öğrencisi**, I want **sohbet arayüzünde AI yanıtlarını canlı olarak görmek**, so that **doğal bir konuşma deneyimi yaşayabileyim**.

## Independent Test

React Chat UI mock-API'ye bağlanır; mesaj gönderildiğinde streaming yanıt chat balonunda token token görünür; loading ve error state'leri mevcuttur.

## Acceptance Scenarios

1. **Given** öğrenci chat ekranında, **When** mesaj yazar ve gönderir, **Then** kullanıcı mesajı sağda, AI yanıtı solda balon olarak görünür.
2. **Given** AI yanıt streaming geliyor, **When** token'lar ulaşır, **Then** balon içeriği gerçek zamanlı güncellenir.
3. **Given** ağ hatası oluşur, **When** istek başarısız olur, **Then** kullanıcıya anlaşılır hata mesajı ve yeniden deneme seçeneği gösterilir.
4. **Given** yanıt bekleniyor, **When** istek devam eder, **Then** loading indicator görünür.

## Dependencies

- [S01](S01-pwa-responsive-shell.md) — layout
- [S03](S03-api-contract-lock.md) — mock API kontratı

## Out of Scope

- Gerçek backend bağlantısı (Sprint 1'de mock; S04 ile entegrasyon Sprint 1 sonunda)
- Haftalık check-in akış mantığı (S07)

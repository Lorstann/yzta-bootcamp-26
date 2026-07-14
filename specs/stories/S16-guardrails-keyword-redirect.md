# S16 — Anahtar Kelime Guardrails + Şefkatli Yönlendirme

**Epic:** [E07](../epics/E07-ai-guardrails.md) | **Sprint:** 2 | **Priority:** P1  
**Persona:** Bunalmış Can  
**PRD:** Section 7 Guardrails

## User Story

As a **bootcamp öğrencisi**, I want **depresyon, intihar veya bırakma isteği içeren mesajlarımda güvenli yönlendirme almak**, so that **klinik olmayan ama destekleyici bir deneyim yaşayabileyim**.

## Independent Test

Guardrail keyword listesi (depresyon, intihar, bırakmak istiyorum vb.) tetiklendiğinde AI klinik tavsiye durdurur; şefkatli yönlendirme template'i çalışır; yanıt ≤ 2 sn.

## Acceptance Scenarios

1. **Given** öğrenci "intihar" veya eşanlamlı kelime içeren mesaj yazar, **When** guardrail tetiklenir, **Then** AI klinik tavsiye vermez; şefkatli yönlendirme template'i gösterilir.
2. **Given** öğrenci "okulu bırakmak istiyorum" der, **When** guardrail çalışır, **Then** eğitimi bırakma konusunda destekleyici ama klinik olmayan yanıt verilir.
3. **Given** guardrail tetiklendi, **When** template çalışır, **Then** mentör/kriz hattı bilgisi ve kurum destek kanalları önerilir.
4. **Given** normal mesaj (guardrail dışı), **When** gönderilir, **Then** standart AI akışı devam eder.

## Dependencies

- [S04](S04-fastapi-streaming-chat.md), [S05](S05-react-chat-ui-mock-api.md)

## Out of Scope

- Kuruma sinyal gönderme (S17)
- Acil servis otomatik araması

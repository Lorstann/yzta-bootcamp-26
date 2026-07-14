# S15 — Kapasiteye Göre Max 3 Görev + Downscale

**Epic:** [E04](../epics/E04-ai-checkin-memory.md) | **Sprint:** 2 | **Priority:** P1  
**Persona:** Bunalmış Can  
**PRD:** FR7, AC3

## User Story

As a **bootcamp öğrencisi**, I want **kapasiteme göre haftalık max 3 görev almak ve yorgun olduğumda hedeflerin otomatik küçültülmesi**, so that **tükenmeden sürdürülebilir ilerleyebileyim**.

## Independent Test

Load balancing algoritması kapasite skoruna göre 1–3 görev atar; öğrenci yorgunluk beyan ettiğinde açık hedefler downscale veya askıya alınır.

## Acceptance Scenarios

1. **Given** kapasite skoru yüksek (≥ 7), **When** haftalık görev ataması yapılır, **Then** max 3 görev atanır.
2. **Given** kapasite skoru düşük (≤ 3), **When** görev ataması yapılır, **Then** max 1 görev atanır.
3. **Given** öğrenci check-in'de "çok yorgunum, kapasitem doldu" der, **When** sistem işler, **Then** açık hedefler otomatik downscale edilir veya askıya alınır (AC3).
4. **Given** downscale uygulandı, **When** öğrenci görev listesine bakar, **Then** güncellenmiş (azaltılmış) hedefleri görür.
5. **Given** task_completion_rate ölçülür, **When** kapasite dengeli görevler atanır, **Then** hedef ≥ %60 tamamlanma oranı.

## Dependencies

- [S09](S09-student-profile-capacity.md), [S07](S07-weekly-checkin-flow.md)

## Out of Scope

- Sınırsız görev veya Jira-style task management

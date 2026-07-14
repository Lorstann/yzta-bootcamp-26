# S09 — Öğrenci Profil Oluşturma ve Kapasite Skoru

**Epic:** [E02](../epics/E02-student-onboarding.md) | **Sprint:** 2 | **Priority:** P1  
**Persona:** Bunalmış Can  
**PRD:** FR2, AC3

## User Story

As a **bootcamp öğrencisi**, I want **profilim ve kapasite skorumun oluşturulması**, so that **AI bana aşırı yük bindirmeden görev atayabilsin**.

## Independent Test

Diagnostic sonrası profil kaydedilir; kapasite skoru (1–10) hesaplanır; skor load balancing algoritmasına (S15) girdi olur.

## Acceptance Scenarios

1. **Given** diagnostic tamamlandı, **When** profil oluşturulur, **Then** ad, hedefler, stres seviyesi ve kapasite skoru kaydedilir.
2. **Given** kapasite skoru düşük (≤ 3), **When** haftalık görev ataması yapılır, **Then** max görev sayısı azaltılır (S15 ile entegre).
3. **Given** öğrenci yorgun olduğunu beyan eder, **When** kapasite güncellenir, **Then** skor otomatik düşer ve açık hedefler downscale edilir (AC3).
4. **Given** profil kaydedildi, **When** check-in başlatılır, **Then** AI profil verisini kullanır.

## Dependencies

- [S08](S08-diagnostic-onboarding.md)
- [S18](S18-postgresql-rls-multitenant.md) — tenant-scoped profil

## Out of Scope

- LinkedIn PDF yetkinlik çıkarma (S11)

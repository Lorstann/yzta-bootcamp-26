# S20 — Kurum Dashboard İskeleti + Öğrenci Listesi

**Epic:** [E05](../epics/E05-b2b-risk-dashboard.md) | **Sprint:** 2 | **Priority:** P2  
**Persona:** Kör Uçuşundaki Zeynep  
**PRD:** FR8, Roadmap Sprint 2

## User Story

As a **kurum koordinatörü**, I want **tüm öğrencilerimi listeleyen bir dashboard görmek**, so that **risk durumlarını tek ekrandan takip edebileyim**.

## Independent Test

Kurum koordinatörü giriş yapar; dashboard öğrenci tablosu (ad, son check-in, risk durumu placeholder) gösterir; yalnızca kendi tenant'ının öğrencileri listelenir.

## Acceptance Scenarios

1. **Given** koordinatör kurum hesabıyla giriş yapar, **When** dashboard açılır, **Then** öğrenci listesi tablo formatında görünür.
2. **Given** tenant A koordinatörü, **When** listeyi görüntüler, **Then** yalnızca tenant A öğrencileri listelenir (AC4).
3. **Given** 100+ öğrenci, **When** tablo yüklenir, **Then** sayfalama ve arama çalışır.
4. **Given** dashboard desktop'ta açılır, **When** viewport ≥ 1024px, **Then** zengin veri tablosu layout'u kullanılır.

## Dependencies

- [S18](S18-postgresql-rls-multitenant.md)

## Out of Scope

- Risk renk kodları (S21)
- ROI metrikleri (S23, S24)

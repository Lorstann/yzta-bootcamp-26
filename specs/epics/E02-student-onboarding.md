# E02 — Chat Tabanlı Onboarding & Teşhis

**Epic ID:** E02  
**Durum:** Draft  
**Hedef Sprint:** Sprint 2  
**PRD Referansları:** FR2, Roadmap Sprint 2

## Özet

Yeni öğrencilerin sisteme katılırken 5 dakikalık chat tabanlı diagnostic akışı ile tanınması ve kişisel profil + kapasite skorunun oluşturulması.

## Hedef Persona

- **Bunalmış Can** — hızlı, düşük sürtünmeli ilk deneyim

## PRD Functional Requirements

| ID | Gereksinim | Öncelik |
|----|------------|---------|
| FR2 | 5 dakikalık chat tabanlı teşhis ve profil oluşturma | Must |

## MVP Kapsamı

- Soru-cevap tabanlı diagnostic chat akışı (≤ 5 dk)
- Öğrenci profili oluşturma (kapasite, hedefler, stres seviyesi)
- Kapasite skoru hesaplama (E04 load balancing için girdi)

## Başarı Metrikleri

- Onboarding tamamlama oranı ≥ %80
- Ortalama onboarding süresi ≤ 5 dakika
- Oluşturulan profiller AI check-in akışına beslenebilmeli

## Story'ler

| ID | Başlık | Sprint | Priority |
|----|--------|--------|----------|
| [S08](../stories/S08-diagnostic-onboarding.md) | 5 dk chat tabanlı diagnostic onboarding | 2 | P1 |
| [S09](../stories/S09-student-profile-capacity.md) | Öğrenci profil oluşturma ve kapasite skoru | 2 | P1 |

## Bağımlılıklar

- **E01** — Platform Foundation (chat UI, API kontratları)
- **E08** — Multi-Tenant (profil tenant_id ile kaydedilmeli)

## Non-Goals

- Klinik psikolojik değerlendirme
- Uzun anket formları (sadece chat)

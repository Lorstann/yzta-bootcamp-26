# S08 — 5 Dk Chat Tabanlı Diagnostic Onboarding

**Epic:** [E02](../epics/E02-student-onboarding.md) | **Sprint:** 2 | **Priority:** P1  
**Persona:** Bunalmış Can  
**PRD:** FR2

## User Story

As a **yeni bootcamp öğrencisi**, I want **5 dakikalık chat tabanlı bir teşhis akışı tamamlamak**, so that **sistem beni tanıyıp kişiselleştirilmiş öneriler sunabilsin**.

## Independent Test

Yeni kullanıcı kayıt sonrası diagnostic chat başlar; 5–8 soru sorulur; akış ≤ 5 dk tamamlanır; profil oluşturma adımına yönlendirilir.

## Acceptance Scenarios

1. **Given** yeni öğrenci ilk giriş yapar, **When** onboarding başlar, **Then** chat tabanlı diagnostic akış otomatik açılır.
2. **Given** öğrenci diagnostic sorularını yanıtlar, **When** akış tamamlanır, **Then** toplam süre ≤ 5 dakika.
3. **Given** öğrenci bir soruyu atlamak ister, **When** "Atla" seçer, **Then** akış devam eder ve eksik alan S09'da tamamlanabilir.
4. **Given** diagnostic tamamlandı, **When** son adıma gelinir, **Then** profil oluşturma ekranına (S09) yönlendirilir.

## Dependencies

- [S01](S01-pwa-responsive-shell.md), [S05](S05-react-chat-ui-mock-api.md)

## Out of Scope

- PDF yükleme (S10–S12)
- Klinik değerlendirme

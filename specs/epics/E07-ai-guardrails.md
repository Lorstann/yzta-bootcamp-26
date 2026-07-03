# E07 — AI Guardrails & Kriz Yönlendirme

**Epic ID:** E07  
**Durum:** Draft  
**Hedef Sprint:** Sprint 2  
**PRD Referansları:** Section 7 Guardrails, Roadmap Sprint 2

## Özet

Kullanıcı sohbetinde depresyon, intihar veya eğitimi bırakma isteğiyle ilgili anahtar kelimeler tespit edildiğinde klinik tavsiyeyi durdurma, şefkatli yönlendirme şablonu çalıştırma ve kuruma "Yüksek Risk" sinyali gönderme — ham sohbet paylaşılmadan.

## Hedef Persona

- **Bunalmış Can** — güvenli, sınırlandırılmış AI etkileşimi
- **Kör Uçuşundaki Zeynep** — proaktif yüksek risk uyarısı (içerik olmadan)

## PRD AI & Security Requirements

- Anahtar kelime guardrails (depresyon, intihar, bırakma isteği)
- Klinik tavsiye vermeyi anında durdurma
- Şefkatli yönlendirme template'i
- Kuruma "Yüksek Risk - Mentör Görüşmesi Bekliyor" sinyali
- Ham sohbet verisi **asla** kurumla paylaşılmaz

## MVP Kapsamı

- Keyword detection engine (guardrails)
- Compassionate redirect template
- Kurum risk sinyali (metadata only, no chat content)
- Audit log (iç kullanım, kuruma gönderilmez)

## Başarı Metrikleri

- Guardrail tetikleme false negative oranı minimize edilmeli (red team testleri)
- Kuruma gönderilen sinyallerde ham sohbet içeriği = %0
- Tetikleme sonrası kullanıcıya şefkatli yönlendirme ≤ 2 saniye

## Story'ler

| ID | Başlık | Sprint | Priority |
|----|--------|--------|----------|
| [S16](../stories/S16-guardrails-keyword-redirect.md) | Anahtar kelime guardrails + şefkatli yönlendirme | 2 | P1 |
| [S17](../stories/S17-high-risk-institution-signal.md) | Kuruma "Yüksek Risk" sinyali (ham sohbet yok) | 2 | P1 |

## Bağımlılıklar

- **E04** — AI chat pipeline (guardrails chat akışına enjekte)
- **E05** — Kurum dashboard (yüksek risk sinyali görüntüleme)
- **E08** — Tenant izolasyonu

## Non-Goals

- Klinik psikolojik destek veya tıbbi teşhis
- Otomatik acil servis araması
- Ham sohbet transcript'inin kuruma iletilmesi

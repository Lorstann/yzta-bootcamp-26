# E03 — PDF Veri Çıkarma & Fallback Akışı

**Epic ID:** E03  
**Durum:** Draft  
**Hedef Sprint:** Sprint 2  
**PRD Referansları:** FR3, FR4, Roadmap Sprint 2

## Özet

LinkedIn profil PDF'i yükleyerek OCR/LLM ile yetkinlik JSON'u çıkarma; PDF okunamadığında AI'ın eksik verileri chat üzerinden sorması.

## Hedef Persona

- **Bunalmış Can** — profil bilgilerini hızlıca sisteme aktarmak

## PRD Functional Requirements

| ID | Gereksinim | Öncelik |
|----|------------|---------|
| FR3 | LinkedIn PDF → OCR/LLM → yetkinlik JSON | Must |
| FR4 | PDF okunamazsa chat fallback | Must |

## MVP Kapsamı

- PDF yükleme (S3 depolama)
- Textract/LlamaParse ile metin çıkarma + LLM ile yapılandırılmış JSON
- Fallback: eksik alanları chat ile tamamlama
- Çıkarılan yetkinlikler öğrenci profiline bağlama

## Başarı Metrikleri

- PDF başarılı parse oranı ≥ %70
- Fallback akışı tamamlama oranı ≥ %90 (parse başarısız olsa bile)
- Yetkinlik JSON'u AI check-in ve gap analysis için kullanılabilir

## Story'ler

| ID | Başlık | Sprint | Priority |
|----|--------|--------|----------|
| [S10](../stories/S10-linkedin-pdf-upload.md) | LinkedIn PDF yükleme (S3) | 2 | P1 |
| [S11](../stories/S11-ocr-llm-competency-json.md) | OCR/LLM ile yetkinlik JSON çıkarma | 2 | P1 |
| [S12](../stories/S12-pdf-fallback-chat.md) | PDF okunamazsa chat fallback akışı | 2 | P1 |

## Bağımlılıklar

- **E02** — Onboarding akışı (PDF yükleme onboarding'e entegre)
- **E01** — API kontratları, S3 altyapısı
- **E08** — Tenant izolasyonu (PDF'ler tenant bazlı)

## Non-Goals

- GitHub repo analizi (FR10 — Won't)
- Otomatik LinkedIn API entegrasyonu

# Equa Story Backlog

**Kaynak PRD:** [specs/prds/prd.md](../prds/prd.md)  
**Epic İndeksi:** [specs/epics/README.md](../epics/README.md)

> **Sprint 2 Notu:** Sprint 2'de 14 story tanımlıdır. Bootcamp kapasitesine göre sprint planning'de 8–10 story seçilmesi önerilir. Kalan story'ler backlog'da kalır.

## Backlog Tablosu

| ID | Başlık | Epic | Sprint | Priority | SP |
|----|--------|------|--------|----------|-----|
| [S01](S01-pwa-responsive-shell.md) | PWA duyarlı kabuk ve mobil-first layout | E01 | 1 | P1 | 5 |
| [S02](S02-service-worker-installable.md) | Service worker + installable Web App | E01 | 1 | P1 | 5 |
| [S03](S03-api-contract-lock.md) | OpenAPI/JSON API kontratlarının kilitlenmesi | E01 | 1 | P1 | 3 |
| [S04](S04-fastapi-streaming-chat.md) | FastAPI iskeleti + streaming chat endpoint | E04 | 1 | P1 | 8 |
| [S05](S05-react-chat-ui-mock-api.md) | Mock-API ile React Chat UI (SSE/streaming) | E04 | 1 | P1 | 8 |
| [S06](S06-curriculum-rag-poc.md) | Manuel müfredat yükleme + vektörel RAG POC | E04 | 1 | P1 | 8 |
| [S07](S07-weekly-checkin-flow.md) | Haftalık 2 dk check-in sohbet akışı (temel) | E04 | 1 | P1 | 5 |
| [S08](S08-diagnostic-onboarding.md) | 5 dk chat tabanlı diagnostic onboarding | E02 | 2 | P1 | 8 |
| [S09](S09-student-profile-capacity.md) | Öğrenci profil oluşturma ve kapasite skoru | E02 | 2 | P1 | 5 |
| [S10](S10-linkedin-pdf-upload.md) | LinkedIn PDF yükleme (S3) | E03 | 2 | P1 | 5 |
| [S11](S11-ocr-llm-competency-json.md) | OCR/LLM ile yetkinlik JSON çıkarma | E03 | 2 | P1 | 8 |
| [S12](S12-pdf-fallback-chat.md) | PDF okunamazsa chat fallback akışı | E03 | 2 | P1 | 5 |
| [S13](S13-rag-memory-context.md) | RAG hafıza — geçmiş beyanlar + müfredat | E04 | 2 | P1 | 8 |
| [S14](S14-curriculum-only-recommendations.md) | Müfredat dışı öneri engeli (FR6/AC2) | E04 | 2 | P1 | 5 |
| [S15](S15-load-balancing-tasks.md) | Kapasiteye göre max 3 görev + downscale | E04 | 2 | P1 | 8 |
| [S16](S16-guardrails-keyword-redirect.md) | Anahtar kelime guardrails + şefkatli yönlendirme | E07 | 2 | P1 | 8 |
| [S17](S17-high-risk-institution-signal.md) | Kuruma "Yüksek Risk" sinyali | E07 | 2 | P1 | 5 |
| [S18](S18-postgresql-rls-multitenant.md) | PostgreSQL multi-tenant şema + RLS | E08 | 2 | P1 | 8 |
| [S19](S19-tenant-isolation-validation.md) | Tenant izolasyonu doğrulama (AC4) | E08 | 2 | P1 | 5 |
| [S20](S20-institution-dashboard-skeleton.md) | Kurum dashboard iskeleti + öğrenci listesi | E05 | 2 | P2 | 5 |
| [S21](S21-risk-signal-display.md) | Yeşil/Sarı/Kırmızı risk sinyali görünümü | E05 | 2 | P2 | 5 |
| [S22](S22-risk-scoring-backend.md) | Risk skorlaması backend entegrasyonu | E05 | 3 | P1 | 8 |
| [S23](S23-prevented-dropout-metric.md) | Önlenen dropout sayısı metriği | E06 | 3 | P1 | 5 |
| [S24](S24-protected-revenue-roi.md) | Korunan gelir (ROI) hesaplama ve gösterim | E06 | 3 | P1 | 5 |
| [S25](S25-xai-risk-rationale-logs.md) | XAI — kırmızı bayrak gerekçe logları | E06 | 3 | P1 | 8 |
| [S26](S26-e2e-launch.md) | E2E testler + 2 pilot bootcamp canlıya çıkış | E01, E04 | 3 | P1 | 8 |

**Toplam Story Point (tüm backlog):** ~152 SP

## Sprint Özetleri

| Sprint | Story Sayısı | Toplam SP | Odak |
|--------|--------------|-----------|------|
| Sprint 1 | 7 | 42 | Platform + AI Core POC |
| Sprint 2 | 14 | 80 | Onboarding, güvenlik, multi-tenant, dashboard iskelet |
| Sprint 3 | 5 | 34 | ROI, risk scoring, launch |

## FR Coverage

| FR | Story |
|----|-------|
| FR1 | S01, S02 |
| FR2 | S08, S09 |
| FR3 | S10, S11 |
| FR4 | S12 |
| FR5 | S04, S05, S07, S13 |
| FR6 | S06, S14 |
| FR7 | S15 |
| FR8 | S20, S21, S22 |
| FR9 | S23, S24 |
| FR10 | — (Won't, MVP dışı) |

## AC Coverage

| AC | Story |
|----|-------|
| AC1 (mobil Web App, mağaza indirmesiz) | S01, S02, S26 |
| AC2 (müfredat dışı öneri yok) | S06, S14 |
| AC3 (kapasite downscale/askıya alma) | S09, S15 |
| AC4 (tenant izolasyonu) | S18, S19 |

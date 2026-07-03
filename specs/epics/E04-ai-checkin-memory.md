# E04 — AI Check-in, RAG Hafıza & Görev Dengeleme

**Epic ID:** E04  
**Durum:** Draft  
**Hedef Sprint:** Sprint 1–2  
**PRD Referansları:** FR5, FR6, FR7, Section 7 RAG, AC2, AC3, Roadmap Sprint 1–2

## Özet

Equa'nın çekirdek AI deneyimi: haftalık 2 dakikalık check-in asistanı, RAG tabanlı hafıza, müfredat bağlamında görev önerisi ve kapasiteye göre görev dengeleme.

## Hedef Persona

- **Bunalmış Can** — haftalık bite-sized kariyer reçetesi

## PRD Functional Requirements

| ID | Gereksinim | Öncelik |
|----|------------|---------|
| FR5 | RAG + Memory ile haftalık 2 dk AI Check-in | Must |
| FR6 | Sadece kurum müfredatı bağlamında görev önerisi | Must |
| FR7 | Kapasiteye göre haftalık max 3 görev | Must |

## MVP Kapsamı

**Sprint 1 (Core):**
- FastAPI iskeleti + streaming chat endpoint
- Mock-API ile React Chat UI
- Manuel müfredat + vektörel RAG POC
- Temel haftalık check-in akışı

**Sprint 2 (Memory + Load Balance):**
- Geçmiş hafta beyanları + müfredat RAG hafızası
- Müfredat dışı öneri engeli (AC2)
- Kapasite downscale/askıya alma (AC3)

## Başarı Metrikleri

- `ai_checkin_completion_rate` ≥ %70 (haftalık)
- `task_completion_rate` ≥ %60
- Müfredat dışı öneri oranı = %0 (AC2)
- Ortalama check-in süresi ≤ 2 dakika

## Story'ler

| ID | Başlık | Sprint | Priority |
|----|--------|--------|----------|
| [S04](../stories/S04-fastapi-streaming-chat.md) | FastAPI iskeleti + streaming chat endpoint | 1 | P1 |
| [S05](../stories/S05-react-chat-ui-mock-api.md) | Mock-API ile React Chat UI (SSE/streaming) | 1 | P1 |
| [S06](../stories/S06-curriculum-rag-poc.md) | Manuel müfredat yükleme + vektörel RAG POC | 1 | P1 |
| [S07](../stories/S07-weekly-checkin-flow.md) | Haftalık 2 dk check-in sohbet akışı (temel) | 1 | P1 |
| [S13](../stories/S13-rag-memory-context.md) | RAG hafıza — geçmiş beyanlar + müfredat | 2 | P1 |
| [S14](../stories/S14-curriculum-only-recommendations.md) | Müfredat dışı öneri engeli (FR6/AC2) | 2 | P1 |
| [S15](../stories/S15-load-balancing-tasks.md) | Kapasiteye göre max 3 görev + downscale | 2 | P1 |
| [S26](../stories/S26-e2e-launch.md) | E2E testler + pilot launch | 3 | P1 |

## Bağımlılıklar

- **E01** — Platform, API kontratları, PWA chat UI
- **E02/E03** — Profil ve yetkinlik verisi (Sprint 2 RAG zenginleştirmesi)
- **E08** — Tenant izolasyonu (müfredat tenant bazlı)

## Non-Goals

- Klinik tavsiye veya teşhis (E07 guardrails ile sınırlandırılır)
- Sınırsız görev atama (Jira/Asana alternatifi olmak)

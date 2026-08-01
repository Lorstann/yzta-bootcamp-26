# Equa — Proje İlerleme Takibi

**Takım:** 320  
**Durum:** Sprint 1–3 MVP hardening landed (auth guards, onboarding, PDF UX, institution XAI, TanStack Query, E2E journeys)  
**Kaynak dokümanlar:** [PRD](specs/prds/prd.md) · [Stories](specs/stories/README.md) · [Tech Stack](specs/techstack.md)

---

## Ekip Görev Dağılımı

| Alan | Ekip | Sorumluluk |
|------|------|------------|
| **Database** | Hafize Talya Keysan, Hasibe Nur Tunç, Dilan Özyazıcı | PostgreSQL şema, migration, pgvector, RLS, seed verisi |
| **Backend** | Dilan Özyazıcı, Hasibe Nur Tunç, Elif Kahrıman, Mustafa Kurtar | FastAPI iskelet, API kontratları, servis katmanı, streaming endpoint |
| **Frontend** | Tüm ekip (Dilan, Mustafa, Elif, Hafize, Hasibe) | React PWA, Chat UI, mock/real API entegrasyonu |
| **AI Agent** | Hafize Talya Keysan, Mustafa Kurtar, Elif Kahrıman | LLM entegrasyonu, RAG pipeline, prompt/check-in akışı, guardrails |

### Kişi Bazlı Özet

| Kişi | Rol | Alanlar |
|------|-----|---------| 
| Dilan Özyazıcı | Product Owner | Database, Backend, Frontend |
| Mustafa Kurtar | Scrum Master | Backend, AI Agent, Frontend |
| Elif Kahrıman | Developer | Backend, AI Agent, Frontend |
| Hafize Talya Keysan | Developer | Database, AI Agent, Frontend |
| Hasibe Nur Tunç | Developer | Database, Backend, Frontend |

---

## Önerilen Başlangıç Sırası

```text
1. Backend  → Proje iskeleti + OpenAPI kontratı (diğer ekiplerin bağımlılığı)
2. Database → Local PostgreSQL + temel şema (backend repository katmanı için)
3. Frontend → Mock-API ile Chat UI (backend hazır olmadan paralel başlayabilir)
4. AI Agent → LLM + RAG POC (backend streaming endpoint'e bağlanır)
```

---

## Database — İlk Görevler

**Ekip:** Hafize Talya Keysan · Hasibe Nur Tunç · Dilan Özyazıcı  
**Hedef:** Local geliştirme ortamı ve MVP için minimum veri modeli.  
**İlgili story'ler:** [S18](specs/stories/S18-postgresql-rls-multitenant.md), [S19](specs/stories/S19-tenant-isolation-validation.md), [S06](specs/stories/S06-curriculum-rag-poc.md)

| # | Görev | Durum | Story |
|---|-------|-------|-------|
| D1 | `docker-compose` ile PostgreSQL 15+ local ortamını ayağa kaldır | ✅ | — |
| D2 | `pgvector` extension'ını etkinleştir | ✅ | S06 |
| D3 | Alembic migration altyapısını kur | ✅ | S18 |
| D4 | `tenants` ve `users` tablolarını oluştur (`tenant_id`, `created_at`, `updated_at`) | ✅ | S18 |
| D5 | `student_profiles` tablosunu oluştur (kapasite skoru alanı dahil) | ✅ | S09 |
| D6 | `curricula` ve `curriculum_chunks` tablolarını oluştur (vektör kolonu ile) | ✅ | S06 |
| D7 | `checkin_sessions` ve `weekly_tasks` tablolarını oluştur | ✅ | S07 |
| D8 | Tüm tenant-scoped tablolara Row-Level Security (RLS) politikalarını ekle | ✅ | S18, AC4 |
| D9 | Local geliştirme için seed verisi yaz (2 tenant, örnek öğrenci) | ✅ | S19 |
| D10 | Cross-tenant izolasyon test senaryolarını hazırla | ✅ | S19 |

---

## AI Agent — İlk Görevler

**Ekip:** Hafize Talya Keysan · Mustafa Kurtar · Elif Kahrıman  
**Hedef:** Streaming chat ve müfredat tabanlı RAG POC.  
**İlgili story'ler:** [S04](specs/stories/S04-fastapi-streaming-chat.md), [S06](specs/stories/S06-curriculum-rag-poc.md), [S07](specs/stories/S07-weekly-checkin-flow.md)

| # | Görev | Durum | Story |
|---|-------|-------|-------|
| A1 | LLM sağlayıcısını seç ve ortam değişkenlerini tanımla (Bedrock veya OpenAI/Anthropic) | ✅ | S04 |
| A2 | LangChain veya LlamaIndex bağımlılıklarını backend projesine ekle | ✅ | S06 |
| A3 | Basit streaming yanıt fonksiyonu yaz (LLM → token chunk) | ✅ | S04 |
| A4 | Manuel müfredat metni/PDF için chunk + embedding pipeline'ını oluştur | ✅ | S06 |
| A5 | pgvector üzerinde similarity search (top-k retrieve) POC'unu test et | ✅ | S06 |
| A6 | Check-in akışı için sistem prompt'u ve soru şablonunu tasarla (≤ 2 dk) | ✅ | S07 |
| A7 | RAG context inject: retrieve edilen müfredat chunk'larını prompt'a ekle | ✅ | S06, S13 |
| A8 | Guardrails keyword listesi taslağını hazırla (depresyon, intihar, bırakma) | ✅ | S16 |

---

## Frontend — İlk Görevler

**Ekip:** Tüm ekip (Dilan Özyazıcı · Mustafa Kurtar · Elif Kahrıman · Hafize Talya Keysan · Hasibe Nur Tunç)  
**Hedef:** Mobile-first PWA kabuk ve mock-API ile Chat UI.  
**İlgili story'ler:** [S01](specs/stories/S01-pwa-responsive-shell.md), [S03](specs/stories/S03-api-contract-lock.md), [S05](specs/stories/S05-react-chat-ui-mock-api.md)

| # | Görev | Durum | Story |
|---|-------|-------|-------|
| F1 | Vite + React 18 + TypeScript proje iskeletini oluştur | ✅ | S01 |
| F2 | Mobile-first responsive layout ve temel routing kur | ✅ | S01 |
| F3 | PWA manifest ve service worker (temel kabuk cache) ekle | ✅ | S02 |
| F4 | OpenAPI spec'e uygun API client / mock server entegrasyonu yap | ✅ | S03, S05 |
| F5 | Chat ekranı: mesaj listesi, input, gönder butonu | ✅ | S05 |
| F6 | SSE/streaming yanıtları chat balonunda canlı render et | ✅ | S05 |
| F7 | Loading, error ve empty state bileşenlerini ekle | ✅ | S05 |
| F8 | Mock-API ile uçtan uca chat akışını demo edilebilir hale getir | ✅ | S05 |

---

## Backend — İlk Görevler

**Ekip:** Dilan Özyazıcı · Hasibe Nur Tunç · Elif Kahrıman · Mustafa Kurtar  
**Hedef:** FastAPI iskelet, API kontratı ve streaming chat endpoint.  
**İlgili story'ler:** [S03](specs/stories/S03-api-contract-lock.md), [S04](specs/stories/S04-fastapi-streaming-chat.md)

| # | Görev | Durum | Story |
|---|-------|-------|-------|
| B1 | FastAPI + Uvicorn proje iskeletini oluştur (`backend/` klasör yapısı) | ✅  | S04 |
| B2 | Katmanlı mimariyi kur: `routes → controllers → services → repositories` | ✅  | S04 |
| B3 | Standart API response envelope'unu uygula (`success`, `data`, `error`) | ✅ | S03 |
| B4 | OpenAPI spec dosyasını yaz ve repo'da kilitle (`/api/v1/...`) | ✅ | S03 |
| B5 | `POST /api/v1/chat/stream` streaming endpoint'ini aç | ✅ | S04 |
| B6 | Pydantic request/response şemalarını tanımla | ✅ | S03, S04 |
| B7 | Structured logging (structlog) ve global error handler ekle | ✅ | S04 |
| B8 | Database connection + repository katmanını backend'e bağla | ✅ | S18 |
| B9 | AI Agent streaming fonksiyonunu endpoint'e entegre et | ✅ | S04, A3 |
| B10 | `.env.example` dosyasını oluştur (DB, LLM, JWT placeholder) | ✅ | — |

---

## Sprint 2 İlk Kilometre Taşları

| Kilometre taşı | Kriter | Durum |
|----------------|--------|-------|
| **M1 — Kontrat kilitlendi** | OpenAPI spec + mock server frontend'de çalışıyor | ✅ |
| **M2 — Chat POC** | Mock veya gerçek backend ile streaming chat demo | ✅ |
| **M3 — DB + RLS** | 2 tenant seed verisi, cross-tenant test geçiyor | ✅ |
| **M4 — RAG POC** | Manuel müfredat yüklendi, retrieve + LLM yanıtı alındı | ✅ |

---

## Durum Açıklamaları

| Simge | Anlam |
|-------|-------|
| ⬜ | Başlanmadı |
| 🔄 | Devam ediyor |
| ✅ | Tamamlandı |
| ⏸️ | Beklemede |

---

## Notlar

- Sprint 1'de kod yazılmadı; tüm görevler Sprint 2 geliştirme fazından itibaren geçerlidir.
- Frontend, Backend OpenAPI kontratı (B4) kilitlenene kadar mock-API ile paralel ilerleyebilir.
- AI Agent görevleri (A3–A7), Backend streaming endpoint (B5) hazır olduktan sonra entegre edilir.
- Database RLS (D8) tamamlanmadan multi-tenant özellikler production'a alınmamalıdır (AC4).

**Son güncelleme:** 1 Ağustos 2026

- **Kişiselleştirilmiş burnout koçu:** Onboarding/profil'e şehir, ilçe, program_track, interests (hobi/şarj); Alembic 012; `wellbeing.py` burnout bandı + prompt context; ton yasağı ("Duyduğum şu" vb.) + `opener_hint` rotasyonu; `[PROFIL]` sessiz öğrenme (kullanıcı alanını ezmez); görevler `başlık | detay` + description persist; müfredatsız teknik görev filtresi düzeltildi; jenerik görev yumuşak eleme; SSE daily_tasks obje listesi. pytest 149, Vitest 21 yeşil.
- **Kapsam kilidi (scope guard):** Hibrit off-topic engeli — hızlı deny/allow desenleri + kararsızlarda LLM IN/OUT sınıflandırıcı (timeout/hata fail-open); leisure→aktivite reframing, hard→kısa red; `off_topic` SSE alanı risk sinyalinden ayrı; check-in turu artmaz; prompt KAPSAM bloğu (aktivite evet / içerik hayır). `SCOPE_CLASSIFIER_ENABLED` ile kapatılabilir. pytest 165, Vitest 21 yeşil.

- **Koç modu + kısa check-in + müfredat yükleme:** Check-in bitince aynı sohbette koç modu (`stream_coach_response`, input açık kalır); kelime skalası (Tükendim→Turbo / Hiç yok→Ateşliyim) + `[SECENEKLER]` quick-reply chip'leri; MAX_TURNS 4 / SOFT_CLOSE 3; kurum müfredat upload (PDF/DOCX/TXT/MD + metin yapıştırma, S3 veya `var/uploads` local); Alembic 011; OpenAPI curriculum routes. pytest 129, Vitest 21 yeşil.

- **Check-in sohbet redesign:** LLM'e session history replay (loop kök nedeni); stage makinesi (`opening→explore→focus→closing`, MAX_TURNS=6); inline `[DURUM]` sinyal çıkarımı + `[GOREVLER]`/`[DURUM]` stream sanitizer; Alembic 010 (`energy_level`, `motivation_level`, `workload_level`, `main_blocker`, `stage`, `turn_count`); risk skoruna enerji/motivasyon ortalaması; dost/koç prompt (`build_checkin_prompt`); FE tamamlanma kartı + sinyal göstergesi. pytest 111, Vitest 19 yeşil.

- **Günlük check-in + kurum deneyimi:** Haftalık → günlük geçiş (Alembic 009: `checkin_date`, `daily_tasks`); streak_days; gün pencereli risk; AI Canlı sohbet başlığında; MoodSelector; rol bazlı nav (öğrenci vs instructor/admin); kurum overview/usage/me/settings + metrics-only AI asistan (`POST /institution/assistant/stream`); route contract + role matrix testleri; zombie uvicorn 404 kök nedeni giderildi. pytest 86, Vitest 19 yeşil.

- **Stitch Dark Redesign:** Frontend Deep Space koyu glassmorphism temasına geçildi (Plus Jakarta Sans, lucide-react, `@theme` token’ları). Yeni route’lar: `/` Landing, `/dashboard`, `/tasks`, `/takvim`. Shell: glass sidebar + TopBar + mobil bottom nav. Backend: Alembic 008 (`capacity_snapshots` + task due_date); `GET /tasks`, `GET /checkins/history`, `GET /profiles/me/stats`, `PATCH /checkins/current/mood`. OpenAPI + MSW + Vitest + pytest dashboard stats yeşil.

- **MVP Hardening (P0–P2):** Chat zorunlu auth (tenant JWT’den); session sahipliği; öğrenci happy path (check-in session → chat → görev persist); frontend `RequireAuth` / `RequireRole`; register rolü student-only; guardrail UI; production JWT guard; OpenAPI 12 endpoint + bearerAuth; onboarding sihirbazı; PDF upload doğrulama + chip UX + fallback sohbet; `weekly_tasks.status` + tenant `revenue_per_student` (Alembic 007); kurum filtre/XAI/N+1; TanStack Query + RHF/Zod; UI primitives/motion/offline/install; RAG AC2 filter; logger redaction; pytest + Vitest + Playwright journey genişletmesi.
- **Not:** LinkedIn PDF S3 yok — in-memory parse (MVP bilinci).
- **F5–F8 / M2 tamamlandı:** Chat UI mesaj listesi, SSE streaming, empty/loading/error, MSW Vitest smoke.
- **A4/A5/A7 / M4 tamamlandı:** chunk+embed ingest, pgvector retrieve, chat prompt inject; `python -m backend.scripts.ingest_curriculum`.
- **M3 tamamlandı:** `pytest backend/tests` RLS izolasyon suite yeşil (`equa_app` role).
- **Plan 2–5:** JWT auth, check-in/task persist, onboarding/LinkedIn upload, capacity load-balance, HIGH_RISK sinyali, kurum dashboard + ROI/XAI.
- **Plan 6:** Playwright smoke (`frontend/e2e`); seed 2 tenant + coordinator.
- **Not:** Host Postgres çakışması için Docker port `5433:5432` (bkz. `docker-compose.yml` / `.env.example`).

- **F3 tamamlandı:** `vite-plugin-pwa` ile manifest + service worker; `public/pwa-192.png` / `pwa-512.png`, `offline.html`, shell precache; API istekleri NetworkOnly.
- **F4 tamamlandı:** Kilitli kontrat `specs/openapi/v1.yaml`; typed client (`src/shared/api`); MSW mock (`src/mocks`) health + SSE chat; `npm run generate:api`.
- **B4 / M1:** OpenAPI v1 repo'da kilitli; frontend mock Vitest smoke yeşil.
- **A1 tamamlandı:** OpenAI varsayılan sağlayıcı olarak seçildi; `LLM_PROVIDER` ortam değişkeni `.env.example` ve `backend/config.py`'ye eklendi. `backend/services/llm/provider.py` modülü ile sağlayıcı/model ayarları merkezi okunuyor.
- **A1 güncelleme:** Varsayılan LLM sağlayıcı **Gemini** (`LLM_PROVIDER=gemini`, `LLM_MODEL=gemini-2.0-flash`); `langchain-google-genai` eklendi. Streaming, competency extract ve embeddings Gemini'yi destekliyor.
- **A2 tamamlandı:** LangChain bağımlılıkları `requirements.txt`'e eklendi (`langchain`, `langchain-openai`, `langchain-anthropic`).
- **A3 tamamlandı:** `backend/services/llm/streaming.py` — `stream_llm_response()` async generator; OpenAI/Anthropic streaming + API key yoksa mock mod. Backend B5/B9 endpoint'e bağlayacak.

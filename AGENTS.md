# AGENTS.md — Equa

Instructions for coding agents working in this repository.

## Product

**Equa** (Team 320) is an AI-powered career/capacity coach for bootcamp and academy students (B2B2C). Students get weekly AI check-ins and max-3 task plans; institutions get dropout-risk and ROI dashboards.

- PRD: `specs/prds/prd.md`
- Tech stack: `specs/techstack.md`
- Stories: `specs/stories/README.md`
- Progress: `progress.md` (update on meaningful pushes)

## Stack (source of truth)

| Layer | Choice |
|-------|--------|
| Backend | **Python 3.11+ / FastAPI / Uvicorn / Pydantic / SQLAlchemy** |
| Frontend | **React 18 / TypeScript / Vite / Tailwind** (PWA, mobile-first) |
| DB | **PostgreSQL 16 + pgvector**, Alembic migrations, RLS multi-tenant |
| AI | LangChain + OpenAI (streaming check-in; RAG planned) |
| Tests | pytest (backend), Vitest + RTL (frontend), Playwright (e2e) |

> **Important:** Some `.cursor/rules` and skills still mention Express/Zod. For Equa, prefer **FastAPI + Pydantic**. Keep the same layering and response envelope; map Zod → Pydantic, Express → FastAPI.

## Repository layout

```
backend/          FastAPI app (api → services → repositories)
frontend/         React PWA
specs/            PRD, epics, stories, tech stack
.cursor/rules/    Scoped Cursor rules
.cursor/skills/   Task workflows (read before scaffolding)
.cursor/agents/   Specialized agent personas
```

## Architecture

Layering (do not skip):

`route → controller → service → repository`

- Routes: wire deps + controller only
- Controllers: validate input, call service, return envelope — no DB
- Services: business logic — no FastAPI imports
- Repositories: DB only — return domain entities, never raw rows
- Schemas: `backend/domain/` (Pydantic); shared contracts for frontend when applicable
- Errors: typed errors with `statusCode` / `code`

API versioning: `/api/v1/...` (nouns). Docs: `/api/docs`.

### Response envelope (always)

```json
{ "success": true, "data": {}, "meta": {} }
{ "success": false, "error": { "code": "SNAKE_CASE", "message": "...", "details": [] } }
```

### Naming

- Files: `kebab-case` (e.g. `user.service.py`, `auth.routes.py`)
- DB: `snake_case`
- TS/Python vars: `camelCase` / `snake_case` per language norms
- Types/classes: `PascalCase`

## Commands

```bash
# Infra
docker compose up -d

# Backend (from repo root; ensure venv + deps from requirements.txt)
uvicorn backend.main:app --reload --port 8000
pytest
alembic upgrade head

# Frontend
cd frontend && npm install
npm run dev
npm run test
npm run lint
npm run build
```

Copy `.env.example` / `frontend/.env.example` — never commit secrets.

## Non-negotiables

1. **Secrets:** env only via config (`backend/config.py` / Vite `import.meta.env`). No hardcoded keys.
2. **Validation:** all untrusted input through Pydantic/Zod `.strict()`-style schemas.
3. **AuthZ:** protect non-public routes; verify resource ownership in the **service** layer.
4. **SQL:** parameterized only; respect tenant RLS.
5. **Logging:** use project logger (`backend/utils/logger`); never `console.log` in shipped backend. Never delete existing `logger.*` calls. Never log passwords, tokens, or full auth headers.
6. **API responses:** never return `passwordHash`, refresh tokens, or unnecessary PII.
7. **Scope:** change only what the task requires; no drive-by refactors or unsolicited markdown docs.
8. **Commits:** only when the user explicitly asks.

## Frontend notes

- Mobile-first PWA; chat is the primary student surface.
- Prefer accessible queries in tests (`getByRole`, `getByLabel`).
- Follow existing AppShell / BottomNav patterns before inventing new layout systems.
- Design: one job per section; avoid generic purple/cream AI aesthetics (see user frontend rules).

## When to use skills / rules

Before scaffolding, **read the matching skill** under `.cursor/skills/`:

| Task | Skill |
|------|-------|
| New API endpoint | `create-api-endpoint` |
| Zod/Pydantic schema | `create-zod-schema` |
| React component/page | `create-react-component` |
| TanStack Query hook | `tanstack-query-hook` |
| Migration | `create-database-migration` |
| Auth middleware | `add-authentication-middleware` |
| Logger / errors / rate limit | `setup-logger`, `setup-error-handler`, `setup-rate-limiting` |
| Unit / e2e tests | `write-unit-test`, `write-playwright-e2e` |
| Speckit workflow | `speckit-*` |

Always-on rules: `.cursor/rules/architecture.mdc`, `security.mdc`, `logging.mdc`.  
TS files: `.cursor/rules/typescript.mdc`.

## Verification

After non-trivial changes:

1. Run the relevant tests (`pytest` and/or `npm run test`).
2. Ensure API still returns the standard envelope.
3. Confirm no secrets or `passwordHash` in responses/logs.
4. Update `progress.md` when completing tracked work items.

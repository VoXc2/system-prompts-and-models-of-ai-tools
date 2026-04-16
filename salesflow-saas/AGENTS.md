# AGENTS.md — Dealix AI Revenue OS

## Project Identity
- **Name**: Dealix (ديلكس)
- **Type**: AI-Powered CRM SaaS for Saudi Arabia
- **Stack**: FastAPI + Next.js 15 + PostgreSQL + Redis + Celery
- **Market**: Saudi SMBs (real estate, healthcare, retail, contracting, education)
- **Language**: Arabic-first, bilingual (AR/EN)

## Architecture Boundaries

### Backend (`salesflow-saas/backend/`)
- FastAPI 0.115.6 on Python 3.12
- SQLAlchemy 2.0 async with PostgreSQL 16
- Celery 5.x with Redis broker
- JWT authentication (PyJWT)
- Multi-tenant data isolation via `tenant_id`

### Frontend (`salesflow-saas/frontend/`)
- Next.js 15 with App Router
- TypeScript 5.7, Tailwind CSS 3.4
- RTL-first layout (dir="rtl")
- Fonts: IBM Plex Sans Arabic (primary), Tajawal (secondary)

### AI Layer (`backend/app/services/ai/`)
- LLM Provider: Groq (primary) → OpenAI (fallback)
- Arabic NLP with Saudi dialect support
- Model routing via `services/model_router.py`

### Agent System (`backend/app/services/agents/`)
- Manus-style orchestrator with 8 specialized roles
- Event-to-agent routing via `router.py`
- Executor with retry logic and escalation

## Coding Conventions
- Python: async/await, type hints, Pydantic models, 4-space indent
- TypeScript: strict mode, functional components, Tailwind classes
- Database: all queries through SQLAlchemy ORM, never raw SQL
- API: RESTful, versioned (/api/v1/), proper HTTP status codes
- Naming: snake_case (Python), camelCase (TypeScript)
- Arabic: all user-facing strings must have Arabic versions
- Currency: SAR default, Numeric type for money fields
- Timezone: Asia/Riyadh (UTC+3)

## Forbidden Actions
- Never hardcode API keys or secrets
- Never bypass tenant isolation
- Never send messages without PDPL consent check
- Never delete data without soft-delete first
- Never push directly to main branch
- Never skip security review for auth/payment changes
- Never use synchronous DB calls in async endpoints
- Never store PII in logs

## Policy Classes

### Class A — Auto-allowed
- Code reading and inspection
- Test generation and execution
- Documentation updates
- Memory/knowledge base updates
- Linting and formatting
- Architecture analysis

### Class B — Approval Required
- Database migrations
- Customer-facing message sends
- Payment/billing changes
- Permission model changes
- External API integrations
- Production deployments
- PDPL consent configuration changes

### Class C — Forbidden
- Secret exfiltration
- Bypassing branch protections
- Silent destructive changes
- Disabling security gates
- Cross-tenant data access
- Ungoverned bulk messaging

## How to Install
```bash
cd salesflow-saas
cp .env.example .env  # Configure your environment
docker-compose up -d
make migrate
make seed
```

## How to Test
```bash
cd salesflow-saas/backend
pytest -v
# Or with coverage
pytest --cov=app --cov-report=html
```

## How to Run
```bash
docker-compose up  # All services
# Or individually:
cd backend && uvicorn app.main:app --reload --port 8000
cd frontend && npm run dev
```

## Provider Preferences
1. **Fast classification**: Groq (llama-3.1-70b)
2. **Arabic NLP**: Groq with Arabic context prompts
3. **Sales copy/proposals**: Claude (via model_router)
4. **Research/analysis**: Gemini (via model_router)
5. **Coding tasks**: DeepSeek (via model_router)
6. **Fallback**: OpenAI GPT-4o-mini

## Release Process
1. Feature branch → PR → Code review
2. Run tests + security scan
3. Deploy to staging
4. Smoke test (Arabic + English)
5. Deploy to production with canary (10%)
6. Monitor 30 min → full rollout
7. Rollback plan documented per release

## Cursor Cloud specific instructions

### Services overview

| Service | How to start | Port | Notes |
|---------|-------------|------|-------|
| **Backend** | `cd salesflow-saas/backend && PYTHONPATH=$PWD DATABASE_URL="sqlite+aiosqlite:///./dealix.db" uvicorn app.main:app --reload --host 0.0.0.0 --port 8000` | 8000 | SQLite mode — no Postgres/Redis needed |
| **Frontend** | `cd salesflow-saas/frontend && npx next dev --port 3000` | 3000 | Needs `npm ci` first; `.env.local` from `.env.example` |

### Running without Docker (Cloud Agent default)

The backend has a built-in SQLite fallback (`sqlite_patch.py`) that replaces PostgreSQL types with SQLite-compatible equivalents. Set `DATABASE_URL=sqlite+aiosqlite:///./dealix.db` (env var or in `salesflow-saas/.env`). The backend calls `init_db()` on startup to auto-create all tables — no Alembic migrations needed in SQLite mode.

### Key gotchas

- **PYTHONPATH**: Backend tests and `uvicorn` require `PYTHONPATH` set to the `salesflow-saas/backend` directory. Without it, `from app.main import app` fails with `ModuleNotFoundError`.
- **pytest**: Do not pass `--timeout` — it is not installed. The `pytest.ini` in `backend/` handles asyncio mode.
- **Frontend `predev` script**: `npm run dev` triggers a `predev` hook that runs `node ../scripts/sync-marketing-to-public.cjs`. This script is non-critical; if it fails the dev server still starts.
- **OpenAPI docs**: Available at `/api/docs` and `/api/redoc` when `EXPOSE_OPENAPI=true` (default in dev).
- **Lint**: Backend has no dedicated linter config; frontend uses `next lint` (ESLint 8).
- **Build**: `cd salesflow-saas/frontend && npx next build` produces a static export with 12 routes.
- **Tests**: `cd salesflow-saas/backend && PYTHONPATH=$PWD DATABASE_URL="sqlite+aiosqlite:///./test_dealix.db" pytest -v` — 61 tests, all passing.

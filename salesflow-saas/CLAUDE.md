# Dealix — AI Revenue OS

## Project Overview
Multi-tenant AI Revenue Operating System for Saudi SMEs. FastAPI backend + Next.js 15 frontend.

## Architecture Conventions

### Backend (Python/FastAPI)
- **Auth**: JWT dict-based. `get_current_user` returns `dict` with `user_id`, `tenant_id`, `role`.
  - Access via `current_user["tenant_id"]`, NOT `current_user.tenant_id`
- **Dependencies**: Always import from `app.api.v1.deps`, NOT `app.api.deps`
- **Models**: Inherit from `TenantModel` (includes `tenant_id`, `id`, `created_at`)
- **DB Sessions**: Use `get_db()` dependency — auto-commits on success, auto-rollbacks on error
- **Celery**: Use `asyncio.new_event_loop()` in sync tasks, NOT `asyncio.get_event_loop()`
- **AI calls**: Use `ai_brain.think(system_prompt=..., user_message=..., temperature=..., max_tokens=...)`

### Frontend (Next.js/React)
- **Language**: Arabic-first (RTL). `<html lang="ar" dir="rtl">`
- **API Client**: `frontend/src/lib/api.ts` — all API calls go through `apiFetch()`
- **Styling**: Tailwind CSS with custom Saudi color palette (primary=#0B3B66, secondary=#0FAF9A)
- **State**: React hooks only (useState, useEffect). No Redux/Zustand.
- **Auth**: JWT token in localStorage via `getToken()`/`setToken()`

### Multi-Tenant
- Every model has `tenant_id` (UUID, indexed)
- Every query MUST filter by `tenant_id`
- Never hardcode `tenant_id="default"`

## Commands
- `make up` — Start services
- `make test` — Run pytest
- `make logs-backend` — View backend logs
- `make migrate` — Run migrations
- `docker compose exec backend pytest -v` — Run tests inside container

## File Naming
- API routes: `backend/app/api/v1/{resource}.py`
- Models: `backend/app/models/{entity}.py`
- Services: `backend/app/services/{service_name}.py`
- Workers: `backend/app/workers/{task_type}_tasks.py`

## Critical Rules
1. Never expose stack traces in API responses (global handler catches all)
2. Never use `default={}` or `default=[]` for Column defaults — use `default=dict` or `default=list`
3. All status/stage columns must have `index=True`
4. All foreign key columns should have `index=True`
5. Rate limit auth endpoints (slowapi)
6. PDPL compliance: consent before outreach, opt-out honored

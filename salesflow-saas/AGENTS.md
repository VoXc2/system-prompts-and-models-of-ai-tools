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

## Sovereign Enterprise Growth OS — 5 Planes Architecture

Added in v2.1 — full sovereign enterprise layer on top of the CRM core.

### Decision Plane (`backend/app/services/decision_plane.py`)
- Structured AI recommendations: every recommendation is typed, evidence-backed, policy-aware, provenance-aware, freshness-aware
- `EvidencePack` model captures: sources, assumptions, alternatives, financial_model_version, rollback_notes
- `SovereignDecision` records every AI recommendation with model_used, lane, HITL status
- Approval classes: A (auto), B (human approval required), C (forbidden)
- Reversibility classes: full, partial, none
- Sensitivity levels: low, medium, high, critical

### Execution Plane
- `ContradictionEngine` (`backend/app/services/contradiction_engine.py`) — detects mismatches between intended/claimed/actual agent actions
- `ToolVerificationLedger` — immutable log of every tool call
- `ConnectorFacade` (`backend/app/services/connector_facade.py`) — governed wrapper for ALL external integrations (retry, idempotency, audit, telemetry)

### Trust Plane (`backend/app/services/trust_plane.py`)
- `PolicyEngine` — OPA-compatible policy evaluation (OPA sidecar in production, builtin fallback in dev)
- `AuthorizationEngine` — OpenFGA-compatible relationship-based authz (OPENFGA_URL, OPENFGA_MODEL_ID env vars)
- `PolicyViolation` model — all violations recorded and surfaced on board

### Data Plane (`backend/app/services/otel_instrumentation.py`)
- `CloudEvents`-compatible event envelopes
- OpenTelemetry traces, metrics, logs with correlation IDs (falls back gracefully if otel not installed)
- `ConnectorRegistry` — versioned connector catalog with contract schema + retry + audit mapping

### Operating Plane
- Alembic migration: `20260416_0002_sovereign_enterprise_os.py`
- All new tables: evidence_packs, sovereign_decisions, partners, partner_scorecards, ma_targets, dd_checklists, expansion_markets, expansion_actuals, pmi_programs, pmi_tasks, policy_violations, tool_verification_ledger, contradiction_records, connector_registry, model_routing_configs, saudi_compliance_controls, board_packs

### Business OS Modules (API routes `/api/v1/`)
- `/decision-plane/` — Structured recommendations, evidence packs, HITL approvals
- `/executive-room/` — Board packs, approval center, executive dashboard
- `/partnership-os/` — Partner scouting, scorecards, term sheets
- `/corporate-dev/` — M&A targets, DD rooms, checklists
- `/expansion-os/` — Market scanning, launch readiness, actual vs forecast
- `/pmi-os/` — 30/60/90 integration plans, synergy tracking, risk register
- `/trust-plane/` — Policy violations, tool verification ledger, contradictions
- `/connector-health/` — Governed connector registry with health board
- `/model-routing/` — Sovereign routing fabric config + metrics dashboard
- `/saudi-compliance/` — PDPL + NCA ECC 2024 + NIST AI RMF + OWASP LLM mapping

### Frontend Surface
- `/sovereign-os` page — 8-surface navigation: Executive Room, Partnership OS, M&A, Expansion, Trust Plane, Connectors, Compliance, Model Routing
- RTL-first, Arabic-first, Saudi-ready design

### Environment Variables for Sovereign OS
- `OPA_URL` — OPA policy sidecar (default: http://opa:8181)
- `OPENFGA_URL` — OpenFGA authorization server (default: http://openfga:8080)
- `OPENFGA_MODEL_ID` — Pinned authorization model ID (immutable in OpenFGA)

## Release Process
1. Feature branch → PR → Code review
2. Run tests + security scan
3. Deploy to staging
4. Smoke test (Arabic + English)
5. Deploy to production with canary (10%)
6. Monitor 30 min → full rollout
7. Rollback plan documented per release

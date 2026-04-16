# CLAUDE.md — Dealix Sovereign Growth OS

## Quick Context
Dealix is a **Sovereign Enterprise Growth OS** for GCC companies. Not just a CRM — a multi-layer system managing revenue, partnerships, M&A, market expansion, strategic execution, and governance.

**Three governing layers:**
1. **Decision Plane** — AI explores, analyzes, recommends (structured outputs, not free text)
2. **Execution Plane** — Durable workflows commit actions (retries, compensation, HITL)
3. **Trust Plane** — Policy-as-code, approval routing, audit trail, tool verification

**Primary rule:** AI may recommend. Systems commit. Humans approve critical decisions.

## Key Directories
- `backend/app/api/v1/` — API routes (FastAPI)
- `backend/app/models/` — SQLAlchemy models
- `backend/app/services/` — Business logic layer
- `backend/app/services/ai/` — AI engine (Arabic NLP, scoring, forecasting)
- `backend/app/services/pdpl/` — PDPL compliance engine
- `backend/app/services/cpq/` — Configure, Price, Quote
- `backend/app/services/agents/` — Multi-agent orchestration
- `backend/app/services/llm/` — LLM provider abstraction
- `backend/app/workers/` — Celery async tasks
- `backend/app/integrations/` — WhatsApp, Email, SMS adapters
- `frontend/src/app/` — Next.js pages
- `seeds/` — Industry templates (JSON)
- `memory/` — Project knowledge base

## Database
- PostgreSQL 16 with async driver (asyncpg)
- Multi-tenant: every table has `tenant_id`
- Alembic for migrations
- Money fields use `Numeric` type (never Float)

## AI Architecture
- Provider abstraction: Groq → OpenAI fallback
- Model router: task-specific model selection
- Arabic NLP: intent, sentiment, entity extraction
- Lead scoring: 0-100 composite score
- Conversation intelligence: Arabic dialogue analysis
- Sales agent: autonomous WhatsApp qualification bot

## PDPL Compliance (Critical)
- Check consent before ANY outbound message
- Track consent purpose, channel, timestamp
- Support data subject rights (access, correct, delete)
- Audit trail for all consent changes
- Auto-expire consent after 12 months
- Penalty: up to SAR 5 million per violation

## Testing
```bash
pytest -v                           # All tests
pytest tests/test_ai/ -v            # AI engine tests
pytest tests/test_pdpl/ -v          # PDPL compliance tests
pytest tests/test_api/ -v           # API endpoint tests
```

## Common Tasks
- Add new API endpoint: create route in `api/v1/`, register in `main.py`
- Add new model: create in `models/`, add to `models/__init__.py`, create migration
- Add new AI feature: create in `services/ai/`, wire to relevant API/worker
- Add industry template: create JSON in `seeds/`, match existing schema

## gstack Planning Discipline

Before writing code, classify your task:

| Tier | When | What to do |
|------|------|-----------|
| **SIMPLE** | 1 file, obvious change | Just do it |
| **MEDIUM** | Multi-file, needs thought | Read files → 5-line plan → resolve ambiguity → self-review → report |
| **HEAVY** | Complex, needs specific skill | Load skill → execute workflow → verify → report |
| **FULL** | End-to-end feature/release | Plan → review → implement → test → ship → report |
| **PLAN** | Research/architecture only | Plan only, save to `memory/`, no implementation |

**RULE**: Append to this file, never replace existing instructions.

## Strategic Growth Layer (Layer 8)
- `backend/app/agents/strategic/` — 10 strategic agents (partnerships, M&A, expansion, PMO, governance)
- `backend/app/agents/strategic/events.py` — Event taxonomy (32 typed events across 5 domains)
- `backend/app/services/governance_engine.py` — Policy-as-code engine with approval matrix
- `backend/app/api/v1/strategic_dashboard.py` — 7 dashboard API endpoints
- `docs/EXECUTION-MATRIX.md` — Full agent→KPI mapping
- `docs/governance/` — Executive charter + approval policy
- `docs/MASTER_OPERATING_PROMPT.md` — Operating constitution
- `docs/ai-operating-model.md` — Provider routing + verification + release gates + memory governance
- `docs/DEALIX_SOVEREIGN_GROWTH_OS_FOUNDING_AR.md` — Founding document (Arabic)

## Hermes Profiles

| Profile | Mission | Scope |
|---------|---------|-------|
| `growth` | Customer acquisition | leads, messaging, analytics, content |
| `sales` | Deal closing | deals, proposals, sequences, WhatsApp |
| `security` | Platform protection | compliance, audit, Shannon scans |
| `ops` | Deployment & reliability | workers, monitoring, releases |
| `knowledge` | Wiki & memory management | brain, wiki, indexes |
| `founder` | Strategic decisions | everything (highest permissions) |
| `arabic-ops` | Arabic content & dialect | summarization, dialect detection, RTL |

## Arabic Operations

- Use `arabic_ops.py` for: call notes compression, market research digests, executive briefs
- Always detect dialect before processing (saudi/gulf/msa)
- Check for Arabizi and suggest Arabic conversion
- Check code-switching (Arabic+English mixed) for readability

## claude-mem (Persistent Memory)

Installed and active. Automatically captures every session's work and injects context into new sessions.

- **Worker**: `npx claude-mem start` (port 37777)
- **Web UI**: http://localhost:37777
- **Search**: Use `/mem-search` in Claude Code
- **Data**: `~/.claude-mem/claude-mem.db` (SQLite + Chroma vectors)
- **Privacy**: Wrap sensitive content in `<private>...</private>` tags
- **Token savings**: ~95% reduction via 3-layer progressive retrieval
- **Auto-captures**: tool executions, session summaries, decisions, bugs, patterns

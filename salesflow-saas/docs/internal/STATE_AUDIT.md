# STATE AUDIT — Dealix Pre-Execution Assessment

> **Date**: 2026-04-17  
> **Auditor**: Claude Code (automated)  
> **Scope**: Answer all §1.4 questions from DEALIX_EXECUTION_BLUEPRINT.md

---

## Q1: Is the project still a fork of system-prompts-and-models-of-ai-tools?

**Answer**: YES — Dealix currently lives inside `salesflow-saas/` subdirectory of `VoXc2/system-prompts-and-models-of-ai-tools`, which is a repository containing leaked AI tool prompts from 45+ vendors.

**Risk**: Commercial, legal, and reputational. Core IP shares a repo with leaked/extracted prompts.

**Action**: TASK-001 (repository separation) is BLOCKER.

---

## Q2: What is the actual Python test pass rate?

**Answer**: UNKNOWN (CI failing due to pre-existing dependency drift).

**Evidence**: 
- 19 test files exist in `backend/tests/`
- 1,073 total lines of test code
- CI exit code 4 (pytest collection error) on all commits after `a319feb`
- Root cause: unpinned transitive dependency updated on PyPI between CI runs
- Router.py and pytest.ini byte-identical between passing and failing commits

**Action**: TASK-003 (dependency lockfile with `uv`) will resolve this.

---

## Q3: What is the actual RLS coverage per table?

**Answer**: MIGRATION EXISTS but NOT APPLIED to production.

**Evidence**:
- `alembic/versions/20260417_0002_add_rls.py` — migration defines RLS for 23 tables
- `database_rls.py` — helpers for SET LOCAL app.tenant_id
- `middleware/tenant_rls.py` — extracts tenant_id from JWT
- **Current state**: Migration exists in code but no production PostgreSQL to apply it to

**Action**: Apply migration on first production deployment.

---

## Q4: Which external actions actually have idempotency keys?

**Answer**: MIDDLEWARE EXISTS but NOT YET INTEGRATED into specific routes.

**Evidence**:
- `models/idempotency_key.py` — table defined
- `services/idempotency_service.py` — get_existing/store logic
- `middleware/idempotency.py` — HTTP middleware checks Idempotency-Key header
- **Not integrated**: Middleware not added to FastAPI app middleware stack

**Action**: Add middleware to app initialization in main.py.

---

## Q5: Which code paths actually emit OTel spans?

**Answer**: ONE code path — OpenClaw gateway.

**Evidence**:
- `observability/otel.py` — init_otel/span/inject_correlation_id (graceful degradation)
- `openclaw/gateway.py` — wraps execute() in span with correlation_id bridge
- **NOT instrumented**: Individual golden path stages, LLM calls, DB queries, HTTP handlers
- **OTel packages NOT in requirements.txt** — installed as optional

**Action**: Add OTel packages to requirements, instrument golden path stages.

---

## Q6: Is there any production traffic today?

**Answer**: NO — based on repo evidence.

**Evidence**:
- No production deployment configuration found
- No monitoring/alerting setup active
- docker-compose.yml exists for local dev
- No Kubernetes, Terraform, or cloud deployment files

---

## Q7: Are there any active paying customers?

**Answer**: NO — no billing records, no customer data, no invoices.

**Evidence**: Revenue activation docs exist as plans, not records.

---

## Q8: What is the current infrastructure cost/month?

**Answer**: ~$0 (development only, no production infrastructure running).

---

## Q9: What are the LLM costs/month and which providers?

**Answer**: $0 in production. Configured providers:

| Provider | Model | Status |
|----------|-------|--------|
| Groq | llama-3.3-70b | Configured as primary |
| OpenAI | gpt-4o | Configured as fallback |
| Claude | opus-4-6 | In model_router |
| Gemini | 2.0-flash | Pilot |
| DeepSeek | coder | Pilot |

No production API keys observed. All testing/development.

---

## Summary

| Question | Status |
|----------|--------|
| Repo separated? | **NO** — BLOCKER |
| Tests passing? | **NO** — dependency drift |
| RLS coverage? | **CODE EXISTS** — not applied |
| Idempotency? | **CODE EXISTS** — not integrated |
| OTel spans? | **1 PATH** — gateway only |
| Production traffic? | **NONE** |
| Paying customers? | **NONE** |
| Infrastructure cost? | **$0** |
| LLM cost? | **$0** |

**Verdict**: Dealix is a pre-revenue, pre-production project with strong architecture but no live deployment. TASK-001 (repo separation) and TASK-003 (dependency fix) are true blockers.

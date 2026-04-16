# Dealix — Current vs Target Architecture Register

> **Version:** 1.0 — 2026-04-16
> **Purpose:** Single source of truth for what exists today vs what is needed for enterprise-grade production.
> **Status Key:** `✅ Production` · `🔶 Pilot` · `🟡 Partial` · `⬜ Planned` · `❌ Gap`

---

## 5 Operational Planes — Status Overview

| Plane | Current Maturity | Target | Priority |
|-------|-----------------|--------|---------|
| 1. Decision Plane | 🟡 Partial — schemas informal, some Structured Outputs | ✅ All critical outputs schema-bound, HITL for Executor class | HIGH |
| 2. Execution Plane | 🟡 Partial — Celery + LangGraph for short flows | ✅ Temporal for long-lived, Celery/LangGraph for short-lived | HIGH |
| 3. Trust Plane | 🟡 Partial — app-level checks, PDPL checklist doc | ✅ OPA + OpenFGA + Vault + Keycloak | HIGH |
| 4. Data Plane | 🔶 Pilot — Postgres + pgvector + basic connectors | ✅ Connector facades + event envelopes + Great Expectations | MEDIUM |
| 5. Operating Plane | 🟡 Partial — CI/CD exists, no rulesets/OIDC/attestations | ✅ Rulesets + OIDC + attestations + canary + SIEM streaming | HIGH |

---

## Plane 1 — Decision Plane

### Subsystems

| Subsystem | Current | Target | Status | Owner | WS Ref |
|-----------|---------|--------|--------|-------|--------|
| Agent output schemas | Informal dicts, some Pydantic models | 5 canonical JSON schemas (memo, evidence_pack, risk_register, approval_packet, execution_intent) | 🟡 Partial | AI Lead | WS 2.1 |
| OpenAI Structured Outputs | JSON mode on some paths | `json_schema` response_format on ALL Executor-class agent calls | 🟡 Partial | AI Lead | WS 2.2 |
| Evidence Pack Generator | Not built | Service that compiles tool results → typed evidence_pack_json | ❌ Gap | Backend Engineer | WS 2.3 |
| Decision Memo Compiler | Ad-hoc text generation | Bilingual AR/EN memo from memo_json + evidence_pack | ❌ Gap | Backend Engineer | WS 2.4 |
| Provenance / Freshness / Confidence scoring | Not implemented | Scores on every critical agent output, stored in metadata | ❌ Gap | AI Lead | WS 2.5 |
| HITL interrupts (LangGraph) | Partial — some approval steps | All Executor-class decisions above risk threshold pause for human | 🟡 Partial | AI Lead | WS 2.6 |
| Agent role registry | Informal docs | Formal registry: Observer / Recommender / Executor + action metadata | 🟡 Partial | AI Lead | WS 1.4 |

### Interfaces

- **Input:** Tool results (JSON), KB hits (pgvector), CRM data (connector facade)
- **Output:** One of 5 canonical schemas (never free-text for critical flows)
- **HITL channel:** LangGraph interrupt → approval webhook → resume

---

## Plane 2 — Execution Plane

### Subsystems

| Subsystem | Current | Target | Status | Owner | WS Ref |
|-----------|---------|--------|--------|-------|--------|
| Celery workers | ✅ Production | Retained for short-lived tasks (< 15 min, single system) | ✅ Production | Backend Lead | — |
| LangGraph | 🔶 Pilot | Retained for stateful reasoning + short multi-step flows | 🔶 Pilot | AI Lead | — |
| Temporal (durable workflows) | ❌ Not installed | All workflows: > 15 min OR cross 2+ systems OR need compensation | ❌ Gap | Platform Engineer | WS 3.2 |
| Partner Approval Workflow | Celery task, non-durable | Temporal workflow with compensation + HITL gate | 🟡 Partial | Backend Lead | WS 3.3 |
| Idempotency key enforcement | Partial | Every Temporal activity has idempotency_key; tested with duplicate triggers | 🟡 Partial | Backend Lead | WS 3.4 |
| Workflow versioning strategy | None | `workflow.get_version()` pattern; zero-downtime update runbook | ❌ Gap | Backend Lead | WS 3.5 |
| Celery → Temporal migration | N/A | Phased cut-over runbook; staging dry-run; no split-brain | ❌ Gap | Backend Lead | WS 3.6 |

### Classification Rules (Enforced from Sprint 2)

```
short-lived-local    : duration < 15 min, single service, no compensation needed  → Celery/LangGraph
medium-lived-queued  : duration 15 min–4 h, 1–2 services, simple retry             → Celery + idempotency
long-lived-durable   : duration > 4 h, OR crosses 2+ systems, OR needs compensation → Temporal (mandatory)
```

---

## Plane 3 — Trust Plane

### Subsystems

| Subsystem | Current | Target | Status | Owner | WS Ref |
|-----------|---------|--------|--------|-------|--------|
| Policy engine (OPA) | ❌ Not deployed | OPA policy packs for tenant isolation, agent gating, action sensitivity | ❌ Gap | Security Lead | WS 4.2 |
| Authorization graph (OpenFGA) | ❌ Not deployed | OpenFGA model: tenants, users, agents, tools, workflows | ❌ Gap | Security Lead | WS 4.3 |
| Secret management (Vault) | Static `.env` / env vars | HashiCorp Vault: dynamic DB creds, API keys, audit log | ❌ Gap | Platform Engineer | WS 4.4 |
| Identity / SSO (Keycloak) | Custom JWT | Keycloak OIDC for humans; service accounts for agents/workers | ❌ Gap | Platform Engineer | WS 4.5 |
| Tool Verification Ledger | Not built | Per-tool: intended / claimed / actual / side_effects / contradiction | ❌ Gap | AI Lead | WS 4.6 |
| Contradiction Dashboard | Not built | UI surfacing contradiction_status ≠ none to ops | ❌ Gap | Backend Engineer | WS 4.7 |
| PDPL control enforcement | Checklist doc only | OPA policy enforces residency + consent + transfer controls at runtime | 🟡 Partial | Security Lead | WS 7.3 |

### Trust Enforcement Order

```
Request → Keycloak (identity) → OPA (policy) → OpenFGA (authorization) → App (enforcement hook) → Tool → Ledger (verification) → Response
```

---

## Plane 4 — Data Plane

### Subsystems

| Subsystem | Current | Target | Status | Owner | WS Ref |
|-----------|---------|--------|--------|-------|--------|
| Operational DB (Postgres) | ✅ Production | Operational truth; row-level multi-tenancy | ✅ Production | Backend Lead | — |
| Semantic memory (pgvector) | 🔶 Pilot | Deal context, sector KB, partner history; p95 < 100 ms | 🔶 Pilot | Backend Lead | WS 5.4 |
| Connector facades | Raw SDK calls | Base class + versioning + retry/timeout/idempotency per connector | ❌ Gap | Backend Lead | WS 5.1 |
| HubSpot connector | Raw API | Facade-wrapped, versioned `v1`, unit tested with mock | 🟡 Partial | Backend Engineer | WS 5.2 |
| WhatsApp/Twilio connector | 🔶 Pilot | Facade-wrapped, versioned | 🔶 Pilot | Backend Engineer | WS 5.2 |
| DocuSign connector | 🟡 Partial | Facade-wrapped, versioned, idempotency enforced | 🟡 Partial | Backend Engineer | WS 5.2 |
| Email/Calendar connectors | 🟡 Partial | Facade-wrapped, versioned | 🟡 Partial | Backend Engineer | WS 5.2 |
| Event envelope (CloudEvents) | Informal dicts | CloudEvents spec + AsyncAPI schema registry | ❌ Gap | Backend Lead | WS 5.3 |
| Semantic metrics dictionary | Undocumented | 30+ KPIs: formula, grain, source, owner | ❌ Gap | Product Lead | WS 5.5 |
| Data quality (Great Expectations) | Not deployed | GE suites on lead, deal, partner, telemetry; ≥ 98 % pass | ❌ Gap | Data Engineer | WS 5.6 |
| Lineage / catalog | Not deployed | Every production table catalogued; traceable to dashboard | ❌ Gap | Data Engineer | WS 5.7 |

---

## Plane 5 — Operating Plane

### Subsystems

| Subsystem | Current | Target | Status | Owner | WS Ref |
|-----------|---------|--------|--------|-------|--------|
| CODEOWNERS | Not present | All critical paths owned by ≥ 2 reviewers, enforced in PRs | ❌ Gap | Platform Lead | WS 6.1 |
| Branch rulesets (GitHub) | Basic protection | Rulesets: required status checks, no force-push, required signatures | 🟡 Partial | Platform Lead | WS 6.2 |
| GitHub Environments | Not configured | dev / staging / canary / production with approvals and wait timers | ❌ Gap | Platform Lead | WS 6.3 |
| OIDC federation (CI → cloud) | Long-lived secrets | GitHub Actions OIDC → cloud provider; zero static credentials in CI | ❌ Gap | Platform Engineer | WS 6.4 |
| Artifact attestations | Not implemented | `gh attestation verify` passes for all production images | ❌ Gap | Platform Engineer | WS 6.5 |
| Canary release workflow | Not implemented | 5 % → 25 % → 100 %; auto-rollback on error spike; < 2 min | ❌ Gap | Platform Engineer | WS 6.6 |
| Audit log streaming (SIEM) | Not streaming | Events to external warehouse; covers GitHub 180-day limit | ❌ Gap | Security Lead | WS 6.7 |

---

## 6 Business Tracks — Agent Role Matrix

| Track | Observer Agents | Recommender Agents | Executor Agents | Long-lived Durable? |
|-------|----------------|-------------------|----------------|-------------------|
| Prospecting | Market Scanner, Lead Scorer | Outreach Advisor | Outreach Sender (gated) | No |
| Qualification | Conversation Listener | Qualification Advisor | Booking Agent (gated) | No |
| Proposal | Proposal Analyzer | Proposal Writer | Proposal Sender (gated) | No |
| Negotiation | Deal Monitor | Negotiation Advisor | Counter-offer Sender (gated) | No |
| Closing | Signature Tracker | Closing Advisor | DocuSign Trigger (gated) | Yes → Temporal |
| Post-Sale / Upsell | Health Monitor, Billing Watch | Upsell Advisor | Renewal Trigger, PMI Agent (gated) | Yes → Temporal |

**Gated = requires HITL approval or OPA policy pass before execution.**

---

## Action Metadata Standard (All Executor-class actions)

```json
{
  "action_id": "uuid",
  "track": "closing",
  "agent_role": "Executor",
  "approval_required": true,
  "reversibility": "irreversible | reversible | compensatable",
  "sensitivity": "low | medium | high | critical",
  "provenance_score": 0.0,
  "freshness_score": 0.0,
  "confidence_score": 0.0,
  "tenant_id": "uuid",
  "data_residency": "KSA | EU | US",
  "timestamp_utc": "ISO-8601"
}
```

---

## Open Architecture Decisions (to be resolved in Sprint 1)

| Decision | Options | Owner | Deadline |
|----------|---------|-------|---------|
| Temporal hosting: self-hosted Docker vs Temporal Cloud | Self-hosted (cost control) vs Cloud (ops simplicity) | Platform Engineer | Sprint 1 |
| OpenFGA hosting: self-hosted vs managed | Self-hosted initially | Security Lead | Sprint 1 |
| Keycloak vs Auth0 for SSO | Keycloak (open source, on-prem control) | Platform Engineer | Sprint 1 |
| AsyncAPI vs manual event docs | AsyncAPI (tooling ecosystem) | Backend Lead | Sprint 1 |
| Single SIEM target: Elastic vs Splunk vs warehouse | Cloud data warehouse (BigQuery/Redshift) initially | Security Lead | Sprint 2 |

---

*This register must be reviewed and updated at the start of every sprint. Any change to "Target" state requires Platform Architect sign-off.*

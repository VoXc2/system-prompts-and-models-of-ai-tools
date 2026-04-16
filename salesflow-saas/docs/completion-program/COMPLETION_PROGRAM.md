# Dealix Completion Program — برنامج إغلاق الفجوات التشغيلية

**Version**: 1.0  
**Date**: 2026-04-16  
**Status**: canonical  
**Owner**: Founder / CTO  
**Scope**: Transform Dealix from strong documentation + Tier-1 vision → production enterprise-grade platform  

---

## Executive Summary / الملخص التنفيذي

Dealix has completed its **constitutional and reference layer**: MASTER-BLUEPRINT, Architecture docs, ADRs, PDPL checklist, agent system, durable flows via OpenClaw, and a 250+ Python module backend. The documentation is strong; the vision is Tier-1.

**What remains** is closing the gap between documentation and operational capability — until Dealix can serve enterprises with auditable trust, deterministic execution, typed decisions, and Saudi compliance.

This program defines **5 Operational Planes**, identifies **8 Operational Gaps**, and prescribes **8 Workstreams** to close them.

---

## Part 1: Five Operational Planes — الطبقات التشغيلية الخمس

### Plane 1 — Decision Plane (طبقة القرار)

**Purpose**: Every agent output becomes schema-bound, auditable, typed, and resumable.

| Component | Technology | Status |
|-----------|-----------|--------|
| LLM Interface | OpenAI Responses API + Structured Outputs | Target |
| Function Calling / MCP | OpenAI tools / MCP protocol | Target |
| Stateful Loops | LangGraph checkpoints + HITL interrupts | Partial (LangGraph in `master_langgraph.py`) |
| Decision Schemas | `memo_json`, `evidence_pack_json`, `risk_register_json`, `approval_packet_json`, `execution_intent_json` | Target |
| Provenance Scoring | `provenance_score`, `freshness_score`, `confidence_score` | Target |

**Current state in code**: `model_router.py` routes tasks to providers; `orchestrator.py` manages lead lifecycle; agents produce free-text outputs. No mandatory structured output schemas exist for critical flows.

### Plane 2 — Execution Plane (طبقة التنفيذ)

**Purpose**: All long-running business commitments run in a deterministic, durable workflow runtime.

| Component | Technology | Status |
|-----------|-----------|--------|
| Short-lived tasks | Celery workers (7 task modules) | Production |
| Durable flows | OpenClaw `DurableTaskFlow` (checkpoint state machine) | Partial (2 flows) |
| Long-lived deterministic | Temporal.io | Target |
| Compensation policies | Saga pattern with rollback | Target |
| Idempotency keys | Per-workflow dedup | Target |
| Workflow versioning | Temporal worker versioning | Target |

**Current state in code**: Celery handles 7 async task types. OpenClaw `durable_flow.py` provides checkpointed state machine. `prospecting_durable_flow.py` and `self_improvement_flow.py` are the only durable flows. No Temporal integration exists.

### Plane 3 — Trust Plane (طبقة الثقة)

**Purpose**: Make Dealix an "enterprise-grid" platform, not just an AI app.

| Component | Technology | Status |
|-----------|-----------|--------|
| Policy engine | OPA (Open Policy Agent) | Target |
| Fine-grained authorization | OpenFGA | Target |
| Secrets management | HashiCorp Vault | Target |
| Identity / SSO | Keycloak | Target |
| Tool verification | `tool_verification.py` + `tool_receipts.py` | Partial |
| Action metadata | Approval / Reversibility / Sensitivity / Provenance / Freshness | Target |
| Contradiction dashboard | Real-time intended vs actual execution | Target |

**Current state in code**: `security_gate.py` makes binary decisions. `tool_verification.py` and `tool_receipts.py` exist with pre-exec policy and trust analytics. `openclaw/policy.py` classifies safe vs approval-gated. `auth_service.py` handles JWT. No OPA, OpenFGA, Vault, or Keycloak integration.

### Plane 4 — Data Plane (طبقة البيانات)

**Purpose**: Structured data governance — no chaotic tool calls.

| Component | Technology | Status |
|-----------|-----------|--------|
| Operational truth | PostgreSQL 16 | Production |
| Semantic memory | pgvector via `knowledge_service.py` | Production |
| Ingestion / connectors | Airbyte | Target |
| Document processing | Unstructured | Target |
| Semantic metrics | Metrics dictionary | Target |
| Data quality | Great Expectations | Target |
| Event contracts | AsyncAPI + CloudEvents | Target |
| Lineage / catalog | Single catalog | Target |
| Schema registry | Enforced envelope schemas | Target |

**Current state in code**: PostgreSQL and pgvector are production. `knowledge_service.py` + `SectorAsset` provide RAG. 3 integration adapters (WhatsApp, email, SMS) exist. 6 OpenClaw plugins handle external systems. No Airbyte, no schema registry, no data quality framework.

### Plane 5 — Operating Plane (طبقة التشغيل والإصدار)

**Purpose**: GitHub + SDLC + promotion system that is enterprise-ready.

| Component | Technology | Status |
|-----------|-----------|--------|
| CI pipeline | GitHub Actions (`dealix-ci.yml`) | Production |
| Repo hygiene | `repo-hygiene.yml` (required files, block secrets) | Production |
| Branch protection | GitHub rulesets | Target |
| CODEOWNERS | Ownership mapping | Target |
| Environments | dev / staging / canary / prod | Target |
| OIDC federation | GitHub OIDC → cloud | Target |
| Artifact attestations | SLSA provenance | Target |
| Audit log streaming | GitHub → SIEM/warehouse | Target |
| Release gates | Required checks + approvals | Target |

**Current state in code**: Two CI workflows exist. Docker Compose defines local dev stack. No protected environments, no OIDC, no artifact attestations, no CODEOWNERS.

---

## Part 2: Eight Operational Gaps — الفجوات التشغيلية الثمان

### Gap 1: Documentation stronger than implementation (الوثائق أقوى من التنفيذ)

**Severity**: Critical  
**Evidence**: MASTER-BLUEPRINT describes 40+ agents, Salesforce Agentforce 360, voice GA, predictive revenue — while code shows partial implementations. `autonomous_core.py` and `auto_pipeline.py` use mock stores. Many service files are scaffolds with placeholder logic.

**Required**:
- Code-level implementation map with status per subsystem
- Status dashboard: Current / Partial / Pilot / Production
- Acceptance gates for each subsystem

→ See: [CURRENT_VS_TARGET_REGISTER.md](./CURRENT_VS_TARGET_REGISTER.md)

### Gap 2: Decision plane is theoretical, not typed execution-ready (طبقة القرار نظرية)

**Severity**: High  
**Evidence**: Agent outputs are free-text strings routed through `model_router.py`. No Pydantic schemas enforce structured decision outputs. `tool_receipts.py` captures post-hoc receipts but does not enforce input/output contracts.

**Required**:
- Every agentic decision outputs: `memo_json`, `evidence_pack_json`, `risk_register_json`, `approval_packet_json`, `execution_intent_json`
- Structured Outputs mandatory for critical flows
- Provenance + freshness + confidence scores on every decision

### Gap 3: Execution durability (متانة التنفيذ)

**Severity**: High  
**Evidence**: Only 2 durable flows exist (`prospecting_durable_flow.py`, `self_improvement_flow.py`). Business-critical processes like partner approvals, DD rooms, signature requests, and launches rely on Celery tasks without compensation logic.

**Required**:
- Any workflow >15 min OR crossing >2 systems OR needing compensation → migrates to Temporal
- Compensation policies, idempotency keys, workflow versioning

### Gap 4: Policy & auth not single source of truth (السياسات والتفويض غير موحدة)

**Severity**: High  
**Evidence**: Policy logic scattered across `openclaw/policy.py`, `security_gate.py`, `skill_governance.py`, `outbound_governance.py`, `autopilot.py`. Authorization is JWT-based only with basic role checks. No centralized policy evaluation or authorization graph.

**Required**:
- OPA = all policy decisions
- OpenFGA = authorization graph
- App code = enforcement hooks only
- No policy logic inside prompts or scattered conditionals

### Gap 5: Tool verification not mandatory evidence (التحقق من الأدوات لم يصل للإلزام)

**Severity**: High  
**Evidence**: `tool_verification.py` and `tool_receipts.py` exist but are advisory. No mandatory pre/post evidence chain. Risk of hallucinated operations per OWASP GenAI Top 10 (excessive agency, insecure output handling).

**Required per tool/action**:
- `intended_action` — what was requested
- `claimed_action` — what the agent says it did
- `actual_execution` — verified system state change
- `side_effects` — downstream impacts
- `contradiction_status` — intended vs actual delta

### Gap 6: Enterprise connectors not wrapped (الموصلات غير مغلفة)

**Severity**: Medium  
**Evidence**: 3 raw integrations (`whatsapp.py`, `email_sender.py`, `sms.py`) + 6 OpenClaw plugins (`whatsapp_plugin.py`, `voice_plugin.py`, `salesforce_agentforce_plugin.py`, `stripe_plugin.py`, `contract_intelligence_plugin.py`). No versioned connector facades, no retry/timeout/idempotency contracts.

**Required**:
- Connector facades versioned (vendor APIs change — e.g. HubSpot date-based API versioning 2026)
- Standard retry/timeout/idempotency/circuit-breaker policies
- Internal contract per connector

### Gap 7: Observability/evals not a gate (المراقبة والتقييم ليست بوابة)

**Severity**: Medium  
**Evidence**: `observability.py` provides workflow metrics and anomaly alerts. No OTel instrumentation, no `trace_id`/`correlation_id` propagation, no offline eval datasets, no red-team coverage, no regression review per release.

**Required**:
- OTel traces/metrics/logs with vendor-neutral export
- `trace_id` / `correlation_id` on every request
- Offline eval datasets for agent quality
- Online trace review pipeline
- Red-team for agent/tool surfaces
- Regression review per release gate

### Gap 8: Saudi enterprise posture needs operationalization (الامتثال السعودي يحتاج تفعيل)

**Severity**: Medium  
**Evidence**: `pdpl-checklist.md` exists as a checklist. Legal docs (privacy, terms, data protection) exist in Arabic. `consent_manager.py` and `data_rights.py` provide PDPL engine. No NCA ECC matrix, no NIST AI RMF mapping, no OWASP LLM controls per release, no data residency flags in policy engine.

**Required**:
- PDPL data classification matrix (operational, not just checklist)
- NCA ECC-2:2024 readiness matrix
- AI governance controls mapped to NIST AI RMF + OWASP LLM Top 10
- Region/data residency flags inside policy engine

→ See: [SAUDI_ENTERPRISE_READINESS.md](./SAUDI_ENTERPRISE_READINESS.md)

---

## Part 3: Eight Workstreams — المسارات الثمانية

| # | Workstream | Primary Plane | Priority |
|---|-----------|---------------|----------|
| WS-1 | Productization & Architecture Closure | All | P0 — Foundation |
| WS-2 | Decision Plane Hardening | Decision | P0 — Foundation |
| WS-3 | Execution Plane Hardening | Execution | P1 — Core |
| WS-4 | Trust Fabric Hardening | Trust | P1 — Core |
| WS-5 | Data & Connector Fabric | Data | P1 — Core |
| WS-6 | Enterprise Delivery Fabric | Operating | P2 — Scale |
| WS-7 | Saudi Enterprise Readiness | Trust + Data | P2 — Scale |
| WS-8 | Executive & Customer Readiness | All | P3 — Launch |

### Execution Order (non-negotiable)

1. **Control/Trust** before more agents
2. **Execution** before more autonomy
3. **Connector facades** before more tool calls
4. **Semantic metrics** before more dashboards
5. **Saudi governance** before enterprise rollout
6. **Executive room** before external scaling

### Workstream Details

→ See: [EXECUTION_MATRIX.md](./EXECUTION_MATRIX.md) for the full matrix with Deliverables / Owner / Evidence Gate / Exit Criteria / Dependencies / Risk / SLA per workstream.

---

## Part 4: Agent Role Locks — أدوار الوكلاء

| Role | Description | Autonomy Level | HITL Required |
|------|-------------|----------------|---------------|
| **Observer** | Monitors signals, surfaces recommendations | Full autonomy | No |
| **Recommender** | Produces structured recommendations with evidence | High autonomy | Optional review |
| **Executor** | Takes actions in external systems | Bounded autonomy | Yes for Class B/C actions |

### Action Metadata (mandatory per action)

| Field | Type | Description |
|-------|------|-------------|
| `approval_level` | enum | `auto` / `review` / `manual` / `executive` |
| `reversibility` | enum | `fully_reversible` / `partially_reversible` / `irreversible` |
| `sensitivity` | enum | `public` / `internal` / `confidential` / `restricted` |
| `provenance` | object | `source`, `model`, `retrieval_ids`, `freshness_score` |
| `freshness` | ISO 8601 | Data timestamp + staleness threshold |

---

## Part 5: Business Track Locks — المسارات التجارية الستة

| Track | Agent Coverage | Primary Flow | Status |
|-------|---------------|-------------|--------|
| **Prospecting** | Prospector, Lead Engine, Enrichment | `prospecting_durable_flow.py` | Partial — durable flow exists |
| **Qualification** | Qualifier, Scorer, Intent Detector | `orchestrator.py` state machine | Partial — agents defined |
| **Proposal/Negotiation** | CPQ, Deal Negotiator, Contract Intel | `quote_engine.py` + `proposal_generator.py` | Partial — CPQ exists |
| **Closing** | Closer, Pricing, Market Intel | `revenue_room.py` | Partial — agents defined |
| **Post-Sale/Upsell** | Onboarding, Support, Expansion | `customer_onboarding_journey.py` | Scaffold |
| **Analytics/Forecasting** | Forecast, Revenue Prediction | `forecasting.py` + `predictive_revenue_service.py` | Scaffold |

---

## Part 6: Definition of Done — Enterprise Readiness

Dealix is NOT "enterprise-ready" until ALL of the following are true:

- [ ] Every business-critical recommendation exits structured + evidence-backed
- [ ] Every long-running commitment passes through deterministic durable workflow
- [ ] Every sensitive action carries Approval / Reversibility / Sensitivity metadata
- [ ] Every connector is versioned with retry / idempotency / audit mapping
- [ ] Every release has rulesets + approvals + OIDC + provenance
- [ ] Every traceable surface has OTel telemetry and correlation IDs
- [ ] Every enterprise deployment has security review and red-team coverage for LLM/application surfaces
- [ ] Every Saudi-sensitive workflow has PDPL/NCA-aware control mapping

→ See: [DEFINITION_OF_DONE.md](./DEFINITION_OF_DONE.md) for the expanded checklist.

---

## Navigation

| Document | Purpose |
|----------|---------|
| [EXECUTION_MATRIX.md](./EXECUTION_MATRIX.md) | Full workstream execution matrix |
| [CURRENT_VS_TARGET_REGISTER.md](./CURRENT_VS_TARGET_REGISTER.md) | Subsystem status dashboard |
| [DEFINITION_OF_DONE.md](./DEFINITION_OF_DONE.md) | Enterprise readiness checklist |
| [SAUDI_ENTERPRISE_READINESS.md](./SAUDI_ENTERPRISE_READINESS.md) | PDPL / NCA / NIST AI RMF matrix |
| [ADR-003: Five Operational Planes](../../memory/adr/003-five-operational-planes.md) | Architecture decision record |
| [ADR-004: Temporal Migration](../../memory/adr/004-temporal-migration.md) | Architecture decision record |

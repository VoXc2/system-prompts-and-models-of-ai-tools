# Dealix Tier-1 Master Closure & Operating Blueprint v1.0

> **Status**: Canonical · Source of truth for architecture, governance, and execution
> **Last updated**: 2026-04-21
> **Owner**: Architecture Council

---

## 0. One-line definition

> **Dealix is a sovereign, policy-governed Growth & Execution OS for Saudi enterprises. It combines agentic intelligence, deterministic execution, approval controls, and executive observability to drive revenue, partnerships, expansion, and strategic operations with enterprise-grade trust.**

---

## 1. Executive governance

Dealix is operated as a **sovereign platform for growth, execution, and governance** — not a CRM, not a chatbot, not a sales automation tool.

It serves **six interlocking tracks**:

1. **Revenue OS** — lead to close, pipeline, forecasting
2. **Partnership OS** — partner discovery, joint pursuits, co-sell
3. **Corporate Development / M&A OS** — sourcing, diligence, integration
4. **Expansion OS** — new-market entry, localization
5. **PMI / Strategic PMO OS** — post-merger integration, cross-BU initiatives
6. **Trust, Policy & Executive Governance OS** — controls, approvals, risk, audit

### The Prime Operating Rule

> **AI explores, analyzes, and recommends.**
> **Deterministic workflows execute.**
> **Humans approve critical moves.**

No agent makes an external commitment on its own. No critical output leaves the system without being structured, evidence-backed, policy-evaluated, and (where required) human-approved.

---

## 2. The five mandatory planes

Every feature in Dealix lives in exactly one plane. Crossing planes happens via **contracts**, never via shared memory or direct calls.

### A. Decision Plane

**What lives here**: agents, reasoning, synthesis, qualification, scenario analysis, memo generation, recommendation, evidence assembly.

**Built on**:
- OpenAI Responses API + Structured Outputs (or equivalent provider-native structured output)
- MCP / connectors for tool access
- Prompt library with explicit roles, tasks, output schemas
- Deterministic JSON Schema validation on every critical output

**Does NOT**: execute commitments, call sensitive tools directly, hold long-running state.

### B. Execution Plane

**What lives here**: anything long-lived, multi-system, needing retries/checkpoints/compensation, or that may create external commitment.

**Built on**:
- **Phase 0–1**: LangGraph-style stateful runtime with persistence + interrupts (HITL)
- **Phase 2+**: Temporal for business-critical never-fail workflows

**Rule**: if a step causes an external commitment, it MUST be here, not inside an agent loop.

### C. Trust Plane

**Not a feature — a mandatory overlay.**

Contains:
- Policy evaluation (OPA/Rego or equivalent)
- Approval routing (Approval Center)
- Authorization (OpenFGA for fine-grained, Cedar optional)
- Identity & SSO (Keycloak)
- Secrets (Vault — dynamic secrets, rotation, audit)
- Tool verification ledger (intended vs. actual action)
- Audit trails
- Evidence pack assembly
- AI risk controls (NIST AI RMF, OWASP LLM Top 10)

Agent-level guardrails (e.g., SDK guardrails) are additive, not a replacement for this plane.

### D. Data Plane

**What lives here**: operational source of truth, semantic metrics, lineage, document intelligence.

**Built on**:
- PostgreSQL (operational source of truth)
- pgvector (semantic search near data)
- Connector facade (versioned) — all external integrations flow through this
- Semantic metrics layer (dbt-style semantic layer)
- Lineage/quality (OpenLineage or OpenMetadata — pick one)
- Document parsing pipeline
- Event store (structured, CloudEvents-compatible)

### E. Operating Plane

**What lives here**: the product AS a living system — repo governance, CI/CD, releases, environments, rollback, provenance, SDLC security, runbooks, incident response.

**Built on**:
- GitHub rulesets (required reviews, status checks, linear history)
- GitHub environments (dev → staging → canary → prod) with deployment gates
- OIDC to cloud providers (no long-lived secrets)
- Artifact attestations (cryptographic provenance)
- Pre-commit (gitleaks, detect-secrets, ruff, mypy, bandit, hadolint)
- Structured runbooks for every P0/P1 incident

---

## 3. The ten constitutional principles

1. **No agent makes an external commitment directly.** External commitments flow only through the Execution Plane after Trust Plane approval.
2. **Every important decision emits an evidence pack.**
3. **Every sensitive action passes through policy + approval + audit.**
4. **Every critical output is structured and validated against a schema.**
5. **Every event carries a contract version + traceability IDs.**
6. **Every integration goes through a versioned facade — no direct vendor SDK calls from prompts or workflows.**
7. **Every claim in docs / README / deck is evidence-backed.** No-overclaim register is enforced.
8. **Executive Arabic is part of the system, not a translation layer.** Board-grade wording, Gulf business register.
9. **The design is PDPL/NCA-aligned from day one**, not retrofitted.
10. **Observability is part of runtime, not a later phase.** Traces link decision → execution.

---

## 4. Agent operating model

### 4.1 Classification (mandatory on every agent)

Every agent is explicitly one of:
- **Observer** — read-only sensing, no recommendations leaving the system
- **Recommender** — produces structured recommendations with evidence, no execution
- **Executor-through-workflow-only** — triggers deterministic workflows; never calls sensitive tools directly

There is **no** unconstrained "Executor" that talks to sensitive systems on its own.

### 4.2 The four agent families

1. **Sensing & Discovery** — intake, enrichment, signal detection
2. **Decision & Analysis** — ICP match, pain extraction, sector intel, market research, scenario analysis
3. **Execution** — (thin wrappers that hand off to workflows) booking, proposal, CRM sync, content distribution
4. **Trust & Learning** — policy gates, tool verification, evidence packers, eval harness

### 4.3 The rule

- **Agents** = inference + recommendation
- **Workflows** = state transitions + commitments
- **Policies** = allow / deny / escalate
- **Human approvals** = financial, legal, brand-sensitive gates

---

## 5. Contracts

### 5.1 Decision Output Contract

Every critical decision emits a JSON document matching `dealix.contracts.decision.DecisionOutput`:

```json
{
  "decision_id": "uuid",
  "tenant_id": "...",
  "entity_id": "...",
  "objective": "qualify_lead | recommend_proposal | select_target | ...",
  "recommendation": {...},
  "confidence": 0.0-1.0,
  "rationale": "why",
  "evidence": [{ "source": "...", "uri": "...", "excerpt": "...", "hash": "..." }],
  "freshness_window_hours": 24,
  "approval_class": "A0|A1|A2|A3",
  "reversibility_class": "R0|R1|R2|R3",
  "sensitivity_class": "S0|S1|S2|S3",
  "next_actions": [...],
  "policy_requirements": [...],
  "trace_id": "...",
  "agent_name": "...",
  "schema_version": "1.0",
  "created_at": "ISO 8601"
}
```

### 5.2 Event Envelope Contract (CloudEvents 1.0 + extensions)

Every event carries:
- `event_id`, `event_type`, `spec_version` (CloudEvents), `schema_version`
- `tenant_id`, `entity_id`
- `correlation_id`, `causation_id`
- `source`, `actor_type` (`system|agent|human`)
- `approval_class`, `sensitivity_class`, `reversibility_class`
- `trace_id`, `span_id`
- `timestamp` (ISO 8601)
- `data` (payload conforming to a registered `data_schema`)

### 5.3 Evidence Pack Specification

Every Tier-A/B decision has an assembled evidence pack containing:
- decision metadata (pointer to `decision_id`)
- source list with URIs, excerpts, retrieval timestamps, content hashes
- prompt templates used
- model/version used
- tool calls made (intended → actual)
- data freshness
- reviewer (if human in the loop)
- produced memo in Arabic + English

### 5.4 Audit Log Contract

Every Trust-Plane decision (policy evaluation, approval, action) is appended as immutable `AuditEntry`.

---

## 6. Mandatory classifications on every action

### 6.1 Approval Class

- **A0** — no approval (routine, reversible, non-sensitive)
- **A1** — team / manager
- **A2** — department head + legal/finance
- **A3** — executive / board

### 6.2 Reversibility Class

- **R0** — auto-reversible (e.g. a draft email)
- **R1** — reversible with limited ops (e.g. a CRM update)
- **R2** — costly to reverse (e.g. a sent proposal)
- **R3** — irreversible / external commitment (e.g. a signed NDA, a price quote sent to a regulator)

### 6.3 Sensitivity Class

- **S0** — public
- **S1** — internal
- **S2** — confidential / commercial
- **S3** — regulated / board / personal data

**Every event, decision, and action carries all three.** They are encoded in the event envelope and feed policy evaluation directly.

---

## 7. Actions that are NEVER auto-executed

These always require: `recommendation → evidence pack → policy eval → approval request → deterministic execution`:

- Pricing offer
- Contract change
- NDA, MOU, exclusivity clauses
- Payment terms
- Any external commitment
- Market-facing statement (press, LinkedIn posts under corporate identity)
- Sensitive data export
- Access grant to a strategic room (e.g. M&A data room)
- Communication with regulators
- Changes to a customer's system of record

---

## 8. Trust Fabric (condensed)

| Component | Responsibility | Implementation |
|---|---|---|
| Policy | allow / deny / escalate decisions | OPA/Rego (or local policy service) in `dealix.trust.policy` |
| Authorization | fine-grained access to rooms, memos, data | OpenFGA (Phase 2); permission stub (Phase 0–1) |
| Identity | SSO, federation, roles | Keycloak (Phase 2); local user model (Phase 0–1) |
| Secrets | rotation, dynamic, audit | HashiCorp Vault (Phase 2); `.env` + SecretStr (Phase 0–1) |
| Tool verification | intended vs actual action ledger | `dealix.trust.tool_verification` |
| Audit | immutable action log | `dealix.trust.audit` → Postgres `audit_log` table |
| Evidence pack assembly | bundle decision + sources + tool calls | `dealix.contracts.evidence_pack.Assembler` |

---

## 9. Data Plane (condensed)

- **Operational DB**: PostgreSQL 16
- **Vector search**: pgvector (managed as a production component — track CVEs and upgrade)
- **Event store**: structured CloudEvents in `events` table
- **Connector facade**: `dealix.data.connector_facade` — versioned, with timeout/retry/idempotency/approval/audit mapping for every integration
- **Semantic metrics**: `dealix.data.semantic_metrics` (dbt-style definitions as code)
- **Lineage**: OpenLineage emitters from workflow runs (Phase 2)
- **Validation**: Great Expectations checkpoints on critical datasets (Phase 2)
- **Ingestion**: Airbyte (Phase 2 for managed connectors)

---

## 10. Observability & Evaluation

### What we emit
- OpenTelemetry traces (HTTP spans, agent spans, LLM generations, tool calls, workflow activities, policy evals)
- Structured JSON logs (structlog)
- Metrics: latency/workflow, tokens/task, tool failure rate, approval lag, override rate, cost/closed-opportunity, forecast-vs-actual, hallucination/contradiction incidents, unsafe-action blocks, evidence-completeness rate

### Tracing rules
- Every Decision → Trace ID
- Every Event → Trace + Span IDs
- Every Workflow Activity → propagated Trace
- Every LLM call → `gen_ai.*` semantic conventions
- Every Tool call → `tool.name`, `tool.intended_action`, `tool.actual_action`

---

## 11. Operating Plane (condensed)

### GitHub
- **Rulesets** on `main` and `release/*`: required reviews, required status checks, linear history, CODEOWNERS, conversation resolution, no direct push
- **Environments**: `dev`, `staging`, `canary`, `prod` — with required reviewers where plan supports it
- **OIDC** to cloud providers — no long-lived secrets in Actions
- **Artifact attestations** on every release (requires GitHub Enterprise Cloud for private repos)
- **CODEOWNERS** — security-critical paths owned by security-aware maintainers

### CI/CD
- `security` job blocks everything if secrets leak (gitleaks + detect-secrets + trufflehog)
- `lint + type-check` job
- `test` job (matrix: Python 3.11, 3.12)
- `docker build` sanity job
- `release` workflow on `v*.*.*` tags: GitHub Release + GHCR image push

---

## 12. Saudi Tier-1 readiness

### PDPL
Data lifecycle controls, baked in from day one:
- Data inventory + lawful basis register (`dealix/registers/compliance_saudi.yaml`)
- Purpose register
- Retention schedule
- Breach response workflow
- Consent/notice controls where applicable
- Controller/processor map
- DPO applicability assessment
- Platform registration assessment (SDAIA) for qualifying controllers

### NCA alignment
Designed to be mappable to:
- **ECC 2-2024** (Essential Cybersecurity Controls)
- **DCC-1:2022** (Data Cybersecurity Controls)
- **CCC 2:2024** (Cloud Cybersecurity Controls)

### AI governance
- NIST AI RMF 1.0 applied
- NIST AI RMF Playbook used as reference
- OWASP Top 10 for LLM Applications integrated into eval harness

See [`dealix/registers/compliance_saudi.yaml`](../../dealix/registers/compliance_saudi.yaml) for the full mapped register.

---

## 13. Executive UX

### Executive Room screens

1. **Executive Overview** — "what changed this week", "what matters now"
2. **Sovereign Weekly Report** — board-grade briefing
3. **Alerts & Approvals** — pending gates with evidence packs
4. **Opportunity Graph** — strategic view of prospects/partners/targets
5. **Deal / Partner Room** — per-entity state + history + people
6. **KPI & Forecast Board** — semantic metrics, forecast vs actual
7. **Evidence Pack Viewer** — read-only, for diligence and audit
8. **Audit & Policy Log** — immutable record, filterable

### Language

Arabic is a first-class output surface:
- Board-grade wording
- Gulf business register (not MSA of a news article)
- Arabic negotiation modes (formal/neutral/firm)
- Bilingual exports side-by-side
- Consistent terminology via a maintained glossary

---

## 14. The twelve Master Documents

All live under `dealix/masters/`:

1. Master Architecture Blueprint (this document)
2. AI Operating Constitution → `constitution.md`
3. Trust Fabric Specification → `trust_fabric_spec.md`
4. Execution Fabric Specification → `execution_fabric_spec.md`
5. Repo Operating Pack → `repo_operating_pack.md`
6. 90-Day Execution Matrix → `../registers/90_day_execution.yaml`
7. Saudi Compliance Register → `../registers/compliance_saudi.yaml`
8. Technology Radar → `../registers/technology_radar.yaml`
9. Incident & Rollback Runbook → `incident_rollback_runbook.md`
10. Release Readiness Checklist → `release_readiness_checklist.md`
11. No-Overclaim Register → `../registers/no_overclaim.yaml`
12. Evidence Pack Specification → `evidence_pack_spec.md`

---

## 15. Definition of Done

Dealix is **not considered enterprise-ready** until:

- [ ] Every claim in README / deck / docs is evidence-backed (no-overclaim register enforced)
- [ ] Every critical flow has an owner + SLA + rollback
- [ ] Every integration has timeout / retry / idempotency / health checks
- [ ] Every critical output is structured and evaluated
- [ ] Every approval path is documented and auditable
- [ ] Every release has provenance and rollback
- [ ] Every secret lifecycle is managed
- [ ] Every trace links decision → execution
- [ ] Every data class has retention / visibility / export rules
- [ ] Every P0/P1 incident has a runbook
- [ ] Every feature is classified: Planned / Pilot / Partial / Production

Current status: see [`dealix/registers/no_overclaim.yaml`](../../dealix/registers/no_overclaim.yaml).

---

## 16. Technology Adoption Policy

### Official Now (Phase 0–1)

- OpenAI Responses API (or Anthropic with Structured Outputs via strict prompts)
- Structured Outputs / JSON Schema
- FastAPI + Pydantic v2
- PostgreSQL 16 + pgvector
- MCP / connectors where useful
- LangGraph-style stateful flow (via the `AcquisitionPipeline` orchestrator)
- CloudEvents envelope (`dealix/contracts`)
- AsyncAPI for documenting event channels
- OpenTelemetry baseline
- GitHub rulesets + OIDC
- PDPL / NCA / NIST / OWASP registers

### Strong Optional (Phase 1–2)

- OpenFGA (fine-grained authorization)
- Keycloak (identity)
- HashiCorp Vault (secrets)
- Airbyte (ingestion)
- Great Expectations (validation)
- OpenLineage or OpenMetadata (pick one)
- dbt semantic layer

### Pilot Only (Phase 2+)

- Temporal — single spike on one high-risk long workflow before rollout
- Advanced graph DB — only after proof of need
- Experimental memory systems — only behind benchmarks
- Local model runtime — only behind adapter + eval gates

See [`dealix/registers/technology_radar.yaml`](../../dealix/registers/technology_radar.yaml).

---

## 17. 90-Day Strategic Execution Plan

### Phase 0 — Days 0–30: Control plane first
Lock down contracts, classifications, policy skeleton, audit trail, OTel baseline, GitHub hygiene, compliance register, executive-room wireframe.

### Phase 1 — Days 31–60: Revenue + Partnership controlled MVP
Ship qualification/triage with Decision Outputs, evidence packs v1, approval center v1, connector facade v1, alerts/approvals UX, KPI semantic definitions, forecast vs actual board, data validation checkpoints.

### Phase 2 — Days 61–90: Enterprise readiness lift
Fine-grained authorization pilot, secrets hardening, provenance/attestations on releases, integration health center, incident/rollback runbooks, policy coverage expansion, eval harness in CI, Temporal spike on one critical workflow.

Full matrix: [`dealix/registers/90_day_execution.yaml`](../../dealix/registers/90_day_execution.yaml).

---

## 18. Day-One priorities (what to do immediately)

1. Adopt this blueprint as the single source of truth.
2. Populate the no-overclaim register and review every public claim.
3. Enforce Decision Output Contract on every critical agent output.
4. Unify the event envelope and trace IDs across the whole stack.
5. Turn on the OpenTelemetry baseline and link decision → execution.
6. Activate GitHub rulesets + OIDC before any further feature expansion.
7. Build the Saudi Compliance Register (don't leave compliance as a vague idea).
8. Isolate all integrations behind the versioned connector facade.
9. Build the Approval Center early — not after launch.
10. Postpone any large expansion in agent count until the trust fabric is solid.

---

**End of blueprint.**

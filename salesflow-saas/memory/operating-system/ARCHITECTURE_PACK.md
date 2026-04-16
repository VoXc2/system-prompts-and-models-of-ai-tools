# Dealix Sovereign OS Architecture Pack

**Version**: 1.0  
**Status**: Active  
**Type**: Implementation architecture (current-to-target)

---

## 1) Architecture Goal

Operationalize Dealix as:

- Decision Fabric
- Execution Fabric
- Trust Fabric
- Enterprise Delivery Fabric

The architecture must produce typed, governed, durable outcomes across revenue, partnerships, M&A, expansion, and PMI.

---

## 2) Plane-by-Plane Build

## Decision Plane

**Target Components**
- Responses API runtime facade
- Structured output validators (JSON schema strict mode)
- Tool/MCP adapter layer
- Guardrail middleware for sensitive actions
- Trace bridge to OTel

**Current Baseline**
- FastAPI services + agent orchestration + model router

**Required Additions**
- Decision contract registry (`decision_type -> schema`)
- Unified tool call envelope (`tool_name`, `policy_context`, `receipt_ref`)
- Run-level approval metadata injection

---

## Execution Plane

**Target Components**
- Durable workflow runtime (Temporal target)
- Workflow commitment store
- Interrupt/resume checkpoints for approvals
- SLA timers and escalation transitions

**Current Baseline**
- Celery workers + task queue + async services

**Required Additions**
- Long-running flow taxonomy (durable vs short-lived)
- Idempotency keys for cross-system writes
- Deterministic retry profiles per workflow type

---

## Trust Plane

**Target Components**
- OPA policy decision point
- OpenFGA authorization relationships
- Vault-backed secret operations
- Keycloak SSO / identity broker
- Tool verification ledger + evidence pack store

**Current Baseline**
- Consent and compliance services, tenant/RBAC controls

**Required Additions**
- Standardized approval classes (`A0-A3`)
- Reversibility classes (`R0-R3`)
- Sensitivity classes (`S0-S3`)
- Policy decision logs bound to trace IDs

---

## Data Plane

**Target Components**
- Postgres operational source of truth
- pgvector semantic memory near operational data
- Governed connector ingestion (Airbyte-style model)
- Document extraction for contracts/DD packs
- Event contract layer (CloudEvents + JSON Schema + AsyncAPI)
- Data quality checkpoints

**Current Baseline**
- Postgres + domain services + AI/knowledge services

**Required Additions**
- Event schema repository and compatibility checks
- Data quality gate per critical pipeline
- Semantic metrics contract for board/executive views

---

## Operating Plane

**Target Components**
- Protected branches + required checks + code owners
- Environment protections and release gates
- OIDC-based cloud auth from CI
- Artifact attestations/provenance
- Externalized audit stream

**Current Baseline**
- CI workflow and basic deployment docs

**Required Additions**
- Ruleset-as-policy checklist in release pipeline
- Release readiness dashboard and gate status endpoint
- Provenance metadata attachment per deploy artifact

---

## 3) Mandatory Metadata Envelope

All critical requests must include:

- `tenant_id`
- `trace_id`
- `correlation_id`
- `approval_class`
- `reversibility_class`
- `sensitivity_class`
- `policy_refs`
- `evidence_pack_id`

Missing any required field must fail closed.

---

## 4) Build Sequence (Waves)

### Wave 1: Governance Typing
- Introduce schemas for approval, workflow commitments, tool receipts.
- Enforce schema validation at request boundaries.

### Wave 2: Trust + Observability
- Attach policy/auth decisions to all sensitive tool calls.
- Add trace correlation across API, agents, workflows, and dashboards.

### Wave 3: Durable Execution
- Move long-lived commitments to durable runtime patterns.
- Add resumable checkpoints for all approval-dependent flows.

### Wave 4: Executive Surfaces
- Activate executive, approval, risk, and forecast surfaces with evidence linkage.
- Publish model routing and connector health dashboards.

---

## 5) Definition of Enterprise-Ready

Dealix is enterprise-ready only when:

1. Critical decisions are typed and evidence-backed.
2. Long commitments are durable and resumable.
3. Sensitive actions are approval and policy gated.
4. Connector operations are versioned, auditable, and idempotent.
5. Releases are gated, attestable, and traceable.
6. Executive surfaces show financial impact, risks, alternatives, and accountable owners.


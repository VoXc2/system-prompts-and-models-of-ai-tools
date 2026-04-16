# Dealix Sovereign Growth, Execution & Governance OS

**Version**: 1.0  
**Status**: Active  
**Scope**: Enterprise operating model (Saudi-first, bilingual, policy-native)

---

## 1) Operating Mandate

Dealix is not a chat-first CRM. Dealix is a sovereign operating system for:

- Revenue execution
- Partnership execution
- M&A / corporate development execution
- Market expansion execution
- PMI / strategic PMO execution
- Executive and board decisioning

Every business-critical action must be:

1. Structured (typed)
2. Evidence-backed
3. Approval-aware
4. Traceable
5. Durable when long-running

---

## 2) Five-Plane Enterprise Architecture

### Decision Plane
- Runtime: Responses API + Structured Outputs + function calling + MCP tools
- Responsibilities:
  - Produce typed decisions (`decision_payload`)
  - Route to tools via governed connectors
  - Attach `trace_id`, `correlation_id`, and evidence references
  - Enforce guardrails before side effects

### Execution Plane
- Runtime: Temporal (target), Celery/LangGraph for short-lived flows
- Responsibilities:
  - Execute durable workflows that survive retries/crashes/restarts
  - Track workflow commitments (SLA, owner, due date, escalation path)
  - Resume safely after interruptions

### Trust Plane
- Runtime: OPA + OpenFGA + Vault + Keycloak + verification ledger
- Responsibilities:
  - Policy decisions and authorization checks
  - Secret lifecycle and auditability
  - Approval metadata and reversibility control
  - Evidence pack generation for audits and boards

### Data Plane
- Runtime: Postgres + pgvector + Airbyte + Unstructured + OTel
- Responsibilities:
  - Operational truth + semantic memory near truth
  - Document extraction for contracts/CIM/DD artifacts
  - Event contracts (CloudEvents + JSON Schema + AsyncAPI)
  - Data quality gates and semantic metric definitions

### Operating Plane
- Runtime: GitHub rulesets + protected branches + environments + provenance
- Responsibilities:
  - Enforced release gates and deployment protection
  - OIDC federation and ephemeral credentials
  - Artifact attestations and external audit streaming
  - Repo-level governance and release readiness signals

---

## 3) Automation Doctrine

### Fully Automated (Low-risk, reversible, high-volume)
- Capture, enrichment, scoring, routing
- Follow-ups and reminders
- Memo drafting and evidence-pack assembly
- Checklist/task orchestration
- Connector sync and variance detection
- Telemetry, anomaly alerts, and quality checks

### Automated With Mandatory Approval Gate (Irreversible or sensitive)
- Sending term sheets
- Signature requests and final commercial commitments
- Non-standard discount approvals
- M&A offer submissions
- Strategic partner activation with external commitments
- New market launch go/no-go
- Production rollout of sensitive workflows
- High-sensitivity data sharing

---

## 4) Approval Metadata Standard

Each sensitive action MUST carry:

- `approval_class`: `A0` | `A1` | `A2` | `A3`
- `reversibility_class`: `R0` | `R1` | `R2` | `R3`
- `sensitivity_class`: `S0` | `S1` | `S2` | `S3`
- `policy_refs`: list of policy IDs (PDPL/NCA/internal policy IDs)
- `evidence_pack_id`: immutable evidence bundle identifier

### Class Meaning
- `A0`: no approval required
- `A1`: team lead approval
- `A2`: function head / delegated authority approval
- `A3`: executive or board-level approval

- `R0`: fully reversible
- `R1`: reversible with low cost
- `R2`: difficult-to-reverse commitment
- `R3`: effectively irreversible external commitment

- `S0`: non-sensitive
- `S1`: internal-sensitive
- `S2`: regulated/contractual sensitive
- `S3`: high-criticality data or fiduciary exposure

---

## 5) Mandatory Live Surfaces

Dealix enterprise readiness requires these live surfaces:

1. Executive Room
2. Approval Center
3. Evidence Pack Viewer
4. Partner Room
5. DD Room
6. Risk Board
7. Policy Violations Board
8. Actual vs Forecast Dashboard
9. Revenue Funnel Control Center
10. Partnership Scorecards
11. M&A Pipeline Board
12. Expansion Launch Console
13. PMI 30/60/90 Engine
14. Tool Verification Ledger
15. Connector Health Board
16. Release Gate Dashboard
17. Saudi Compliance Matrix
18. Model Routing Dashboard

Live status tracking is defined in `LIVE_SURFACES_TRACKER.md`.

---

## 6) Output Contract for Business-Critical Decisions

Every business-critical decision payload MUST include:

- `decision_id`
- `tenant_id`
- `domain` (`sales`, `partnership`, `mna`, `expansion`, `pmi`, `executive`)
- `decision_type`
- `recommended_action`
- `alternatives`
- `financial_impact`
- `risk_assessment`
- `approval_metadata`
- `evidence_refs`
- `workflow_commitment_ref` (if long-running)
- `trace_context` (`trace_id`, `correlation_id`)

---

## 7) Operating Rules (Non-Negotiable)

1. No external commitment without explicit policy/approval result.
2. No sensitive tool call without authorization + verification ledger receipt.
3. No long-running commitment without durable workflow identity.
4. No executive memo without evidence links and timestamped assumptions.
5. No production release without release gates and provenance attestations.
6. No AI-assisted surface without observability and security controls.

---

## 8) Implementation Pack

This prompt is implemented by:

- `ARCHITECTURE_PACK.md`
- `EXECUTION_MATRIX.md`
- `WEEKLY_OPERATING_SYSTEM.md`
- `LIVE_SURFACES_TRACKER.md`
- `../contracts/approval_request.schema.json`
- `../contracts/workflow_commitment.schema.json`
- `../contracts/tool_verification_receipt.schema.json`


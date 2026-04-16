# Architecture Overview

## Purpose

This document distinguishes between:
- the **current operating architecture** running Dealix today, and
- the **target sovereign architecture** required for Dealix to become a true enterprise growth operating system.

The target state is not "more agents". It is a controlled split between:
- decision,
- execution,
- trust,
- data, and
- operating controls.

---

## 1) Current Operating Architecture

```
                         +------------------+
                         |   Client / App   |
                         | (Browser/Mobile) |
                         +--------+---------+
                                  |
                             HTTPS (443)
                                  |
                         +--------+---------+
                         |      Nginx       |
                         | (Reverse Proxy)  |
                         +---+---------+----+
                             |         |
                    /api/*   |         |  /*
                             |         |
               +-------------+    +----+-----------+
               |   FastAPI   |    |    Next.js     |
               |   Backend   |    |    Frontend    |
               |   :8000     |    |    :3000       |
               +--+-----+----+    +----------------+
                  |     |
         +--------+     +--------+
         |                       |
 +-------+--------+    +--------+-------+
 | PostgreSQL 16  |    |    Redis 7     |
 | Source of Truth|    | Cache / Broker  |
 +----------------+    +-------+--------+
                               |
                       +-------+--------+
                       |  Celery Workers |
                       |  + Celery Beat  |
                       +----------------+
```

### Current-state characteristics
- `Next.js` serves the product surfaces and public assets.
- `FastAPI` owns API orchestration, business logic, and integrations.
- `PostgreSQL` is the operational source of truth.
- `Redis + Celery` provide async processing, retries, and scheduled work.
- AI orchestration exists, but durable workflow boundaries and trust boundaries are still evolving.

---

## 2) Multi-Tenant Isolation Model

```
Request --> Auth Middleware --> Extract tenant_id from JWT
               |
               v
       Query scoping: WHERE tenant_id = :tid
               |
               v
       All reads/writes isolated per tenant
```

- Every tenant-scoped table includes `tenant_id`.
- Request auth extracts tenant context from JWT.
- ORM-layer query scoping blocks cross-tenant access by default.
- Elevated access must remain explicit, auditable, and policy-controlled.

---

## 3) Current Agentic Runtime Boundary

```
Incoming Event
    |
    v
+------------------+
| Agent Router     |
+------------------+
    |
    v
+------------------+     +----------------------+
| Agent Executor   | --> | LLM Provider / Tools |
| (app + workers)  |     +----------------------+
+------------------+
    |
    v
+------------------+
| Action Handler   |
+------------------+
    |
    v
DB updates / notifications / escalations / follow-up tasks
```

### Limitation of the current boundary
This shape is good enough for short-lived orchestration, but it is not yet sufficient for:
- long-running business commitments,
- pause/resume approvals,
- external side-effect verification,
- irreversible actions,
- audit-grade contradiction detection.

---

## 4) Target Sovereign Architecture

```
                    +--------------------------------------+
                    |        Executive / Product UI        |
                    | Rooms, boards, approvals, evidence   |
                    +------------------+-------------------+
                                       |
                +----------------------+----------------------+
                |                                             |
                v                                             v
    +--------------------------+                 +--------------------------+
    |      Decision Plane      |                 |      Trust Plane         |
    | Responses API            |                 | OPA                      |
    | Structured Outputs       |                 | OpenFGA                  |
    | LangGraph                |                 | Vault                    |
    | MCP / function calling   |                 | Keycloak                 |
    +------------+-------------+                 +------------+-------------+
                 |                                            |
                 +-------------------+------------------------+
                                     |
                                     v
                         +--------------------------+
                         |     Execution Plane      |
                         | LangGraph (short loops)  |
                         | Temporal (durable work)  |
                         +------------+-------------+
                                      |
                                      v
                         +--------------------------+
                         |       Data Plane         |
                         | Postgres + pgvector      |
                         | Airbyte + Unstructured   |
                         | GE + CloudEvents         |
                         | OTel                     |
                         +------------+-------------+
                                      |
                                      v
                         +--------------------------+
                         |    Operating Plane       |
                         | GitHub rulesets          |
                         | Environments + OIDC      |
                         | Attestations + evidence  |
                         +--------------------------+
```

---

## 5) Plane Responsibilities

| Plane | Responsibility | Must own | Must not own |
|-------|----------------|----------|--------------|
| Decision | analysis and recommendation | signals, triage, scenarios, memos, forecasting, next best action | durable commitments and unmanaged side effects |
| Execution | deterministic business execution | retries, timeouts, approvals, compensation, resumption | free-form reasoning as the source of truth |
| Trust | policy and verification | authn, authz, secrets, policy checks, audit, contradiction detection | business logic shortcuts embedded in app code only |
| Data | governed operational and semantic data | contracts, quality, freshness, metrics, traces | ad hoc vendor-shaped schemas |
| Operating | SDLC and release trust | environments, checks, provenance, deployment protection | release-by-convention without evidence |

---

## 6) Runtime Split: LangGraph vs Temporal

### LangGraph is the right boundary for
- stateful reasoning loops
- interrupts / HITL
- memo generation
- evidence assembly
- short to medium orchestration

### Temporal is the right boundary for
- approval workflows
- signature requests
- DD room lifecycle
- partner activation
- market launch orchestration
- PMI 30/60/90 execution
- any business commitment that must survive crashes or outages

### Rule
If a workflow:
- lasts beyond a short interaction,
- crosses systems,
- creates an external commitment, or
- needs compensation,

then it belongs in the durable execution boundary, not inside agent reasoning.

---

## 7) Trust Plane Components

| Component | Role in target architecture |
|-----------|-----------------------------|
| `OPA` | policy decisions for sensitive actions, approvals, and release gates |
| `OpenFGA` | fine-grained relationship-based authorization for rooms, memos, approvals, and boards |
| `Vault` | secrets, rotation, dynamic credentials, auditability |
| `Keycloak` | SSO, identity brokering, enterprise IAM |

### Trust metadata required on sensitive actions
- `authorized_actor`
- `approval_class`
- `reversibility_class`
- `sensitivity`
- `policy_result`
- `tool_trace_id`
- `verification_status`
- `audit_record_id`

---

## 8) Data Plane Contracts

### Core systems
- `Postgres` remains the operational source of truth.
- `pgvector` stores semantic memory close to operational context.
- `Airbyte` standardizes ingestion and connector sync.
- `Unstructured` extracts structured elements from raw documents.
- `Great Expectations` enforces data quality checkpoints.
- `CloudEvents`, `JSON Schema`, and `AsyncAPI` define event contracts.
- `OpenTelemetry` provides traces, metrics, and logs.

### Required cross-cutting metadata
Every critical event, decision, and workflow should carry:
- `tenant_id`
- `correlation_id`
- `schema_version`
- `approval_class`
- `reversibility_class`
- `sensitivity`
- `provenance`
- `freshness`
- `confidence`

---

## 9) Operating Plane Controls

### Repository and release controls
- protected branches
- rulesets
- `CODEOWNERS`
- required status checks
- environment protections
- deployment reviewers where needed
- OIDC federation instead of long-lived CI secrets
- artifact attestations and provenance
- external audit-log export for audit-grade retention

### Release principle
No enterprise-grade deployment should rely on trust-by-convention. It must be:
- reviewed,
- attributable,
- reproducible,
- and auditable.

---

## 10) Connector Boundary

Dealix should not allow direct agent-to-vendor coupling at scale.

Every connector facade should define:
- contract
- version
- retry policy
- timeout policy
- idempotency key strategy
- approval policy
- audit mapping
- telemetry mapping
- rollback or compensation notes

This is the control point that keeps vendor API drift from breaking product semantics.

---

## 11) Mandatory Product Surfaces for the Target State

The architecture is incomplete if these surfaces do not exist in live form:
- Executive Room
- Approval Center
- Evidence Pack Viewer
- Partner Room
- DD Room
- Risk Board
- Policy Violations Board
- Actual vs Forecast Dashboard
- Revenue Funnel Control Center
- Partnership Scorecards
- M&A Pipeline Board
- Expansion Launch Console
- PMI 30/60/90 Engine
- Tool Verification Ledger
- Connector Health Board
- Release Gate Dashboard
- Saudi Compliance Matrix
- Model Routing Dashboard

---

## 12) Architecture Principles

1. **Decision is typed.** Recommendations must be schema-bound and evidence-backed.
2. **Execution is durable.** Long-running commitments must survive crashes and resumes.
3. **Trust is externalized.** Authorization, policy, and secret governance should not live only inside app conditionals.
4. **Data is contracted.** Events, syncs, and documents must follow explicit schemas and quality gates.
5. **Operations are evidenced.** Releases, approvals, and side effects must be provable after the fact.
6. **Arabic-first is architectural.** It is not a copy layer; it affects retrieval, executive reporting, approvals, and terminology normalization.

---

## 13) Summary

The current stack is a strong operating base.
The sovereign target state adds the missing enterprise-grade boundaries:
- typed decisions,
- durable execution,
- enforced trust,
- governed data,
- and audit-grade operating controls.

That is the architectural path from "AI-enhanced CRM" to "Sovereign Enterprise Growth OS".

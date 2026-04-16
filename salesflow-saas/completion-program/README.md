# Dealix Completion Program

> **Status:** Active — Started 2026-04-16
> **Goal:** Close the gap between documentation and operational capability. Transform Dealix from strong blueprints into enterprise-grade production: Decision Fabric + Execution Fabric + Trust Fabric + Enterprise Delivery Fabric.

---

## Structure

```
completion-program/
├── README.md                          ← This file (program index)
├── EXECUTION_MATRIX_FINAL.md          ← Master matrix: 8 workstreams × all columns
├── ARCHITECTURE_REGISTER.md           ← Current vs Target for 5 planes, 6 tracks
│
├── decision-plane/
│   ├── agent-role-registry.md         ← Observer / Recommender / Executor registry
│   └── schemas/
│       ├── memo.schema.json           ← Decision memo (bilingual)
│       ├── evidence_pack.schema.json  ← Evidence pack with tool verification
│       ├── risk_register.schema.json  ← Risk register
│       ├── approval_packet.schema.json ← HITL approval packet
│       └── execution_intent.schema.json ← Typed execution intent for workers
│
├── execution-plane/
│   └── workflow-inventory.md          ← All workflows classified + Temporal pilot plan
│
├── trust-plane/
│   └── policy-inventory.md            ← OPA packs, OpenFGA model, tool verification ledger
│
├── data-plane/
│   ├── connector-facade-standard.md   ← Base connector class + versioning + CloudEvents
│   └── semantic-metrics.md            ← 30+ KPIs with formulas, grain, source, owner
│
├── operating-plane/
│   └── enterprise-delivery.md         ← CODEOWNERS, rulesets, OIDC, attestations, canary, SIEM
│
├── saudi-governance/
│   ├── pdpl-classification-matrix.md  ← Data classification + consent + DSAR SLAs
│   ├── nca-ecc-readiness.md           ← ECC 2-2024 gap register (32 controls)
│   ├── ai-governance-nist-rmf.md      ← NIST AI RMF mapping + OWASP LLM Top 10
│   └── owasp-llm-checklist.md         ← Per-release sign-off checklist
│
└── observability/
    └── otel-standard.md               ← OTel traces/metrics/logs + eval gates + red-team
```

---

## 8 Workstreams at a Glance

| # | Workstream | Plane | Sprint Target |
|---|-----------|-------|-------------|
| WS1 | Productization & Architecture Closure | Cross-cutting | Sprint 1 |
| WS2 | Decision Plane Hardening | Decision | Sprint 1–4 |
| WS3 | Execution Plane Hardening (Temporal) | Execution | Sprint 2–8 |
| WS4 | Trust Fabric Hardening (OPA + OpenFGA + Vault + Keycloak) | Trust | Sprint 2–5 |
| WS5 | Data & Connector Fabric | Data | Sprint 2–8 |
| WS6 | Enterprise Delivery Fabric (GitHub + SDLC) | Operating | Sprint 1–4 |
| WS7 | Saudi Enterprise Readiness (PDPL + NCA ECC + NIST AI RMF) | Trust + Operating | Sprint 1–4 |
| WS8 | Executive & Customer Readiness (dashboards, NBA, scorecards) | Operating (UX) | Sprint 4–7 |

Full detail with deliverables, owners, evidence gates, exit criteria, dependencies, risk, and SLA: **[EXECUTION_MATRIX_FINAL.md](./EXECUTION_MATRIX_FINAL.md)**

---

## Definition of Done (Binary Gates)

Dealix is enterprise-ready when **all** of the following are true:

- [ ] Every business-critical recommendation exits as `memo_json` + `evidence_pack_json` (structured, schema-validated)
- [ ] Every long-running commitment (Closing, PMI, Billing renewal) runs through Temporal durable workflow
- [ ] Every Executor-class action carries `approval_required`, `reversibility`, `sensitivity`, `provenance`, `freshness`, `confidence` metadata
- [ ] Every external connector is wrapped in a versioned `BaseConnector` facade with retry/idempotency/audit
- [ ] Every production release has GitHub rulesets + CODEOWNERS + OIDC + attestations + canary + SIEM streaming
- [ ] Every traceable surface emits OTel traces/metrics/logs with `correlation_id` and `tenant_id`
- [ ] Every release has OWASP LLM Top 10 checklist signed by AI Lead + Security Lead
- [ ] Every Saudi-sensitive workflow has PDPL classification + NCA ECC control mapping
- [ ] Architecture register shows zero subsystems with status `❌ Gap` in Trust Plane and Operating Plane

---

## Priority Sequence

```
1. Control/Trust → before more agents
2. Execution durability → before more autonomy
3. Connector facades → before more tool calls
4. Semantic metrics → before more dashboards
5. Saudi governance → before enterprise rollout
6. Executive room → before external scaling
```

---

## How to Use This Program

1. **Sprint planning:** Pull deliverables from `EXECUTION_MATRIX_FINAL.md` for the current sprint column.
2. **Architecture decisions:** Reference `ARCHITECTURE_REGISTER.md` for current/target state before building.
3. **New agent PRs:** Reference `decision-plane/agent-role-registry.md` and output against a schema in `decision-plane/schemas/`.
4. **New connector PRs:** Subclass `BaseConnector` from `data-plane/connector-facade-standard.md`.
5. **Release gate:** Run `owasp-llm-checklist.md` and get signatures before creating release branch.
6. **Compliance review:** Reference `saudi-governance/` for PDPL + NCA ECC + AI governance mapping.
7. **Observability review:** All new endpoints/agents/activities must conform to `observability/otel-standard.md`.

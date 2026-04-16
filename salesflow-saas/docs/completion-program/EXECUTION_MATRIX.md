# Dealix Execution Matrix — مصفوفة التنفيذ النهائية

**Version**: 1.0  
**Date**: 2026-04-16  
**Status**: canonical  
**Format**: Workstream → Deliverables → Owner → Evidence Gate → Exit Criteria → Dependencies → Risk → SLA  

---

## How to Read This Matrix

- **Owner**: Role responsible (not individual names — assign during sprint planning)
- **Evidence Gate**: What artifact proves the deliverable is done
- **Exit Criteria**: Binary pass/fail conditions
- **Dependencies**: Other deliverables or external factors that must be in place
- **Risk**: What can go wrong + severity (H/M/L)
- **SLA**: Target completion window from workstream kickoff

---

## WS-1: Productization & Architecture Closure (إغلاق المعمار)

**Priority**: P0 — Foundation  
**Plane**: All  
**Prerequisite for**: All other workstreams  

| # | Deliverable | Owner | Evidence Gate | Exit Criteria | Dependencies | Risk | SLA |
|---|------------|-------|--------------|---------------|-------------|------|-----|
| 1.1 | Current-vs-Target Architecture Register | Architect | Published `CURRENT_VS_TARGET_REGISTER.md` with status per subsystem | Every backend module (250+ files) has a status: `current` / `partial` / `scaffold` / `target` | Codebase audit complete | M — Disagreement on "partial" vs "scaffold" | Week 1–2 |
| 1.2 | Five Planes formal lock | Architect + CTO | ADR-003 merged to main with sign-off | Decision / Execution / Trust / Data / Operating planes defined, no ambiguity | 1.1 | L — Naming churn | Week 2 |
| 1.3 | Six Business Tracks lock | Product Lead | Track document with agent coverage map | Prospecting / Qualification / Proposal / Closing / Post-Sale / Analytics tracks defined with primary flow + agent roster | 1.1 | L | Week 2 |
| 1.4 | Agent Role taxonomy lock | AI Lead | Enum in codebase: `Observer` / `Recommender` / `Executor` with HITL rules | Every agent in `app/agents/` classified; `BaseAgent` updated with `role` field | 1.1, 1.2 | M — Agent behavior reclassification needed | Week 2–3 |
| 1.5 | Action Metadata schema lock | AI Lead | Pydantic model: `ActionMetadata` with approval / reversibility / sensitivity / provenance / freshness | Schema importable from `app/schemas/action_metadata.py`; unit tests pass | 1.4 | L | Week 3 |
| 1.6 | Module map refresh | Architect | Updated `memory/architecture/module-map.md` | All 250+ modules listed with owner + status + plane | 1.1 | L — Tedious but low risk | Week 3 |

---

## WS-2: Decision Plane Hardening (تقوية طبقة القرار)

**Priority**: P0 — Foundation  
**Plane**: Decision  
**Closes Gap**: #2  

| # | Deliverable | Owner | Evidence Gate | Exit Criteria | Dependencies | Risk | SLA |
|---|------------|-------|--------------|---------------|-------------|------|-----|
| 2.1 | Decision output schemas | AI Lead | Pydantic models: `DecisionMemo`, `EvidencePack`, `RiskRegister`, `ApprovalPacket`, `ExecutionIntent` | Models in `app/schemas/decision/`; full test coverage; JSON Schema export | WS-1.5 | M — Schema design iterations | Week 2–4 |
| 2.2 | Structured Outputs integration | AI Lead | OpenAI Responses API integration with `response_format` enforcing JSON Schema | `model_router.py` updated; critical flows produce typed outputs; fallback for non-OpenAI providers | 2.1 | H — Provider compatibility; Groq may not support structured outputs | Week 3–5 |
| 2.3 | Evidence Pack generator | AI Lead | Service class `EvidencePackGenerator` | Generates evidence packs from agent runs with source citations, confidence, freshness | 2.1 | M | Week 4–6 |
| 2.4 | Decision Memo compiler (bilingual) | AI Lead + Arabic Ops | Service class `DecisionMemoCompiler` | Produces AR/EN memos from structured decision data; tested with 5+ real scenarios | 2.1, 2.3 | M — Arabic template quality | Week 4–6 |
| 2.5 | Provenance scoring | AI Lead | Fields: `provenance_score`, `freshness_score`, `confidence_score` on every decision output | Scores computed from retrieval metadata; persisted in DB; queryable | 2.1 | L | Week 5–7 |
| 2.6 | Free-text output ban for critical flows | AI Lead + CTO | Linter/runtime check that critical agent outputs conform to decision schemas | CI check blocks non-structured outputs in designated flows | 2.2 | H — May break existing flows; needs migration period | Week 6–8 |

---

## WS-3: Execution Plane Hardening (تقوية طبقة التنفيذ)

**Priority**: P1 — Core  
**Plane**: Execution  
**Closes Gap**: #3  

| # | Deliverable | Owner | Evidence Gate | Exit Criteria | Dependencies | Risk | SLA |
|---|------------|-------|--------------|---------------|-------------|------|-----|
| 3.1 | Workflow inventory & classification | Architect | Spreadsheet/doc: every workflow → `short-lived-local` / `medium-lived-queued` / `long-lived-durable` | All 7 Celery task modules + 2 durable flows + ad-hoc service workflows classified | WS-1.1 | L | Week 3–4 |
| 3.2 | Temporal infrastructure pilot | DevOps | Temporal server running in dev (Docker); SDK integrated in backend | `docker-compose.yml` updated; `temporalio` in `requirements.txt`; health check passes | None | M — Operational complexity | Week 4–6 |
| 3.3 | First Temporal workflow: Partner Approval | Backend Lead | `partner_approval_workflow.py` in Temporal | Full lifecycle: submit → review → approve/reject → notify; checkpointed; crash-recoverable | 3.2 | H — First Temporal integration; learning curve | Week 5–8 |
| 3.4 | Compensation policy framework | Backend Lead | `CompensationPolicy` base class + first saga | Rollback logic defined for partner approval; tested with simulated failures | 3.3 | M | Week 6–8 |
| 3.5 | Idempotency key framework | Backend Lead | Middleware/decorator: `@idempotent(key_expr)` | Applied to Temporal activities + API mutations; dedup verified under retry | 3.2 | L | Week 5–7 |
| 3.6 | Workflow versioning strategy | Backend Lead + DevOps | ADR-004 merged; versioning implemented in Temporal workers | Workers handle v1→v2 workflow transitions; zero-downtime deployment tested | 3.3 | M — Temporal versioning nuances | Week 7–10 |
| 3.7 | Migration plan for remaining long-lived workflows | Architect | Prioritized backlog: workflows to migrate from Celery/OpenClaw → Temporal | At least 3 additional candidates identified with migration order | 3.1, 3.3 | L | Week 8–10 |

---

## WS-4: Trust Fabric Hardening (تقوية طبقة الثقة)

**Priority**: P1 — Core  
**Plane**: Trust  
**Closes Gap**: #4, #5  

| # | Deliverable | Owner | Evidence Gate | Exit Criteria | Dependencies | Risk | SLA |
|---|------------|-------|--------------|---------------|-------------|------|-----|
| 4.1 | Policy inventory | Security Lead | Document listing every policy decision point in codebase | `openclaw/policy.py`, `security_gate.py`, `skill_governance.py`, `outbound_governance.py`, `autopilot.py` policies catalogued | WS-1.1 | L | Week 3–4 |
| 4.2 | OPA policy packs (pilot) | Security Lead | OPA server in dev; first 5 policies ported from Python → Rego | OPA evaluates policies; Python code calls OPA via REST; tests pass | 4.1 | M — Rego learning curve | Week 5–8 |
| 4.3 | OpenFGA authorization model (draft) | Security Lead | OpenFGA model YAML with tenant/user/agent/resource tuples | Model handles: tenant isolation, agent scoped actions, user RBAC, resource permissions | 4.1 | H — Complex authorization graph design | Week 5–8 |
| 4.4 | Vault integration plan | DevOps + Security | Architecture doc + PoC for dynamic secrets | Vault running in dev; at least one secret (DB password) dynamically fetched | None | M — Infrastructure change | Week 5–7 |
| 4.5 | Keycloak SSO & service identity plan | Security Lead + DevOps | Architecture doc + Keycloak in dev with test realm | OIDC login flow working for frontend; service-to-service tokens via client credentials | None | H — Major auth migration from JWT-only | Week 6–10 |
| 4.6 | Tool verification ledger v1 | AI Lead + Security | DB table: `tool_verification_ledger` with 5 required fields per action | `intended_action`, `claimed_action`, `actual_execution`, `side_effects`, `contradiction_status` recorded for every tool execution | WS-2.1 | M | Week 6–8 |
| 4.7 | Contradiction dashboard | Frontend Lead + AI Lead | UI page showing intended vs actual execution deltas | Real-time feed from verification ledger; filterable by agent, severity, time | 4.6 | M | Week 8–10 |

---

## WS-5: Data & Connector Fabric (طبقة البيانات والموصلات)

**Priority**: P1 — Core  
**Plane**: Data  
**Closes Gap**: #6  

| # | Deliverable | Owner | Evidence Gate | Exit Criteria | Dependencies | Risk | SLA |
|---|------------|-------|--------------|---------------|-------------|------|-----|
| 5.1 | Connector facade standard | Architect | `ConnectorBase` ABC with standard interface | `send()`, `receive()`, `health()`, `version()` methods; retry/timeout/idempotency built-in | WS-1.2 | L | Week 4–5 |
| 5.2 | WhatsApp connector refactor | Backend Lead | `connectors/whatsapp.py` implementing `ConnectorBase` | Existing `integrations/whatsapp.py` + `whatsapp_plugin.py` consolidated; versioned; retry/circuit-breaker | 5.1 | M — Breaking change to existing integration | Week 5–7 |
| 5.3 | Email connector refactor | Backend Lead | `connectors/email.py` implementing `ConnectorBase` | Existing `integrations/email_sender.py` consolidated; versioned | 5.1 | L | Week 5–7 |
| 5.4 | Salesforce connector refactor | Backend Lead | `connectors/salesforce.py` implementing `ConnectorBase` | Existing `salesforce_agentforce_plugin.py` + `salesforce_agentforce.py` consolidated | 5.1 | M — Agentforce API complexity | Week 6–8 |
| 5.5 | Stripe connector refactor | Backend Lead | `connectors/stripe.py` implementing `ConnectorBase` | Existing `stripe_service.py` + `stripe_plugin.py` consolidated; idempotency keys | 5.1 | M — Payment safety critical | Week 6–8 |
| 5.6 | Event envelope standard | Architect | `EventEnvelope` Pydantic model (CloudEvents-compatible) | All inter-service events wrapped in envelope; schema validated | 5.1 | L | Week 5–6 |
| 5.7 | Schema registry discipline | Architect + Backend Lead | JSON Schema files per event type in `schemas/events/` | CI validates schemas; breaking changes require version bump | 5.6 | M | Week 6–8 |
| 5.8 | Semantic metrics dictionary | Data Lead | `docs/semantic-metrics.md` with business metric definitions | Each metric: name, definition (AR/EN), formula, source table, owner, SLO | None | L | Week 5–7 |
| 5.9 | Data quality checks (pilot) | Data Lead | Great Expectations suite for 3 critical datasets | Leads, deals, consents validated; quality report generated; CI gate | None | M — New tooling adoption | Week 7–10 |

---

## WS-6: Enterprise Delivery Fabric (نظام الإصدار المؤسسي)

**Priority**: P2 — Scale  
**Plane**: Operating  
**Closes Gap**: #7  

| # | Deliverable | Owner | Evidence Gate | Exit Criteria | Dependencies | Risk | SLA |
|---|------------|-------|--------------|---------------|-------------|------|-----|
| 6.1 | GitHub rulesets | DevOps | Rulesets active on `main` and release branches | No direct push to `main`; signed commits required on release branches | None | L | Week 4–5 |
| 6.2 | CODEOWNERS | DevOps + All Leads | `.github/CODEOWNERS` file | Every top-level directory + critical file has owner; PR auto-assigns reviewers | None | L | Week 4–5 |
| 6.3 | Required checks enforcement | DevOps | Branch protection rules | `pytest`, `lint`, `build` must pass before merge; no override without admin | 6.1 | L | Week 4–5 |
| 6.4 | Environments: dev/staging/canary/prod | DevOps | GitHub Environments configured | Each environment has: protection rules, required reviewers, wait timers, secrets | 6.1 | M — May need GitHub Enterprise for private repo features | Week 5–7 |
| 6.5 | OIDC federation | DevOps | GitHub OIDC → cloud provider (AWS/GCP) | No long-lived cloud credentials in GitHub; OIDC token exchange verified | 6.4 | M | Week 6–8 |
| 6.6 | Artifact attestations | DevOps | SLSA provenance on Docker images | `gh attestation verify` passes for production images | 6.5 | M — SLSA compliance complexity | Week 7–9 |
| 6.7 | Audit log streaming | DevOps + Security | GitHub audit logs → external SIEM/warehouse | Streaming active; retention >180 days; Git events captured | 6.4 | M — Enterprise plan requirement | Week 7–9 |
| 6.8 | OTel instrumentation | Backend Lead + DevOps | `opentelemetry-*` packages in backend | `trace_id` on every HTTP request; spans for LLM calls, DB queries, external API calls; Jaeger/Grafana Tempo in dev | None | M — Instrumentation effort across 250+ modules | Week 5–9 |
| 6.9 | Eval datasets & regression gate | AI Lead | `tests/evals/` directory with offline datasets | 50+ eval cases per critical agent; CI runs evals; regression = release blocker | WS-2.1 | H — Quality dataset creation | Week 8–12 |
| 6.10 | Red-team coverage | Security Lead | Red-team report for agent/tool surfaces | OWASP LLM Top 10 coverage; prompt injection tests; tool abuse scenarios | 4.6 | H — Requires security expertise | Week 10–14 |

---

## WS-7: Saudi Enterprise Readiness (الجاهزية المؤسسية السعودية)

**Priority**: P2 — Scale  
**Plane**: Trust + Data  
**Closes Gap**: #8  

| # | Deliverable | Owner | Evidence Gate | Exit Criteria | Dependencies | Risk | SLA |
|---|------------|-------|--------------|---------------|-------------|------|-----|
| 7.1 | PDPL data classification matrix | Compliance Lead | `SAUDI_ENTERPRISE_READINESS.md` Section A | Every data field classified: public / internal / confidential / restricted; processing purpose documented | WS-1.1 | M — Cross-team data audit | Week 4–6 |
| 7.2 | Personal data processing register | Compliance Lead | Spreadsheet/doc per PDPL Art. 29 | Activities, lawful basis, retention periods, transfer destinations documented | 7.1 | M | Week 5–7 |
| 7.3 | Residency/transfer control flags | Backend Lead + Compliance | Policy engine flags: `data_residency_region`, `transfer_allowed_destinations` | Enforced at data write + external API call layers; tested | 7.1, WS-4.2 | H — Requires policy engine integration | Week 6–9 |
| 7.4 | NCA ECC-2:2024 readiness gaps register | Security Lead | Gap analysis document | Every ECC domain mapped: current status + gap + remediation plan | None | M — Requires NCA domain expertise | Week 5–8 |
| 7.5 | AI governance profile (NIST AI RMF) | AI Lead + Compliance | Mapping document | NIST AI RMF functions (Govern/Map/Measure/Manage) → Dealix controls | None | M | Week 6–8 |
| 7.6 | OWASP LLM controls checklist | Security Lead | Per-release checklist | Top 10 risks assessed; mitigations documented; integrated into release gate | 6.10 | M | Week 8–10 |

---

## WS-8: Executive & Customer Readiness (جاهزية الإدارة والعملاء)

**Priority**: P3 — Launch  
**Plane**: All  

| # | Deliverable | Owner | Evidence Gate | Exit Criteria | Dependencies | Risk | SLA |
|---|------------|-------|--------------|---------------|-------------|------|-----|
| 8.1 | Executive Room (live dashboard) | Frontend Lead | `/dashboard/executive` page | Board-ready view: revenue, pipeline, agent performance, compliance status, risk heatmap | WS-2.4, WS-6.8 | M — Data pipeline from multiple planes | Week 10–14 |
| 8.2 | Board-ready memo view | Frontend Lead | Memo viewer component | Renders `DecisionMemo` in AR/EN with evidence links; PDF export | WS-2.4 | L | Week 10–12 |
| 8.3 | Evidence Pack viewer | Frontend Lead | Evidence pack component | Displays citations, data sources, confidence scores, freshness indicators | WS-2.3 | L | Week 10–12 |
| 8.4 | Approval Center | Frontend Lead + Backend Lead | `/dashboard/approvals` page | Pending approvals queue; approve/reject with comments; audit trail; notifications | WS-4.3 | M | Week 12–16 |
| 8.5 | Policy Violations board | Frontend Lead + Security Lead | `/dashboard/violations` page | Real-time policy violation feed from OPA; severity classification; trend charts | WS-4.2 | M | Week 12–16 |
| 8.6 | Partner scorecards | Frontend Lead | Partner scorecard component | Trust score, deal history, compliance status, revenue attribution per partner | WS-5.4 | L | Week 14–18 |
| 8.7 | Actual vs Forecast view | Frontend Lead + Data Lead | Dashboard widget | Predicted vs actual revenue overlay; confidence bands; drill-down by track | WS-2.5 | M | Week 14–18 |
| 8.8 | Risk heatmap | Frontend Lead | Dashboard widget | Risks by category × severity; clickable cells link to risk register entries | WS-2.1 | L | Week 14–16 |
| 8.9 | Next-best-action dashboard | Frontend Lead + AI Lead | Dashboard widget | Per-deal recommended actions with provenance; one-click execution triggers | WS-2.1, WS-3.3 | H — Requires full decision + execution planes | Week 16–20 |

---

## Dependency Graph — خريطة التبعيات

```
WS-1 (Architecture Closure)
 ├── WS-2 (Decision Plane)
 │    └── WS-8 (Executive Readiness) [partial]
 ├── WS-3 (Execution Plane)
 │    └── WS-8.9 (Next-best-action)
 ├── WS-4 (Trust Fabric)
 │    ├── WS-7 (Saudi Readiness) [partial]
 │    └── WS-8.4, 8.5 (Approval Center, Violations)
 ├── WS-5 (Data & Connectors)
 │    └── WS-8.6 (Partner scorecards)
 └── WS-6 (Delivery Fabric)
      ├── WS-7.6 (OWASP per release)
      └── WS-8.1 (Executive Room) [telemetry]
```

---

## Risk Register Summary — ملخص المخاطر

| Risk ID | Description | Severity | Mitigation |
|---------|-------------|----------|------------|
| R-01 | Temporal learning curve delays execution plane | H | Dedicated spike + pair programming + single pilot flow first |
| R-02 | Keycloak migration breaks existing JWT auth | H | Parallel auth during transition; feature flag for Keycloak |
| R-03 | Structured Outputs not supported by all LLM providers | H | Fallback: validate post-hoc with Pydantic; prioritize OpenAI for critical flows |
| R-04 | GitHub Enterprise required for advanced environment features | M | Evaluate GitHub Enterprise vs alternative; document minimum viable without Enterprise |
| R-05 | Red-team expertise not available in-house | H | External security partner; OWASP LLM testing guide as self-service baseline |
| R-06 | Breaking changes to existing integrations during connector refactor | M | Adapter pattern; old interface calls new facade; deprecation period |
| R-07 | NCA ECC compliance requires specialized auditor | M | Engage NCA-certified auditor; use ECC self-assessment tool first |
| R-08 | Eval dataset creation is time-intensive | H | Start with 10 cases per agent; grow incrementally; synthetic data generation |

---

## Review Cadence — إيقاع المراجعة

| Frequency | Ceremony | Participants | Artifact |
|-----------|----------|-------------|----------|
| Weekly | Workstream sync | Workstream owner + contributors | Updated deliverable statuses in this matrix |
| Bi-weekly | Cross-workstream review | All leads + CTO | Dependency check + risk re-assessment |
| Monthly | Executive review | CTO + Founder | Progress vs SLA; blocker escalation; resource allocation |
| Per release | Readiness gate | All leads | Definition of Done checklist verification |

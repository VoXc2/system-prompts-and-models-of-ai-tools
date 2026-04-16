# Dealix Completion Program — Final Execution Matrix

> **Version:** 1.0 — 2026-04-16
> **Status:** Authoritative Execution Reference
> **Owner:** Platform Engineering & GTM Leadership
> **Format:** Workstream → Deliverables → Owner → Evidence Gate → Exit Criteria → Dependencies → Risk → SLA

---

## Reading Guide

| Column | Definition |
|--------|-----------|
| **Workstream** | One of 8 closing programs mapped to the 5 operational planes |
| **Deliverables** | Specific, code/doc/config artefacts to be produced |
| **Owner** | Role accountable (not a person — assign per org chart) |
| **Evidence Gate** | Automated or manual proof required before "Done" is declared |
| **Exit Criteria** | Binary pass/fail conditions |
| **Dependencies** | Upstream workstreams or external services that must be ready first |
| **Risk** | Highest-impact risk if workstream slips |
| **SLA** | Completion target expressed in elapsed sprints (2-week sprints) |

---

## Workstream 1 — Productization & Architecture Closure

**Plane:** Cross-cutting · **Track:** All 6 business tracks

| # | Deliverable | Owner | Evidence Gate | Exit Criteria | Dependencies | Risk | SLA |
|---|------------|-------|--------------|--------------|-------------|------|-----|
| 1.1 | `ARCHITECTURE_REGISTER.md` — current-vs-target for all 5 planes, all subsystems tagged Current / Partial / Pilot / Production | Platform Architect | Register reviewed by all plane owners and merged to `main` | Zero subsystems with ambiguous status | None — first deliverable | No shared map → duplicated or contradictory work across teams | Sprint 1 |
| 1.2 | Plane lock documents: Decision, Execution, Trust, Data, Operating — each with locked scope, interfaces, and SLA | Platform Architect | Document signed off by CTO / Tech Lead | Five plane docs in `completion-program/` folder, all merged | 1.1 | Scope creep during build phase | Sprint 1 |
| 1.3 | Business track lock: 6 tracks (Prospecting, Qualification, Proposal, Negotiation, Closing, Post-Sale) each with defined agent roles and action metadata | Product Lead | Track matrix reviewed by Business Owner | Track matrix merged, no open rows | 1.2 | Wrong automation priority → wasted Temporal quota | Sprint 1 |
| 1.4 | Agent role registry: Observer / Recommender / Executor + per-role action metadata (Approval, Reversibility, Sensitivity, Provenance, Freshness) | AI Lead | Role registry referenced in all new agent PRs | Registry in `completion-program/decision-plane/agent-role-registry.md` | 1.3 | Agent acts as Executor without approval → compliance incident | Sprint 1 |
| 1.5 | Status dashboard (living doc, auto-updated by CI): subsystem → plane → status | Platform Engineer | CI workflow outputs dashboard on every merge | Dashboard URL accessible, updated within 1 h of merge | 1.1 | No visibility → silent regression of completed work | Sprint 2 |

---

## Workstream 2 — Decision Plane Hardening

**Plane:** Decision · **Track:** All tracks (especially Proposal, Negotiation, Closing)

| # | Deliverable | Owner | Evidence Gate | Exit Criteria | Dependencies | Risk | SLA |
|---|------------|-------|--------------|--------------|-------------|------|-----|
| 2.1 | Unified JSON schemas for all 5 canonical outputs: `memo`, `evidence_pack`, `risk_register`, `approval_packet`, `execution_intent` | AI Lead + Backend Engineer | Schema files in `completion-program/decision-plane/schemas/`, validated by `jsonschema` CI job | CI green on schema lint + `pytest` schema round-trip tests | 1.4 | Free-text outputs in critical flows → hallucinated decisions | Sprint 1 |
| 2.2 | OpenAI Structured Outputs enforced for all critical agent calls — no `JSON mode` fallback on Executor-class agents | AI Lead | Code diff shows `response_format={"type":"json_schema",...}` on all critical paths; `grep` confirms no JSON-mode in critical modules | PR merged + CI green | 2.1 | Non-conforming agent output reaches CRM/DocuSign → data corruption | Sprint 2 |
| 2.3 | Evidence Pack Generator service — builds `evidence_pack_json` from tool results, web sources, KB hits | Backend Engineer | Integration test: given agent tool results, service returns valid `evidence_pack` matching schema | Test pass rate ≥ 99 % on 100-sample eval set | 2.1, 2.2 | Evidence fabrication not detected → trust loss with enterprise clients | Sprint 3 |
| 2.4 | Decision Memo Compiler — bilingual (AR/EN) formatted memo from `memo_json` + `evidence_pack_json` | Backend Engineer | End-to-end test: memo generated for 3 sample deals, reviewed by Business Owner for quality | Business Owner approval + schema conformance CI green | 2.3 | Low-quality memos → adoption refusal by sales team | Sprint 3 |
| 2.5 | Provenance / Freshness / Confidence scoring on all agent outputs — stored in `evidence_pack.metadata` | AI Lead | Scoring visible in executive dashboard sample; all 3 scores non-null in 100 % of critical outputs | Dashboard shows scores; regression test suite green | 2.3 | Stale data presented as current → wrong deal decision | Sprint 4 |
| 2.6 | HITL interrupts via LangGraph for Executor-class decisions above risk threshold | AI Lead | Staging demo: high-risk action paused, human approval UI shown, action resumes | Demo recording in `artifacts/` + CI integration test | 2.2, 2.5 | Fully autonomous high-risk action → regulatory or financial exposure | Sprint 4 |

---

## Workstream 3 — Execution Plane Hardening

**Plane:** Execution · **Track:** Partnerships, DD Room, Approvals, Launches, PMI

| # | Deliverable | Owner | Evidence Gate | Exit Criteria | Dependencies | Risk | SLA |
|---|------------|-------|--------------|--------------|-------------|------|-----|
| 3.1 | Workflow inventory — all existing Celery tasks + LangGraph flows tagged: short-lived / medium / long-lived-durable | Backend Lead | Inventory sheet in `completion-program/execution-plane/workflow-inventory.md` | Every existing background task classified; zero unclassified | 1.1 | Unknown workflows continue to run without durability guarantees | Sprint 1 |
| 3.2 | Temporal installation + local dev smoke test (`temporalio` Python SDK) | Platform Engineer | `docker-compose up temporal` + worker registers + simple workflow executes | Temporal UI accessible; workflow history visible | None | Long-lived flows stay on Celery → crash-loss risk | Sprint 2 |
| 3.3 | Temporal pilot: Partner Approval workflow — request → approval gate → execution → compensation on rejection | Backend Lead + AI Lead | End-to-end test on staging: approval granted path + rejected-with-compensation path both pass | Both paths automated CI tested; workflow history in Temporal UI | 3.1, 3.2 | No durable workflows → enterprise client SLA violations | Sprint 3–4 |
| 3.4 | Idempotency key strategy documented + enforced on all external-facing Temporal activities | Backend Lead | `rg 'idempotency_key'` finds enforcement in all connector activities | Code review pass + integration test with duplicate triggers | 3.3 | Duplicate triggers → double-billing or double-signature | Sprint 4 |
| 3.5 | Workflow versioning strategy (`workflow.get_version()`) for safe zero-downtime updates | Backend Lead | Staging update test: old workflow instances survive worker update | Test pass + runbook in `runbooks/temporal-versioning.md` | 3.3 | Breaking workflow update → corrupted in-flight deals | Sprint 5 |
| 3.6 | Migration plan + cut-over runbook for all `long-lived-durable` workflows from Celery → Temporal | Backend Lead | Runbook reviewed; staging dry-run recorded | Runbook in `runbooks/`; dry-run artifact uploaded | 3.5 | Incomplete migration → split-brain execution state | Sprint 6–8 |

---

## Workstream 4 — Trust Fabric Hardening

**Plane:** Trust · **Track:** All tracks (security gate for every action)

| # | Deliverable | Owner | Evidence Gate | Exit Criteria | Dependencies | Risk | SLA |
|---|------------|-------|--------------|--------------|-------------|------|-----|
| 4.1 | Policy inventory — all access-control and authorization checks extracted from app code, prompts, and scattered conditionals | Security Lead | Inventory doc in `completion-program/trust-plane/policy-inventory.md`; peer-reviewed | Zero app-level authorization logic unaccounted for | 1.1 | Hidden policy drift → privilege escalation | Sprint 1 |
| 4.2 | OPA policy packs v1 — tenant isolation, agent role gating, action sensitivity enforcement | Security Lead | OPA unit tests (`opa test`) green; policies loaded in staging | `opa test` CI green; staging smoke test passes | 4.1 | App code enforces policy inconsistently → bypasses | Sprint 3 |
| 4.3 | OpenFGA model draft — authorization graph for: tenants, users, agents, tools, workflows | Security Lead | Model uploaded to staging OpenFGA instance; 10 check() assertions pass | All assertions in `trust-plane/openfga-assertions.yaml` pass | 4.1 | Coarse-grained RBAC → agent over-privilege | Sprint 3 |
| 4.4 | HashiCorp Vault integration — dynamic secrets for DB, API keys; audit log enabled | Platform Engineer | Vault audit log shows DB cred issuance; app env vars sourced from Vault in staging | `vault audit list` shows enabled sink; app boots with Vault creds | 1.2 | Static secrets in `.env` → credential leakage | Sprint 3–4 |
| 4.5 | Keycloak SSO + service identity — OIDC for human users; service accounts for agents/workers | Platform Engineer | Login via Keycloak on staging; worker JWT verified by backend | Login flow recorded; `curl` with JWT returns 200 on secured endpoint | 4.4 | No SSO → no enterprise buyer trust | Sprint 4 |
| 4.6 | Tool Verification Ledger v1 — every tool/action emits: `intended`, `claimed`, `actual`, `side_effects`, `contradiction_status` | AI Lead | Ledger populated in staging for 3 tool calls; contradiction detected in 1 injected test case | Ledger schema in `trust-plane/tool-verification-schema.json`; test passes | 2.2, 4.2 | Hallucinated operations not caught → enterprise trust destruction | Sprint 4–5 |
| 4.7 | Contradiction Dashboard — surfaces `contradiction_status != none` items from ledger to ops team | Backend Engineer | Dashboard loads in staging with at least 1 sample contradiction | Dashboard screenshot in `artifacts/`; data sourced from real ledger | 4.6 | Silent contradictions → incorrect decisions propagate | Sprint 5 |

---

## Workstream 5 — Data & Connector Fabric

**Plane:** Data · **Track:** All tracks (data quality gate)

| # | Deliverable | Owner | Evidence Gate | Exit Criteria | Dependencies | Risk | SLA |
|---|------------|-------|--------------|--------------|-------------|------|-----|
| 5.1 | Connector Facade standard — base class + versioning contract (`v1`, `v2`) + retry/timeout/idempotency policy template | Backend Lead | `completion-program/data-plane/connector-facade-standard.md` reviewed; base class in `backend/app/connectors/base.py` | Standard merged; base class passes `mypy` type check | 1.2 | Raw vendor API chaos → cascading failures on API version changes | Sprint 2 |
| 5.2 | Connector wrappers (HubSpot, WhatsApp/Twilio, DocuSign, email, calendar) — all implementing facade | Backend Engineers | Each connector has unit tests with mocked vendor; retry/timeout/idempotency tested | All tests green in CI; `mypy` clean | 5.1 | Vendor SDK update breaks multiple flows silently | Sprint 3–5 |
| 5.3 | Event envelope standard (`CloudEvents` spec) — schema registry entry per event type | Backend Lead + AI Lead | `asyncapi.yaml` in repo; schema registry seeded with 10 core event types | AsyncAPI lint CI job green; schema registry browsable in staging | 5.1 | Untyped events → silent data contract breakage between services | Sprint 3 |
| 5.4 | pgvector semantic memory — embeddings for deal context, sector KB, partner history | Backend Lead | Embedding round-trip test: text → embed → nearest-neighbour → correct result | Test pass + performance benchmark (`< 100 ms p95`) logged | None (already partially exists) | Context-blind agents → low-quality recommendations | Sprint 2–3 |
| 5.5 | Semantic metrics dictionary — 30+ KPIs defined: formula, grain, source table, owner | Product Lead | Dictionary in `completion-program/data-plane/semantic-metrics.md`; reviewed by Business Owner | Every dashboard metric traceable to dictionary entry | 5.4 | Metric disagreement between teams → executive distrust | Sprint 3 |
| 5.6 | Data quality gates (Great Expectations suites) on lead, deal, partner, telemetry datasets | Data Engineer | GE HTML report in CI artefacts; all critical expectations pass at `≥ 98 %` | CI job `ge-validate` green on `main` | 5.3, 5.4 | Silent dirty data → corrupted AI recommendations | Sprint 4–6 |
| 5.7 | Lineage/catalog (single source): table → service → agent → dashboard | Data Engineer | Catalog browsable in staging; 100 % of production tables catalogued | No uncatalogued table in production | 5.5, 5.6 | Unknown data flow → compliance and debugging nightmare | Sprint 6–8 |

---

## Workstream 6 — Enterprise Delivery Fabric

**Plane:** Operating · **Track:** Release, SDLC

| # | Deliverable | Owner | Evidence Gate | Exit Criteria | Dependencies | Risk | SLA |
|---|------------|-------|--------------|--------------|-------------|------|-----|
| 6.1 | `CODEOWNERS` file — all critical paths owned by ≥ 2 reviewers | Platform Lead | `CODEOWNERS` merged; PR to critical path requires owner approval in CI | GitHub enforces review; test PR blocked without owner | None | Single point of knowledge on critical paths | Sprint 1 |
| 6.2 | GitHub branch rulesets — `main` + `release/*` protected: required status checks, no force push, required signatures | Platform Lead | Ruleset visible in GitHub repo settings; test force-push rejected | Force-push blocked; status checks enforced | 6.1 | Unreviewed code reaches production | Sprint 1 |
| 6.3 | GitHub Environments: `dev`, `staging`, `canary`, `production` — with required reviewers and wait timers | Platform Lead | Each environment visible in GitHub; deployment to `production` requires manual approval | Environments configured; test deployment shows approval gate | 6.2 | Uncontrolled production deploys | Sprint 2 |
| 6.4 | OIDC federation — GitHub Actions → cloud provider, no long-lived secrets in CI | Platform Engineer | `aws sts get-caller-identity` (or equivalent) succeeds in CI from OIDC token; no `AWS_SECRET_ACCESS_KEY` in secrets | OIDC login in CI logs; no static credential in repo | 6.3 | Long-lived CI secrets → credential exposure | Sprint 2 |
| 6.5 | Artifact attestations (`gh attestation verify`) on all production container images | Platform Engineer | Attestation generated and verified in staging pipeline | `gh attestation verify` returns `Verified` for last 3 releases | 6.4 | Unsigned images → supply-chain attack surface | Sprint 3 |
| 6.6 | Canary release workflow — 5 % → 25 % → 100 % traffic shift with automated rollback on error rate | Platform Engineer | Staging canary deploy recorded; automated rollback triggered by injected 5xx spike | Rollback completes in `< 2 min`; recorded in `artifacts/` | 6.3, 6.5 | Big-bang deploys → full outage on bad release | Sprint 3–4 |
| 6.7 | Audit log streaming to external SIEM / data warehouse (covers 180-day GitHub limit) | Security Lead | Log stream active; sample events queryable in warehouse after 24 h | Query returns events; streaming confirmed in runbook | 6.4 | Audit log expiry → compliance gap for enterprise customers | Sprint 3–4 |

---

## Workstream 7 — Saudi Enterprise Readiness

**Plane:** Trust + Operating · **Track:** All (compliance gate)

| # | Deliverable | Owner | Evidence Gate | Exit Criteria | Dependencies | Risk | SLA |
|---|------------|-------|--------------|--------------|-------------|------|-----|
| 7.1 | PDPL Data Classification Matrix — all data types classified: Public / Internal / Confidential / Personal / Sensitive-Personal | Compliance Lead | Matrix in `completion-program/saudi-governance/pdpl-classification-matrix.md`; reviewed by legal counsel | No unclassified data type in production schema | 4.1 | PDPL violation → SAR 5 M fine + reputational damage | Sprint 1 |
| 7.2 | Personal Data Processing Register — purpose, legal basis, retention period, cross-border transfer flag for every personal data flow | Compliance Lead | Register in `saudi-governance/pdpl-processing-register.md`; ≥ 1 legal-basis entry per flow | Zero flows without legal basis documented | 7.1 | SAMA/SDAIA audit findings → license risk | Sprint 2 |
| 7.3 | Data Residency & Transfer Control flags — enforced in Vault/OPA policy: `data_residency: KSA` required for personal data | Security Lead + Platform Engineer | OPA unit test: cross-border transfer of personal data rejected without transfer mechanism | OPA test green; staging request with wrong residency returns 403 | 4.2, 7.1 | Personal data processed outside KSA without safeguard → PDPL breach | Sprint 3 |
| 7.4 | NCA ECC 2-2024 Readiness Gap Register — all controls mapped: Compliant / Gap / N/A + remediation owner | Security Lead | Gap register in `saudi-governance/nca-ecc-readiness.md`; reviewed by CISO | Zero gaps without owner + target date | 4.2, 6.7 | CITC/NCA audit → operating license suspension | Sprint 2–3 |
| 7.5 | AI Governance Profile — NIST AI RMF (Govern, Map, Measure, Manage) mapped to Dealix controls | Compliance Lead + AI Lead | Profile in `saudi-governance/ai-governance-nist-rmf.md`; reviewed by external advisor if available | All 4 NIST functions have at least 1 Dealix control mapped | 4.6, 2.5 | No AI governance → rejected by enterprise procurement | Sprint 3 |
| 7.6 | OWASP LLM Top 10 Controls Checklist — per-release gate, signed by AI Lead | AI Lead | Checklist template in `saudi-governance/owasp-llm-checklist.md`; completed for last release | Release blocked if any HIGH-severity unchecked item | 2.6, 4.6 | LLM-specific attacks (prompt injection, training data poisoning) → breach | Sprint 2 (template) / every release (execution) |
| 7.7 | SAMA Open Banking / financial data controls (if applicable) — mapped to existing PDPL controls | Compliance Lead | Controls mapping in `saudi-governance/sama-controls.md` | Document reviewed by legal + linked from NCA ECC register | 7.2, 7.4 | Financial data mishandling → SAMA enforcement | Sprint 4 |

---

## Workstream 8 — Executive & Customer Readiness

**Plane:** Operating (UX layer) · **Track:** All tracks (enterprise buyer journey)

| # | Deliverable | Owner | Evidence Gate | Exit Criteria | Dependencies | Risk | SLA |
|---|------------|-------|--------------|--------------|-------------|------|-----|
| 8.1 | Executive Room UI — board-ready memo view, evidence pack view, approval center | Frontend Lead + Product Lead | User acceptance test by Business Owner: memo, evidence, and approval flow complete | UAT passed; recorded demo in `artifacts/` | 2.4, 2.6 | No executive view → enterprise deal stalls at C-suite sign-off | Sprint 4–5 |
| 8.2 | Policy Violations Board — surfaces OPA/OpenFGA rejections + tool contradictions to compliance officer | Frontend Lead | Board populates with injected test violation; compliance officer persona tested | UAT passed; live data from trust fabric | 4.2, 4.7 | Compliance officers cannot see violations → audit failure | Sprint 5–6 |
| 8.3 | Partner Scorecards — live score per partner: engagement, revenue, risk, next-best-action | Product Lead + Backend | Scorecard loads with real data for 3 sample partners in staging | Data sourced from semantic metrics; scorecard screenshot in `artifacts/` | 5.5, 3.3 | No scorecard → manual tracking in spreadsheets, churn risk | Sprint 5–6 |
| 8.4 | Actual vs Forecast Dashboard — track → deal stage → revenue forecast vs actual with variance | Product Lead | Dashboard loads with real data; 1-week variance tracked | Dashboard screenshot; data sourced from production | 5.5, 5.6 | No forecast visibility → executive decisions without data | Sprint 5–6 |
| 8.5 | Risk Heatmap — deal, partner, compliance risk aggregated, colour-coded | Frontend Lead | Heatmap loads with ≥ 5 real risk events in staging | Heatmap screenshot; data sourced from trust fabric + telemetry | 4.7, 5.5 | Risk blind spots → enterprise client due-diligence failure | Sprint 6 |
| 8.6 | Next-Best-Action Dashboard — per deal, per partner, per track; action linked to execution intent | AI Lead + Frontend | Dashboard shows ≥ 3 actions per deal in staging; action triggers Temporal workflow | End-to-end demo recorded | 2.6, 3.3, 8.1 | No NBA → sales team ignores AI → ROI not demonstrated | Sprint 6–7 |

---

## Priority Sequencing

```
Sprint 1:  WS1 (arch closure) + WS6.1-6.2 (branch protection) + WS7.1 (PDPL matrix)
Sprint 2:  WS2.1-2.2 (schemas) + WS3.1-3.2 (workflow inventory + Temporal) + WS5.1 (connector facade) + WS7.2 + WS7.6 template
Sprint 3:  WS2.3-2.4 (evidence pack + memo) + WS3.3 (Temporal pilot) + WS4.2-4.4 (OPA + OpenFGA + Vault) + WS5.2-5.3
Sprint 4:  WS2.5-2.6 (scoring + HITL) + WS3.4-3.5 (idempotency + versioning) + WS4.5-4.6 (Keycloak + tool ledger) + WS5.4-5.5 + WS6.4-6.5 + WS7.3-7.5
Sprint 5:  WS3.6 (Celery→Temporal migration) + WS4.7 + WS5.6 + WS6.6-6.7 + WS8.1-8.2
Sprint 6+: WS5.7 + WS7.7 + WS8.3-8.6
```

---

## Definition of Done (Binary Gates)

A workstream is **Done** only when **all** of the following are true:

- [ ] All deliverable artefacts merged to `main` (or tagged release branch)
- [ ] All evidence gates passed (CI logs, staging screenshots, recorded demos)
- [ ] All exit criteria met (binary, no partial credit)
- [ ] No open HIGH or CRITICAL security findings related to the workstream
- [ ] Runbook updated if the workstream introduces a new operational component
- [ ] Saudi compliance control mapped (if workstream touches personal data or AI output)

---

*This matrix is a living document. Update status column weekly. Any change to Exit Criteria requires sign-off from Platform Architect + CTO.*

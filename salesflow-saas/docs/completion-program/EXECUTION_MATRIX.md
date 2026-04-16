# Dealix Execution Matrix — المصفوفة التنفيذية النهائية

**الإصدار:** 1.0  
**التاريخ:** 2026-04-16  
**المرجع:** [`COMPLETION_PROGRAM.md`](./COMPLETION_PROGRAM.md)

---

## كيفية القراءة

| العمود | الوصف |
|--------|-------|
| **Workstream** | المسار التنفيذي (WS-1 إلى WS-8) |
| **Deliverable** | المخرج المحدد |
| **Owner** | المسؤول (Role-based, not person-named) |
| **Evidence Gate** | ما يثبت الإنجاز (لا يُقبل الادعاء بدون evidence) |
| **Exit Criteria** | معايير الخروج الدقيقة |
| **Dependencies** | ما يجب أن يسبق هذا المخرج |
| **Risk** | المخاطر المحددة |
| **SLA** | الالتزام الزمني المستهدف |

**حالات المخرجات:**
- 🔴 Not Started — لم يبدأ
- 🟡 In Progress — قيد التنفيذ
- 🟢 Complete — مكتمل ومثبَت بالدليل
- ⏸️ Blocked — معلّق بسبب اعتمادية

---

## WS-1: Productization & Architecture Closure

| # | Deliverable | Owner | Evidence Gate | Exit Criteria | Dependencies | Risk | SLA |
|---|-------------|-------|---------------|---------------|--------------|------|-----|
| 1.1 | Current-vs-Target Architecture Register | Architect | Published register with status per subsystem | Every subsystem has one of: `Current` / `Partial` / `Pilot` / `Production` status. No `Unknown` entries. | Codebase audit complete | Subsystem scope creep if register is incomplete | Sprint 1 |
| 1.2 | 5 Planes Lock | Architect + Tech Lead | ADR per plane signed off in `memory/adr/` | Each plane has: purpose statement, boundary contract, technology selection, interface spec. Reviewed by ≥2 engineers. | WS-1.1 complete | Premature lock without implementation reality check | Sprint 1 |
| 1.3 | 6 Business Tracks Lock | Product Owner + Architect | Track definition doc with entry/exit criteria per track | Tracks: Prospecting, Qualification, Proposal, Negotiation, Closing, Post-Sale. Each has measurable KPIs. | WS-1.1 | Tracks don't map to actual agent capabilities | Sprint 1 |
| 1.4 | Agent Roles Lock | AI Lead | Role matrix: every agent classified as Observer / Recommender / Executor | No agent operates without explicit role classification. Role determines permission scope. | WS-1.2, WS-4.1 | Agents promoted to Executor without trust controls | Sprint 2 |
| 1.5 | Action Metadata Standard | Architect | Schema definition in code: `ActionMetadata` Pydantic model | Every sensitive action carries: `approval_required`, `reversibility`, `sensitivity_level`, `provenance_source`, `freshness_ttl` | WS-1.4 | Over-engineering metadata for trivial actions | Sprint 2 |

---

## WS-2: Decision Plane Hardening

| # | Deliverable | Owner | Evidence Gate | Exit Criteria | Dependencies | Risk | SLA |
|---|-------------|-------|---------------|---------------|--------------|------|-----|
| 2.1 | Decision Schema Library | AI Lead | JSON Schema files in `schemas/decisions/` | 5 schemas defined: `memo`, `evidence_pack`, `risk_register`, `approval_packet`, `execution_intent`. All pass validation tests. | WS-1.5 | Schema too rigid for evolving agent capabilities | Sprint 2 |
| 2.2 | Structured Outputs Enforcement | AI Lead + Backend Lead | Integration tests proving no free-text critical output | Critical flows (deal approval, compliance check, partner evaluation) produce only schema-bound output. Tested with ≥10 scenarios per flow. | WS-2.1 | LLM hallucination bypasses schema enforcement | Sprint 3 |
| 2.3 | Evidence Pack Generator | AI Lead | Service class `EvidencePackGenerator` with unit tests | Auto-generates evidence packs from agent outputs. Includes: data sources, confidence scores, timestamps, chain of reasoning. Output validated against `evidence_pack` schema. | WS-2.1 | Evidence too shallow to be trustworthy | Sprint 3 |
| 2.4 | Decision Memo Compiler (AR/EN) | AI Lead + Arabic Ops | Bilingual memo output from ≥2 critical flows | Memos render correctly RTL (Arabic) and LTR (English). Reviewed by native Arabic speaker. | WS-2.3 | Translation quality degrades for domain terminology | Sprint 4 |
| 2.5 | Provenance + Freshness + Confidence Scores | AI Lead | Score calculation logic with tests; scores appear in all agent outputs | `provenance_score` (0–1): data source reliability. `freshness_score` (0–1): recency. `confidence_score` (0–1): model certainty. All ≥ 0.5 for critical decisions or human review triggered. | WS-2.2 | Score gaming or calibration drift | Sprint 4 |

---

## WS-3: Execution Plane Hardening

| # | Deliverable | Owner | Evidence Gate | Exit Criteria | Dependencies | Risk | SLA |
|---|-------------|-------|---------------|---------------|--------------|------|-----|
| 3.1 | Workflow Inventory & Classification | Backend Lead | Spreadsheet/doc listing every workflow with classification | Every workflow classified: `short-lived-local` (<5 min, single service), `medium-lived-queued` (5–15 min, Celery), `long-lived-durable` (>15 min or multi-system or needs compensation). No unclassified workflows. | WS-1.1 | Workflows misclassified to avoid migration effort | Sprint 2 |
| 3.2 | Temporal Infrastructure Setup | DevOps Lead | Temporal server running in dev + staging; health check passing | Docker Compose includes Temporal; README documents connection. Worker template exists. | None | Temporal operational complexity underestimated | Sprint 3 |
| 3.3 | Temporal Pilot: Partner Approval Flow | Backend Lead + AI Lead | End-to-end test: submit partner application → multi-step approval → notification → status update | Flow survives worker restart. Compensation on rejection works. Idempotency keys prevent duplicate approvals. Audit trail in DB. | WS-3.1, WS-3.2 | Pilot scope creep; mixing pilot with feature work | Sprint 4–5 |
| 3.4 | Compensation Policy Library | Backend Lead | Compensation handlers for ≥3 critical flows | Each compensation: rollback action defined, tested with failure injection, logged. Patterns: saga, retry-with-backoff, dead-letter. | WS-3.3 | Compensation logic not tested under real failure modes | Sprint 5 |
| 3.5 | Idempotency Key Standard | Backend Lead | Middleware/decorator enforcing idempotency keys on critical endpoints | `X-Idempotency-Key` header required on POST/PUT for critical flows. Duplicate detection within 24h window. Tests prove replay safety. | WS-3.3 | Key storage overhead if TTL not managed | Sprint 5 |
| 3.6 | Workflow Versioning Strategy | Architect + Backend Lead | ADR documenting versioning approach | Strategy covers: breaking changes, worker rollout order, backward compatibility window. Temporal workflow versioning or equivalent documented. | WS-3.3 | Version conflicts during rolling deployments | Sprint 6 |

---

## WS-4: Trust Fabric Hardening

| # | Deliverable | Owner | Evidence Gate | Exit Criteria | Dependencies | Risk | SLA |
|---|-------------|-------|---------------|---------------|--------------|------|-----|
| 4.1 | Policy Inventory | Security Lead | Document listing every policy decision currently in code | Every `if tenant_role == ...`, `if agent_can(...)`, permission check catalogued. Source file + line reference. | WS-1.1 | Policies scattered in prompts/templates missed | Sprint 2 |
| 4.2 | OPA Policy Packs | Security Lead | OPA bundle with ≥10 policies; unit tests passing | Policies cover: agent action authorization, data access scoping, outbound message gating, deal approval thresholds, PDPL consent checks. Tested with Rego unit tests. | WS-4.1 | OPA latency on hot path if not cached | Sprint 4 |
| 4.3 | OpenFGA Authorization Model | Security Lead + Backend Lead | Model YAML + integration test | Model covers: tenant → user → role → permission → resource. Agent permissions scoped. Tested with ≥20 authorization scenarios. | WS-4.1 | Model complexity grows unmanageably with agent roles | Sprint 5 |
| 4.4 | Vault Integration Plan | DevOps Lead | Architecture doc + PoC connecting 1 service to Vault | Dynamic secrets for DB credentials. Audit logging enabled. Rotation policy defined. | None | Secret sprawl during migration from .env files | Sprint 4 |
| 4.5 | Keycloak SSO & Service Identity Plan | Security Lead + DevOps | Architecture doc + PoC with one SSO flow | SSO for admin portal. Service-to-service identity via OIDC. Tenant isolation in Keycloak realms. | WS-4.4 | Keycloak operational burden for small team | Sprint 5 |
| 4.6 | Tool Verification Ledger v1 | AI Lead + Security Lead | Ledger table in DB; verification entries for ≥5 tools | Each tool action logged: `intended_action`, `claimed_action`, `actual_execution`, `side_effects`, `contradiction_status`. Query API exists. | WS-4.2 | High-volume tool calls create storage pressure | Sprint 5 |
| 4.7 | Contradiction Dashboard | Frontend Lead + AI Lead | Dashboard page showing tool verification contradictions | Real-time view of: contradiction count, severity, affected agents, resolution status. Filterable by date/agent/tool. | WS-4.6 | Low contradiction rate makes dashboard seem unused | Sprint 6 |

---

## WS-5: Data & Connector Fabric

| # | Deliverable | Owner | Evidence Gate | Exit Criteria | Dependencies | Risk | SLA |
|---|-------------|-------|---------------|---------------|--------------|------|-----|
| 5.1 | Connector Facade Standard | Architect + Backend Lead | Interface definition: `ConnectorFacade` ABC with standard methods | Standard interface: `connect()`, `execute()`, `health_check()`, `get_version()`. Error handling contract. Retry policy per connector. | WS-1.2 | Over-abstraction reduces connector-specific optimizations | Sprint 3 |
| 5.2 | WhatsApp Connector Facade | Backend Lead | `WhatsAppConnector(ConnectorFacade)` with tests | Wraps existing `whatsapp_service.py`. Versioned API calls. Retry with exponential backoff. Rate limiting. Audit log per message. | WS-5.1 | Breaking change in Meta API during migration | Sprint 4 |
| 5.3 | Email Connector Facade | Backend Lead | `EmailConnector(ConnectorFacade)` with tests | Wraps existing `email_service.py`. Provider-agnostic (Resend/SendGrid). Retry. Bounce handling. | WS-5.1 | Provider switching requires re-testing deliverability | Sprint 4 |
| 5.4 | CRM Connector Facade (Salesforce) | Backend Lead | `SalesforceConnector(ConnectorFacade)` with tests | Wraps `salesforce_agentforce.py`. OAuth flow. Field mapping versioned. Sync conflict resolution. | WS-5.1 | Salesforce API version deprecation | Sprint 5 |
| 5.5 | Event Envelope Standard | Architect | Schema definition: CloudEvents-compatible envelope | Every inter-service event wrapped in: `id`, `source`, `type`, `specversion`, `time`, `datacontenttype`, `data`, `correlation_id`. Validated by middleware. | WS-1.2 | Retrofitting existing events is high-effort | Sprint 4 |
| 5.6 | Semantic Metrics Dictionary | Product Owner + Data Lead | Published dictionary with ≥30 metrics | Each metric: name, definition, formula, source table, update frequency, owner. No ambiguous metrics. | WS-1.3 | Metrics definitions disputed between teams | Sprint 4 |
| 5.7 | Data Quality Checks | Data Lead | Great Expectations suite for ≥5 critical datasets | Checks: completeness, uniqueness, freshness, referential integrity, value ranges. Runs in CI. Failures block deployment. | WS-5.6 | Quality checks too strict cause false CI failures | Sprint 6 |

---

## WS-6: Enterprise Delivery Fabric

| # | Deliverable | Owner | Evidence Gate | Exit Criteria | Dependencies | Risk | SLA |
|---|-------------|-------|---------------|---------------|--------------|------|-----|
| 6.1 | CODEOWNERS | Tech Lead | File committed; PR assignments working | Every directory has ≥1 owner. Critical paths (`services/pdpl/`, `services/ai/`, `integrations/`) have ≥2 reviewers. | None | CODEOWNERS bottleneck if reviewers unavailable | Sprint 1 |
| 6.2 | GitHub Branch Rulesets | DevOps Lead | Rulesets enforced on `main` and `release/*` | `main`: require PR, ≥1 approval, status checks pass, no force push. `release/*`: ≥2 approvals, security scan pass. | WS-6.1 | Rules bypass via admin override not audited | Sprint 1 |
| 6.3 | Required CI Checks | DevOps Lead | CI gates enforced; PRs blocked on failure | Required checks: `pytest`, `npm run lint`, `npm run build`, `playwright e2e`, security scan (Bandit/Trivy). All must pass before merge. | WS-6.2 | Flaky tests cause merge delays | Sprint 2 |
| 6.4 | Environment Promotion Pipeline | DevOps Lead | Environments configured: dev → staging → canary → prod | Each environment: separate config, deployment approval (staging: auto, canary: 1 approval, prod: 2 approvals). Health checks between stages. | WS-6.2, WS-6.3 | Environment drift between staging and production | Sprint 3 |
| 6.5 | OIDC Federation for CI/CD | DevOps Lead | GitHub Actions authenticate via OIDC (no long-lived secrets) | AWS/GCP credentials via OIDC. No static access keys in repo secrets. Rotation-free. | WS-6.4 | Cloud provider OIDC config complexity | Sprint 4 |
| 6.6 | Artifact Attestations | DevOps Lead | Container images signed; provenance metadata attached | Every release artifact: SHA256 digest, build provenance (SLSA Level 2+), sigstore signature. Verification script in repo. | WS-6.5 | Signing infrastructure availability | Sprint 5 |
| 6.7 | External Audit Log Streaming | DevOps Lead + Security Lead | Audit logs flowing to external SIEM/warehouse | GitHub audit log → S3/BigQuery. Retention: ≥1 year. Dashboard for access pattern anomalies. | WS-6.4 | GitHub Enterprise Cloud required for advanced audit features | Sprint 6 |

---

## WS-7: Saudi Enterprise Readiness

| # | Deliverable | Owner | Evidence Gate | Exit Criteria | Dependencies | Risk | SLA |
|---|-------------|-------|---------------|---------------|--------------|------|-----|
| 7.1 | PDPL Data Classification Matrix | Compliance Lead | Matrix document mapping every data field to classification | Every PII field classified: `public`, `internal`, `confidential`, `restricted`. Storage and access rules per class. Reviewed by legal. | WS-4.1 | Classification too coarse to be actionable | Sprint 3 |
| 7.2 | Personal Data Processing Register | Compliance Lead | Register document per PDPL Art. 29 requirements | Each processing activity: purpose, legal basis, data categories, recipients, retention period, transfer safeguards. SDAIA-ready format. | WS-7.1 | Register becomes stale without update triggers | Sprint 4 |
| 7.3 | Residency/Transfer Control Flags | Backend Lead + Compliance | Policy engine flags enforced in data layer | `data_residency_region` flag on tenant config. Cross-border transfer blocked unless explicit consent + adequate safeguards. Tested. | WS-7.1, WS-4.2 | Multi-region complexity increases infrastructure cost | Sprint 5 |
| 7.4 | NCA ECC Readiness Gaps Register | Security Lead | Gaps register against ECC 2-2024 controls | Every ECC domain assessed: `compliant`, `partial`, `non-compliant`. Remediation plan for each gap. Priority by risk. | WS-4.1 | ECC requirements evolve; register needs maintenance | Sprint 4 |
| 7.5 | AI Governance Profile (NIST AI RMF) | AI Lead + Compliance | Governance profile document | Mapped to NIST AI RMF functions: Govern, Map, Measure, Manage. Risk tolerance defined per agent type. Bias testing plan. | WS-1.4 | NIST framework too abstract without Saudi-specific anchoring | Sprint 5 |
| 7.6 | OWASP LLM Controls Checklist | Security Lead + AI Lead | Checklist integrated into release process | Every release reviewed against OWASP LLM Top 10: prompt injection, data leakage, excessive agency, insecure output, etc. Sign-off required. | WS-6.3 | Checklist becomes checkbox exercise without enforcement | Sprint 5 |

---

## WS-8: Executive & Customer Readiness

| # | Deliverable | Owner | Evidence Gate | Exit Criteria | Dependencies | Risk | SLA |
|---|-------------|-------|---------------|---------------|--------------|------|-----|
| 8.1 | Executive Room Page | Frontend Lead + Product Owner | Live page at `/executive-room` | Real-time: revenue metrics, pipeline health, agent performance, compliance status. Arabic + English. Mobile responsive. | WS-5.6, WS-2.4 | Data latency makes real-time view misleading | Sprint 5 |
| 8.2 | Board-Ready Memo View | Frontend Lead + AI Lead | Memo rendered from agent decision output | Memo displays: recommendation, evidence, risk, confidence. Exportable as PDF. Bilingual. | WS-2.4 | Memo quality depends on LLM output quality | Sprint 5 |
| 8.3 | Evidence Pack Viewer | Frontend Lead | Evidence pack rendered with source links | Pack shows: data sources, calculation chain, timestamps, provider attribution. Drill-down to raw data. | WS-2.3 | Evidence volume overwhelms viewer UX | Sprint 6 |
| 8.4 | Approval Center | Frontend Lead + Backend Lead | Approval workflows visible and actionable in UI | Pending approvals, approval history, SLA tracking, escalation alerts. Role-based visibility. | WS-3.3, WS-4.3 | Approval fatigue if too many items require manual review | Sprint 6 |
| 8.5 | Policy Violations Board | Frontend Lead + Security Lead | Dashboard showing policy violations from OPA/Trust | Violations: count, severity, affected resource, remediation status. Trend charts. | WS-4.2, WS-4.7 | Low violation count makes board seem unused | Sprint 7 |
| 8.6 | Partner Scorecards | Frontend Lead + Product Owner | Scorecard page for each partner/affiliate | Metrics: revenue generated, lead quality, response time, compliance score. Benchmark vs peers. | WS-5.6 | Scorecard metrics disputed by partners | Sprint 6 |
| 8.7 | Actual vs Forecast Dashboard | Frontend Lead + Data Lead | Comparison view: forecast vs actuals with variance | Time series: daily/weekly/monthly. Variance alerts >20%. Model accuracy tracking. | WS-5.6, WS-2.5 | Forecast model accuracy insufficient for meaningful comparison | Sprint 7 |
| 8.8 | Risk Heatmap | Frontend Lead + AI Lead | Interactive heatmap: risk by deal/sector/region | Color-coded: green/yellow/red. Drill-down to deal details. Updated in near-real-time. | WS-2.5 | Risk model oversimplifies complex deal dynamics | Sprint 7 |
| 8.9 | Next-Best-Action Dashboard | AI Lead + Frontend Lead | NBA recommendations shown per lead/deal | Agent-generated recommendations with confidence scores. Accept/reject/defer actions. Impact tracking. | WS-2.2, WS-2.5 | Recommendations too generic without deep context | Sprint 8 |

---

## ملخص التبعيات الحرجة

```
WS-1 (Architecture Lock)
  ├── WS-2 (Decision Schemas depend on Action Metadata)
  ├── WS-3 (Workflow Classification depends on Architecture Register)
  ├── WS-4 (Policy Inventory depends on Architecture Register)
  └── WS-7 (Saudi Readiness depends on Architecture clarity)

WS-4 (Trust Fabric)
  ├── WS-3 (Temporal workflows need authorization)
  ├── WS-6 (Delivery gates need policy enforcement)
  └── WS-8 (Executive views need trust data)

WS-5 (Data & Connectors)
  └── WS-8 (Executive dashboards need semantic metrics)

WS-6 (Delivery Fabric)
  └── WS-7 (Saudi readiness needs release gates)
```

---

## مصفوفة المخاطر العليا

| المخاطرة | الأثر | الاحتمال | التخفيف |
|----------|-------|----------|---------|
| Temporal operational complexity | High: team capacity drain | Medium | Start with single pilot; evaluate before expanding |
| OPA/OpenFGA learning curve | Medium: slow initial progress | Medium | Dedicate spike sprint; pair with security expert |
| Structured Outputs LLM limitations | High: schema violations in edge cases | Low | Validation layer + fallback to human review |
| GitHub Enterprise Cloud dependency | Medium: delivery gates limited | High | Prioritize features available in Team plan; escalate Enterprise decision |
| Saudi regulatory changes | High: compliance gap | Low | Quarterly review cycle; legal counsel on retainer |
| Team capacity vs 8 parallel workstreams | High: burnout, quality drop | High | Phase workstreams; WS-1 + WS-6 first, WS-3 + WS-4 second |

---

*هذه المصفوفة قابلة للتنفيذ أسبوعاً بأسبوع. كل مخرج له دليل إنجاز واضح. لا يُقبل الادعاء بدون evidence.*

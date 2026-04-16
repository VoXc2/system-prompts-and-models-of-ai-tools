# Dealix Sovereign Enterprise Growth OS — Architecture Reference

> **Status:** Canonical Reference · **Version:** 1.0 · **Maintainer:** Dealix Architecture Board
>
> This document is the single source of truth for the 5-plane, 6-track sovereign architecture of the Dealix platform.

---

## Vision

Dealix is not just an AI CRM. It is a **Sovereign Enterprise Growth OS**: a platform that manages Sales, Partnerships, Corporate Development / M&A, Expansion, PMI / PMO, Governance / Compliance, and Executive Decision-Making on a single unified foundation where **AI explores / analyzes / recommends**, **systems execute**, and **humans approve critical decisions**.

The architecture is designed for Saudi-market sovereignty, Arabic-first operations, and enterprise-grade trust from day one.

---

## Five Architecture Planes (الطبقات المعمارية الخمس)

```
┌──────────────────────────────────────────────────────────────────┐
│                   5. Operating Plane  (طبقة التشغيل)             │
├──────────────────────────────────────────────────────────────────┤
│                   4. Data Plane       (طبقة البيانات)             │
├──────────────────────────────────────────────────────────────────┤
│                   3. Trust Plane      (طبقة الثقة)               │
├──────────────────────────────────────────────────────────────────┤
│                   2. Execution Plane  (طبقة التنفيذ)             │
├──────────────────────────────────────────────────────────────────┤
│                   1. Decision Plane   (طبقة القرار)              │
└──────────────────────────────────────────────────────────────────┘
```

---

### 1. Decision Plane — طبقة القرار

The cognitive core of Dealix. All intelligence flows originate here.

**Responsibilities:**

- Signal detection and triage
- Scenario analysis and memo generation
- Forecasting and recommendation
- Next-best-action computation
- Evidence pack assembly

**Stack:**

| Component | Role |
|---|---|
| Responses API | Structured AI completions |
| Structured Outputs | Schema-bound generation |
| Function Calling / MCP | Tool invocation and integration |
| Agent Tracing / Guardrails | Safety, observability, policy enforcement |
| LangGraph | Stateful loops, interrupts, checkpointing |

**Invariants — every recommendation must be:**

- **Typed** — conforms to a declared output schema
- **Evidence-backed** — cites specific data sources
- **Policy-aware** — evaluated against active policy rules
- **Approval-aware** — carries the correct approval class
- **Provenance-aware** — records model version, data lineage
- **Freshness-aware** — timestamps on every input datum

---

### 2. Execution Plane — طبقة التنفيذ

The durable operations layer. Any operation meeting one or more of the following criteria runs here:

- Spans more than minutes
- Crosses more than one system boundary
- Needs retry, timeout, or compensation logic
- Creates external commitments (contracts, signatures, payments)
- Requires approval with resume-later semantics

**Orchestration Split:**

| Engine | Scope |
|---|---|
| **LangGraph** | Cognition + HITL + short/medium orchestration (agent loops, approval interrupts, checkpointed reasoning) |
| **Temporal** | Durable business commitments — approvals, DD rooms, signatures, launches, PMI plans, multi-day/multi-week workflows |

**Invariants — every commitment must be:**

- **Durable** — survives process/node restarts
- **Resumable** — picks up from last checkpoint after interruption
- **Idempotent** — safe to replay without side effects
- **Compensatable** — has a defined rollback or compensation path
- **Observable** — emits traces, metrics, and logs via OpenTelemetry

---

### 3. Trust Plane — طبقة الثقة

The governance and authorization backbone. No action bypasses this plane.

**Components:**

| Component | Role |
|---|---|
| **OPA (Open Policy Agent)** | Policy engine — evaluates every action against declarative rules |
| **OpenFGA** | Fine-grained authorization — relationship-based access control |
| **Keycloak** | IAM, SSO, identity brokering, federation |
| **Vault** | Secrets governance, dynamic credentials, encryption-as-a-service |
| Tool Verification Ledger | Records intended vs. actual tool calls with side-effect audit |
| Evidence Packs | Immutable decision records attached to every major action |
| Contradiction Detection | Catches mismatches between claimed and actual execution |
| AI Governance Controls | Model routing policies, output guardrails, bias detection |

**OpenFGA Relationship Model:**

```
user ──┬── member_of ──▶ organization
       ├── belongs_to ──▶ workspace
       ├── can_access ──▶ deal_room
       ├── can_view   ──▶ memo
       ├── can_approve ──▶ approval_object
       ├── can_read   ──▶ board_pack
       └── can_manage ──▶ partner_entity
```

**Invariants — every action must be:**

- **Authorized** — passes OpenFGA relationship check
- **Policy-evaluated** — passes OPA policy check
- **Audited** — logged with actor, timestamp, context, outcome
- **Verified** — compared against actual execution result

---

### 4. Data Plane — طبقة البيانات

The persistent memory and integration substrate.

| Component | Role |
|---|---|
| **Postgres** | Operational source of truth — all transactional data |
| **pgvector** | Semantic memory co-located with operational data |
| **Airbyte** | Ingestion and connectors (600+ connectors, Agent Engine, MCP server) |
| **Unstructured** | Document extraction — PDF, DOCX, scanned documents |
| **Semantic Metrics Layer** | Business-meaningful metric definitions decoupled from raw tables |
| **Great Expectations** | Data quality — Checkpoints, Data Docs, automated validation |
| **CloudEvents + JSON Schema + AsyncAPI** | Event and data contracts between services |
| **OpenTelemetry** | Traces, metrics, logs — vendor-neutral observability |

---

### 5. Operating Plane — طبقة التشغيل

The CI/CD, supply-chain, and release governance layer.

| Mechanism | Purpose |
|---|---|
| **GitHub Rulesets** | Branch protection, merge requirements, status checks |
| **Protected Branches** | Prevent direct pushes to main/release branches |
| **CODEOWNERS** | Mandatory review from domain owners |
| **Required Status Checks** | CI gates before merge |
| **Environments with Deployment Protection Rules** | Staging/production gates, required reviewers |
| **OIDC Federation** | No long-lived secrets — workload identity federation |
| **Artifact Attestations (Sigstore)** | Cryptographic provenance for every build artifact |
| **External Audit Log Streaming** | 180-day retention limit for enterprise; streaming for audit-grade compliance |

---

## Six Business Tracks (المسارات التجارية الستة)

Each track is a vertical domain that spans all five planes. Tracks share the common plane infrastructure but own their domain logic, surfaces, and workflows.

---

### Track 1: Revenue OS — نظام الإيرادات

**Primary Surface:** Revenue Funnel Control Center

**Manages:**

- Capture (all channels — web, WhatsApp, phone, referral, API)
- Enrichment and deduplication
- Qualification and scoring
- Routing to owners
- Outreach orchestration (email, WhatsApp, calls)
- Meeting scheduling and orchestration
- Proposal generation
- Pricing and discount governance
- Contract handoff to legal
- Onboarding handoff to CS
- Renewal, upsell, and cross-sell

---

### Track 2: Partnership OS — نظام الشراكات

**Primary Surfaces:** Partner Room, Partnership Scorecards

**Manages:**

- Partner scouting and discovery
- Strategic fit scoring
- Channel economics modeling
- Alliance structure recommendation
- Term sheet drafting
- Approval and legal routing
- Partner activation workflows
- Partner scorecards and KPIs
- Contribution margin tracking

---

### Track 3: M&A / CorpDev OS — نظام الاستحواذ والتطوير المؤسسي

**Primary Surfaces:** DD Room, M&A Pipeline Board

**Manages:**

- Target sourcing and pipeline building
- Target screening and preliminary assessment
- Due diligence orchestration
- DD room access control (fine-grained via OpenFGA)
- Valuation range estimation
- Synergy modeling
- Investment committee memo generation
- Board pack assembly
- Offer strategy recommendation
- Signing and close readiness tracking

---

### Track 4: Expansion OS — نظام التوسع

**Primary Surface:** Expansion Launch Console

**Manages:**

- Market scanning and opportunity identification
- Market prioritization framework
- Compliance readiness assessment
- Localization (language, legal, cultural)
- Pricing and channel plan
- Launch readiness checklist and gate reviews
- Stop-loss logic and kill criteria
- Post-launch actual vs. forecast tracking

---

### Track 5: PMI / PMO OS — نظام التكامل وإدارة المشاريع

**Primary Surface:** PMI 30/60/90 Engine

**Manages:**

- Day-1 readiness planning
- 30/60/90-day integration plans
- Dependency tracking and critical path analysis
- Owner assignment and RACI matrices
- Escalation engine with SLA enforcement
- Synergy realization tracking
- Risk registers
- Weekly executive review generation

---

### Track 6: Executive / Board OS — نظام القيادة ومجلس الإدارة

**Primary Surfaces:** Executive Room, Approval Center, Evidence Pack Viewer, Risk Board, Policy Violations Board, Actual vs Forecast Dashboard

**Manages:**

- Board-ready memo generation
- Evidence pack assembly and presentation
- Approval center with multi-level routing
- Risk heatmaps and trend analysis
- Actual vs. forecast variance analysis
- Next-best-action recommendations
- Policy violation tracking and remediation
- Partner, M&A, and expansion pipeline overview

---

## 18 Mandatory Surfaces (الواجهات الإلزامية)

Every surface is a first-class UI component backed by a dedicated API module.

| # | Surface | Track | API Module |
|---|---|---|---|
| 1 | Executive Room | Executive | `sovereign_executive` |
| 2 | Approval Center | Executive | `sovereign_executive` |
| 3 | Evidence Pack Viewer | Executive | `sovereign_executive` |
| 4 | Partner Room | Partnership | `sovereign_partnership` |
| 5 | DD Room | M&A | `sovereign_ma` |
| 6 | Risk Board | Executive | `sovereign_executive` |
| 7 | Policy Violations Board | Executive | `sovereign_trust` |
| 8 | Actual vs Forecast Dashboard | Executive | `sovereign_executive` |
| 9 | Revenue Funnel Control Center | Revenue | `sovereign_revenue` |
| 10 | Partnership Scorecards | Partnership | `sovereign_partnership` |
| 11 | M&A Pipeline Board | M&A | `sovereign_ma` |
| 12 | Expansion Launch Console | Expansion | `sovereign_expansion` |
| 13 | PMI 30/60/90 Engine | PMI | `sovereign_pmi` |
| 14 | Tool Verification Ledger | Trust | `sovereign_trust` |
| 15 | Connector Health Board | Data | `sovereign_data` |
| 16 | Release Gate Dashboard | Operating | `sovereign_operating` |
| 17 | Saudi Compliance Matrix | Trust | `sovereign_trust` |
| 18 | Model Routing Dashboard | Decision | `sovereign_decision` |

---

## Program Locks (أقفال البرنامج)

Program locks define the control boundaries of the system. They classify every action, approval, reversibility level, and sensitivity tier.

### Action Classes

| Class | Description | Examples |
|---|---|---|
| **Auto-execute** | System performs autonomously; no human gate required | Intake, enrichment, scoring, memo drafting, evidence aggregation, workflow kickoff, reminders, task assignment, SLA tracking, dashboard refresh, variance detection, anomaly alerts, document extraction, connector syncs, quality checks, telemetry collection |
| **Execute with mandatory approval** | System prepares; human must approve before execution | Term sheet sending, signature request, strategic partner activation, market launch, M&A offer, out-of-policy discount, high-sensitivity data sharing, production promotion, capital commitments |
| **Human-only** | System cannot execute; human performs directly | Board votes, legal sign-off, regulatory submissions |

### Approval Classes

| Level | Approver | Scope |
|---|---|---|
| **L1** | Manager / Team Lead | Operational decisions within team boundaries |
| **L2** | VP / Director + Compliance | Cross-functional or compliance-sensitive decisions |
| **L3** | C-suite / Board | Strategic, high-capital, or irreversible decisions |

### Reversibility Classes

| Class | Description | Mechanism |
|---|---|---|
| **R1 — Fully reversible** | Can be undone with no residual effect | Undo / revert operation |
| **R2 — Reversible with cost** | Can be undone but incurs cost or delay | Compensation workflow |
| **R3 — Partially reversible** | Some effects can be reversed, others cannot | Manual intervention required |
| **R4 — Irreversible** | Cannot be undone once executed | Requires pre-approval gate (L2 or L3) |

### Sensitivity Model

| Tier | Access |
|---|---|
| **Public** | No restrictions |
| **Internal** | Organization members only |
| **Confidential** | Need-to-know, role-gated |
| **Restricted** | Named individuals, audit-logged access |
| **Board-Only** | Board members and designated officers only |

### Provenance / Freshness / Confidence Trio

Every AI recommendation carries the following metadata:

| Field | Description |
|---|---|
| **Data Sources** | Enumerated list of inputs used |
| **Assumption List** | Explicit assumptions made during analysis |
| **Data Freshness Timestamp** | When each source was last refreshed |
| **Confidence Score** | Quantified model confidence (0.0–1.0) |
| **Model Version** | Exact model identifier and version used |
| **Policy Notes** | Relevant policy rules evaluated and their outcomes |

---

## Sovereign Routing Fabric (نسيج التوجيه السيادي)

Policy-based model routing ensures the right model handles the right task at the right cost.

### Routing Lanes

| Lane | Models | Use Case |
|---|---|---|
| **Coding** | DeepSeek / Codex | Code generation, code review, technical analysis |
| **Executive Reasoning** | Claude Opus / GPT-4o | Strategic memos, board packs, complex scenario analysis |
| **Throughput Drafting** | Groq / Llama | High-volume drafting, email generation, summaries |
| **Fallback** | GPT-4o-mini | Cost-efficient fallback for non-critical tasks |

### Routing Quality Metrics

| Metric | Description |
|---|---|
| Latency | End-to-end response time per task |
| Schema Adherence | Percentage of outputs conforming to declared schema |
| Contradiction Rate | Frequency of outputs contradicting known facts or prior outputs |
| Arabic Quality | Fluency, accuracy, and cultural appropriateness of Arabic output |
| Cost per Successful Task | Total model cost divided by tasks meeting quality threshold |

---

## Connector Facade Pattern (نمط واجهة الموصلات)

Every external connector — regardless of provider — must implement a uniform contract to ensure governance, reliability, and auditability.

| Attribute | Description |
|---|---|
| **Contract** | Input/output schema (JSON Schema) |
| **Version** | Semantic versioning (MAJOR.MINOR.PATCH) |
| **Retry Policy** | Max retries, backoff strategy (exponential, fixed, jitter) |
| **Timeout Policy** | Per-call and total-workflow timeouts |
| **Idempotency Key** | Unique key ensuring safe replay |
| **Approval Policy** | Which action class applies (auto-execute, mandatory approval, human-only) |
| **Audit Mapping** | Which events to log and at what detail level |
| **Telemetry Mapping** | OpenTelemetry span configuration (attributes, sampling) |
| **Rollback / Compensation Notes** | Steps to reverse or compensate the connector's side effects |

---

## Evidence-Native Operations (العمليات المبنية على الأدلة)

Dealix is evidence-native: every major decision produces a structured evidence pack, not just a recommendation.

### Evidence Pack Schema

| Field | Description |
|---|---|
| **Sources** | Enumerated data inputs with provenance |
| **Assumptions** | Explicit list of assumptions made |
| **Freshness** | Timestamp of each data source's last refresh |
| **Financial Model Version** | Version of the financial model used (if applicable) |
| **Policy Notes** | Policy rules evaluated and their pass/fail status |
| **Alternatives Considered** | Other options evaluated and why they were ranked lower |
| **Rollback / Compensation Plan** | Steps to reverse the decision if needed |
| **Approval Class** | L1, L2, or L3 |
| **Reversibility Class** | R1, R2, R3, or R4 |

---

## Contradiction Engine (محرك التناقضات)

A dedicated subsystem that detects mismatches between what the system intended, what it claimed, and what actually happened.

### Contradiction Dashboard Fields

| Field | Description |
|---|---|
| **Intended Action** | What the decision plane recommended |
| **Claimed Action** | What the execution plane reported it did |
| **Actual Tool Call** | What the tool verification ledger recorded |
| **Side Effects** | Observed downstream changes (DB writes, API calls, notifications) |
| **Contradiction Status** | `clean` · `mismatch_detected` · `under_investigation` · `resolved` |

---

## Saudi Market Sovereignty (السيادة في السوق السعودي)

Dealix is built for Saudi Arabia first. Compliance is not bolted on — it is woven into every plane.

### PDPL Compliance (نظام حماية البيانات الشخصية)

- **Personal data** is broadly defined: any data from any source in any format that identifies or can identify an individual.
- **Processing** includes: collection, recording, storage, indexing, retrieval, use, disclosure, transfer, publication, linking, blocking, erasure, and destruction.
- Every data operation in the Data Plane is tagged with its PDPL processing basis.

### ECC 2-2024 (ضوابط الأمن السيبراني)

- Updated national cybersecurity controls from NCA.
- Mapped to Trust Plane policy rules and Operating Plane release gates.

### NIST AI RMF

- Risk management framework for AI systems.
- Applied to Decision Plane model governance, bias detection, and output validation.

### OWASP LLM Top 10

Protection against:

- Prompt injection
- Insecure output handling
- Sensitive information disclosure
- All other OWASP LLM attack vectors

### Arabic-First (الأولوية للعربية)

The following operations are Arabic-native by default:

| Operation | Description |
|---|---|
| Classification | Entity and intent classification in Arabic |
| Memo Generation | Board memos, investment memos, partner summaries |
| Board Packs | Full board pack generation in Arabic |
| Approval Reasons | Approval/rejection justifications in Arabic |
| Notifications | All system notifications localized to Arabic |
| Partner Summaries | Partner profiles and scorecards in Arabic |
| Search / Retrieval | Arabic semantic search via pgvector |
| Executive UI | All executive surfaces render in Arabic |
| Terminology Normalization | Consistent Arabic business terminology across the platform |

---

## Readiness Criteria (معايير الجاهزية)

Dealix is **not enterprise-ready** until every criterion below is satisfied:

| # | Criterion | Plane(s) |
|---|---|---|
| 1 | Every business-critical decision is **structured + evidence-backed + schema-bound** | Decision |
| 2 | Every long-running commitment is **durable + resumable + crash-tolerant** | Execution |
| 3 | Every sensitive action carries **approval / reversibility / sensitivity metadata** | Trust |
| 4 | Every connector is **versioned with retry / idempotency / audit mapping** | Data |
| 5 | Every release has **rulesets + environments + OIDC + provenance** | Operating |
| 6 | Every surface is **traceable via OpenTelemetry + correlation IDs** | All |
| 7 | Every enterprise deployment has **security review + red-team for LLM/tool execution surfaces** | Trust, Operating |
| 8 | Every sensitive Saudi workflow has **PDPL / NCA / AI governance mapping** | Trust, Data |

---

> **End of Canonical Architecture Reference**
>
> This document is maintained under version control. All changes require review from CODEOWNERS and must pass the `docs-lint` status check before merge.

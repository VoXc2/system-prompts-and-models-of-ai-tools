# Dealix — Approval & Policy Matrix

> **Owner:** Governance & Trust Squad
> **Review cadence:** Quarterly
> **Enforcement:** `backend/app/services/governance_engine.py`

---

## Action Classification System

Every action in Dealix carries three mandatory classifications:

### 1. Approval Class

| Class | Who Approves | Examples |
|---|---|---|
| **A0** | No approval (auto-execute with logging) | Scoring, routing, enrichment, internal analysis, test runs, memo drafts |
| **A1** | Manager | Outreach sequences, follow-up cadences, partner longlist, meeting agendas |
| **A2** | Director + Legal/Finance review | Term sheets, discount overrides, DD initiation, market entry prep |
| **A3** | CXO / Executive Committee | Acquisition offers, JV signing, market launch, stop-loss triggers |
| **A4** | Board resolution | Acquisitions > 10M SAR, strategic pivots, regulated market entry |

### 2. Reversibility Class

| Class | What It Means | Examples |
|---|---|---|
| **R0** | Fully auto-reversible | Draft generation, scoring recalculation, internal memo |
| **R1** | Reversible with limited ops effort | Email sequence pause, meeting reschedule, partner longlist edit |
| **R2** | Costly/painful to reverse | Sent term sheet, published pricing, activated partner |
| **R3** | Irreversible / creates external commitment | Signed contract, acquisition offer, regulatory filing |

### 3. Sensitivity Class

| Class | Data Handling | Examples |
|---|---|---|
| **S0** | Public / low sensitivity | Marketing content, public pricing, job listings |
| **S1** | Internal operational | Pipeline metrics, internal memos, team assignments |
| **S2** | Confidential / commercially sensitive | Partner financials, M&A targets, valuation models |
| **S3** | Regulated / highly sensitive | Personal data (PDPL), board deliberations, legal privileged |

---

## Combined Policy Rules

| Rule | Enforcement |
|---|---|
| **R0/R1 + A0** may auto-execute | Governance engine auto-approves |
| **R2** requires explicit HITL approval | Governance engine escalates |
| **R3** requires A2+ approval with evidence pack | Governance engine blocks without pack |
| **S2/S3 data** may NOT cross tool/provider boundaries without policy review | Routing layer enforces |
| **S3 data** requires audit trail + encryption at rest + access logging | Data plane enforces |

---

## Agent Role Classification

Every agent is classified as exactly one of:

| Role | Can Do | Cannot Do |
|---|---|---|
| **Observer** | Detect, summarize, monitor, score | Commit, send, sign, modify external state |
| **Recommender** | Analyze, propose, compare scenarios, generate memos | Commit directly, bypass HITL |
| **Executor** | Trigger commitments via execution plane | Act without policy gate, skip evidence |

**No agent may operate outside its role classification.**

### Current Agent Assignments

| Agent | Role | Approval Class |
|---|---|---|
| partnership_scout | Observer | A0 |
| alliance_structuring | Recommender | A2 |
| ma_screener | Observer | A0 |
| dd_analyst | Recommender | A2 |
| valuation_synergy | Recommender | A3 |
| strategic_pmo | Executor | A1 |
| expansion_playbook | Recommender | A2 |
| executive_negotiator | Recommender | A3 |
| post_merger_integration | Executor | A2 |
| sovereign_growth | Observer | A0 |

---

## Governance Engine Integration

### How It Works

```python
from app.services.governance_engine import get_governance_engine

engine = get_governance_engine()
result = await engine.evaluate(
    tenant_id=tenant.id,
    action_type="ma.submit_loi",
    actor="valuation_synergy",
    amount_sar=5_000_000,
    context={
        "risk_memo": True,
        "compliance_cleared": True,
        "financial_data_age_days": 12,
        "dd_completed": True,
    }
)

if result.decision == "auto_approved":
    # Proceed
elif result.decision == "escalated":
    # Route to HITL via /strategic/pending-approvals
elif result.decision == "denied":
    # Policy gate failed — log and notify
```

### 5 Mandatory Policy Gates

| Gate ID | Description | Applies To | Severity |
|---|---|---|---|
| PG-001 | Risk memo must exist before term sheet | Partnership signing, M&A LOI/offer | Blocking |
| PG-002 | Compliance clearance for new market entry | Market launch | Blocking |
| PG-003 | Financial inputs < 30 days old for valuation | M&A LOI/offer | Blocking |
| PG-004 | PDPL consent verified before bulk outreach | Mass messaging | Blocking |
| PG-005 | DD completed before acquisition offer | M&A offer | Blocking |

---

## Escalation Matrix

| Severity | Response SLA | Escalated To | Examples |
|---|---|---|---|
| **P1** — Business-critical | 1 hour | CXO + PMO | System-wide outage, data breach, regulatory violation |
| **P2** — Revenue-impacting | 4 hours | Director + PMO | Pipeline workflow failure, integration down, SLA breach |
| **P3** — Process deviation | 24 hours | Manager | Policy violation (non-critical), approval timeout |
| **P4** — Improvement | Next sprint | Team lead | Performance optimization, UX improvement |

---

## Evidence Pack Requirements

Every Class B/C decision must produce an **Evidence Pack** containing:

| Component | Required for A2 | Required for A3/A4 |
|---|---|---|
| Decision Memo (AR/EN) | Yes | Yes |
| Financial Impact Model | Yes | Yes |
| Risk Register | Yes | Yes |
| Data Sources + Freshness | Yes | Yes |
| Alternatives Considered | No | Yes |
| Scenario Analysis | No | Yes |
| Compliance Notes | Conditional | Yes |
| Rollback Plan | Conditional | Yes |
| Contradiction Report | If any | Yes |
| Board Summary (1 page) | No | Yes |

---

## Audit Trail Requirements

| What | Retention | Storage |
|---|---|---|
| All governance decisions | 24 months minimum | Event store + external backup |
| Evidence packs | 36 months for M&A, 24 months otherwise | Document store |
| Tool verification records | 12 months | Verification ledger |
| Approval records | 24 months | Audit log |
| Policy violation records | 36 months | Compliance store |

# Agent Role Registry

> **Version:** 1.0 — 2026-04-16
> **Authority:** This registry is the single source of truth for agent roles and action metadata.
> Every new agent PR must reference this registry. Any new role or action metadata field requires Platform Architect sign-off.

---

## Role Definitions

### Observer

- **Purpose:** Collect, monitor, and report data. No external write actions.
- **Permitted actions:** read CRM, read KB, read telemetry, emit structured observations
- **Forbidden actions:** write to external systems, trigger approvals, execute financial actions
- **Output schema:** `memo.schema.json` with `agent_role: Observer`, `approval_required: false`
- **Examples:** Market Scanner, Lead Scorer, Conversation Listener, Health Monitor, Billing Watch

### Recommender

- **Purpose:** Analyse observations and propose actions. Cannot execute.
- **Permitted actions:** all Observer actions + generate recommendations + trigger HITL approval requests
- **Forbidden actions:** direct write to external systems without human review, execute financial transactions
- **Output schema:** `memo.schema.json` with `agent_role: Recommender`, `approval_required: true` for HIGH/CRITICAL sensitivity
- **Examples:** Outreach Advisor, Qualification Advisor, Proposal Writer, Negotiation Advisor, Upsell Advisor

### Executor

- **Purpose:** Execute approved actions. Always requires a valid `approval_packet_id` for HIGH/CRITICAL sensitivity.
- **Permitted actions:** write to external systems (CRM, DocuSign, WhatsApp, billing) **after** valid approval
- **Required conditions:** `approval_packet.status = approved` OR `sensitivity ∈ {low, medium}` with OPA pass
- **Output schema:** `execution_intent.schema.json` — must include `idempotency_key` and `approval_packet_id`
- **Examples:** Outreach Sender, Booking Agent, Proposal Sender, Counter-offer Sender, DocuSign Trigger, Renewal Trigger

---

## Action Metadata Definitions

| Field | Type | Values | Description |
|-------|------|--------|-------------|
| `approval_required` | boolean | true / false | Must a human approve before execution? |
| `reversibility` | enum | `irreversible` · `reversible` · `compensatable` | Can the action be undone? |
| `sensitivity` | enum | `low` · `medium` · `high` · `critical` | Risk level of the action |
| `provenance_score` | float 0–1 | — | Fraction of claims backed by traceable sources |
| `freshness_score` | float 0–1 | — | Recency of underlying data (0=stale, 1=real-time) |
| `confidence_score` | float 0–1 | — | Model confidence in the recommendation/action |
| `data_residency` | enum | `KSA` · `EU` · `US` · `GLOBAL` | Where data is processed/stored |

---

## Approval Thresholds

| Sensitivity | Reversibility | Approval Required | Approver |
|-------------|--------------|-------------------|---------|
| low | any | No (OPA pass sufficient) | — |
| medium | reversible | No (OPA pass sufficient) | — |
| medium | irreversible / compensatable | Yes | Team Lead |
| high | any | Yes | Department Head |
| critical | any | Yes + dual approval | C-Suite + Legal |

---

## Registered Agents (2026-04-16)

| Agent | Role | Track | Sensitivity Range | Durable Workflow? |
|-------|------|-------|-----------------|-----------------|
| Market Scanner | Observer | Prospecting | low | No |
| Lead Scorer | Observer | Prospecting | low | No |
| Outreach Advisor | Recommender | Prospecting | medium | No |
| Outreach Sender | Executor | Prospecting | medium–high | No |
| Conversation Listener | Observer | Qualification | low | No |
| Qualification Advisor | Recommender | Qualification | medium | No |
| Booking Agent | Executor | Qualification | medium | No |
| Proposal Analyzer | Observer | Proposal | low–medium | No |
| Proposal Writer | Recommender | Proposal | medium | No |
| Proposal Sender | Executor | Proposal | high | No |
| Deal Monitor | Observer | Negotiation | low | No |
| Negotiation Advisor | Recommender | Negotiation | high | No |
| Counter-offer Sender | Executor | Negotiation | high | Yes → Temporal |
| Signature Tracker | Observer | Closing | medium | No |
| Closing Advisor | Recommender | Closing | high | No |
| DocuSign Trigger | Executor | Closing | critical | Yes → Temporal |
| Health Monitor | Observer | Post-Sale | low | No |
| Billing Watch | Observer | Post-Sale | medium | No |
| Upsell Advisor | Recommender | Post-Sale | medium | No |
| Renewal Trigger | Executor | Post-Sale | high | Yes → Temporal |
| PMI Agent | Executor | Post-Sale | critical | Yes → Temporal |

---

## Adding a New Agent — Checklist

- [ ] Assign role (Observer / Recommender / Executor)
- [ ] Define action metadata (all 7 fields)
- [ ] Add row to registry table above
- [ ] Reference registry in agent code file (comment: `# Role: Executor — see agent-role-registry.md`)
- [ ] If Executor: ensure output conforms to `execution_intent.schema.json`
- [ ] If Executor + HIGH/CRITICAL: add HITL interrupt in LangGraph graph
- [ ] If long-lived-durable: add Temporal workflow stub
- [ ] OPA policy pack updated for new agent's permissions
- [ ] OpenFGA model updated for new agent's authorization scope
- [ ] PR reviewed by AI Lead + Security Lead

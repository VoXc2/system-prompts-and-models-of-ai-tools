# Dealix Execution Matrix (Enterprise Commitments)

**Version**: 1.0  
**Status**: Active  
**Purpose**: Define what is auto-executed vs what must pass approval/policy gates.

---

## Automation Modes

- `AUTO`: fully automated without approval
- `AUTO_GATE`: automated preparation + mandatory approval before commit
- `HITL`: human-in-the-loop operation by design

---

## Sales & Revenue OS

| Step | Mode | Default Classes | System Action |
|------|------|-----------------|--------------|
| Lead capture (web/WhatsApp/email/import) | AUTO | A0/R0/S1 | Ingest + entity link |
| Enrichment and profile stitching | AUTO | A0/R0/S1 | Append verified attributes |
| Scoring, qualification, routing | AUTO | A0/R0/S1 | Route to queue/owner |
| Personalized follow-up drafting | AUTO | A0/R0/S1 | Draft + schedule |
| Meeting orchestration and reminders | AUTO | A0/R0/S1 | Book/update reminders |
| Proposal/CPQ draft generation | AUTO | A0/R1/S1 | Generate draft pack |
| Non-standard discount approval | AUTO_GATE | A2/R2/S2 | Pause + approval request |
| Non-standard terms approval | AUTO_GATE | A2/R2/S2 | Pause + legal/policy check |
| E-signature trigger | AUTO_GATE | A2/R3/S2 | Trigger only after approval |
| Final commercial commitment | HITL | A3/R3/S3 | Human finalization required |

## Partnership OS

| Step | Mode | Default Classes | System Action |
|------|------|-----------------|--------------|
| Partner scouting | AUTO | A0/R0/S1 | Discover + rank |
| Strategic fit scoring | AUTO | A0/R0/S1 | Scorecard generation |
| Channel economics modeling | AUTO | A0/R1/S1 | Financial model draft |
| Alliance structure draft | AUTO | A0/R1/S1 | Structure recommendation |
| Term sheet drafting | AUTO | A0/R1/S2 | Draft terms package |
| Term sheet send | AUTO_GATE | A2/R2/S2 | Gate before outbound |
| Rev-share / exclusivity changes | AUTO_GATE | A3/R3/S3 | Executive approval required |
| Signature orchestration | AUTO_GATE | A2/R3/S2 | Trigger by approved packet |
| Activation plan and scorecards | AUTO | A0/R1/S1 | Launch tasks + KPIs |

## M&A / Corporate Development OS

| Step | Mode | Default Classes | System Action |
|------|------|-----------------|--------------|
| Target sourcing and screening | AUTO | A0/R0/S1 | Build target list |
| Management/ownership mapping | AUTO | A0/R0/S2 | Graph + confidence score |
| DD request orchestration | AUTO | A0/R1/S2 | Request checklist flow |
| DD room control and tracking | AUTO | A0/R1/S2 | Permissions + status |
| Legal/financial/product/security DD streams | AUTO | A0/R1/S2 | Multi-stream orchestration |
| Valuation and synergy model draft | AUTO | A0/R1/S2 | Model + assumptions |
| IC / board pack draft | AUTO | A0/R1/S2 | Assemble evidence packet |
| Offer strategy recommendation | AUTO | A0/R1/S2 | Scenarios + limits |
| Offer submission | AUTO_GATE | A3/R3/S3 | Board-level approval gate |
| Signing / close workflow | AUTO_GATE | A3/R3/S3 | Controlled finalization |

## Expansion OS

| Step | Mode | Default Classes | System Action |
|------|------|-----------------|--------------|
| Market scanning and segmentation | AUTO | A0/R0/S1 | Opportunity map |
| Regulatory/readiness assessment | AUTO | A0/R1/S2 | Compliance checklist |
| Pricing/channel strategy draft | AUTO | A0/R1/S1 | GTM options |
| Localized GTM planning | AUTO | A0/R1/S1 | Launch plan draft |
| Launch readiness checks | AUTO | A0/R1/S2 | Readiness score |
| Canary launch execution | AUTO_GATE | A2/R2/S2 | Gate + blast-radius limits |
| Stop-loss and rollback trigger | AUTO | A0/R1/S2 | Automatic guardrail response |
| Full rollout | AUTO_GATE | A3/R3/S2 | Executive approval required |

## PMI / Strategic PMO OS

| Step | Mode | Default Classes | System Action |
|------|------|-----------------|--------------|
| Day-1 readiness | AUTO | A0/R1/S2 | Readiness pack |
| 30/60/90 planning | AUTO | A0/R1/S1 | Structured plan generation |
| Workstream/task assignment | AUTO | A0/R1/S1 | Owner + SLA assignment |
| Dependency and risk tracking | AUTO | A0/R1/S2 | Critical path + alerts |
| Escalation routing | AUTO | A0/R1/S2 | Escalation board updates |
| Synergy realization updates | AUTO | A0/R1/S1 | KPI deltas |
| Executive intervention requests | AUTO_GATE | A2/R2/S2 | Approval center routing |

## Executive / Board OS

| Step | Mode | Default Classes | System Action |
|------|------|-----------------|--------------|
| Executive room memo rendering | AUTO | A0/R0/S1 | Board-ready view |
| Evidence pack linking | AUTO | A0/R0/S1 | Immutable references |
| Policy violations surfacing | AUTO | A0/R1/S2 | Violation board entries |
| Next-best-action recommendation | AUTO | A0/R1/S1 | Prioritized options |
| Critical decision sign-off | HITL | A3/R3/S3 | Human decision with audit |

---

## Cross-System Rules

1. Any `R2/R3` action is blocked until policy and approval return `ALLOW`.
2. Any `S2/S3` action requires explicit `policy_refs`.
3. Any action producing external legal/financial commitment requires evidence pack attachment.
4. Any commitment with duration > 24h requires durable workflow registration.
5. All executed actions must produce a tool verification receipt.


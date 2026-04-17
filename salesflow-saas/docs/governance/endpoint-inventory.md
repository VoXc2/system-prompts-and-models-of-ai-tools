# Endpoint Inventory — Trust Classification

> **Parent**: [`MASTER_OPERATING_PROMPT.md`](../../MASTER_OPERATING_PROMPT.md)  
> **Purpose**: Every endpoint classified by risk, side effects, and trust requirements.

---

## Classification Key

| Class | Meaning | Trust Requirements |
|-------|---------|-------------------|
| **A** | Safe auto — read-only, no side effects | None |
| **B** | Approval-gated — causes side effects or external communication | correlation_id + approval_token |
| **B+** | Critical — financial, legal, or irreversible | correlation_id + approval_token + evidence_pack |
| **C** | Forbidden — never allowed via API | Blocked unconditionally |

---

## Tier-1 Governance Endpoints

| Endpoint | Method | Class | Side Effects | Trust Enforced |
|----------|--------|-------|-------------|---------------|
| `/executive-room/snapshot` | GET | A | None | — |
| `/executive-room/weekly-pack` | GET | A | None | — |
| `/executive-room/risks` | GET | A | None | — |
| `/executive-room/decisions-pending` | GET | A | None | — |
| `/executive-room/forecast-vs-actual` | GET | A | None | — |
| `/approval-center/` | GET | A | None | — |
| `/approval-center/stats` | GET | A | None | — |
| `/approval-center/{id}/approve` | POST | **B+** | Updates approval status | correlation_id via payload |
| `/approval-center/{id}/reject` | POST | **B+** | Updates approval status | correlation_id via payload |
| `/approval-center/{id}/escalate` | POST | **B** | Escalation notification | — |
| `/contradictions/` | GET | A | None | — |
| `/contradictions/` | POST | A | Creates record | — |
| `/contradictions/stats` | GET | A | None | — |
| `/contradictions/{id}/resolve` | POST | **B** | Status update | — |
| `/evidence-packs/assemble` | POST | **B** | Creates SHA256 pack | — |
| `/evidence-packs/` | GET | A | None | — |
| `/evidence-packs/{id}/review` | PUT | **B** | Status update | — |
| `/evidence-packs/{id}/verify` | GET | A | None | — |
| `/compliance/matrix/` | GET | A | None | — |
| `/compliance/matrix/scan` | POST | A | Updates control status | — |
| `/compliance/matrix/posture` | GET | A | None | — |
| `/compliance/matrix/risk-heatmap` | GET | A | None | — |
| `/connectors/governance` | GET | A | None | — |
| `/connectors/{key}/health-check` | POST | A | Updates status | — |
| `/model-routing/dashboard` | GET | A | None | — |
| `/model-routing/health` | GET | A | None | — |
| `/model-routing/costs` | GET | A | None | — |
| `/forecast-control/unified` | GET | A | None | — |
| `/forecast-control/variance` | GET | A | None | — |
| `/forecast-control/recalibrate` | POST | **B** | Triggers AI reforecast | — |
| `/golden-path/run` | POST | **B+** | Creates approval + evidence | correlation_id generated |
| `/golden-path/dossier` | POST | A | None (generates schema) | — |

---

## Core Business Endpoints

| Endpoint | Method | Class | Side Effects | Trust Required |
|----------|--------|-------|-------------|---------------|
| `/leads` | GET | A | None | — |
| `/leads` | POST | A | Creates record | — |
| `/leads/import` | POST | **B** | Bulk create | — |
| `/deals` | GET | A | None | — |
| `/deals` | POST | A | Creates record | — |
| `/deals/{id}/stage` | PUT | **B+** | Stage change + auto evidence on close | Auto evidence on closed_won |
| `/deals/{id}` | DELETE | **B** | Soft delete | — |

---

## External Communication Endpoints

| Endpoint | Method | Class | Side Effects | Trust Required |
|----------|--------|-------|-------------|---------------|
| `/outreach/*` | POST | **B** | Sends WhatsApp/email/SMS | PDPL consent + approval_token |
| `/sequences/*` | POST | **B** | Starts multi-channel sequence | PDPL consent + approval_token |
| `/whatsapp-webhook` | POST | A | Processes inbound | Webhook verification |

---

## Strategic Deal Endpoints

| Endpoint | Method | Class | Side Effects | Trust Required |
|----------|--------|-------|-------------|---------------|
| `/strategic-deals/` | GET | A | None | — |
| `/strategic-deals/` | POST | **B** | Creates deal | — |
| `/strategic-deals/{id}/negotiate` | POST | **B+** | Negotiation action | correlation_id |
| `/strategic-deals/match` | POST | A | AI matching | — |

---

## Summary

| Class | Count | Enforcement Status |
|-------|-------|--------------------|
| A (safe auto) | ~45 | No enforcement needed |
| B (approval-gated) | ~15 | correlation_id enforced via gateway |
| B+ (critical) | ~6 | correlation_id + evidence (golden path enforced) |
| C (forbidden) | 5 | Blocked in policy.py |

# Workflow Inventory — Execution Plane

> **Version:** 1.0 — 2026-04-16
> **Purpose:** Classify every background task and workflow for correct runtime placement.
> **Classification Rules:**
> - `short-lived-local`: duration < 15 min, single service, no compensation → Celery / LangGraph
> - `medium-lived-queued`: 15 min–4 h, ≤ 2 services, simple retry → Celery + idempotency key
> - `long-lived-durable`: > 4 h, OR crosses 2+ services, OR needs compensation → **Temporal (mandatory)**

---

## Current Workflows — Classification Table

| Workflow / Task | Current Runtime | Duration Estimate | Systems Crossed | Compensation Needed? | Classification | Target Runtime | Migration Priority | WS Ref |
|----------------|----------------|-------------------|----------------|---------------------|---------------|---------------|-------------------|--------|
| Lead scoring batch | Celery beat | < 5 min | Postgres | No | short-lived-local | Celery | Low | — |
| Outreach message queue | Celery | < 10 min | WhatsApp/Twilio | No | short-lived-local | Celery | Low | — |
| Booking confirmation | Celery | < 2 min | Calendar API, CRM | No | short-lived-local | Celery | Low | — |
| Proposal PDF generation | Celery | < 5 min | Storage | No | short-lived-local | Celery | Low | — |
| Email sequence drip | Celery beat | Days (recurring) | Email, CRM | No | long-lived-durable | **Temporal** | HIGH | WS 3.3 |
| Partner approval flow | Celery + ad-hoc | Hours–Days | CRM, DocuSign, Notifications | Yes | long-lived-durable | **Temporal** | HIGH (Pilot) | WS 3.3 |
| Due Diligence room setup | Manual + partial Celery | Days | Storage, CRM, NDA service | Yes | long-lived-durable | **Temporal** | HIGH | WS 3.3 |
| DocuSign signature request + tracking | Celery | Hours–Days | DocuSign, CRM, Notification | Yes (void if timeout) | long-lived-durable | **Temporal** | HIGH | WS 3.3 |
| Billing renewal cycle | Celery beat | Monthly (recurring) | Billing, CRM, WhatsApp | Yes (refund if error) | long-lived-durable | **Temporal** | HIGH | WS 3.6 |
| Post-merger integration (PMI) tasks | Manual | Weeks | CRM, Billing, Storage, Notifications | Yes | long-lived-durable | **Temporal** | MEDIUM | WS 3.6 |
| Upsell campaign orchestration | LangGraph (partial) | Hours | CRM, Email, WhatsApp | No | medium-lived-queued | Celery + idempotency | MEDIUM | — |
| KB embedding sync | Celery beat | < 30 min | Postgres/pgvector | No | medium-lived-queued | Celery + idempotency | Low | — |
| Analytics aggregation | Celery beat | < 1 h | Postgres | No | medium-lived-queued | Celery | Low | — |
| Red-team eval runs | Ad-hoc script | < 2 h | AI model API | No | medium-lived-queued | Celery | Low | — |

---

## Temporal Pilot Scope (Sprint 3–4)

**Selected workflow:** Partner Approval Flow

**Rationale:** Most representative of long-lived-durable patterns; crosses CRM, DocuSign, and notification systems; requires compensation on rejection.

### Partner Approval Workflow — State Machine

```
START
  │
  ├─► validate_partner_data (activity)
  │     └─► emit evidence_pack_json
  │
  ├─► create_approval_packet (activity)
  │     └─► emit approval_packet_json with status=pending
  │
  ├─► HITL_gate (LangGraph interrupt OR Temporal signal)
  │     ├─► approved  ──► execute_crm_update (activity)
  │     │                  execute_docusign_request (activity)
  │     │                  send_confirmation_notification (activity)
  │     │                  END (status=completed)
  │     │
  │     └─► rejected  ──► compensation: void_crm_draft (activity)
  │                        send_rejection_notification (activity)
  │                        END (status=rejected)
  │
  └─► timeout (configurable, default 72 h)
        └─► compensation: void_crm_draft (activity)
             send_expiry_notification (activity)
             END (status=expired)
```

### Idempotency Key Format

```
{tenant_id}:{workflow_type}:{entity_id}:{date_yyyymmdd}
Example: "acme-corp:partner_approval:partner-uuid-123:20260416"
```

### Compensation Policy

| Failure Point | Compensation Action |
|--------------|-------------------|
| After CRM update, before DocuSign | Revert CRM draft status |
| After DocuSign sent, before signature | Void envelope via DocuSign API |
| Timeout (72 h) | Void drafts, notify all parties |

---

## Temporal Infrastructure Requirements

```yaml
# docker-compose.temporal.yml (local dev)
services:
  temporal:
    image: temporalio/auto-setup:1.26
    ports: ["7233:7233"]
    environment:
      - DB=postgres12
      - DB_PORT=5432
      - POSTGRES_USER=temporal
      - POSTGRES_PWD=temporal
      - POSTGRES_SEEDS=postgres

  temporal-ui:
    image: temporalio/ui:2.34
    ports: ["8080:8080"]
    environment:
      - TEMPORAL_ADDRESS=temporal:7233

  temporal-worker:
    build: ./backend
    command: python -m app.temporal.worker
    depends_on: [temporal]
    environment:
      - TEMPORAL_HOST=temporal:7233
      - TEMPORAL_NAMESPACE=dealix-dev
```

---

## Versioning Strategy

Use `workflow.get_version()` for any breaking change to a workflow definition:

```python
# Pattern: version-gated activity call
v = workflow.get_version("add-dual-approval", workflow.DEFAULT_VERSION, 1)
if v == 1:
    await workflow.execute_activity(dual_approval_activity, ...)
else:
    await workflow.execute_activity(single_approval_activity, ...)
```

**Rules:**
1. Never remove a version branch while in-flight workflows exist on that version.
2. Bump version ID for: new activities, changed activity signatures, new signals, changed compensation logic.
3. Old workers must remain deployed until all in-flight workflows on the old version complete.

---

## Open Items (to resolve in Sprint 2)

| Item | Decision Needed | Owner | Sprint |
|------|----------------|-------|--------|
| Temporal hosting: self-hosted Docker vs Temporal Cloud | Cost/ops trade-off | Platform Engineer | Sprint 1 |
| Temporal namespace strategy: single vs per-environment | Isolation vs ops overhead | Platform Engineer | Sprint 1 |
| LangGraph ↔ Temporal handoff pattern | How HITL signal flows from LangGraph interrupt to Temporal signal | AI Lead + Backend Lead | Sprint 2 |
| Celery task deprecation timeline | Which tasks stay, which migrate | Backend Lead | Sprint 3 |

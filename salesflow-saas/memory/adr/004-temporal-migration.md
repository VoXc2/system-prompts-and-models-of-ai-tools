# ADR-004: Temporal Migration Strategy for Durable Workflows — استراتيجية الانتقال إلى Temporal

**Date**: 2026-04-16  
**Status**: proposed  
**Deciders**: CTO, Backend Lead, DevOps Lead  

## Context

Dealix currently uses two execution runtimes:
1. **Celery** (7 task modules) — short-lived async tasks: message dispatch, sequence processing, agent background runs, affiliate reporting, notifications, follow-ups
2. **OpenClaw DurableTaskFlow** (2 flows) — medium-lived checkpointed flows: prospecting and self-improvement

Business-critical processes like partner approvals, deal room workflows, signature requests, product launches, and post-merger integration require:
- **Crash recovery**: workflow resumes after process/server restart
- **Long-running state**: workflows that span hours to weeks
- **Compensation**: rollback/undo for partially completed multi-system operations
- **Versioning**: update workflow logic without breaking in-flight executions
- **Visibility**: inspect running workflow state, history, and pending timers

Celery provides none of these guarantees. OpenClaw provides checkpointing but lacks compensation, versioning, and enterprise-grade visibility.

## Decision

### Migration Criteria

Any workflow that meets **one or more** of the following criteria MUST migrate to Temporal:

| Criterion | Threshold | Rationale |
|-----------|-----------|-----------|
| Duration | >15 minutes | Exceeds reasonable Celery task timeout |
| System span | Crosses >2 external systems | Needs compensation on partial failure |
| Compensation required | Any rollback/undo needed | Celery has no saga support |
| Human approval | Requires HITL mid-workflow | Temporal supports long-lived waits natively |
| Regulatory audit | Workflow must be fully reconstructable | Temporal event history provides this |

### Three-Tier Execution Model

| Tier | Runtime | When to Use | Examples |
|------|---------|-------------|---------|
| **Short-lived** | Celery | <15 min, single system, fire-and-forget | Message dispatch, notification digest, follow-up processing |
| **Medium-lived** | OpenClaw DurableTaskFlow → Celery | 15 min–1 hr, checkpointed, no compensation needed | Self-improvement cycle, prospecting batch |
| **Long-lived** | Temporal | >15 min OR multi-system OR compensation OR HITL | Partner approval, DD room, signature request, launch sequence |

### Migration Approach

1. **Phase 1 — Infrastructure**: Add Temporal server to Docker Compose dev stack; add `temporalio` SDK to backend requirements
2. **Phase 2 — Pilot**: Migrate one workflow (partner approval flow) to Temporal; validate crash recovery, compensation, and visibility
3. **Phase 3 — Gradual migration**: Prioritize remaining long-lived workflows by business criticality; migrate one at a time
4. **Phase 4 — Celery optimization**: Remaining Celery tasks stay; OpenClaw medium-lived flows evaluated case-by-case

### Coexistence Rules

- Celery and Temporal run side-by-side indefinitely; this is not an all-or-nothing migration
- Temporal workers are separate Python processes (not mixed into Celery workers)
- Shared code (services, models, schemas) is consumed by both runtimes
- Temporal activities call the same service layer as Celery tasks (no duplication)

### Workflow Standards (for Temporal workflows)

| Standard | Requirement |
|----------|-------------|
| Idempotency | Every activity has an idempotency key; retries are safe |
| Compensation | Every side-effecting activity has a compensating activity |
| Versioning | Workflows use Temporal's `patched()` API for non-breaking changes; breaking changes get new workflow type |
| Observability | Every workflow emits OTel spans; `workflow_run_id` propagated as correlation ID |
| Timeout policy | Every activity has explicit `start_to_close_timeout` and `schedule_to_close_timeout` |
| Retry policy | Defined per activity type; exponential backoff; max attempts |

## Consequences

### Positive
- Business-critical workflows survive crashes and restarts
- Full audit trail via Temporal event history (regulatory compliance)
- Built-in visibility (Temporal UI) for running workflows
- Clean separation of short-lived (Celery) vs long-lived (Temporal) execution
- Compensation/saga pattern enables safe multi-system operations

### Negative
- Operational complexity: another infrastructure component (Temporal server, PostgreSQL for Temporal, Temporal UI)
- Learning curve for Temporal SDK (workflow/activity separation, deterministic constraints)
- Initial development velocity may decrease during pilot phase

### Risks and Mitigations

| Risk | Severity | Mitigation |
|------|----------|------------|
| Temporal learning curve | H | Dedicated spike; pair programming; single pilot flow first |
| Infrastructure overhead | M | Temporal runs in Docker for dev; managed Temporal Cloud for prod |
| Vendor lock-in | M | Temporal is open-source (MIT); self-hosted option always available |
| Migration disruption | M | Coexistence model; no big-bang migration; gradual adoption |

## Candidates for First Migration Wave

| Workflow | Current Runtime | Migration Priority | Reason |
|----------|----------------|-------------------|--------|
| Partner approval flow | Ad-hoc service calls | P0 — Pilot | Multi-day HITL; needs compensation; ideal pilot |
| DD room flow | Ad-hoc service calls | P1 | Multi-system; sensitive data; audit trail needed |
| Contract signature flow | `esign_service.py` (mock) | P1 | External system; long wait; compensation needed |
| Product launch sequence | Not implemented | P2 | Multi-system; regulatory checks; rollback needed |
| Post-merger integration | Not implemented | P2 | Long-running; many systems; complex compensation |

## Related

- [ADR-003: Five Operational Planes](003-five-operational-planes.md) — Execution Plane definition
- [COMPLETION_PROGRAM.md](../../docs/completion-program/COMPLETION_PROGRAM.md) — WS-3: Execution Plane Hardening
- [EXECUTION_MATRIX.md](../../docs/completion-program/EXECUTION_MATRIX.md) — WS-3 deliverables and SLAs

# Execution Fabric Specification

> How long-lived, multi-system, durable, or externally committing work is run. What agent loops must NEVER do.

---

## 1. What lives in the Execution Plane

Anything that is any of:
- long-lived (minutes to days)
- multi-system (coordinating across HubSpot, WhatsApp, Calendar, Email, etc.)
- needs retries, checkpoints, or compensation
- creates an external commitment
- needs idempotency across failures

---

## 2. What MUST NOT live inside an agent loop

- External commitments
- Writes to a customer system of record
- Sending an email, WhatsApp, or SMS
- Creating a calendar event
- Any multi-step workflow that must complete even if the process crashes mid-way

If it's on this list, it belongs to the Execution Plane.

---

## 3. Implementation phases

### Phase 0-1 — In-process orchestrator

The current `auto_client_acquisition.pipeline.AcquisitionPipeline` is a lightweight orchestrator with per-step error isolation. It is durable only across retries within one request. Good enough to start; insufficient for production-grade commitments.

### Phase 1-2 — LangGraph-style state machines

For flows that need HITL with interrupts (approval gates mid-flow, multi-step decisions spanning hours), introduce a stateful graph runtime. The `ExecutionRuntime` interface below is designed to accept either an in-process adapter or a LangGraph adapter without changing callers.

### Phase 2+ — Temporal for business-critical never-fail flows

One spike first: the proposal-send workflow. Evaluate operational cost (infra, monitoring, SDK ergonomics). Only expand after the spike proves value.

---

## 4. The ExecutionRuntime interface

```python
class ExecutionRuntime(Protocol):
    async def start(
        self,
        *,
        workflow_name: str,
        input: dict,
        idempotency_key: str,
        correlation_id: str,
        trace_id: str | None = None,
    ) -> WorkflowHandle: ...

    async def signal(self, workflow_id: str, name: str, payload: dict) -> None: ...
    async def cancel(self, workflow_id: str, reason: str) -> None: ...
    async def get(self, workflow_id: str) -> WorkflowState: ...
```

Implementations:
- `InProcessRuntime` — Phase 0-1 default
- `LangGraphRuntime` — Phase 1-2
- `TemporalRuntime` — Phase 2+

---

## 5. Workflow hygiene

Every workflow MUST:
- Accept an `idempotency_key` (prevents duplicate sends on retry)
- Propagate `trace_id` + `correlation_id`
- Log start / checkpoint / end via structured logs
- Emit events via the CloudEvents envelope
- Call the Policy Evaluator before any external-commit activity
- Record every tool call in the ToolVerificationLedger
- Have a named compensation path for every externally-visible step

---

## 6. Patterns

### 6.1 Saga with compensation

For multi-step external commitments (e.g. create CRM deal → send proposal email → schedule follow-up): each forward step has a compensating step. Failure after step 2 runs compensations for 2 then 1.

### 6.2 Idempotent writes

Every outbound API call that mutates external state MUST send an `Idempotency-Key` header where the provider supports it, or maintain a local `outbound_key → result` cache.

### 6.3 Outbox pattern

Commit an `outbox` row in the same DB transaction as the business change; a poller publishes it to the event envelope. Prevents lost events on crash.

### 6.4 HITL interrupts

A workflow that needs human approval calls the Approval Center and SUSPENDS. A webhook / polling resumes it when the ApprovalRequest resolves.

---

## 7. Retry policy

Default: exponential backoff with jitter, max 3 attempts, max 60s total wait. Overridable per-activity.

No retries for:
- 4xx responses that indicate caller error (400, 401, 403, 404, 422)
- Explicit "do not retry" side-effect errors

Always retry:
- 5xx, timeouts, connection errors (up to the cap)

---

## 8. Observability

Every workflow emits:
- `workflow.start`, `workflow.checkpoint`, `workflow.end` spans
- `activity.<name>` span per activity
- `activity.retry` span for each retry
- Events: `dealix.workflow.started`, `dealix.workflow.completed`, `dealix.workflow.failed`, `dealix.workflow.compensated`

Metrics:
- `workflow_duration_seconds{name,status}`
- `activity_retries_total{activity,reason}`
- `workflow_compensations_total{workflow,step}`

---

## 9. Mapping current Phase 8 steps

| Step | Plane | Rationale |
|---|---|---|
| IntakeAgent | Decision (agent-like but normalizer) | No external I/O |
| PainExtractorAgent | Decision | LLM inference |
| ICPMatcherAgent | Decision | Pure computation |
| QualificationAgent | Decision | LLM inference |
| CRMAgent upsert+deal | **Execution** | External mutation, needs retry + idempotency |
| BookingAgent | **Execution** (or facade call) | External mutation |
| ProposalAgent draft | Decision | LLM output, no send |
| ProposalAgent send | **Execution** | External commitment — MUST go through approval |
| OutreachAgent draft | Decision | LLM output |
| OutreachAgent send | **Execution** | External commitment |
| FollowUpAgent schedule | **Execution** | Timed external action |

The current implementation blurs some of these. Phase 1 refactor splits them cleanly.

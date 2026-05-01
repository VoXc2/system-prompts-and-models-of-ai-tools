# Trust Fabric Specification

> How the Trust Plane is assembled, what each component does, and the contracts that bind them.

This is a normative specification. Implementations in `dealix/trust/` MUST conform.

---

## 1. Components

| # | Component | Responsibility | Current implementation | Phase-2 target |
|---|---|---|---|---|
| 1 | Policy Evaluator | `ALLOW` / `DENY` / `ESCALATE` decisions | `dealix.trust.policy` (in-process rules) | OPA/Rego service |
| 2 | Approval Center | Queue + TTL + multi-approver grant/reject | `dealix.trust.approval` (in-memory) | Postgres-backed + real notifications |
| 3 | Authorization | Fine-grained access to rooms/memos/data | Role checks in API | OpenFGA |
| 4 | Identity | SSO, federation, roles | `.env` + stub user model | Keycloak |
| 5 | Secrets | Rotation, dynamic creds, audit | `.env` + `SecretStr` | HashiCorp Vault |
| 6 | Tool Verification | Intended vs actual action ledger | `dealix.trust.tool_verification` | Same, persisted |
| 7 | Audit | Immutable append-only log | `dealix.trust.audit.InMemoryAuditSink` | Postgres `audit_log` with partitioning |
| 8 | Evidence Pack Assembler | Bundle sources + tool calls + memo | `dealix.contracts.evidence_pack` | Same, with PDF export |
| 9 | AI Risk Controls | NIST RMF + OWASP LLM Top 10 | `compliance_saudi.yaml` | Enforced in eval harness |

---

## 2. Data flow

```
Agent produces DecisionOutput with NextActions
    ↓
for each NextAction:
    Policy Evaluator(NextAction, Decision) → PolicyResult
    ↓
    if ALLOW   → enqueue to Execution Plane (workflow)
    if DENY    → reject + audit; notify agent; return refusal
    if ESCALATE → submit to Approval Center with required_approvers
        ↓
        humans grant/reject via Approval Center UI
        ↓
        if GRANTED → enqueue to Execution Plane
        if REJECTED → audit + notify caller
        if TIMED_OUT → audit + notify; re-evaluate or drop
    ↓
    every step appends an AuditEntry
    every tool call in the workflow appends to the ToolVerificationLedger
```

---

## 3. Interface contracts

### 3.1 PolicyEvaluator

```python
class PolicyEvaluator(Protocol):
    def evaluate(
        self, action: NextAction, decision: DecisionOutput
    ) -> PolicyResult: ...

    def evaluate_all(
        self, decision: DecisionOutput
    ) -> list[tuple[NextAction, PolicyResult]]: ...
```

Returning `ALLOW` means the caller MAY proceed. Returning anything else means the caller MUST NOT proceed without handling the result.

### 3.2 ApprovalCenter

```python
class ApprovalCenter(Protocol):
    def submit(
        self,
        decision: DecisionOutput,
        action: NextAction,
        required_approvers: int,
        ttl_hours: int | None = None,
        evidence_pack_id: str | None = None,
    ) -> ApprovalRequest: ...

    def grant(self, request_id: str, approver_id: str) -> ApprovalRequest: ...
    def reject(self, request_id: str, approver_id: str, reason: str) -> ApprovalRequest: ...
    def check_timeouts(self) -> list[ApprovalRequest]: ...
    def list_pending(self, entity_id: str | None = None) -> list[ApprovalRequest]: ...
```

### 3.3 AuditSink

```python
class AuditSink(Protocol):
    def append(self, entry: AuditEntry) -> None: ...
    def recent(self, limit: int = 100) -> list[AuditEntry]: ...
```

### 3.4 ToolVerificationLedger

```python
class ToolVerificationLedger(Protocol):
    def record(
        self,
        *,
        tool_name: str,
        agent_name: str,
        intended_action: str,
        actual_action: str,
        decision_id: str | None = None,
        inputs: dict | None = None,
        outputs: dict | None = None,
        side_effects: list[str] | None = None,
    ) -> ToolInvocation: ...
```

---

## 4. Guarantees

- **Non-bypassable**: The Execution Plane MUST call `PolicyEvaluator.evaluate` for every NextAction before executing it. Bypass is a release-blocker bug.
- **Append-only audit**: `AuditSink` MUST NOT expose mutation. Append is the only operation.
- **Classification completeness**: `PolicyEvaluator` MUST refuse to evaluate a NextAction that lacks a full (A, R, S) classification. Fail-closed.
- **Evidence bound**: A2/A3 and R3 decisions without Evidence are rejected at the contract layer (Pydantic validator) before even reaching the evaluator.

---

## 5. Observability

Every Trust Plane call emits:
- `trust.policy.evaluate` span — attrs: `action_type`, `rule_matched`, `decision`
- `trust.approval.submit` / `trust.approval.grant` / `trust.approval.reject` / `trust.approval.timeout` spans
- `trust.tool.verify` span — attrs: `tool_name`, `contradiction_flag`
- `trust.audit.append` span — low sample rate

Metrics:
- `trust_policy_decisions_total{decision,rule}`
- `trust_approval_lag_seconds{status}`
- `trust_tool_contradictions_total{tool}`
- `trust_audit_entries_total{action}`

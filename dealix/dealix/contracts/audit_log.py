"""
Audit Log Contract — immutable record of every Trust Plane action.

Every policy evaluation, approval decision, tool verification, and sensitive
action is appended as an AuditEntry. Entries are append-only.
"""

from __future__ import annotations

import uuid
from datetime import UTC, datetime
from enum import StrEnum
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from dealix.classifications import ApprovalClass, ReversibilityClass, SensitivityClass


def _utcnow_iso() -> str:
    return datetime.now(UTC).isoformat()


def _new_audit_id() -> str:
    return f"aud_{uuid.uuid4().hex[:16]}"


class AuditAction(StrEnum):
    """The category of audited action."""

    DECISION_EMITTED = "decision.emitted"
    POLICY_EVALUATED = "policy.evaluated"
    POLICY_ALLOWED = "policy.allowed"
    POLICY_DENIED = "policy.denied"
    POLICY_ESCALATED = "policy.escalated"
    APPROVAL_REQUESTED = "approval.requested"
    APPROVAL_GRANTED = "approval.granted"
    APPROVAL_REJECTED = "approval.rejected"
    APPROVAL_TIMED_OUT = "approval.timed_out"
    TOOL_INVOKED = "tool.invoked"
    TOOL_VERIFIED = "tool.verified"
    TOOL_CONTRADICTED = "tool.contradicted"
    TOOL_BLOCKED = "tool.blocked"
    WORKFLOW_STARTED = "workflow.started"
    WORKFLOW_COMPLETED = "workflow.completed"
    WORKFLOW_FAILED = "workflow.failed"
    WORKFLOW_COMPENSATED = "workflow.compensated"
    ACCESS_GRANTED = "access.granted"
    ACCESS_DENIED = "access.denied"
    DATA_EXPORTED = "data.exported"


class AuditEntry(BaseModel):
    """A single audit log entry — append-only."""

    model_config = ConfigDict(extra="forbid")

    schema_version: str = "1.0"
    audit_id: str = Field(default_factory=_new_audit_id)
    tenant_id: str = "default"

    action: AuditAction
    actor_type: str = "system"  # system | agent | human | workflow
    actor_id: str | None = None

    # Link to what was audited
    decision_id: str | None = None
    entity_id: str | None = None
    event_id: str | None = None
    workflow_id: str | None = None

    # Classifications for fast filtering
    approval_class: ApprovalClass = ApprovalClass.A0
    reversibility_class: ReversibilityClass = ReversibilityClass.R0
    sensitivity_class: SensitivityClass = SensitivityClass.S1

    # Outcome
    outcome: str = "ok"  # ok | denied | escalated | failed | blocked
    reason: str | None = None

    # Free-form context (but never secrets or PII — Trust Plane strips those)
    details: dict[str, Any] = Field(default_factory=dict)

    trace_id: str | None = None
    correlation_id: str | None = None
    at: str = Field(default_factory=_utcnow_iso)

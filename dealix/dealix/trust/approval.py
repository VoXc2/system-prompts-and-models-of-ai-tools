"""
Approval Center — routes approval requests to humans and tracks their status.

In Phase 0–1 this is an in-memory store with callback hooks for notification
(email / Slack / WhatsApp). Phase 2 replaces it with a durable queue (Postgres
or a workflow runtime like Temporal).
"""

from __future__ import annotations

import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from typing import Any

from dealix.classifications import ApprovalClass
from dealix.contracts.decision import DecisionOutput, NextAction


class ApprovalStatus(StrEnum):
    PENDING = "pending"
    GRANTED = "granted"
    REJECTED = "rejected"
    TIMED_OUT = "timed_out"
    WITHDRAWN = "withdrawn"


@dataclass
class ApprovalRequest:
    request_id: str
    decision_id: str
    entity_id: str
    action_type: str
    action_description: str
    approval_class: ApprovalClass
    required_approvers: int
    approvers_needed: int  # remaining count
    evidence_pack_id: str | None = None
    status: ApprovalStatus = ApprovalStatus.PENDING
    granted_by: list[str] = field(default_factory=list)
    rejected_by: str | None = None
    reject_reason: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    expires_at: datetime | None = None
    resolved_at: datetime | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "request_id": self.request_id,
            "decision_id": self.decision_id,
            "entity_id": self.entity_id,
            "action_type": self.action_type,
            "action_description": self.action_description,
            "approval_class": self.approval_class.value,
            "required_approvers": self.required_approvers,
            "approvers_needed": self.approvers_needed,
            "status": self.status.value,
            "granted_by": self.granted_by,
            "rejected_by": self.rejected_by,
            "reject_reason": self.reject_reason,
            "created_at": self.created_at.isoformat(),
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "resolved_at": self.resolved_at.isoformat() if self.resolved_at else None,
            "metadata": self.metadata,
        }


class ApprovalCenter:
    """In-memory approval queue with pluggable notification hook."""

    def __init__(
        self,
        default_ttl_hours: int = 48,
        notifier: Callable[[ApprovalRequest], None] | None = None,
    ) -> None:
        self._requests: dict[str, ApprovalRequest] = {}
        self._default_ttl = timedelta(hours=default_ttl_hours)
        self._notifier = notifier

    def submit(
        self,
        decision: DecisionOutput,
        action: NextAction,
        required_approvers: int,
        ttl_hours: int | None = None,
        evidence_pack_id: str | None = None,
    ) -> ApprovalRequest:
        """Create a new approval request."""
        ttl = timedelta(hours=ttl_hours) if ttl_hours else self._default_ttl
        request = ApprovalRequest(
            request_id=f"apr_{uuid.uuid4().hex[:16]}",
            decision_id=decision.decision_id,
            entity_id=decision.entity_id,
            action_type=action.action_type,
            action_description=action.description,
            approval_class=action.approval_class,
            required_approvers=required_approvers,
            approvers_needed=required_approvers,
            evidence_pack_id=evidence_pack_id,
            expires_at=datetime.now(UTC) + ttl,
        )
        self._requests[request.request_id] = request
        if self._notifier:
            try:
                self._notifier(request)
            except Exception:
                pass  # notification failure must not break the queue
        return request

    def grant(self, request_id: str, approver_id: str) -> ApprovalRequest:
        """Record an approver's grant; flip status when threshold met."""
        request = self._get(request_id)
        if request.status != ApprovalStatus.PENDING:
            return request
        if approver_id in request.granted_by:
            return request
        request.granted_by.append(approver_id)
        request.approvers_needed = max(0, request.approvers_needed - 1)
        if request.approvers_needed == 0:
            request.status = ApprovalStatus.GRANTED
            request.resolved_at = datetime.now(UTC)
        return request

    def reject(self, request_id: str, approver_id: str, reason: str = "") -> ApprovalRequest:
        request = self._get(request_id)
        if request.status != ApprovalStatus.PENDING:
            return request
        request.status = ApprovalStatus.REJECTED
        request.rejected_by = approver_id
        request.reject_reason = reason
        request.resolved_at = datetime.now(UTC)
        return request

    def check_timeouts(self) -> list[ApprovalRequest]:
        """Mark expired pending requests as TIMED_OUT. Returns the flipped ones."""
        now = datetime.now(UTC)
        flipped: list[ApprovalRequest] = []
        for req in self._requests.values():
            if req.status == ApprovalStatus.PENDING and req.expires_at and req.expires_at < now:
                req.status = ApprovalStatus.TIMED_OUT
                req.resolved_at = now
                flipped.append(req)
        return flipped

    def get(self, request_id: str) -> ApprovalRequest | None:
        return self._requests.get(request_id)

    def list_pending(self, entity_id: str | None = None) -> list[ApprovalRequest]:
        return [
            r
            for r in self._requests.values()
            if r.status == ApprovalStatus.PENDING
            and (entity_id is None or r.entity_id == entity_id)
        ]

    def _get(self, request_id: str) -> ApprovalRequest:
        req = self._requests.get(request_id)
        if req is None:
            raise KeyError(f"Approval request not found: {request_id}")
        return req

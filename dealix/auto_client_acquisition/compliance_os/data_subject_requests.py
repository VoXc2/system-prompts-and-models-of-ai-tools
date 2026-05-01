"""
Data Subject Requests (DSR) — PDPL-compliant lifecycle.

PDPL grants 6 rights to data subjects (Art. 4-9):
  - Right of access
  - Right to be informed
  - Right to obtain
  - Right to correct
  - Right to delete
  - Right to object/restrict

Each DSR has its own SLA (5-30 days depending on type) and must be
documented start to finish for SDAIA inspection.
"""

from __future__ import annotations

import uuid
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any


class DSRStatus:
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    AWAITING_VERIFICATION = "awaiting_verification"
    COMPLETED = "completed"
    REJECTED = "rejected"
    EXPIRED_NO_RESPONSE = "expired_no_response"


DSR_TYPES: tuple[str, ...] = (
    "access",      # provide a copy of all data
    "correct",     # fix inaccurate data
    "delete",      # right to be forgotten
    "object",      # stop processing for marketing
    "restrict",    # restrict use of data
    "portability", # export in structured format
)


# SLA by request type (calendar days)
SLA_DAYS: dict[str, int] = {
    "access": 30,
    "correct": 15,
    "delete": 30,
    "object": 5,    # immediate / very short
    "restrict": 5,
    "portability": 30,
}


@dataclass
class DataSubjectRequest:
    request_id: str
    customer_id: str
    data_subject_id: str       # email / phone / contact_id
    request_type: str
    received_at: datetime
    sla_due_at: datetime
    status: str = DSRStatus.OPEN
    completed_at: datetime | None = None
    rejection_reason: str | None = None
    handled_by: str | None = None
    artifacts: dict[str, Any] = field(default_factory=dict)  # links to exports / receipts


def _new_id() -> str:
    return f"dsr_{uuid.uuid4().hex[:20]}"


def open_dsr(
    *,
    customer_id: str,
    data_subject_id: str,
    request_type: str,
    received_at: datetime | None = None,
) -> DataSubjectRequest:
    if request_type not in DSR_TYPES:
        raise ValueError(f"unknown DSR type: {request_type}")
    received = received_at or datetime.now(timezone.utc).replace(tzinfo=None)
    sla = received + timedelta(days=SLA_DAYS[request_type])
    return DataSubjectRequest(
        request_id=_new_id(),
        customer_id=customer_id,
        data_subject_id=data_subject_id,
        request_type=request_type,
        received_at=received,
        sla_due_at=sla,
    )


def process_dsr(
    request: DataSubjectRequest,
    *,
    action_taken: str,           # "completed" | "rejected"
    handled_by: str,
    rejection_reason: str | None = None,
    artifact_url: str | None = None,
    completed_at: datetime | None = None,
) -> DataSubjectRequest:
    """Mark a DSR as completed or rejected. Updates the request in place."""
    n = completed_at or datetime.now(timezone.utc).replace(tzinfo=None)
    request.handled_by = handled_by
    request.completed_at = n
    if action_taken == "completed":
        request.status = DSRStatus.COMPLETED
        if artifact_url:
            request.artifacts["export_url"] = artifact_url
    elif action_taken == "rejected":
        if not rejection_reason:
            raise ValueError("rejection requires a reason")
        request.status = DSRStatus.REJECTED
        request.rejection_reason = rejection_reason
    else:
        raise ValueError(f"unknown action_taken: {action_taken}")
    return request


def is_overdue(request: DataSubjectRequest, *, now: datetime | None = None) -> bool:
    n = now or datetime.now(timezone.utc).replace(tzinfo=None)
    return request.status not in (DSRStatus.COMPLETED, DSRStatus.REJECTED) and n > request.sla_due_at


def dsr_dashboard(requests: list[DataSubjectRequest], *, now: datetime | None = None) -> dict[str, Any]:
    """Aggregate counts for the Trust Center DSR tile."""
    n = now or datetime.now(timezone.utc).replace(tzinfo=None)
    by_type: dict[str, int] = {}
    by_status: dict[str, int] = {}
    overdue = 0
    completed_within_sla = 0
    completed_total = 0
    for r in requests:
        by_type[r.request_type] = by_type.get(r.request_type, 0) + 1
        by_status[r.status] = by_status.get(r.status, 0) + 1
        if is_overdue(r, now=n):
            overdue += 1
        if r.status == DSRStatus.COMPLETED:
            completed_total += 1
            if r.completed_at and r.completed_at <= r.sla_due_at:
                completed_within_sla += 1
    rate = round(completed_within_sla / completed_total, 4) if completed_total else None
    return {
        "n_total": len(requests),
        "by_type": by_type,
        "by_status": by_status,
        "n_overdue": overdue,
        "sla_compliance_rate": rate,
    }

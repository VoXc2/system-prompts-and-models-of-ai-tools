"""
Audit exports — produce the SDAIA / DPO inspection bundle.

Two export modes:
  - full_audit_export()  — all events for one customer, JSON Lines
  - dsr_export()         — events about ONE data subject (PDPL Art. 4 right to access)
"""

from __future__ import annotations

import json
from collections.abc import Iterable
from datetime import datetime
from typing import Any

from auto_client_acquisition.revenue_memory.events import RevenueEvent, event_to_dict


def full_audit_export(
    *, customer_id: str, events: Iterable[RevenueEvent]
) -> list[dict[str, Any]]:
    """All events for one customer — for compliance audits."""
    return [event_to_dict(e) for e in events if e.customer_id == customer_id]


def dsr_export(
    *,
    customer_id: str,
    data_subject_id: str,
    events: Iterable[RevenueEvent],
) -> dict[str, Any]:
    """
    Data Subject Request export — PDPL right of access.

    Returns every event about a specific contact / lead / company that
    represents the data subject. Strips internal-only fields.
    """
    matching: list[dict[str, Any]] = []
    for e in events:
        if e.customer_id != customer_id:
            continue
        # Match by subject_id OR by payload referencing this subject
        if e.subject_id == data_subject_id:
            matching.append(event_to_dict(e))
            continue
        for key in ("contact_id", "lead_id", "email", "phone"):
            if e.payload.get(key) == data_subject_id:
                matching.append(event_to_dict(e))
                break
    return {
        "customer_id": customer_id,
        "data_subject_id": data_subject_id,
        "n_events": len(matching),
        "events": matching,
        "generated_at": datetime.utcnow().isoformat(),
        "right_invoked": "Right of access (PDPL Art. 4)",
    }


def to_jsonl(events: list[dict[str, Any]]) -> str:
    """One event per line — friendly for grep/jq pipelines."""
    return "\n".join(json.dumps(e, ensure_ascii=False) for e in events)

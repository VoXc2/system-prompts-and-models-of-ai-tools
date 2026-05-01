"""Revenue Work Units — Dealix's unit of measurement (Salesforce-inspired).

Each completed, measurable task by Dealix counts as 1 RWU. The platform
proves its value by RWUs delivered + risks blocked, not by abstract "AI usage".
"""

from __future__ import annotations

import time
import uuid
from typing import Any

# Categories of Revenue Work Units.
REVENUE_WORK_UNIT_TYPES: tuple[str, ...] = (
    "opportunity_created",
    "target_ranked",
    "contact_blocked",
    "draft_created",
    "approval_collected",
    "message_sent_after_approval",
    "meeting_drafted",
    "meeting_held",
    "followup_created",
    "proof_generated",
    "partner_suggested",
    "payment_link_drafted",
    "payment_received",
    "review_reply_drafted",
    "list_classified",
    "risk_blocked",
    "service_completed",
    "upsell_offered",
    "subscription_started",
)


def build_revenue_work_unit(
    *,
    unit_type: str,
    service_id: str = "",
    customer_id: str = "",
    risk_level: str = "low",
    revenue_influenced_sar: float = 0.0,
    proof_event: str = "",
    notes: str = "",
) -> dict[str, Any]:
    """Build a single RWU. Validates `unit_type` strictly."""
    if unit_type not in REVENUE_WORK_UNIT_TYPES:
        raise ValueError(
            f"Unknown RWU type: {unit_type}. "
            f"Valid: {', '.join(REVENUE_WORK_UNIT_TYPES)}"
        )
    return {
        "unit_id": str(uuid.uuid4()),
        "unit_type": unit_type,
        "service_id": service_id,
        "customer_id": customer_id,
        "risk_level": risk_level if risk_level in ("low", "medium", "high") else "low",
        "revenue_influenced_sar": float(revenue_influenced_sar),
        "proof_event": proof_event,
        "notes": notes[:200],
        "ts": time.time(),
    }


def aggregate_work_units(
    units: list[dict[str, Any]] | None,
) -> dict[str, Any]:
    """Aggregate RWUs → counts + total revenue + risks blocked."""
    units = units or []
    by_type: dict[str, int] = {}
    by_customer: dict[str, int] = {}
    total_revenue = 0.0
    risks_blocked = 0
    high_risk_count = 0

    for u in units:
        ut = str(u.get("unit_type", ""))
        by_type[ut] = by_type.get(ut, 0) + 1
        cid = str(u.get("customer_id", "unknown"))
        by_customer[cid] = by_customer.get(cid, 0) + 1
        total_revenue += float(u.get("revenue_influenced_sar", 0) or 0)
        if ut == "risk_blocked":
            risks_blocked += 1
        if u.get("risk_level") == "high":
            high_risk_count += 1

    return {
        "total_units": len(units),
        "by_type": by_type,
        "by_customer": by_customer,
        "total_revenue_influenced_sar": round(total_revenue, 2),
        "risks_blocked": risks_blocked,
        "high_risk_count": high_risk_count,
    }

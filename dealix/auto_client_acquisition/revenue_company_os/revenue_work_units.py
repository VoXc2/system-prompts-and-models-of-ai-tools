"""Revenue Work Units (RWU) — countable completed work items (demo)."""

from __future__ import annotations

from typing import Any

RWU_TYPES: tuple[str, ...] = (
    "opportunity_created",
    "target_ranked",
    "contact_blocked",
    "draft_created",
    "approval_collected",
    "meeting_drafted",
    "followup_created",
    "proof_generated",
    "partner_suggested",
    "payment_link_drafted",
)


def demo_work_units() -> dict[str, Any]:
    units: list[dict[str, Any]] = []
    for i, ut in enumerate(RWU_TYPES[:6]):
        units.append(
            {
                "unit_id": f"rwu_demo_{i}",
                "unit_type": ut,
                "service_id": "first_10_opportunities",
                "customer_id": "demo_customer",
                "risk_level": "low" if i % 2 == 0 else "medium",
                "revenue_influenced_sar": 0,
                "proof_event": ut,
                "timestamp": "2026-05-01T12:00:00Z",
            }
        )
    return {"work_units": units, "demo": True}

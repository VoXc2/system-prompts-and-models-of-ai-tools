"""Approval manager — Arabic approval cards (≤3 buttons) + decision processing."""

from __future__ import annotations

from typing import Any

APPROVAL_STATES: tuple[str, ...] = (
    "pending",
    "approved",
    "edited",
    "rejected",
    "expired",
)


def build_approval_card(
    *,
    action_type: str,
    title_ar: str,
    summary_ar: str,
    risk_level: str = "low",
    why_now_ar: str = "",
    recommended_action_ar: str = "",
    expected_impact_sar: float = 0.0,
    service_id: str | None = None,
    customer_id: str | None = None,
    action_id: str | None = None,
) -> dict[str, Any]:
    """Build a structured Arabic approval card."""
    return {
        "type": "approval",
        "action_id": action_id,
        "action_type": action_type,
        "service_id": service_id,
        "customer_id": customer_id,
        "title_ar": title_ar[:140],
        "summary_ar": summary_ar[:280],
        "why_now_ar": why_now_ar[:200],
        "recommended_action_ar": recommended_action_ar[:200],
        "risk_level": risk_level if risk_level in (
            "low", "medium", "high",
        ) else "medium",
        "expected_impact_sar": float(expected_impact_sar),
        "buttons_ar": ["اعتمد", "عدّل", "تخطي"],
        "state": "pending",
        "approval_required": True,
        "live_send_allowed": False,
    }


def process_approval_decision(
    card: dict[str, Any],
    *,
    decision: str,
    decided_by: str = "user",
    note: str = "",
) -> dict[str, Any]:
    """
    Process an approval decision (`approve` / `edit` / `skip` / `reject`).

    Returns the updated card with new state + audit info.
    """
    decision_lc = (decision or "").strip().lower()
    if decision_lc in ("approve", "approved", "موافق", "اعتمد", "نعم"):
        new_state = "approved"
        next_action = "execute_with_audit"
    elif decision_lc in ("edit", "عدّل", "تعديل"):
        new_state = "edited"
        next_action = "rewrite_then_resend_for_approval"
    elif decision_lc in ("skip", "تخطي", "تجاوز"):
        new_state = "rejected"
        next_action = "archive"
    elif decision_lc in ("reject", "ارفض", "لا"):
        new_state = "rejected"
        next_action = "archive_with_reason"
    else:
        return {
            "error": f"unknown decision: {decision}",
            "valid_decisions": ["approve", "edit", "skip", "reject"],
        }

    out = dict(card)
    out["state"] = new_state
    out["decided_by"] = decided_by
    out["decision_note"] = note[:200]
    out["next_action"] = next_action
    return out

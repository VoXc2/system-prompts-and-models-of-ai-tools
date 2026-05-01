"""Service delivery mode: running client services with SLA-oriented checklist."""

from __future__ import annotations

from typing import Any


def mode_profile() -> dict[str, Any]:
    return {
        "mode": "service_delivery",
        "priority_intents": ["approve_action", "ask_proof", "want_meetings"],
        "card_types_first": ["approval_needed", "proof", "meeting_prep"],
        "sla_reminder_ar": "التسليم حسب نافذة الـ Pilot المتفق عليها؛ لا live send افتراضياً.",
        "demo": True,
    }

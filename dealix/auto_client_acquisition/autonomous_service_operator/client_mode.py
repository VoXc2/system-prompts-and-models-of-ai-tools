"""End-customer (growth manager) prioritization."""

from __future__ import annotations

from typing import Any


def mode_profile() -> dict[str, Any]:
    return {
        "mode": "client",
        "priority_intents": ["want_more_customers", "has_contact_list", "want_meetings"],
        "card_types_first": ["approval_needed", "opportunity", "proof_update"],
        "demo": True,
    }

"""Agency partner prioritization."""

from __future__ import annotations

from typing import Any


def mode_profile() -> dict[str, Any]:
    return {
        "mode": "agency_partner",
        "priority_intents": ["want_partnerships", "ask_services", "ask_proof"],
        "card_types_first": ["opportunity", "proof_update", "compliance_risk"],
        "demo": True,
    }

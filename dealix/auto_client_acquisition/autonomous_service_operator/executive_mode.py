"""CEO-style prioritization hints for cards and intents."""

from __future__ import annotations

from typing import Any


def mode_profile() -> dict[str, Any]:
    return {
        "mode": "executive",
        "priority_intents": ["want_more_customers", "ask_proof", "approve_action"],
        "card_types_first": ["leak", "approval_needed", "opportunity"],
        "demo": True,
    }

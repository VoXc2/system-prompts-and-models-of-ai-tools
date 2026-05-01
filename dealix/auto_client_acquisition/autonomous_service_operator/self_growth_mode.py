"""Self-growth mode: Dealix uses its own OS for prospecting (drafts + manual approval only)."""

from __future__ import annotations

from typing import Any


def mode_profile() -> dict[str, Any]:
    return {
        "mode": "self_growth",
        "priority_intents": ["want_more_customers", "ask_services", "ask_demo"],
        "rules_ar": [
            "لا scraping ولا إرسال جماعي.",
            "كل outreach مسودة + موافقة يدوية.",
            "Proof Pack أسبوعي للنتائج الداخلية.",
        ],
        "demo": True,
    }

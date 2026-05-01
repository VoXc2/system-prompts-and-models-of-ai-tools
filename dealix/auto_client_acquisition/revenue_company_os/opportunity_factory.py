"""Demo opportunities for Company OS feed."""

from __future__ import annotations

from typing import Any


def demo_opportunities() -> dict[str, Any]:
    return {
        "opportunities": [
            {
                "id": "opp_demo_1",
                "company_ar": "شركة تدريب — الرياض",
                "why_now_ar": "توسع في فريق المبيعات",
                "suggested_service_id": "first_10_opportunities",
            }
        ],
        "demo": True,
    }

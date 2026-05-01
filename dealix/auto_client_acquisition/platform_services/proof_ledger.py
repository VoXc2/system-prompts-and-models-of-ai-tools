"""
Platform Proof Ledger — value rolled up across the entire platform.

Tracks: leads, meetings, drafts, sends, payments, revenue influenced,
risks blocked, time saved, partner ops. Pure functions.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class PlatformProofLedger:
    """Aggregated platform value over a period."""

    customer_id: str
    period_label: str
    leads_created: int = 0
    meetings_booked: int = 0
    drafts_approved: int = 0
    messages_sent: int = 0
    payments_initiated: int = 0
    payments_paid: int = 0
    revenue_influenced_sar: float = 0.0
    risks_blocked: int = 0
    time_saved_hours: float = 0.0
    partner_opportunities: int = 0
    by_channel: dict[str, dict[str, float]] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "customer_id": self.customer_id,
            "period_label": self.period_label,
            "totals": {
                "leads_created": self.leads_created,
                "meetings_booked": self.meetings_booked,
                "drafts_approved": self.drafts_approved,
                "messages_sent": self.messages_sent,
                "payments_initiated": self.payments_initiated,
                "payments_paid": self.payments_paid,
                "revenue_influenced_sar": self.revenue_influenced_sar,
                "risks_blocked": self.risks_blocked,
                "time_saved_hours": self.time_saved_hours,
                "partner_opportunities": self.partner_opportunities,
            },
            "by_channel": self.by_channel,
        }


def build_demo_platform_proof(
    *,
    customer_id: str = "demo",
    period_label: str = "May 2026",
) -> PlatformProofLedger:
    """Deterministic demo for the dashboard."""
    return PlatformProofLedger(
        customer_id=customer_id,
        period_label=period_label,
        leads_created=72,
        meetings_booked=14,
        drafts_approved=58,
        messages_sent=58,
        payments_initiated=4,
        payments_paid=3,
        revenue_influenced_sar=185_000,
        risks_blocked=21,        # cold whatsapp + secrets in payload + opt-out + ...
        time_saved_hours=42,
        partner_opportunities=6,
        by_channel={
            "whatsapp": {"messages_sent": 33, "replies": 12, "meetings": 5},
            "gmail": {"drafts": 18, "sent": 18, "replies": 6},
            "google_calendar": {"events_drafted": 14, "events_inserted": 0},
            "moyasar": {"links_drafted": 4, "paid": 3},
            "google_business_profile": {"reviews_replied": 8},
            "linkedin_lead_forms": {"leads_ingested": 11},
            "website_forms": {"leads_ingested": 22},
        },
    )

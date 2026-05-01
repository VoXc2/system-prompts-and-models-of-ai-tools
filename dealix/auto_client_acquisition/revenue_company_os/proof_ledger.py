"""Revenue Proof Ledger — revenue-tier proof aggregator across all services.

Distinct from `platform_services.proof_ledger`: this aggregates Revenue Work
Units + Action Graph edges into a customer-facing scoreboard.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

from .revenue_work_units import REVENUE_WORK_UNIT_TYPES, aggregate_work_units


@dataclass
class RevenueProofLedger:
    """In-memory revenue proof ledger. Production = Supabase append-only."""
    work_units: list[dict[str, Any]] = field(default_factory=list)
    notable_events: list[dict[str, Any]] = field(default_factory=list)

    def append_work_unit(self, unit: dict[str, Any]) -> None:
        """Append an RWU after validating its type."""
        ut = str(unit.get("unit_type", ""))
        if ut not in REVENUE_WORK_UNIT_TYPES:
            raise ValueError(f"Unknown RWU type: {ut}")
        self.work_units.append(dict(unit))

    def append_notable_event(
        self, *, event_type: str, summary_ar: str, customer_id: str = "",
    ) -> None:
        self.notable_events.append({
            "ts": time.time(),
            "event_type": event_type,
            "summary_ar": summary_ar[:200],
            "customer_id": customer_id,
        })

    def summary_for_customer(self, customer_id: str) -> dict[str, Any]:
        """Build the customer-facing Arabic Proof scoreboard."""
        units = [u for u in self.work_units
                 if u.get("customer_id") == customer_id]
        agg = aggregate_work_units(units)

        opps = agg["by_type"].get("opportunity_created", 0)
        approvals = agg["by_type"].get("approval_collected", 0)
        meetings = agg["by_type"].get("meeting_drafted", 0)
        meetings_held = agg["by_type"].get("meeting_held", 0)
        risks_blocked = agg["risks_blocked"]
        revenue = agg["total_revenue_influenced_sar"]

        events_for_customer = [
            e for e in self.notable_events
            if e.get("customer_id") == customer_id
        ]

        return {
            "customer_id": customer_id,
            "totals": {
                "opportunities_created": opps,
                "approvals_collected": approvals,
                "meetings_drafted": meetings,
                "meetings_held": meetings_held,
                "risks_blocked": risks_blocked,
                "revenue_influenced_sar": revenue,
            },
            "summary_ar": [
                f"الفرص: {opps} | الاعتمادات: {approvals}.",
                f"الاجتماعات: {meetings} drafted, {meetings_held} held.",
                f"مخاطر منعت: {risks_blocked}.",
                f"إيراد متأثر: {revenue:.0f} ريال.",
            ],
            "notable_events": events_for_customer[-5:],
            "by_type": agg["by_type"],
        }


def build_revenue_proof_ledger_demo() -> dict[str, Any]:
    """Demo ledger with 12 sample RWUs for a single customer."""
    from .revenue_work_units import build_revenue_work_unit
    led = RevenueProofLedger()
    cust = "demo"
    sample_units = [
        build_revenue_work_unit(unit_type="opportunity_created",
                                service_id="first_10_opportunities_sprint",
                                customer_id=cust, revenue_influenced_sar=18000),
        build_revenue_work_unit(unit_type="opportunity_created",
                                service_id="first_10_opportunities_sprint",
                                customer_id=cust, revenue_influenced_sar=12000),
        build_revenue_work_unit(unit_type="draft_created",
                                service_id="first_10_opportunities_sprint",
                                customer_id=cust),
        build_revenue_work_unit(unit_type="draft_created",
                                service_id="first_10_opportunities_sprint",
                                customer_id=cust),
        build_revenue_work_unit(unit_type="approval_collected",
                                service_id="first_10_opportunities_sprint",
                                customer_id=cust),
        build_revenue_work_unit(unit_type="approval_collected",
                                service_id="first_10_opportunities_sprint",
                                customer_id=cust),
        build_revenue_work_unit(unit_type="meeting_drafted",
                                service_id="meeting_booking_sprint",
                                customer_id=cust, revenue_influenced_sar=20000),
        build_revenue_work_unit(unit_type="risk_blocked",
                                service_id="whatsapp_compliance_setup",
                                customer_id=cust, risk_level="high"),
        build_revenue_work_unit(unit_type="risk_blocked",
                                service_id="whatsapp_compliance_setup",
                                customer_id=cust, risk_level="high"),
        build_revenue_work_unit(unit_type="proof_generated",
                                service_id="growth_os_monthly",
                                customer_id=cust),
        build_revenue_work_unit(unit_type="upsell_offered",
                                service_id="growth_os_monthly",
                                customer_id=cust),
        build_revenue_work_unit(unit_type="payment_received",
                                customer_id=cust, revenue_influenced_sar=499),
    ]
    for u in sample_units:
        led.append_work_unit(u)
    led.append_notable_event(
        event_type="risk.blocked", customer_id=cust,
        summary_ar="منع cold WhatsApp بدون opt-in (PDPL).",
    )
    led.append_notable_event(
        event_type="service.completed", customer_id=cust,
        summary_ar="اكتمل First 10 Opportunities Sprint بنجاح.",
    )
    return led.summary_for_customer(cust)

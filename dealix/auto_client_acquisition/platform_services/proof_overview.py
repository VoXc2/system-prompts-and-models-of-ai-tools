"""Single JSON view combining innovation proof summary + business proof pack demo."""

from __future__ import annotations

from typing import Any

from auto_client_acquisition.business.proof_pack import build_demo_proof_pack
from auto_client_acquisition.platform_services.proof_summary import build_proof_summary


def build_proof_overview() -> dict[str, Any]:
    summary = build_proof_summary()
    pack = build_demo_proof_pack()
    return {
        "demo": True,
        "approval_required": False,
        "innovation_ledger_summary": summary,
        "business_proof_pack_excerpt": {
            "executive_summary_ar": pack.get("executive_summary_ar"),
            "qualified_leads": pack.get("qualified_leads"),
            "meetings_booked": pack.get("meetings_booked"),
            "revenue_influenced_sar": pack.get("revenue_influenced_sar"),
            "next_month_plan_ar": pack.get("next_month_plan_ar"),
        },
        "related_routes": {
            "innovation_proof_ledger_demo": "GET /api/v1/innovation/proof-ledger/demo",
            "innovation_proof_events": "GET /api/v1/innovation/proof-ledger/events",
            "innovation_proof_report_week": "GET /api/v1/innovation/proof-ledger/report/week",
            "business_proof_pack_demo": "GET /api/v1/business/proof-pack/demo",
            "platform_proof_summary": "GET /api/v1/platform/proof/summary",
        },
    }

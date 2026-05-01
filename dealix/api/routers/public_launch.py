"""Public Launch API — Layer 13 endpoints.

Endpoints:
    GET  /api/v1/public-launch/criteria
    POST /api/v1/public-launch/gate-check
    POST /api/v1/public-launch/pilot-tracker
    POST /api/v1/public-launch/pdpl-compliance
    POST /api/v1/public-launch/brand-moat
    GET  /api/v1/public-launch/demo
"""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter
from pydantic import BaseModel, Field

from auto_client_acquisition.public_launch import (
    PUBLIC_LAUNCH_CRITERIA,
    evaluate_public_launch_gate,
    pilot_tracker_summary,
    compute_pdpl_compliance,
    compute_brand_moat_score,
)


router = APIRouter(prefix="/api/v1/public-launch", tags=["public-launch"])


class GateCheckRequest(BaseModel):
    state: dict[str, Any] = Field(default_factory=dict)


class PilotTrackerRequest(BaseModel):
    pilots: list[dict[str, Any]] = Field(default_factory=list)


class PDPLRequest(BaseModel):
    state: dict[str, Any] = Field(default_factory=dict)


class BrandMoatRequest(BaseModel):
    state: dict[str, Any] = Field(default_factory=dict)


@router.get("/criteria")
def list_criteria() -> dict[str, Any]:
    """Return the 9 Public Launch criteria definitions."""
    return {
        "criteria": [
            {
                "key": c.key,
                "name_ar": c.name_ar,
                "threshold": c.threshold,
                "unit": c.unit,
                "description_ar": c.description_ar,
            }
            for c in PUBLIC_LAUNCH_CRITERIA
        ],
        "count": len(PUBLIC_LAUNCH_CRITERIA),
    }


@router.post("/gate-check")
def gate_check(req: GateCheckRequest) -> dict[str, Any]:
    verdict = evaluate_public_launch_gate(req.state)
    return verdict.to_dict()


@router.post("/pilot-tracker")
def pilot_tracker(req: PilotTrackerRequest) -> dict[str, Any]:
    summary = pilot_tracker_summary(req.pilots)
    return summary.to_dict()


@router.post("/pdpl-compliance")
def pdpl_compliance(req: PDPLRequest) -> dict[str, Any]:
    report = compute_pdpl_compliance(req.state)
    return report.to_dict()


@router.post("/brand-moat")
def brand_moat(req: BrandMoatRequest) -> dict[str, Any]:
    score = compute_brand_moat_score(req.state)
    return score.to_dict()


@router.get("/demo")
def demo() -> dict[str, Any]:
    """Combined demo response showing realistic Paid-Beta-stage data."""
    # State: company is at Paid Beta with 2 pilots, 1 paid, etc.
    gate_state = {
        "pilots_completed": 2,
        "paid_customers": 1,
        "unsafe_sends": 0,
        "proof_cadence_weeks": 1,
        "support_first_response_minutes_p1": 90,
        "funnel_visible": True,
        "staging_uptime_days": 3,
        "billing_webhook_verified": False,
        "legal_complete": False,
    }
    pilots = [
        {
            "pilot_id": "p1",
            "company": "وكالة النمو السعودي",
            "sector": "agency",
            "city": "الرياض",
            "started_at": "2026-04-25",
            "stage": "completed",
            "paid": True,
            "pilot_price_sar": 499,
            "proof_pack_sent": True,
            "proof_pack_sent_at": "2026-05-01",
            "upgrade_outcome": "growth_os_monthly",
            "upgrade_value_sar": 2999,
        },
        {
            "pilot_id": "p2",
            "company": "شركة تدريب الرياض",
            "sector": "training",
            "city": "الرياض",
            "started_at": "2026-04-28",
            "stage": "proof_pack_sent",
            "paid": False,
            "pilot_price_sar": 0,
            "proof_pack_sent": True,
            "proof_pack_sent_at": "2026-05-01",
            "upgrade_outcome": "case_study",
            "upgrade_value_sar": 0,
        },
    ]
    pdpl_state = {
        "data_residency_saudi": True,
        "whatsapp_opt_in_audit": True,
        "email_opt_in_audit": True,
        "breach_notification_72h_ready": True,
        "dpa_template_published": True,
        "privacy_policy_bilingual": False,
        "data_retention_policy": True,
        "trace_redaction_active": True,
        "action_ledger_audit": True,
        "consent_revocation_path": False,
    }
    moat_state = {
        "events_logged_count": 50,
        "messages_per_sector_count": 10,
        "sectors_covered_count": 4,
        "linkedin_followers": 200,
        "newsletter_subscribers": 30,
        "monthly_branded_searches": 5,
        "case_studies_published": 1,
        "pdpl_compliance_pct": 80,
        "iso_27001_progress_pct": 0,
        "audit_count_last_year": 0,
        "dpa_signed_with_customers_pct": 50,
        "agency_partners_count": 1,
        "active_referring_agencies_count": 0,
        "agency_revenue_share_paid_sar": 0,
        "certified_operators_count": 0,
        "operators_active_last_30d": 0,
        "operator_revenue_share_paid_sar": 0,
    }

    return {
        "gate": evaluate_public_launch_gate(gate_state).to_dict(),
        "pilots": pilot_tracker_summary(pilots).to_dict(),
        "pdpl": compute_pdpl_compliance(pdpl_state).to_dict(),
        "brand_moat": compute_brand_moat_score(moat_state).to_dict(),
    }

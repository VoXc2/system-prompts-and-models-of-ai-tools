"""Revenue Today — offers, outreach templates, pilot delivery, manual payment (no live charge)."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Query

from auto_client_acquisition.revenue_launch.demo_closer import (
    build_12_min_demo_flow,
    build_close_script,
    build_discovery_questions,
    build_objection_responses,
)
from auto_client_acquisition.revenue_launch.offer_i18n import build_revenue_offers_payload
from auto_client_acquisition.revenue_launch.outreach_sequence import (
    build_first_20_segments,
    build_outreach_message,
)
from auto_client_acquisition.revenue_launch.payment_manual_flow import (
    build_moyasar_invoice_instructions,
    build_payment_confirmation_checklist,
    build_payment_link_message,
)
from auto_client_acquisition.revenue_launch.pilot_delivery import (
    build_24h_delivery_plan,
    build_client_intake_form,
    build_first_10_opportunities_delivery,
    build_growth_diagnostic_delivery,
    build_list_intelligence_delivery,
)
from auto_client_acquisition.revenue_launch.pipeline_tracker import build_pipeline_schema
from auto_client_acquisition.revenue_launch.proof_pack_template import (
    build_private_beta_proof_pack,
)

router = APIRouter(prefix="/api/v1/revenue-launch", tags=["revenue_launch"])


@router.get("/offer")
async def revenue_launch_offer(lang: str = Query("ar", description="ar or en — en adds title_en/summary_en alongside Arabic fields")) -> dict[str, Any]:
    return build_revenue_offers_payload(lang)


@router.get("/outreach/first-20")
async def revenue_launch_outreach_first_20() -> dict[str, Any]:
    segs = build_first_20_segments()
    samples = [
        build_outreach_message("agency_b2b"),
        build_outreach_message("training"),
    ]
    return {**segs, "sample_messages": samples, "demo": True}


@router.get("/demo-flow")
async def revenue_launch_demo_flow() -> dict[str, Any]:
    return {
        "flow": build_12_min_demo_flow(),
        "discovery": build_discovery_questions(),
        "close": build_close_script(),
        "objections": build_objection_responses(),
        "demo": True,
    }


@router.get("/pipeline/schema")
async def revenue_launch_pipeline_schema() -> dict[str, Any]:
    return build_pipeline_schema()


@router.get("/pilot-delivery")
async def revenue_launch_pilot_delivery() -> dict[str, Any]:
    return {
        "intake": build_client_intake_form(),
        "plan_24h": build_24h_delivery_plan(),
        "first_10": build_first_10_opportunities_delivery(),
        "list_intelligence": build_list_intelligence_delivery(),
        "diagnostic": build_growth_diagnostic_delivery(),
        "no_live_send": True,
        "demo": True,
    }


@router.get("/payment/manual-flow")
async def revenue_launch_payment_manual() -> dict[str, Any]:
    return {
        "instructions": build_moyasar_invoice_instructions(),
        "message_template": build_payment_link_message(),
        "confirmation": build_payment_confirmation_checklist(),
        "no_live_charge": True,
        "demo": True,
    }


@router.get("/proof-pack/template")
async def revenue_launch_proof_pack_template() -> dict[str, Any]:
    return build_private_beta_proof_pack()

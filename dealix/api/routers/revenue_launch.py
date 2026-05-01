"""Revenue Launch router — paid offer + pipeline + delivery + payment + proof."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body

from auto_client_acquisition.revenue_launch import (
    build_24h_delivery_plan,
    build_499_pilot_offer,
    build_case_study_free_offer,
    build_client_intake_form,
    build_client_summary,
    build_first_10_opportunities_delivery,
    build_first_20_segments_v2,
    build_followup_1,
    build_followup_2,
    build_growth_diagnostic_delivery,
    build_growth_os_pilot_offer,
    build_list_intelligence_delivery,
    build_moyasar_invoice_instructions,
    build_next_step_recommendation,
    build_outreach_message_v2,
    build_payment_confirmation_checklist,
    build_payment_link_message,
    build_pipeline_schema,
    build_private_beta_offer,
    build_private_beta_proof_pack,
    build_reply_handlers_v2,
    demo_12_min,
    demo_close_script,
    demo_discovery,
    demo_objections,
    recommend_offer_for_segment,
    summarize_pipeline,
)

router = APIRouter(prefix="/api/v1/revenue-launch", tags=["revenue-launch"])


# ── Offers ───────────────────────────────────────────────────
@router.get("/offers")
async def offers() -> dict[str, Any]:
    return {
        "private_beta": build_private_beta_offer(),
        "pilot_499": build_499_pilot_offer(),
        "growth_os_pilot": build_growth_os_pilot_offer(),
        "case_study_free": build_case_study_free_offer(),
    }


@router.post("/offers/recommend")
async def offers_recommend(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
    return recommend_offer_for_segment(payload.get("segment_id", ""))


# ── Outreach ─────────────────────────────────────────────────
@router.get("/outreach/first-20")
async def outreach_first_20() -> dict[str, Any]:
    seg = build_first_20_segments_v2()
    return {
        **seg,
        "messages": {
            s["id"]: build_outreach_message_v2(s["id"])
            for s in seg["segments"]
        },
        "reply_handlers": build_reply_handlers_v2(),
    }


@router.post("/outreach/followup")
async def outreach_followup(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
    step = int(payload.get("step", 1))
    builder = build_followup_2 if step >= 2 else build_followup_1
    return builder(
        segment_id=payload.get("segment_id", ""),
        name=payload.get("name", "[الاسم]"),
    )


# ── Demo ─────────────────────────────────────────────────────
@router.get("/demo-flow")
async def demo_flow() -> dict[str, Any]:
    return {
        "flow": demo_12_min(),
        "discovery_questions": demo_discovery(),
        "objections": demo_objections(),
        "close": demo_close_script(),
    }


# ── Pipeline ─────────────────────────────────────────────────
@router.get("/pipeline/schema")
async def pipeline_schema() -> dict[str, Any]:
    return build_pipeline_schema()


@router.post("/pipeline/summarize")
async def pipeline_summarize(
    pipeline: list[dict[str, Any]] = Body(default_factory=list, embed=True),
) -> dict[str, Any]:
    return summarize_pipeline(pipeline)


# ── Pilot delivery ───────────────────────────────────────────
@router.get("/pilot-delivery/intake-form")
async def pilot_intake_form() -> dict[str, Any]:
    return build_client_intake_form()


@router.post("/pilot-delivery/24h-plan")
async def pilot_24h_plan(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
    return build_24h_delivery_plan(payload.get("service_id", ""))


@router.post("/pilot-delivery/first-10")
async def pilot_first_10(intake: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    return build_first_10_opportunities_delivery(intake)


@router.post("/pilot-delivery/list-intelligence")
async def pilot_list_intelligence(intake: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    return build_list_intelligence_delivery(intake)


@router.post("/pilot-delivery/free-diagnostic")
async def pilot_free_diagnostic(intake: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    return build_growth_diagnostic_delivery(intake)


# ── Payment manual flow ──────────────────────────────────────
@router.post("/payment/invoice-instructions")
async def payment_invoice_instructions(payload: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    return build_moyasar_invoice_instructions(
        amount_sar=int(payload.get("amount_sar", 499)),
        customer_name=payload.get("customer_name", ""),
        invoice_description=payload.get(
            "invoice_description",
            "Dealix Private Beta Pilot — 7 days",
        ),
    )


@router.post("/payment/link-message")
async def payment_link_message(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
    return build_payment_link_message(
        customer_name=payload.get("customer_name", "[الاسم]"),
        invoice_url=payload.get("invoice_url", "[INVOICE_URL]"),
        amount_sar=int(payload.get("amount_sar", 499)),
    )


@router.get("/payment/confirmation-checklist")
async def payment_confirmation_checklist() -> dict[str, Any]:
    return build_payment_confirmation_checklist()


# ── Proof Pack ───────────────────────────────────────────────
@router.post("/proof-pack/template")
async def proof_pack_template(payload: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    return build_private_beta_proof_pack(
        company_name=payload.get("company_name", ""),
        metrics=payload.get("metrics", {}),
    )


@router.post("/proof-pack/client-summary")
async def proof_pack_client_summary(payload: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    return build_client_summary(
        company_name=payload.get("company_name", ""),
        opportunities_count=int(payload.get("opportunities_count", 0)),
        approved_drafts=int(payload.get("approved_drafts", 0)),
        meetings=int(payload.get("meetings", 0)),
        pipeline_sar=float(payload.get("pipeline_sar", 0)),
        risks_blocked=int(payload.get("risks_blocked", 0)),
    )


@router.post("/proof-pack/next-step")
async def proof_pack_next_step(payload: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    return build_next_step_recommendation(pilot_metrics=payload)

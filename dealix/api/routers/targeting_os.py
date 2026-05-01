"""Targeting & Acquisition OS router."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body

from auto_client_acquisition.targeting_os import (
    analyze_uploaded_list_preview,
    build_dealix_self_growth_plan,
    build_daily_targeting_brief,
    build_end_of_day_report,
    build_followup_sequence,
    build_free_growth_diagnostic,
    build_lead_gen_form_plan,
    build_outreach_plan,
    build_self_growth_daily_brief,
    build_weekly_learning_report,
    calculate_channel_reputation,
    draft_b2b_email,
    draft_role_based_angle,
    draft_whatsapp_message,
    enforce_daily_limits,
    evaluate_contactability,
    explain_contactability_ar,
    list_targeting_services,
    map_buying_committee,
    recommend_accounts,
    recommend_dealix_targets,
    recommend_linkedin_strategy,
    recommend_recovery_action,
    recommend_service_offer,
    recommend_today_actions,
    score_email_risk,
    score_whatsapp_risk,
    summarize_plan_ar,
    summarize_reputation_ar,
)
from auto_client_acquisition.targeting_os.contract_drafts import (
    draft_agency_partner_outline,
    draft_dpa_outline,
    draft_pilot_agreement_outline,
    draft_referral_agreement_outline,
)

router = APIRouter(prefix="/api/v1/targeting", tags=["targeting-os"])


# ── Accounts ─────────────────────────────────────────────────
@router.post("/accounts/recommend")
async def accounts_recommend(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
    return recommend_accounts(
        sector=payload.get("sector", "saas"),
        city=payload.get("city", "Riyadh"),
        offer=payload.get("offer", ""),
        goal=payload.get("goal", "fill_pipeline"),
        limit=int(payload.get("limit", 10)),
    )


# ── Buying committee ─────────────────────────────────────────
@router.post("/buying-committee/map")
async def buying_committee_map(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
    return map_buying_committee(
        sector=payload.get("sector", "saas"),
        company_size=payload.get("company_size", "small"),
        goal=payload.get("goal", "fill_pipeline"),
    )


# ── Contacts ─────────────────────────────────────────────────
@router.post("/contacts/evaluate")
async def contacts_evaluate(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
    contact = payload.get("contact") or payload
    desired = payload.get("desired_channel")
    result = evaluate_contactability(contact, desired_channel=desired)
    result["explanation_ar"] = explain_contactability_ar(result)
    return result


@router.post("/uploaded-list/analyze")
async def uploaded_list_analyze(
    contacts: list[dict[str, Any]] = Body(..., embed=True),
) -> dict[str, Any]:
    return analyze_uploaded_list_preview(contacts)


# ── Outreach ─────────────────────────────────────────────────
@router.post("/outreach/plan")
async def outreach_plan(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
    plan = build_outreach_plan(
        targets=payload.get("targets", []),
        channels=payload.get("channels"),
        goal=payload.get("goal", "fill_pipeline"),
    )
    plan = enforce_daily_limits(plan)
    plan["summary_ar"] = summarize_plan_ar(plan)
    return plan


# ── Daily autopilot ──────────────────────────────────────────
@router.get("/daily-autopilot/demo")
async def daily_autopilot_demo() -> dict[str, Any]:
    return {
        "brief": build_daily_targeting_brief(),
        "today_actions": recommend_today_actions(),
        "end_of_day_template": build_end_of_day_report(),
    }


# ── Self-Growth Mode ─────────────────────────────────────────
@router.get("/self-growth/demo")
async def self_growth_demo() -> dict[str, Any]:
    return {
        "plan": build_dealix_self_growth_plan(),
        "today": build_self_growth_daily_brief(),
    }


@router.post("/self-growth/targets")
async def self_growth_targets(payload: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    return recommend_dealix_targets(
        sector_focus=payload.get("sector"),
        city_focus=payload.get("city"),
        limit=int(payload.get("limit", 10)),
    )


@router.post("/self-growth/weekly-report")
async def self_growth_weekly(payload: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    return build_weekly_learning_report(payload)


# ── Reputation guard ────────────────────────────────────────
@router.get("/reputation/status")
async def reputation_status() -> dict[str, Any]:
    """Demo reputation snapshot."""
    healthy_email = {"bounce_rate": 0.005, "complaint_rate": 0.0001,
                     "opt_out_rate": 0.01, "reply_rate": 0.04}
    risky_wa = {"block_rate": 0.04, "report_rate": 0.005,
                "opt_out_rate": 0.06, "reply_rate": 0.02}
    return {
        "email": calculate_channel_reputation(healthy_email, channel="email"),
        "whatsapp": calculate_channel_reputation(risky_wa, channel="whatsapp"),
    }


@router.post("/reputation/recovery")
async def reputation_recovery(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
    return recommend_recovery_action(
        payload.get("metrics", {}),
        channel=payload.get("channel", "email"),
    )


# ── LinkedIn strategy ────────────────────────────────────────
@router.post("/linkedin/strategy")
async def linkedin_strategy(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
    strategy = recommend_linkedin_strategy(
        segment=payload.get("segment", "B2B Saudi"),
        goal=payload.get("goal", "fill_pipeline"),
    )
    if payload.get("with_lead_gen_form"):
        strategy["lead_gen_form_plan"] = build_lead_gen_form_plan(
            segment=payload.get("segment", "B2B Saudi"),
            offer=payload.get("offer", "Pilot 7 days"),
            campaign_name=payload.get("campaign_name", ""),
        )
    return strategy


# ── Drafts ───────────────────────────────────────────────────
@router.post("/drafts/email")
async def drafts_email(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
    contact = payload.get("contact", {})
    draft = draft_b2b_email(
        contact,
        offer=payload.get("offer", ""),
        why_now=payload.get("why_now", ""),
    )
    risk = score_email_risk(contact, draft.get("body_ar", ""))
    return {**draft, "risk": risk}


@router.post("/drafts/whatsapp")
async def drafts_whatsapp(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
    contact = payload.get("contact", {})
    return draft_whatsapp_message(
        contact,
        offer=payload.get("offer", ""),
        why_now=payload.get("why_now", ""),
    )


@router.post("/drafts/email-followup")
async def drafts_email_followup(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
    return build_followup_sequence(
        payload.get("contact", {}),
        offer=payload.get("offer", ""),
    )


@router.post("/drafts/role-angle")
async def drafts_role_angle(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
    return draft_role_based_angle(
        role_key=payload.get("role_key", "founder_ceo"),
        sector=payload.get("sector", "saas"),
        offer=payload.get("offer", ""),
    )


# ── Free diagnostic ──────────────────────────────────────────
@router.post("/free-diagnostic")
async def free_diagnostic(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
    return build_free_growth_diagnostic(payload)


# ── Services + contracts ─────────────────────────────────────
@router.get("/services")
async def services_list() -> dict[str, Any]:
    return list_targeting_services()


@router.post("/services/recommend")
async def services_recommend(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
    return recommend_service_offer(
        customer_type=payload.get("customer_type", ""),
        goal=payload.get("goal", "fill_pipeline"),
    )


@router.get("/contracts/templates")
async def contracts_templates() -> dict[str, Any]:
    return {
        "pilot": draft_pilot_agreement_outline(),
        "dpa": draft_dpa_outline(),
        "referral": draft_referral_agreement_outline(),
        "agency_partner": draft_agency_partner_outline(),
    }

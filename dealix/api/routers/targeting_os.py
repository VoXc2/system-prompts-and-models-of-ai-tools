"""Targeting & Acquisition OS API — planning and evaluation only, no live send."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body

from auto_client_acquisition.intelligence_layer.trust_score import compute_trust_score
from auto_client_acquisition.platform_services.contact_import_preview import build_import_preview
from auto_client_acquisition.targeting_os.account_finder import recommend_accounts, recommend_account_source_strategy
from auto_client_acquisition.targeting_os.acquisition_scorecard import build_acquisition_scorecard
from auto_client_acquisition.targeting_os.buyer_role_mapper import map_buying_committee
from auto_client_acquisition.targeting_os.contactability_matrix import evaluate_contactability
from auto_client_acquisition.targeting_os.contract_drafts import list_contract_templates
from auto_client_acquisition.targeting_os.daily_autopilot import build_daily_targeting_brief
from auto_client_acquisition.targeting_os.free_diagnostic import (
    build_free_growth_diagnostic,
    recommend_paid_pilot_offer,
)
from auto_client_acquisition.targeting_os.linkedin_strategy import (
    build_lead_gen_form_plan,
    recommend_linkedin_strategy,
)
from auto_client_acquisition.targeting_os.outreach_scheduler import build_outreach_plan
from auto_client_acquisition.targeting_os.reputation_guard import calculate_channel_reputation, should_pause_channel
from auto_client_acquisition.targeting_os.self_growth_mode import build_self_growth_daily_brief
from auto_client_acquisition.targeting_os.service_offers import list_targeting_services

router = APIRouter(prefix="/api/v1/targeting", tags=["targeting_os"])


@router.post("/accounts/recommend")
async def accounts_recommend(payload: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    return recommend_accounts(
        str(payload.get("sector") or ""),
        str(payload.get("city") or ""),
        str(payload.get("offer") or ""),
        str(payload.get("goal") or ""),
        limit=int(payload.get("limit") or 10),
    )


@router.post("/buying-committee/map")
async def buying_committee_map(payload: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    return map_buying_committee(
        str(payload.get("sector") or ""),
        payload.get("company_size"),
        payload.get("goal"),
    )


@router.post("/contacts/evaluate")
async def contacts_evaluate(payload: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    contact = payload.get("contact") if isinstance(payload.get("contact"), dict) else payload
    desired = payload.get("desired_channel")
    return evaluate_contactability(contact, str(desired) if desired else None)


@router.post("/uploaded-list/analyze")
async def uploaded_list_analyze(payload: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    """Delegates to platform import preview for full bucket logic."""
    return build_import_preview(payload or {})


@router.post("/outreach/plan")
async def outreach_plan(payload: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    targets = payload.get("targets") if isinstance(payload.get("targets"), list) else []
    channels = payload.get("channels") if isinstance(payload.get("channels"), list) else ["email"]
    goal = str(payload.get("goal") or "growth")
    return build_outreach_plan([dict(t) for t in targets if isinstance(t, dict)], [str(c) for c in channels], goal)


@router.get("/daily-autopilot/demo")
async def daily_autopilot_demo() -> dict[str, Any]:
    return build_daily_targeting_brief({"sector": "training", "city": "الرياض", "offer": "Growth OS", "goal": "meetings"})


@router.get("/self-growth/demo")
async def self_growth_demo() -> dict[str, Any]:
    return build_self_growth_daily_brief()


@router.get("/reputation/status")
async def reputation_status() -> dict[str, Any]:
    metrics = {"bounce_rate": 0.12, "opt_out_rate": 0.01, "complaint_rate": 0.0, "reply_rate": 0.08}
    rep = calculate_channel_reputation(metrics)
    return {**rep, "should_pause": should_pause_channel(metrics)}


@router.post("/linkedin/strategy")
async def linkedin_strategy(payload: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    seg = str(payload.get("segment") or "b2b")
    goal = str(payload.get("goal") or "leads")
    base = recommend_linkedin_strategy(seg, goal)
    if payload.get("include_lead_gen_plan"):
        base["lead_gen_plan"] = build_lead_gen_form_plan(
            seg,
            str(payload.get("offer") or "Pilot"),
            str(payload.get("campaign_name") or "dealix"),
        )
    return base


@router.get("/services")
async def targeting_services() -> dict[str, Any]:
    return list_targeting_services()


@router.post("/free-diagnostic")
async def free_diagnostic(payload: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    company = payload.get("company") if isinstance(payload.get("company"), dict) else payload
    if not isinstance(company, dict):
        company = {}
    diag = build_free_growth_diagnostic(company or {"sector": "b2b", "city": "الرياض"})
    return {"diagnostic": diag, "pilot_offer": recommend_paid_pilot_offer(diag)}


@router.get("/contracts/templates")
async def contracts_templates() -> dict[str, Any]:
    return list_contract_templates()


@router.post("/trust-score")
async def targeting_trust_score(signals: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    """Bridge to intelligence trust score for targeting workflows."""
    return compute_trust_score(signals or {})


@router.post("/account-strategy")
async def account_strategy(payload: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    acct = payload.get("account") if isinstance(payload.get("account"), dict) else {}
    return recommend_account_source_strategy(acct)

"""Autonomous Service Operator router — chat + decisions + sessions + bundles."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body, HTTPException

from auto_client_acquisition.autonomous_service_operator import (
    OperatorMemory,
    add_agency_client,
    build_agency_dashboard,
    build_approval_card,
    build_ceo_command_center,
    build_client_dashboard,
    build_co_branded_proof_pack,
    build_executive_daily_brief,
    build_intake_questions_for_intent,
    build_new_session,
    build_revenue_risks_summary,
    build_service_pipeline,
    build_session_context,
    build_upsell_card,
    classify_intent,
    dispatch_proof_pack,
    handle_message,
    list_bundles,
    list_agency_revenue_share,
    plan_tool_action,
    process_approval_decision,
    recommend_bundle,
    recommend_upsell_after_service,
    render_approval_card_for_whatsapp,
    render_card_for_whatsapp,
    render_daily_brief_for_whatsapp,
    transition_session,
    validate_intake_completeness,
)

router = APIRouter(prefix="/api/v1/operator", tags=["autonomous-service-operator"])

# Process-level memory (demo). Production = Redis/Supabase.
_MEMORY = OperatorMemory()


# ── Chat ─────────────────────────────────────────────────────
@router.post("/chat/message")
async def chat_message(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """Send a message to the operator. Classifies intent + recommends action."""
    return handle_message(
        message=payload.get("message", ""),
        customer_id=payload.get("customer_id"),
        has_contact_list=bool(payload.get("has_contact_list", False)),
        is_agency=bool(payload.get("is_agency", False)),
        is_local_business=bool(payload.get("is_local_business", False)),
        budget_sar=int(payload.get("budget_sar", 1000)),
    )


@router.post("/chat/decision")
async def chat_decision(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """Process an approval/edit/skip decision on an action card."""
    card = payload.get("card") or build_approval_card(
        action_type="example",
        title_ar="فعل مثال",
        summary_ar="مثال",
    )
    return process_approval_decision(
        card,
        decision=payload.get("decision", "skip"),
        decided_by=payload.get("decided_by", "user"),
        note=payload.get("note", ""),
    )


@router.post("/chat/classify")
async def chat_classify(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
    return classify_intent(payload.get("message", ""))


# ── Sessions ─────────────────────────────────────────────────
@router.post("/sessions/new")
async def sessions_new(payload: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    session = build_new_session(customer_id=payload.get("customer_id"))
    _MEMORY.upsert_session(session)
    return session.to_dict()


@router.get("/sessions/{session_id}")
async def sessions_get(session_id: str) -> dict[str, Any]:
    session = _MEMORY.get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="session not found")
    return session.to_dict()


@router.post("/sessions/{session_id}/transition")
async def sessions_transition(
    session_id: str,
    payload: dict[str, Any] = Body(...),
) -> dict[str, Any]:
    session = _MEMORY.get_session(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="session not found")
    transition_session(
        session,
        new_state=payload.get("new_state", "new"),
        note=payload.get("note", ""),
    )
    return session.to_dict()


@router.get("/sessions/{session_id}/context")
async def sessions_context(session_id: str) -> dict[str, Any]:
    return build_session_context(memory=_MEMORY, session_id=session_id)


# ── Cards / Approvals ────────────────────────────────────────
@router.post("/cards/approval")
async def cards_approval(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
    return build_approval_card(
        action_type=payload.get("action_type", "unknown"),
        title_ar=payload.get("title_ar", ""),
        summary_ar=payload.get("summary_ar", ""),
        risk_level=payload.get("risk_level", "low"),
        why_now_ar=payload.get("why_now_ar", ""),
        recommended_action_ar=payload.get("recommended_action_ar", ""),
        expected_impact_sar=float(payload.get("expected_impact_sar", 0)),
        service_id=payload.get("service_id"),
        customer_id=payload.get("customer_id"),
        action_id=payload.get("action_id"),
    )


@router.post("/cards/whatsapp/render")
async def cards_whatsapp_render(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
    kind = payload.get("kind", "card")
    if kind == "approval":
        return render_approval_card_for_whatsapp(payload.get("card") or {})
    if kind == "daily_brief":
        return render_daily_brief_for_whatsapp(payload.get("brief") or {})
    return render_card_for_whatsapp(payload.get("card") or {})


# ── Intake ───────────────────────────────────────────────────
@router.get("/intake/questions/{intent}")
async def intake_questions(intent: str) -> dict[str, Any]:
    return build_intake_questions_for_intent(intent)


@router.post("/intake/validate")
async def intake_validate(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
    return validate_intake_completeness(
        payload.get("intent", "ask_services"),
        payload.get("payload") or {},
    )


# ── Service workflow ─────────────────────────────────────────
@router.post("/service/start")
async def service_start(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
    return build_service_pipeline(
        service_id=payload.get("service_id", ""),
        customer_id=payload.get("customer_id", ""),
    )


@router.post("/tools/plan")
async def tools_plan(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
    return plan_tool_action(
        tool=payload.get("tool", ""),
        payload=payload.get("payload"),
        customer_id=payload.get("customer_id"),
        context=payload.get("context"),
    )


# ── Proof + Upsell ───────────────────────────────────────────
@router.post("/proof-pack/dispatch")
async def proof_pack_dispatch(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
    return dispatch_proof_pack(
        service_id=payload.get("service_id", ""),
        customer_id=payload.get("customer_id"),
        channel=payload.get("channel", "email"),
        metrics=payload.get("metrics"),
    )


@router.post("/upsell/recommend")
async def upsell_recommend(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
    return recommend_upsell_after_service(
        completed_service_id=payload.get("completed_service_id", ""),
        pilot_metrics=payload.get("pilot_metrics"),
    )


@router.post("/upsell/card")
async def upsell_card(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
    return build_upsell_card(
        completed_service_id=payload.get("completed_service_id", ""),
        pilot_metrics=payload.get("pilot_metrics"),
    )


# ── Bundles ──────────────────────────────────────────────────
@router.get("/bundles")
async def bundles() -> dict[str, Any]:
    return list_bundles()


@router.post("/bundles/recommend")
async def bundles_recommend(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
    return recommend_bundle(
        intent=payload.get("intent"),
        has_contact_list=bool(payload.get("has_contact_list", False)),
        is_agency=bool(payload.get("is_agency", False)),
        is_local_business=bool(payload.get("is_local_business", False)),
        budget_sar=int(payload.get("budget_sar", 1000)),
    )


# ── Modes ────────────────────────────────────────────────────
@router.post("/mode/ceo")
async def mode_ceo(payload: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    return build_ceo_command_center(
        company_name=payload.get("company_name", ""),
        sector=payload.get("sector", "saas"),
    )


@router.post("/mode/ceo/daily-brief")
async def mode_ceo_daily(payload: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    return build_executive_daily_brief(
        company_name=payload.get("company_name", ""),
        sector=payload.get("sector", "saas"),
    )


@router.post("/mode/ceo/risks")
async def mode_ceo_risks() -> dict[str, Any]:
    return build_revenue_risks_summary()


@router.post("/mode/client")
async def mode_client(payload: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    return build_client_dashboard(
        customer_id=payload.get("customer_id", ""),
        company_name=payload.get("company_name", ""),
        active_services=payload.get("active_services") or [],
        open_actions=int(payload.get("open_actions", 0)),
        proof_pack_due=bool(payload.get("proof_pack_due", False)),
    )


@router.post("/mode/agency")
async def mode_agency(payload: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    return build_agency_dashboard(
        agency_id=payload.get("agency_id", "agency_demo"),
        agency_name=payload.get("agency_name", ""),
        clients=payload.get("clients") or [],
    )


@router.post("/mode/agency/add-client")
async def mode_agency_add_client(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
    return add_agency_client(
        agency_id=payload.get("agency_id", "agency_demo"),
        client_company_name=payload.get("client_company_name", ""),
        sector=payload.get("sector", ""),
        monthly_subscription_sar=int(payload.get("monthly_subscription_sar", 0)),
        revenue_share_pct=int(payload.get("revenue_share_pct", 20)),
    )


@router.post("/mode/agency/revenue-share")
async def mode_agency_revenue_share(payload: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    return list_agency_revenue_share(clients=payload.get("clients") or [])


@router.post("/mode/agency/co-branded-proof")
async def mode_agency_co_branded_proof(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
    return build_co_branded_proof_pack(
        agency_name=payload.get("agency_name", ""),
        client_company_name=payload.get("client_company_name", ""),
        metrics=payload.get("metrics"),
    )


# ── Demos ────────────────────────────────────────────────────
@router.get("/whatsapp/daily-brief/demo")
async def whatsapp_daily_brief_demo() -> dict[str, Any]:
    brief = build_executive_daily_brief(company_name="Acme")
    return render_daily_brief_for_whatsapp(brief)


@router.get("/proof-pack/demo")
async def proof_pack_demo() -> dict[str, Any]:
    return dispatch_proof_pack(
        service_id="first_10_opportunities_sprint",
        customer_id="demo",
        metrics={"opportunities_generated": 10, "drafts_approved": 6,
                 "meetings_drafted": 2, "pipeline_influenced_sar": 30000,
                 "risks_blocked": 3},
    )

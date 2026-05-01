"""Autonomous Service Operator — /api/v1/operator (deterministic MVP)."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body, HTTPException

from auto_client_acquisition.autonomous_service_operator import (
    approval_manager as am,
    agency_mode,
    client_mode,
    conversation_router,
    executive_mode,
    intake_collector,
    proof_pack_dispatcher,
    self_growth_mode,
    service_bundles,
    service_delivery_mode,
    session_state as ss,
    tool_action_planner,
    upsell_engine,
    whatsapp_renderer,
    workflow_runner as wr,
)
from auto_client_acquisition.service_excellence.service_scoring import calculate_service_excellence_score

router = APIRouter(prefix="/api/v1/operator", tags=["autonomous_service_operator"])


def _mode_profile(mode: str) -> dict[str, Any]:
    m = (mode or "client").strip().lower()
    if m == "executive":
        return executive_mode.mode_profile()
    if m in ("agency_partner", "agency"):
        return agency_mode.mode_profile()
    if m in ("self_growth", "self-growth"):
        return self_growth_mode.mode_profile()
    if m in ("service_delivery", "delivery"):
        return service_delivery_mode.mode_profile()
    return client_mode.mode_profile()


@router.post("/chat/message")
async def operator_chat_message(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    msg = str(body.get("message") or "").strip()
    if not msg:
        raise HTTPException(status_code=400, detail="message_required")
    sid = str(body.get("session_id") or ss.new_session_id())
    ss.touch_session(sid)
    mode = str(body.get("mode") or "client")
    result = conversation_router.handle_message(sid, msg, mode=mode)
    result["mode_profile"] = _mode_profile(mode)
    return result


@router.post("/chat/decision")
async def operator_chat_decision(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    sid = str(body.get("session_id") or "").strip()
    dec = str(body.get("decision") or "").strip()
    if not sid or not dec:
        raise HTTPException(status_code=400, detail="session_id_and_decision_required")
    updated = am.apply_decision(sid, dec)
    return {"session": updated, "demo": True}


@router.get("/session/{session_id}")
async def operator_get_session(session_id: str) -> dict[str, Any]:
    s = ss.get_session(session_id)
    if not s:
        raise HTTPException(status_code=404, detail="session_not_found")
    return {**s, "demo": True}


@router.get("/cards/pending")
async def operator_cards_pending() -> dict[str, Any]:
    return {"pending": ss.list_sessions_with_pending(), "demo": True}


@router.post("/service/start")
async def operator_service_start(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    sid = str(body.get("session_id") or ss.new_session_id())
    svc_id = str(body.get("service_id") or "").strip()
    if not svc_id:
        raise HTTPException(status_code=400, detail="service_id_required")
    ss.touch_session(sid)
    wr.advance(sid, "start_service")
    intake = intake_collector.intake_questions(svc_id)
    am.set_pending_approval(
        sid,
        {
            "title_ar": f"بدء خدمة: {svc_id}",
            "buttons_ar": ["موافقة", "تعديل", "تخطي"],
            "service_id": svc_id,
        },
    )
    return {
        "session_id": sid,
        "intake": intake,
        "excellence": calculate_service_excellence_score(svc_id),
        "demo": True,
    }


@router.post("/service/continue")
async def operator_service_continue(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    sid = str(body.get("session_id") or "").strip()
    event = str(body.get("event") or "draft_ready").strip()
    if not sid:
        raise HTTPException(status_code=400, detail="session_id_required")
    ss.touch_session(sid)
    return {"session": wr.advance(sid, event), "demo": True}


@router.get("/proof-pack/demo")
async def operator_proof_pack_demo(service_id: str = "first_10_opportunities") -> dict[str, Any]:
    return proof_pack_dispatcher.build_proof_pack(service_id)


@router.get("/whatsapp/daily-brief")
async def operator_whatsapp_daily_brief() -> dict[str, Any]:
    return whatsapp_renderer.render_daily_brief_stub()


@router.get("/bundles")
async def operator_bundles() -> dict[str, Any]:
    return service_bundles.list_bundles()


@router.get("/tools/matrix")
async def operator_tools_matrix() -> dict[str, Any]:
    return tool_action_planner.list_tool_matrix()


@router.get("/upsell")
async def operator_upsell(service_id: str = "first_10_opportunities") -> dict[str, Any]:
    return upsell_engine.suggest_upsell(service_id)

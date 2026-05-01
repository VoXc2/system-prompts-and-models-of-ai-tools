"""Service Tower API — sellable services wizard (no live send)."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body

from auto_client_acquisition.platform_services.service_catalog import get_service_catalog
from auto_client_acquisition.service_tower.deliverables import (
    build_client_report_outline,
    build_deliverables,
    build_internal_operator_checklist,
    build_proof_pack_template,
)
from auto_client_acquisition.service_tower.mission_templates import build_service_workflow
from auto_client_acquisition.service_tower.pricing_engine import (
    calculate_monthly_offer,
    calculate_setup_fee,
    quote_service,
    recommend_plan_after_service,
)
from auto_client_acquisition.service_tower.service_catalog import get_service_by_id, list_tower_services
from auto_client_acquisition.service_tower.service_scorecard import build_service_scorecard
from auto_client_acquisition.service_tower.service_wizard import (
    build_intake_questions,
    recommend_service,
    start_service,
    summarize_recommendation_ar,
    validate_service_inputs,
)
from auto_client_acquisition.service_tower.contract_templates import list_contract_templates
from auto_client_acquisition.service_tower.upgrade_paths import build_all_upgrade_paths, recommend_upgrade
from auto_client_acquisition.service_tower.vertical_service_map import build_vertical_service_map
from auto_client_acquisition.service_tower.whatsapp_ceo_control import (
    build_ceo_daily_service_brief,
    build_end_of_day_service_report,
    build_service_approval_card,
)

router = APIRouter(prefix="/api/v1/services", tags=["service_tower"])


@router.get("/catalog")
async def services_catalog() -> dict[str, Any]:
    tower = list_tower_services()
    platform = get_service_catalog()
    return {
        "tower": tower,
        "platform_service_catalog": platform,
        "note_ar": "برج الخدمات (تفصيل بيع) + كتالوج المنصة (طبقة تقنية) — يُدمجان للعرض.",
        "demo": True,
    }


@router.post("/recommend")
async def services_recommend(payload: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    p = payload or {}
    rec = recommend_service(
        company_type=str(p.get("company_type") or ""),
        goal=str(p.get("goal") or ""),
        has_contact_list=bool(p.get("has_contact_list")),
        channels=list(p.get("channels") or []),
        budget_sar=p.get("budget_sar"),
    )
    rec["summary_ar"] = summarize_recommendation_ar(rec)
    return rec


@router.post("/start")
async def services_start(payload: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    p = payload or {}
    return start_service(str(p.get("service_id") or ""), dict(p.get("payload") or p))


@router.get("/demo/dashboard")
async def services_demo_dashboard() -> dict[str, Any]:
    ids = [s["service_id"] for s in list_tower_services().get("services") or []][:5]
    cards = []
    for sid in ids:
        svc = get_service_by_id(sid)
        cards.append(
            {
                "service_id": sid,
                "name_ar": (svc or {}).get("name_ar"),
                "deliverables": build_deliverables(sid),
                "scorecard": build_service_scorecard(
                    sid,
                    {"drafts_created": 2, "approvals": 1, "meetings_booked": 0, "risks_blocked": 3},
                ),
            }
        )
    return {"cards": cards, "live_send": False, "demo": True}


@router.get("/ceo/daily-brief")
async def ceo_daily_brief() -> dict[str, Any]:
    return build_ceo_daily_service_brief()


@router.get("/ceo/end-of-day")
async def ceo_end_of_day() -> dict[str, Any]:
    return build_end_of_day_service_report()


@router.post("/approval-card")
async def approval_card(payload: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    p = payload or {}
    return build_service_approval_card(str(p.get("service_id") or "growth_os"), str(p.get("action") or "draft_review"))


@router.get("/verticals")
async def services_verticals() -> dict[str, Any]:
    return build_vertical_service_map()


@router.get("/upgrade-paths")
async def services_upgrade_paths() -> dict[str, Any]:
    return build_all_upgrade_paths()


@router.get("/contracts/templates")
async def services_contract_templates() -> dict[str, Any]:
    return list_contract_templates()


@router.get("/{service_id}/workflow")
async def service_workflow(service_id: str) -> dict[str, Any]:
    return build_service_workflow(service_id)


@router.post("/{service_id}/quote")
async def service_quote(
    service_id: str,
    payload: dict[str, Any] = Body(default_factory=dict),
) -> dict[str, Any]:
    p = payload or {}
    q = quote_service(
        service_id,
        company_size=str(p.get("company_size") or "smb"),
        urgency=str(p.get("urgency") or "normal"),
        channels_count=int(p.get("channels_count") or 1),
    )
    q["setup_fee_hint"] = calculate_setup_fee(service_id)
    q["monthly_hint"] = calculate_monthly_offer(service_id)
    q["upgrade_hint"] = recommend_plan_after_service(service_id, str(p.get("outcome") or ""))
    return q


@router.get("/{service_id}/intake-questions")
async def intake_questions(service_id: str) -> dict[str, Any]:
    return build_intake_questions(service_id)


@router.post("/{service_id}/validate")
async def validate_inputs(service_id: str, payload: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    return validate_service_inputs(service_id, payload or {})


@router.get("/{service_id}/deliverables")
async def service_deliverables(service_id: str) -> dict[str, Any]:
    return {
        "deliverables": build_deliverables(service_id),
        "proof_pack": build_proof_pack_template(service_id),
        "client_report": build_client_report_outline(service_id),
        "operator_checklist": build_internal_operator_checklist(service_id),
        "demo": True,
    }


@router.get("/{service_id}/upgrade")
async def service_upgrade(service_id: str) -> dict[str, Any]:
    return recommend_upgrade(service_id, {})

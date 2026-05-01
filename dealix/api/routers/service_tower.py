"""Service Tower router — كتالوج الخدمات + wizard + workflow + pricing + cards."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body

from auto_client_acquisition.service_tower import (
    build_ceo_daily_service_brief,
    build_client_report_outline,
    build_deliverables,
    build_end_of_day_service_report,
    build_intake_questions,
    build_internal_operator_checklist,
    build_proof_pack_template,
    build_risk_alert_card,
    build_service_approval_card,
    build_service_scorecard,
    build_service_workflow,
    build_upsell_message_ar,
    calculate_monthly_offer,
    calculate_setup_fee,
    catalog_summary,
    get_service,
    list_all_services,
    map_service_to_growth_mission,
    map_service_to_subscription,
    quote_service,
    recommend_next_step,
    recommend_plan_after_service,
    recommend_service,
    recommend_upgrade,
    summarize_recommendation_ar,
    summarize_scorecard_ar,
    validate_service_inputs,
)

router = APIRouter(prefix="/api/v1/services", tags=["service-tower"])


# ── Catalog ──────────────────────────────────────────────────
@router.get("/catalog")
async def catalog() -> dict[str, Any]:
    return list_all_services()


@router.get("/summary")
async def summary() -> dict[str, Any]:
    return catalog_summary()


@router.post("/recommend")
async def recommend(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
    rec = recommend_service(
        company_type=payload.get("company_type", ""),
        goal=payload.get("goal", "fill_pipeline"),
        has_contact_list=bool(payload.get("has_contact_list", False)),
        channels=payload.get("channels", []),
        budget_sar=int(payload.get("budget_sar", 1000)),
    )
    rec["summary_ar"] = summarize_recommendation_ar(rec)
    return rec


# ── Per-service ──────────────────────────────────────────────
@router.get("/{service_id}/intake-questions")
async def service_intake_questions(service_id: str) -> dict[str, Any]:
    return build_intake_questions(service_id)


@router.post("/{service_id}/start")
async def service_start(
    service_id: str,
    payload: dict[str, Any] = Body(...),
) -> dict[str, Any]:
    validation = validate_service_inputs(service_id, payload)
    if not validation["valid"]:
        return {"started": False, "validation": validation}
    workflow = build_service_workflow(service_id)
    return {
        "started": True,
        "validation": validation,
        "workflow": workflow,
        "linked_growth_mission": map_service_to_growth_mission(service_id),
        "approval_required": True,
    }


@router.get("/{service_id}/workflow")
async def service_workflow(service_id: str) -> dict[str, Any]:
    return build_service_workflow(service_id)


@router.get("/{service_id}/deliverables")
async def service_deliverables(service_id: str) -> dict[str, Any]:
    return build_deliverables(service_id)


@router.get("/{service_id}/proof-pack-template")
async def service_proof_pack_template(service_id: str) -> dict[str, Any]:
    return build_proof_pack_template(service_id)


@router.get("/{service_id}/client-report-outline")
async def service_client_report_outline(service_id: str) -> dict[str, Any]:
    return build_client_report_outline(service_id)


@router.get("/{service_id}/operator-checklist")
async def service_operator_checklist(service_id: str) -> dict[str, Any]:
    return build_internal_operator_checklist(service_id)


@router.post("/{service_id}/quote")
async def service_quote(
    service_id: str,
    payload: dict[str, Any] = Body(default_factory=dict),
) -> dict[str, Any]:
    return quote_service(
        service_id,
        company_size=payload.get("company_size", "small"),
        urgency=payload.get("urgency", "normal"),
        channels_count=int(payload.get("channels_count", 1)),
    )


@router.get("/{service_id}/setup-fee")
async def service_setup_fee(service_id: str) -> dict[str, Any]:
    return calculate_setup_fee(service_id)


@router.get("/{service_id}/monthly-offer")
async def service_monthly_offer(service_id: str) -> dict[str, Any]:
    return calculate_monthly_offer(service_id)


@router.post("/{service_id}/scorecard")
async def service_scorecard(
    service_id: str,
    metrics: dict[str, Any] = Body(default_factory=dict),
) -> dict[str, Any]:
    return build_service_scorecard(service_id, metrics)


@router.get("/{service_id}/upgrade-path")
async def service_upgrade_path(service_id: str) -> dict[str, Any]:
    return recommend_upgrade(service_id)


@router.get("/{service_id}/post-service-plan")
async def service_post_plan(service_id: str) -> dict[str, Any]:
    return recommend_plan_after_service(service_id)


# ── CEO control via WhatsApp ─────────────────────────────────
@router.get("/ceo/daily-brief")
async def ceo_daily_brief() -> dict[str, Any]:
    return build_ceo_daily_service_brief()


@router.post("/ceo/approval-card")
async def ceo_approval_card(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
    return build_service_approval_card(
        service_id=payload.get("service_id", ""),
        action=payload.get("action", ""),
    )


@router.get("/ceo/risk-alert/demo")
async def ceo_risk_alert_demo() -> dict[str, Any]:
    return build_risk_alert_card()


@router.get("/ceo/end-of-day/demo")
async def ceo_end_of_day_demo() -> dict[str, Any]:
    return build_end_of_day_service_report()

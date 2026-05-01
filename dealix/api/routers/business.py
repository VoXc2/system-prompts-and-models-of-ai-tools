"""Business strategy, pricing, GTM, and unit economics API (deterministic)."""

from __future__ import annotations

from typing import Any, cast

from fastapi import APIRouter, Body

from auto_client_acquisition.ai.model_router import ModelTask, get_model_route, requires_guardrail
from auto_client_acquisition.business import (
    activation_metrics,
    ai_quality_metrics,
    channel_strategy,
    compare_competitors,
    dealix_differentiators,
    estimate_cac_payback,
    estimate_gross_margin,
    estimate_ltv,
    estimate_mrr_path,
    estimate_roi,
    first_100_customers_plan,
    first_10_customers_plan,
    founder_led_sales_script,
    north_star_metrics,
    partner_strategy,
    positioning_statement,
    recommend_plan,
    retention_metrics,
    revenue_metrics,
)
from auto_client_acquisition.business.pricing_strategy import calculate_performance_fee, get_pricing_tiers
from auto_client_acquisition.business.proof_pack import build_demo_proof_pack, calculate_roi_summary, grade_account_health
from auto_client_acquisition.business.market_positioning import Segment
from auto_client_acquisition.business.verticals import get_vertical_playbooks, recommend_vertical

router = APIRouter(prefix="/api/v1/business", tags=["business"])


@router.get("/pricing")
async def pricing() -> dict[str, Any]:
    return get_pricing_tiers()


@router.post("/recommend-plan")
async def recommend_plan_endpoint(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    return recommend_plan(
        company_size=str(body.get("company_size", "sme")),
        monthly_budget_sar=float(body.get("monthly_budget_sar", 2500)),
        goal=str(body.get("goal", "growth")),
    )


@router.post("/roi")
async def roi_endpoint(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    return estimate_roi(
        plan_price_sar=float(body.get("plan_price_sar", 2999)),
        expected_pipeline_sar=float(body.get("expected_pipeline_sar", 90000)),
        expected_revenue_sar=float(body.get("expected_revenue_sar", 25000)),
    )


@router.get("/competitors")
async def competitors() -> dict[str, Any]:
    return {"items": compare_competitors()}


@router.get("/differentiators")
async def differentiators() -> dict[str, Any]:
    return {"differentiators": dealix_differentiators()}


@router.get("/gtm/first-10")
async def gtm_first_10() -> dict[str, Any]:
    return first_10_customers_plan()


@router.get("/gtm/first-100")
async def gtm_first_100() -> dict[str, Any]:
    return first_100_customers_plan()


@router.get("/metrics")
async def metrics() -> dict[str, Any]:
    return {
        "north_star": north_star_metrics(),
        "activation": activation_metrics(),
        "retention": retention_metrics(),
        "revenue": revenue_metrics(),
        "ai_quality": ai_quality_metrics(),
    }


@router.get("/unit-economics/demo")
async def unit_economics_demo() -> dict[str, Any]:
    return {
        "gross_margin": estimate_gross_margin(),
        "cac_payback": estimate_cac_payback(),
        "ltv": estimate_ltv(),
        "mrr_path": estimate_mrr_path(),
    }


@router.post("/performance-fee/demo")
async def performance_fee_demo(body: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    return calculate_performance_fee(
        qualified_leads=int(body.get("qualified_leads", 5)),
        booked_meetings=int(body.get("booked_meetings", 2)),
        won_revenue_sar=float(body.get("won_revenue_sar", 80000)),
    )


@router.get("/positioning/{segment}")
async def positioning(segment: str) -> dict[str, Any]:
    allowed: tuple[Segment, ...] = ("founder", "sme", "enterprise", "agency")
    seg = cast(Segment, segment if segment in allowed else "founder")
    return {"segment": seg, "statement_ar": positioning_statement(seg)}


@router.get("/channels")
async def channels() -> dict[str, Any]:
    return channel_strategy()


@router.get("/partners")
async def partners() -> dict[str, Any]:
    return partner_strategy()


@router.get("/sales-script")
async def sales_script() -> dict[str, Any]:
    return founder_led_sales_script()


@router.get("/verticals")
async def verticals() -> dict[str, Any]:
    return get_vertical_playbooks()


@router.post("/verticals/recommend")
async def vertical_recommend(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    return recommend_vertical(
        industry=str(body.get("industry", "b2b")),
        city=str(body.get("city", "Riyadh")),
        goal=str(body.get("goal", "pipeline")),
    )


@router.get("/proof-pack/demo")
async def proof_pack_demo() -> dict[str, Any]:
    return build_demo_proof_pack()


@router.post("/proof-pack/roi-summary")
async def proof_pack_roi(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    return calculate_roi_summary(
        subscription_sar=float(body.get("subscription_sar", 2999)),
        influenced_revenue_sar=float(body.get("influenced_revenue_sar", 40000)),
        hours_saved=float(body.get("hours_saved", 12)),
    )


@router.post("/account-health")
async def account_health(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    return grade_account_health(
        brief_opens_4w=int(body.get("brief_opens_4w", 8)),
        approvals_4w=int(body.get("approvals_4w", 5)),
        blocks_4w=int(body.get("blocks_4w", 2)),
    )


@router.get("/model-routes")
async def model_routes() -> dict[str, Any]:
    routes = []
    for task in ModelTask:
        r = get_model_route(task)
        routes.append(
            {
                "task": task.value,
                "quality_tier": r.quality_tier,
                "latency": r.latency,
                "cost_class": r.cost_class,
                "guardrail_required": r.guardrail_required,
                "eval_metric": r.eval_metric,
            }
        )
    return {"routes": routes}


@router.get("/model-routes/guardrail-tasks")
async def guardrail_tasks() -> dict[str, Any]:
    return {"tasks": [t.value for t in ModelTask if requires_guardrail(t)]}

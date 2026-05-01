"""Revenue Company OS router — command feed + work units + proof + memory."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body

from auto_client_acquisition.revenue_company_os import (
    REVENUE_EDGE_TYPES,
    REVENUE_WORK_UNIT_TYPES,
    aggregate_work_units,
    build_card_from_event,
    build_channel_health_snapshot,
    build_command_feed_for_customer,
    build_growth_memory_demo,
    build_opportunity_factory_demo,
    build_revenue_action_graph_demo,
    build_revenue_proof_ledger_demo,
    build_revenue_work_unit,
    build_service_factory_demo,
    build_weekly_self_improvement_report,
    instantiate_service,
    revenue_os_command_feed_demo,
)

router = APIRouter(prefix="/api/v1/revenue-os", tags=["revenue-company-os"])


# ── Command Feed ─────────────────────────────────────────────
@router.get("/command-feed/demo")
async def command_feed_demo() -> dict[str, Any]:
    return revenue_os_command_feed_demo()


@router.post("/events/ingest")
async def events_ingest(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """Convert one event → Arabic decision card. Never executes anything."""
    return build_card_from_event(payload)


@router.post("/command-feed/build")
async def command_feed_build(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
    return build_command_feed_for_customer(
        customer_id=payload.get("customer_id", "demo"),
        events=payload.get("events", []),
    )


# ── Work Units ───────────────────────────────────────────────
@router.get("/work-units/types")
async def work_unit_types() -> dict[str, Any]:
    return {"types": list(REVENUE_WORK_UNIT_TYPES)}


@router.post("/work-units/build")
async def work_units_build(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
    try:
        return build_revenue_work_unit(
            unit_type=payload.get("unit_type", ""),
            service_id=payload.get("service_id", ""),
            customer_id=payload.get("customer_id", ""),
            risk_level=payload.get("risk_level", "low"),
            revenue_influenced_sar=float(payload.get("revenue_influenced_sar", 0)),
            proof_event=payload.get("proof_event", ""),
            notes=payload.get("notes", ""),
        )
    except ValueError as exc:
        return {"error": str(exc)}


@router.post("/work-units/aggregate")
async def work_units_aggregate(
    units: list[dict[str, Any]] = Body(default_factory=list, embed=True),
) -> dict[str, Any]:
    return aggregate_work_units(units)


@router.get("/work-units/demo")
async def work_units_demo() -> dict[str, Any]:
    """Demo aggregation across 12 sample units."""
    return build_revenue_proof_ledger_demo()


# ── Proof Ledger ─────────────────────────────────────────────
@router.get("/proof-ledger/demo")
async def proof_ledger_demo() -> dict[str, Any]:
    return build_revenue_proof_ledger_demo()


# ── Action Graph ─────────────────────────────────────────────
@router.get("/action-graph/edge-types")
async def action_graph_edge_types() -> dict[str, Any]:
    return {"edge_types": list(REVENUE_EDGE_TYPES)}


@router.get("/action-graph/demo")
async def action_graph_demo() -> dict[str, Any]:
    return build_revenue_action_graph_demo()


# ── Channel Health ───────────────────────────────────────────
@router.post("/channel-health/snapshot")
async def channel_health_snapshot(payload: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    return build_channel_health_snapshot(
        metrics_per_channel=payload.get("metrics_per_channel"),
    )


@router.get("/channel-health/demo")
async def channel_health_demo() -> dict[str, Any]:
    return build_channel_health_snapshot()


# ── Opportunity Factory ──────────────────────────────────────
@router.post("/opportunity-factory")
async def opportunity_factory(payload: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    return build_opportunity_factory_demo(
        sector=payload.get("sector", "training"),
        city=payload.get("city", "Riyadh"),
        limit=int(payload.get("limit", 5)),
    )


@router.get("/opportunity-factory/demo")
async def opportunity_factory_demo() -> dict[str, Any]:
    return build_opportunity_factory_demo()


# ── Service Factory ──────────────────────────────────────────
@router.post("/service-factory")
async def service_factory(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
    return instantiate_service(
        service_id=payload.get("service_id", ""),
        customer_id=payload.get("customer_id", ""),
        company_size=payload.get("company_size", "small"),
        urgency=payload.get("urgency", "normal"),
    )


@router.get("/service-factory/demo")
async def service_factory_demo() -> dict[str, Any]:
    return build_service_factory_demo()


# ── Growth Memory ────────────────────────────────────────────
@router.get("/growth-memory/demo")
async def growth_memory_demo() -> dict[str, Any]:
    return build_growth_memory_demo()


# ── Self-Improvement Loop ────────────────────────────────────
@router.post("/self-improvement/weekly-report")
async def self_improvement_weekly(payload: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    return build_weekly_self_improvement_report(weekly_metrics=payload)


@router.get("/self-improvement/demo")
async def self_improvement_demo() -> dict[str, Any]:
    return build_weekly_self_improvement_report(weekly_metrics={
        "approval_rate": 0.42,
        "reply_rate": 0.05,
        "meeting_rate": 0.018,
        "blocked_actions": 12,
        "service_revenue_sar": {
            "first_10_opportunities_sprint": 1500,
            "list_intelligence": 999,
            "growth_os_monthly": 2999,
        },
        "top_objections": ["price", "timing"],
        "channel_outcomes": {"email": "healthy", "whatsapp": "watch"},
    })

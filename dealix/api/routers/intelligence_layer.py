"""Intelligence Layer router — growth brain + missions + DNA + simulator + brief."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body

from auto_client_acquisition.intelligence_layer import (
    DecisionMemory,
    analyze_competitive_move,
    build_board_brief,
    build_command_feed_demo,
    build_growth_brain,
    build_revenue_dna_demo,
    compute_trust_score,
    extract_revenue_dna,
    learn_from_decision,
    list_intel_missions,
    recommend_missions,
    simulate_opportunity,
)

router = APIRouter(prefix="/api/v1/intelligence", tags=["intelligence-layer"])

# Per-customer in-memory decision memory (demo; production = Supabase)
_MEMORY: dict[str, DecisionMemory] = {}


def _memory_for(customer_id: str) -> DecisionMemory:
    if customer_id not in _MEMORY:
        _MEMORY[customer_id] = DecisionMemory(customer_id=customer_id)
    return _MEMORY[customer_id]


# ── Growth Brain ──────────────────────────────────────────────
@router.post("/growth-brain/build")
async def growth_brain_build(payload: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    brain = build_growth_brain(payload)
    return {**brain.to_dict(), "ready_for_autopilot": brain.is_ready_for_autopilot()}


# ── Command Feed ──────────────────────────────────────────────
@router.get("/command-feed/demo")
async def command_feed_demo() -> dict[str, Any]:
    return build_command_feed_demo()


# ── Missions ──────────────────────────────────────────────────
@router.get("/missions")
async def missions_list() -> dict[str, Any]:
    return list_intel_missions()


@router.post("/missions/recommend")
async def missions_recommend(payload: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    brain_payload = payload.get("growth_brain") or payload
    brain = build_growth_brain(brain_payload) if brain_payload else None
    return recommend_missions(brain, limit=int(payload.get("limit", 3)))


# ── Trust Score ───────────────────────────────────────────────
@router.post("/trust-score")
async def trust_score(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
    return compute_trust_score(
        source_quality=payload.get("source_quality", "unknown"),
        opt_in=bool(payload.get("opt_in", False)),
        channel=payload.get("channel", "whatsapp"),
        message_text=payload.get("message_text", ""),
        frequency_count_this_week=int(payload.get("frequency_count_this_week", 0)),
        weekly_cap=int(payload.get("weekly_cap", 2)),
        approval_status=payload.get("approval_status", "pending"),
    )


# ── Revenue DNA ───────────────────────────────────────────────
@router.get("/revenue-dna/demo")
async def revenue_dna_demo() -> dict[str, Any]:
    return build_revenue_dna_demo()


@router.post("/revenue-dna")
async def revenue_dna_post(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
    return extract_revenue_dna(
        customer_id=payload.get("customer_id", "unknown"),
        won_deals=payload.get("won_deals", []),
        replies=payload.get("replies", []),
        objections=payload.get("objections", []),
    )


# ── Opportunity Simulator ─────────────────────────────────────
@router.post("/simulate-opportunity")
async def simulate_opportunity_endpoint(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
    return simulate_opportunity(
        target_count=int(payload.get("target_count", 100)),
        sector=payload.get("sector", "saas"),
        avg_deal_value_sar=float(payload.get("avg_deal_value_sar", 25_000)),
        channel=payload.get("channel", "whatsapp"),
        cold_pct=float(payload.get("cold_pct", 0)),
        quality_lift=float(payload.get("quality_lift", 1.0)),
    )


# ── Competitive Moves ─────────────────────────────────────────
@router.post("/competitive-move/analyze")
async def competitive_move_analyze(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
    return analyze_competitive_move(
        competitor_name=payload.get("competitor_name", "?"),
        move_type=payload.get("move_type", "new_offer"),
        payload=payload.get("payload", {}),
    )


# ── Board Brief ───────────────────────────────────────────────
@router.get("/board-brief/demo")
async def board_brief_demo() -> dict[str, Any]:
    return build_board_brief()


# ── Decision Memory ───────────────────────────────────────────
@router.post("/decisions/record")
async def decisions_record(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
    customer_id = payload.get("customer_id", "demo")
    mem = _memory_for(customer_id)
    return learn_from_decision(
        memory=mem,
        decision=payload.get("decision", "skip"),
        action_type=payload.get("action_type", "send_whatsapp"),
        channel=payload.get("channel", "whatsapp"),
        sector=payload.get("sector"),
        tone=payload.get("tone"),
        objection_id=payload.get("objection_id"),
    )


@router.get("/decisions/preferences")
async def decisions_preferences(customer_id: str) -> dict[str, Any]:
    mem = _memory_for(customer_id)
    return {"customer_id": customer_id, "preferences": mem.preferences()}

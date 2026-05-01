"""Intelligence layer API — deterministic JSON; optional ten-in-ten bridge."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body

from auto_client_acquisition.innovation.ten_in_ten import build_ten_opportunities
from auto_client_acquisition.intelligence_layer.action_graph import build_action_graph_trace
from auto_client_acquisition.intelligence_layer.board_brief import build_board_brief
from auto_client_acquisition.intelligence_layer.competitive_moves import build_competitive_moves
from auto_client_acquisition.intelligence_layer.decision_memory import list_decisions, record_decision
from auto_client_acquisition.intelligence_layer.growth_brain import build_growth_profile
from auto_client_acquisition.intelligence_layer.intel_command_feed import build_intel_command_feed
from auto_client_acquisition.intelligence_layer.mission_engine import get_mission, list_mission_catalog
from auto_client_acquisition.intelligence_layer.opportunity_simulator import simulate_opportunities
from auto_client_acquisition.intelligence_layer.revenue_dna import build_revenue_dna
from auto_client_acquisition.intelligence_layer.trust_score import compute_trust_score

router = APIRouter(prefix="/api/v1/intelligence", tags=["intelligence_layer"])


@router.post("/growth-profile")
async def growth_profile(company: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    return build_growth_profile(company or {})


@router.get("/command-feed")
async def intel_command_feed() -> dict[str, Any]:
    return build_intel_command_feed()


@router.get("/command-feed/demo")
async def intel_command_feed_demo() -> dict[str, Any]:
    """Alias of ``GET /command-feed`` for product/docs compatibility."""
    return build_intel_command_feed()


@router.post("/missions/first-10-opportunities")
async def missions_first_10_opportunities(
    payload: dict[str, Any] = Body(default_factory=dict),
) -> dict[str, Any]:
    """Thin wrapper around innovation ``build_ten_opportunities`` — no duplicate logic."""
    return build_ten_opportunities(payload or None)


@router.get("/missions/catalog")
async def missions_catalog() -> dict[str, Any]:
    """Mission engine metadata + pointer to innovation missions."""
    return list_mission_catalog()


@router.get("/missions/{mission_id}")
async def mission_detail(mission_id: str) -> dict[str, Any]:
    return get_mission(mission_id)


@router.post("/action-graph/demo")
async def action_graph_demo(payload: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    return build_action_graph_trace(payload or {})


@router.get("/decision-memory/demo")
async def decision_memory_demo() -> dict[str, Any]:
    return list_decisions(limit=20)


@router.post("/decision-memory/record")
async def decision_memory_record(entry: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    return record_decision(entry or {})


@router.post("/trust-score")
async def trust_score(signals: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    return compute_trust_score(signals or {})


@router.post("/revenue-dna")
async def revenue_dna(context: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    return build_revenue_dna(context or {})


@router.post("/opportunity-simulator")
async def opportunity_simulator(inputs: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    return simulate_opportunities(inputs or {})


@router.post("/board-brief")
async def board_brief(snapshot: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    return build_board_brief(snapshot or {})


@router.get("/competitive-moves")
async def competitive_moves(sector: str | None = None) -> dict[str, Any]:
    return build_competitive_moves(sector)


@router.post("/bundle")
async def intelligence_bundle(
    payload: dict[str, Any] = Body(default_factory=dict),
) -> dict[str, Any]:
    """
    Single round-trip for demos. Optional ``include_ten_in_ten`` merges
    ``build_ten_opportunities`` without exposing a duplicate HTTP path.
    """
    company = payload.get("company") if isinstance(payload.get("company"), dict) else {}
    out: dict[str, Any] = {
        "growth_profile": build_growth_profile(company),
        "intel_command_feed": build_intel_command_feed({"append_custom": payload.get("extra_card")}),
        "trust_score": compute_trust_score(payload.get("trust_signals") if isinstance(payload.get("trust_signals"), dict) else {}),
        "revenue_dna": build_revenue_dna(payload.get("revenue_context") if isinstance(payload.get("revenue_context"), dict) else {}),
        "opportunity_simulator": simulate_opportunities(
            payload.get("simulator") if isinstance(payload.get("simulator"), dict) else {}
        ),
        "board_brief": build_board_brief(payload.get("board") if isinstance(payload.get("board"), dict) else {}),
        "competitive_moves": build_competitive_moves(str(payload.get("sector") or "") or None),
    }
    if payload.get("include_ten_in_ten"):
        ten_payload = payload.get("ten_in_ten") if isinstance(payload.get("ten_in_ten"), dict) else company
        out["ten_in_ten"] = build_ten_opportunities(ten_payload)
    return out

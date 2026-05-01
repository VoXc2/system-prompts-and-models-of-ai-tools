"""Launch Ops router — Private Beta + Demo + Outreach + Go/No-Go + Scorecard."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body

from auto_client_acquisition.launch_ops import (
    build_12_min_demo_flow,
    build_close_script,
    build_daily_launch_scorecard,
    build_discovery_questions,
    build_first_20_segments,
    build_followup_message,
    build_launch_readiness,
    build_objection_responses,
    build_outreach_message,
    build_private_beta_offer,
    build_private_beta_safety_notes,
    build_reply_handlers,
    build_weekly_launch_scorecard,
    decide_go_no_go,
    private_beta_faq,
    record_launch_event,
)

router = APIRouter(prefix="/api/v1/launch", tags=["launch-ops"])


# ── Private Beta ─────────────────────────────────────────────
@router.get("/private-beta/offer")
async def private_beta_offer() -> dict[str, Any]:
    return {
        "offer": build_private_beta_offer(),
        "safety": build_private_beta_safety_notes(),
        "faq": private_beta_faq(),
    }


# ── Demo flow ────────────────────────────────────────────────
@router.get("/demo/flow")
async def demo_flow() -> dict[str, Any]:
    return {
        "flow": build_12_min_demo_flow(),
        "discovery_questions": build_discovery_questions(),
        "objections": build_objection_responses(),
        "close": build_close_script(),
    }


# ── Outreach ─────────────────────────────────────────────────
@router.get("/outreach/first-20")
async def outreach_first_20() -> dict[str, Any]:
    segments = build_first_20_segments()
    sample_messages = {
        s["id"]: build_outreach_message(s["id"])
        for s in segments["segments"]
    }
    return {
        **segments,
        "sample_messages": sample_messages,
        "reply_handlers": build_reply_handlers(),
    }


@router.post("/outreach/message")
async def outreach_message(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
    return build_outreach_message(
        segment_id=payload.get("segment_id", ""),
        name=payload.get("name", "[الاسم]"),
    )


@router.post("/outreach/followup")
async def outreach_followup(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
    return build_followup_message(
        segment_id=payload.get("segment_id", ""),
        step=int(payload.get("step", 1)),
        name=payload.get("name", "[الاسم]"),
    )


# ── Go / No-Go ───────────────────────────────────────────────
@router.post("/go-no-go")
async def go_no_go(payload: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    return decide_go_no_go(statuses=payload.get("statuses"))


@router.get("/readiness")
async def readiness() -> dict[str, Any]:
    """Readiness with all gates assumed False (use POST /go-no-go for real status)."""
    return build_launch_readiness(statuses={})


# ── Scorecard ────────────────────────────────────────────────
@router.post("/scorecard/event")
async def scorecard_event(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
    try:
        return record_launch_event(
            event_type=payload.get("event_type", ""),
            customer_id=payload.get("customer_id"),
            notes=payload.get("notes"),
        )
    except ValueError as exc:
        return {"error": str(exc)}


@router.post("/scorecard/daily")
async def scorecard_daily(
    events: list[dict[str, Any]] = Body(default_factory=list, embed=True),
) -> dict[str, Any]:
    return build_daily_launch_scorecard(events=events)


@router.post("/scorecard/weekly")
async def scorecard_weekly(
    events: list[dict[str, Any]] = Body(default_factory=list, embed=True),
) -> dict[str, Any]:
    return build_weekly_launch_scorecard(events=events)


@router.get("/scorecard/demo")
async def scorecard_demo() -> dict[str, Any]:
    """Demo scorecard with synthetic events."""
    demo_events = [
        {"event_type": "outreach_sent"} for _ in range(15)
    ] + [
        {"event_type": "reply_received"} for _ in range(4)
    ] + [
        {"event_type": "demo_booked"} for _ in range(2)
    ] + [
        {"event_type": "blocked_action"} for _ in range(6)
    ]
    return build_daily_launch_scorecard(events=demo_events)

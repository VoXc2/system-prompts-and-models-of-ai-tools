"""Meeting Intelligence router — pre-meeting brief, transcript summary, follow-up."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body

from auto_client_acquisition.meeting_intelligence import (
    build_post_meeting_followup,
    build_pre_meeting_brief,
    compute_deal_risk,
    extract_objections,
    parse_transcript_entries,
    summarize_meeting,
)

router = APIRouter(prefix="/api/v1/meeting-intelligence", tags=["meeting-intelligence"])


@router.post("/brief")
async def brief(payload: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    return build_pre_meeting_brief(
        company=payload.get("company"),
        contact=payload.get("contact"),
        opportunity=payload.get("opportunity"),
        sector=payload.get("sector"),
    )


@router.get("/brief/demo")
async def brief_demo() -> dict[str, Any]:
    return build_pre_meeting_brief(
        company={"name": "شركة نمو للتدريب", "sector": "training"},
        contact={"name": "أحمد", "role": "مدير المبيعات"},
        opportunity={"expected_value_sar": 18000},
        sector="training",
    )


@router.post("/transcript/summarize")
async def transcript_summarize(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
    parsed = parse_transcript_entries(payload.get("entries") or payload.get("text", ""))
    summary = summarize_meeting(parsed)
    objections = extract_objections(
        " ".join(t["text"] for t in parsed.get("speaker_turns", []))
    )
    return {"parsed": parsed, "summary": summary, "objections": objections}


@router.post("/followup/draft")
async def followup_draft(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
    return build_post_meeting_followup(
        summary=payload.get("summary"),
        next_steps=payload.get("next_steps", []),
        contact_name=payload.get("contact_name", ""),
        company_name=payload.get("company_name", ""),
        objections=payload.get("objections", []),
    )


@router.post("/deal-risk")
async def deal_risk(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
    return compute_deal_risk(
        objections=payload.get("objections", []),
        next_step_set=bool(payload.get("next_step_set", False)),
        decision_maker_present=bool(payload.get("decision_maker_present", False)),
        days_since_last_touch=int(payload.get("days_since_last_touch", 0)),
        expected_value_sar=float(payload.get("expected_value_sar", 0)),
    )

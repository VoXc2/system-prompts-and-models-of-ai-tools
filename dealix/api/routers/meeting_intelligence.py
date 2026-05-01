"""Meeting intelligence API — text in, Arabic briefs out (no Calendar insert)."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body

from auto_client_acquisition.meeting_intelligence.followup_builder import build_post_meeting_followup
from auto_client_acquisition.meeting_intelligence.meeting_brief import build_pre_meeting_brief
from auto_client_acquisition.meeting_intelligence.objection_extractor import extract_objections
from auto_client_acquisition.meeting_intelligence.transcript_parser import summarize_transcript_text

router = APIRouter(prefix="/api/v1/meeting-intelligence", tags=["meeting_intelligence"])


@router.post("/transcript/summarize")
async def transcript_summarize(payload: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    text = str(payload.get("text") or "")
    base = summarize_transcript_text(text)
    base["objections"] = extract_objections(text)
    return base


@router.post("/followup/draft")
async def followup_draft(payload: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    summary = str(payload.get("summary_ar") or "")
    steps = payload.get("next_steps") if isinstance(payload.get("next_steps"), list) else None
    return build_post_meeting_followup(summary, steps)


@router.post("/brief/pre-meeting")
async def pre_meeting_brief(payload: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    company = payload.get("company") if isinstance(payload.get("company"), dict) else {}
    contact = payload.get("contact") if isinstance(payload.get("contact"), dict) else {}
    opportunity = payload.get("opportunity") if isinstance(payload.get("opportunity"), dict) else {}
    return build_pre_meeting_brief(company, contact, opportunity)

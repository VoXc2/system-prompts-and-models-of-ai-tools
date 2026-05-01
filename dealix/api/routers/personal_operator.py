"""Arabic Personal Strategic Operator endpoints."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body, HTTPException

from auto_client_acquisition.personal_operator import (
    ApprovalDecision,
    build_daily_brief,
    default_sami_profile,
    draft_follow_up,
    draft_intro_message,
    suggest_opportunities,
)
from auto_client_acquisition.personal_operator.launch_report import build_launch_report
from auto_client_acquisition.personal_operator.operator import apply_decision, launch_readiness_score
from auto_client_acquisition.v3.project_intelligence import answer_operator_question, explain_project_intelligence_stack

router = APIRouter(prefix="/api/v1/personal-operator", tags=["personal-operator"])


def _opportunity_by_id(opportunity_id: str):
    for opportunity in suggest_opportunities(default_sami_profile()):
        if opportunity.id == opportunity_id:
            return opportunity
    opportunities = suggest_opportunities(default_sami_profile())
    return opportunities[0] if opportunities else None


def _parse_decision(raw: Any) -> ApprovalDecision:
    try:
        return ApprovalDecision(str(raw).lower().strip())
    except ValueError:
        raise HTTPException(status_code=400, detail="invalid_decision") from None


@router.get("/daily-brief")
async def daily_brief() -> dict[str, Any]:
    """Arabic executive daily brief for Sami."""
    return build_daily_brief(default_sami_profile()).to_dict()


@router.get("/opportunities")
async def opportunities() -> dict[str, Any]:
    items = suggest_opportunities(default_sami_profile())
    return {"count": len(items), "items": [item.to_card() for item in items]}


@router.post("/opportunities")
async def create_contextual_opportunities(body: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    """Return operator opportunities with optional context."""
    items = suggest_opportunities(default_sami_profile())
    return {
        "context_received": body,
        "count": len(items),
        "items": [item.to_card() for item in items],
    }


@router.post("/opportunities/{opportunity_id}/decision")
async def decide_opportunity(opportunity_id: str, body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    opportunity = _opportunity_by_id(opportunity_id)
    if not opportunity:
        raise HTTPException(status_code=404, detail="opportunity_not_found")
    decision = _parse_decision(body.get("decision", "draft"))
    result = apply_decision(opportunity, decision)
    approval_required = bool(result.get("approval_required", decision != ApprovalDecision.SKIP))
    next_action = str(result.get("next_action", "none"))
    return {
        "opportunity": opportunity.to_card(),
        "decision": decision.value,
        "result": result,
        "approval_required": approval_required,
        "next_action": next_action,
    }


@router.post("/messages/draft")
async def draft_message(body: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    opportunities = suggest_opportunities(default_sami_profile())
    selected = opportunities[0]
    if body.get("opportunity_id"):
        selected = _opportunity_by_id(str(body["opportunity_id"])) or selected
    tone = str(body.get("tone", "warm"))
    return draft_intro_message(selected, tone=tone)


@router.post("/followups/draft")
async def followup(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    return draft_follow_up(
        meeting_title=str(body.get("meeting_title", "اجتماع Dealix")),
        outcome=str(body.get("outcome", "اتفقنا على مراجعة الفكرة وإرسال ملخص")),
        next_step=str(body.get("next_step", "إرسال ملخص تنفيذي وتجربة قصيرة")),
    )


@router.get("/project/intelligence")
async def project_intelligence() -> dict[str, Any]:
    return explain_project_intelligence_stack()


@router.post("/project/ask")
async def ask_project(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    question = str(body.get("question", "وش ناقص المشروع؟"))
    deep = bool(body.get("deep_scan", False))
    root = str(body.get("root", "."))
    answered = answer_operator_question(question, root=root, deep_scan=deep)
    readiness = launch_readiness_score()
    return {
        "question": question,
        "answer_ar": answered["answer_ar"],
        "semantic_status_ar": answered["semantic_status_ar"],
        "related_files": answered["related_files"],
        "search_hits": answered.get("search_hits", []),
        "launch_readiness": readiness,
    }


@router.get("/launch-readiness")
async def launch_readiness() -> dict[str, Any]:
    return launch_readiness_score()


@router.get("/launch-report")
async def launch_report() -> dict[str, Any]:
    return build_launch_report().to_dict()


@router.post("/meetings/schedule-draft")
async def schedule_draft(body: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    return {
        "status": "calendar_draft_ready",
        "approval_required": True,
        "title": body.get("title", "Dealix Strategic Intro"),
        "duration": int(body.get("duration_minutes", 30)),
        "duration_minutes": int(body.get("duration_minutes", 30)),
        "agenda_ar": [
            "تعريف سريع بـ Dealix",
            "أخذ رأي الشخص في التموضع والسوق",
            "تحديد فرصة تعاون أو intro قادمة",
        ],
        "note_ar": "هذا المسار يجهز payload الاجتماع فقط. إنشاء حدث في Google Calendar يتطلب موافقة صريحة وطبقة تكامل.",
        "note": "This endpoint prepares the meeting payload. Actual Google Calendar creation should only happen after approval.",
    }

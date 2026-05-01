"""Growth Curator router — message grading + weekly curator report."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body

from auto_client_acquisition.growth_curator import (
    build_weekly_curator_report,
    detect_duplicates,
    grade_message,
    inventory_skills,
    recommend_next_mission,
    suggest_improvement,
)

router = APIRouter(prefix="/api/v1/growth-curator", tags=["growth-curator"])


@router.get("/skills/inventory")
async def skills_inventory() -> dict[str, Any]:
    return inventory_skills()


@router.post("/messages/grade")
async def messages_grade(
    message: str = Body(..., embed=True),
    sector: str | None = Body(default=None, embed=True),
    channel: str = Body(default="whatsapp", embed=True),
) -> dict[str, Any]:
    return grade_message(message, sector=sector, channel=channel).to_dict()


@router.post("/messages/improve")
async def messages_improve(
    message: str = Body(..., embed=True),
    sector: str | None = Body(default=None, embed=True),
) -> dict[str, Any]:
    return suggest_improvement(message, sector=sector)


@router.post("/messages/duplicates")
async def messages_duplicates(
    messages: list[str] = Body(..., embed=True),
    threshold: float = Body(default=0.85, embed=True),
) -> dict[str, Any]:
    pairs = detect_duplicates(messages, threshold=threshold)
    return {
        "pairs": [{"i": i, "j": j, "similarity": s} for i, j, s in pairs],
        "count": len(pairs),
    }


@router.post("/missions/next")
async def missions_next(
    history: list[dict[str, Any]] = Body(default_factory=list, embed=True),
    growth_brain: dict[str, Any] | None = Body(default=None, embed=True),
) -> dict[str, Any]:
    return recommend_next_mission(history, growth_brain=growth_brain)


@router.post("/report/weekly")
async def report_weekly(payload: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    return build_weekly_curator_report(
        messages=payload.get("messages", []),
        playbooks=payload.get("playbooks", []),
        missions=payload.get("missions", []),
        sector=payload.get("sector"),
    )


@router.get("/report/demo")
async def report_demo() -> dict[str, Any]:
    """Demo curator report with a small synthetic dataset."""
    return build_weekly_curator_report(
        messages=[
            {"id": "m1", "text": "هلا أحمد، لاحظت توسعكم في المبيعات. يناسبك أعرض لك Pilot 7 أيام؟"},
            {"id": "m2", "text": "هلا محمد، لاحظت توسعكم في المبيعات. يناسبك أعرض لك Pilot 7 أيام؟"},
            {"id": "m3", "text": "آخر فرصة! ضمان 100% نتائج مضمونة!"},
            {"id": "m4", "text": "Hi"},
        ],
        playbooks=[
            {"id": "pb1", "title": "Warm B2B intro - training", "used_count": 20,
             "accept_count": 12, "replied_count": 8, "meeting_count": 4, "deal_count": 2,
             "sectors": "training"},
            {"id": "pb2", "title": "Warm B2B intro - training-ksa", "used_count": 8,
             "accept_count": 4, "replied_count": 2, "meeting_count": 1, "deal_count": 0,
             "sectors": "training"},
            {"id": "pb3", "title": "Cold call SaaS", "used_count": 50,
             "accept_count": 5, "replied_count": 2, "meeting_count": 0, "deal_count": 0,
             "sectors": "saas"},
        ],
        missions=[
            {"mission_id": "first_10_opportunities", "opportunities_generated": 10,
             "drafts_approved": 4, "meetings_booked": 2, "revenue_influenced_sar": 18000,
             "time_to_value_minutes": 8, "risks_blocked": 2},
        ],
        sector="training",
    )

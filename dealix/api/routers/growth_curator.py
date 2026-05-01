"""Growth curator API — grading and weekly report."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body

from auto_client_acquisition.growth_curator.curator_report import build_weekly_curator_report
from auto_client_acquisition.growth_curator.message_curator import grade_message
from auto_client_acquisition.growth_curator.mission_curator import curate_missions_weekly
from auto_client_acquisition.growth_curator.skill_inventory import list_skill_inventory

router = APIRouter(prefix="/api/v1/growth-curator", tags=["growth_curator"])


@router.get("/report/demo")
async def report_demo() -> dict[str, Any]:
    return build_weekly_curator_report()


@router.post("/messages/grade")
async def messages_grade(payload: dict[str, Any] = Body(default_factory=dict)) -> dict[str, Any]:
    return grade_message(
        str(payload.get("message_ar") or ""),
        sector=str(payload.get("sector") or ""),
        channel=str(payload.get("channel") or "whatsapp"),
    )


@router.get("/skills/demo")
async def skills_demo() -> dict[str, Any]:
    return list_skill_inventory()


@router.get("/missions/curate/demo")
async def missions_curate_demo() -> dict[str, Any]:
    return curate_missions_weekly()

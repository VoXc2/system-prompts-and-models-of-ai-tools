"""Partnership OS — Partner lifecycle API."""
from __future__ import annotations
from typing import Any
from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

router = APIRouter(prefix="/partnership-os", tags=["Partnership OS"])


class PartnerCreateRequest(BaseModel):
    name: str
    name_ar: str = ""
    partner_type: str = "channel"
    sector: str = ""
    country: str = "Saudi Arabia"
    contact_name: str = ""
    contact_email: str = ""
    website: str = ""


class PartnerScorecardRequest(BaseModel):
    partner_id: str
    period: str
    leads_generated: int = 0
    deals_closed: int = 0
    revenue_generated: float = 0
    satisfaction_score: int = 0


@router.get("/pipeline")
async def partnership_pipeline():
    return {
        "stages": ["scouted", "evaluating", "negotiating", "active", "inactive"],
        "partners": [],
        "total": 0,
    }


@router.post("/partners")
async def create_partner(req: PartnerCreateRequest):
    return {
        "status": "created",
        "partner": req.model_dump(),
        "message_ar": "تم إنشاء الشريك بنجاح",
    }


@router.get("/partners")
async def list_partners(status: str = Query(default="")):
    return {"partners": [], "total": 0, "filter": status}


@router.get("/scorecards")
async def partner_scorecards(partner_id: str = Query(default="")):
    return {"scorecards": [], "partner_id": partner_id}


@router.post("/scorecards")
async def create_scorecard(req: PartnerScorecardRequest):
    return {"status": "created", "scorecard": req.model_dump()}


@router.get("/health")
async def partner_health():
    return {
        "healthy": 0,
        "at_risk": 0,
        "critical": 0,
        "partners": [],
    }

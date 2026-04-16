"""Expansion OS — Market expansion lifecycle API."""
from __future__ import annotations
from typing import Any
from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

router = APIRouter(prefix="/expansion-os", tags=["Expansion OS"])


class MarketCreateRequest(BaseModel):
    name: str
    name_ar: str = ""
    country: str
    region: str = ""
    segment_priority: int = 0


@router.get("/markets")
async def list_markets(status: str = Query(default="")):
    return {"markets": [], "total": 0, "filter": status}


@router.post("/markets")
async def create_market(req: MarketCreateRequest):
    return {
        "status": "created",
        "market": req.model_dump(),
        "message_ar": "تم إضافة السوق المستهدف",
    }


@router.get("/launch-console")
async def launch_console():
    return {
        "markets_scanning": 0,
        "markets_approved": 0,
        "markets_live": 0,
        "canary_active": 0,
        "markets": [],
    }


@router.get("/readiness/{market_id}")
async def launch_readiness(market_id: str):
    return {
        "market_id": market_id,
        "readiness_score": 0,
        "checklist": {
            "regulatory": False,
            "pricing": False,
            "channel": False,
            "gtm": False,
            "partner": False,
            "localization": False,
        },
    }

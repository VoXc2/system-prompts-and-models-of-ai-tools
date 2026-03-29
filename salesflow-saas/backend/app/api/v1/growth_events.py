"""Growth events & attribution API — track every touchpoint in the revenue journey."""
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from app.api.v1.deps import get_current_user, get_db
from app.services.attribution import AttributionService

router = APIRouter()


class EventTrack(BaseModel):
    event_type: str  # page_view, form_submit, demo_booked, deal_created, deal_won
    event_category: Optional[str] = None  # awareness, consideration, decision, retention
    lead_id: Optional[UUID] = None
    customer_id: Optional[UUID] = None
    anonymous_id: Optional[str] = None
    source: Optional[str] = None
    medium: Optional[str] = None
    campaign: Optional[str] = None
    content: Optional[str] = None
    term: Optional[str] = None
    page_url: Optional[str] = None
    referrer_url: Optional[str] = None
    landing_page: Optional[str] = None
    revenue_attributed: Optional[float] = None
    deal_id: Optional[UUID] = None


@router.post("/track", status_code=201)
async def track_event(
    data: EventTrack,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = AttributionService(db, current_user["tenant_id"])
    event = await svc.track_event(**data.model_dump(exclude_none=True))
    return {"status": "tracked", "event_id": str(event.id) if hasattr(event, "id") else None}


@router.get("/journey/{lead_id}")
async def get_journey(
    lead_id: UUID,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = AttributionService(db, current_user["tenant_id"])
    journey = await svc.get_lead_journey(str(lead_id))
    return journey


@router.get("/channels")
async def channel_attribution(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = AttributionService(db, current_user["tenant_id"])
    return await svc.get_channel_attribution()


@router.get("/campaigns")
async def campaign_performance(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    svc = AttributionService(db, current_user["tenant_id"])
    return await svc.get_campaign_performance()

"""Activities API — track lead/deal interactions and milestones."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional
from uuid import UUID
from app.api.v1.deps import get_current_user, get_db
from app.models.activity import Activity

router = APIRouter()


class ActivityCreate(BaseModel):
    lead_id: Optional[UUID] = None
    deal_id: Optional[UUID] = None
    activity_type: str  # call, email, whatsapp, meeting, note, task
    title: str
    description: Optional[str] = None
    outcome: Optional[str] = None


@router.get("")
async def list_activities(
    lead_id: Optional[UUID] = None,
    deal_id: Optional[UUID] = None,
    activity_type: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    tenant_id = current_user["tenant_id"]
    query = select(Activity).where(Activity.tenant_id == tenant_id)

    if lead_id:
        query = query.where(Activity.lead_id == lead_id)
    if deal_id and hasattr(Activity, "deal_id"):
        query = query.where(Activity.deal_id == deal_id)
    if activity_type and hasattr(Activity, "activity_type"):
        query = query.where(Activity.activity_type == activity_type)

    query = query.order_by(Activity.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    items = result.scalars().all()

    return {"items": [_serialize(a) for a in items]}


@router.post("", status_code=201)
async def create_activity(
    data: ActivityCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    activity = Activity(
        tenant_id=current_user["tenant_id"],
        user_id=current_user["user_id"],
    )
    for field in ("lead_id", "deal_id", "activity_type", "title", "description", "outcome"):
        val = getattr(data, field, None)
        if val is not None and hasattr(activity, field):
            setattr(activity, field, val)
    db.add(activity)
    await db.flush()
    return _serialize(activity)


def _serialize(a):
    return {
        "id": str(a.id),
        "lead_id": str(a.lead_id) if getattr(a, "lead_id", None) else None,
        "deal_id": str(a.deal_id) if getattr(a, "deal_id", None) else None,
        "activity_type": getattr(a, "activity_type", None),
        "title": getattr(a, "title", None),
        "description": getattr(a, "description", None),
        "outcome": getattr(a, "outcome", None),
        "user_id": str(a.user_id) if getattr(a, "user_id", None) else None,
        "created_at": a.created_at.isoformat() if a.created_at else None,
    }

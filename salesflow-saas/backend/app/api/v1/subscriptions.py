"""Subscription management API — plan details, upgrades."""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
from typing import Optional
from app.api.v1.deps import get_current_user, get_db, require_role
from app.models.subscription import Subscription

router = APIRouter()


class SubscriptionUpdate(BaseModel):
    plan: Optional[str] = None  # free, starter, growth, enterprise
    billing_cycle: Optional[str] = None  # monthly, annual


@router.get("")
async def get_subscription(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    tenant_id = current_user["tenant_id"]
    result = await db.execute(
        select(Subscription).where(Subscription.tenant_id == tenant_id).order_by(Subscription.created_at.desc())
    )
    sub = result.scalar_one_or_none()
    if not sub:
        return {"plan": "free", "status": "active", "features": {}}
    return _serialize(sub)


@router.put("")
async def update_subscription(
    data: SubscriptionUpdate,
    current_user: dict = Depends(require_role("owner")),
    db: AsyncSession = Depends(get_db),
):
    tenant_id = current_user["tenant_id"]
    result = await db.execute(
        select(Subscription).where(Subscription.tenant_id == tenant_id).order_by(Subscription.created_at.desc())
    )
    sub = result.scalar_one_or_none()
    if not sub:
        raise HTTPException(status_code=404, detail="لا يوجد اشتراك")
    for field, value in data.model_dump(exclude_none=True).items():
        if hasattr(sub, field):
            setattr(sub, field, value)
    await db.flush()
    return _serialize(sub)


def _serialize(s):
    return {
        "id": str(s.id),
        "plan": getattr(s, "plan", "free"),
        "status": getattr(s, "status", "active"),
        "billing_cycle": getattr(s, "billing_cycle", None),
        "current_period_start": s.created_at.isoformat() if s.created_at else None,
        "features": getattr(s, "features", {}),
    }

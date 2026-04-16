"""Partnership OS — API routes for full partner lifecycle management."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional

from app.database import get_db
from app.models.partnership import Partner, PartnerScorecard, PartnerTermSheet
from app.schemas.sovereign import PartnerCreate, PartnerResponse, PartnerScorecardResponse

router = APIRouter(prefix="/partnership", tags=["Partnership OS — شراكات"])


@router.get("/partners", response_model=list[PartnerResponse])
async def list_partners(
    status: Optional[str] = None,
    partner_type: Optional[str] = None,
    tier: Optional[str] = None,
    limit: int = Query(default=50, le=200),
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    """List all partners with optional filtering."""
    q = select(Partner)
    if status:
        q = q.where(Partner.status == status)
    if partner_type:
        q = q.where(Partner.partner_type == partner_type)
    if tier:
        q = q.where(Partner.tier == tier)
    q = q.order_by(Partner.created_at.desc()).offset(offset).limit(limit)
    result = await db.execute(q)
    return result.scalars().all()


@router.post("/partners", response_model=PartnerResponse, status_code=201)
async def create_partner(
    data: PartnerCreate,
    db: AsyncSession = Depends(get_db),
):
    """Register a new partner prospect."""
    partner = Partner(**data.model_dump())
    partner.tenant_id = "00000000-0000-0000-0000-000000000001"
    db.add(partner)
    await db.flush()
    await db.refresh(partner)
    return partner


@router.get("/partners/{partner_id}", response_model=PartnerResponse)
async def get_partner(partner_id: str, db: AsyncSession = Depends(get_db)):
    """Get partner details."""
    result = await db.execute(select(Partner).where(Partner.id == partner_id))
    partner = result.scalar_one_or_none()
    if not partner:
        raise HTTPException(status_code=404, detail="Partner not found")
    return partner


@router.get("/partners/{partner_id}/scorecards", response_model=list[PartnerScorecardResponse])
async def list_partner_scorecards(partner_id: str, db: AsyncSession = Depends(get_db)):
    """Get scorecards for a partner."""
    q = select(PartnerScorecard).where(
        PartnerScorecard.partner_id == partner_id
    ).order_by(PartnerScorecard.period.desc())
    result = await db.execute(q)
    return result.scalars().all()


@router.get("/dashboard")
async def partnership_dashboard(db: AsyncSession = Depends(get_db)):
    """Partnership OS dashboard summary."""
    total = await db.execute(select(func.count(Partner.id)))
    active = await db.execute(
        select(func.count(Partner.id)).where(Partner.status == "active")
    )
    evaluating = await db.execute(
        select(func.count(Partner.id)).where(Partner.status == "evaluating")
    )
    return {
        "total_partners": total.scalar() or 0,
        "active": active.scalar() or 0,
        "evaluating": evaluating.scalar() or 0,
        "module": "partnership_os",
        "module_ar": "نظام الشراكات",
    }

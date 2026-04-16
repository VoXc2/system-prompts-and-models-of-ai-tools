"""Sovereign Partnership OS: strategic partner management."""

from __future__ import annotations

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.sovereign_partnership import Partner
from app.schemas.sovereign import (
    PartnerCreate,
    PartnerResponse,
    PartnerUpdate,
)

router = APIRouter(prefix="/sovereign/partnerships", tags=["Sovereign Partnership OS"])


@router.post("/", response_model=PartnerResponse, status_code=201)
async def create_partner(
    data: PartnerCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    partner = Partner(
        tenant_id=current_user.tenant_id,
        **data.model_dump(exclude_none=True),
    )
    db.add(partner)
    await db.flush()
    await db.refresh(partner)
    return PartnerResponse.model_validate(partner)


@router.get("/", response_model=List[PartnerResponse])
async def list_partners(
    status: Optional[str] = Query(None),
    type: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    q = select(Partner).where(Partner.tenant_id == current_user.tenant_id)
    if status:
        q = q.where(Partner.status == status)
    if type:
        q = q.where(Partner.partner_type == type)
    q = q.order_by(Partner.created_at.desc())
    result = await db.execute(q)
    return [PartnerResponse.model_validate(p) for p in result.scalars().all()]


@router.get("/scorecards", response_model=List[PartnerResponse])
async def partnership_scorecards(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Partnership scorecards: active partners with scorecard data."""
    q = (
        select(Partner)
        .where(
            Partner.tenant_id == current_user.tenant_id,
            Partner.status == "active",
        )
        .order_by(Partner.created_at.desc())
    )
    result = await db.execute(q)
    return [PartnerResponse.model_validate(p) for p in result.scalars().all()]


@router.get("/{id}", response_model=PartnerResponse)
async def get_partner(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Partner).where(
            Partner.id == id,
            Partner.tenant_id == current_user.tenant_id,
        )
    )
    partner = result.scalar_one_or_none()
    if not partner:
        raise HTTPException(status_code=404, detail="Partner not found")
    return PartnerResponse.model_validate(partner)


@router.patch("/{id}", response_model=PartnerResponse)
async def update_partner(
    id: UUID,
    data: PartnerUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Partner).where(
            Partner.id == id,
            Partner.tenant_id == current_user.tenant_id,
        )
    )
    partner = result.scalar_one_or_none()
    if not partner:
        raise HTTPException(status_code=404, detail="Partner not found")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(partner, field, value)
    await db.flush()
    await db.refresh(partner)
    return PartnerResponse.model_validate(partner)

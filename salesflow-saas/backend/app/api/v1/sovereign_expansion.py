"""Sovereign Expansion OS: market expansion tracking and launch console."""

from __future__ import annotations

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.sovereign_expansion import ExpansionMarket
from app.schemas.sovereign import (
    ExpansionMarketCreate,
    ExpansionMarketResponse,
    ExpansionMarketUpdate,
)

router = APIRouter(prefix="/sovereign/expansion", tags=["Sovereign Expansion OS"])


@router.post("/markets", response_model=ExpansionMarketResponse, status_code=201)
async def create_market(
    data: ExpansionMarketCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    market = ExpansionMarket(
        tenant_id=current_user.tenant_id,
        assigned_to_id=current_user.id,
        **data.model_dump(exclude_none=True),
    )
    db.add(market)
    await db.flush()
    await db.refresh(market)
    return ExpansionMarketResponse.model_validate(market)


@router.get("/markets", response_model=List[ExpansionMarketResponse])
async def list_markets(
    status: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    q = select(ExpansionMarket).where(ExpansionMarket.tenant_id == current_user.tenant_id)
    if status:
        q = q.where(ExpansionMarket.status == status)
    q = q.order_by(ExpansionMarket.created_at.desc())
    result = await db.execute(q)
    return [ExpansionMarketResponse.model_validate(m) for m in result.scalars().all()]


@router.get("/markets/{id}", response_model=ExpansionMarketResponse)
async def get_market(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ExpansionMarket).where(
            ExpansionMarket.id == id,
            ExpansionMarket.tenant_id == current_user.tenant_id,
        )
    )
    market = result.scalar_one_or_none()
    if not market:
        raise HTTPException(status_code=404, detail="Market not found")
    return ExpansionMarketResponse.model_validate(market)


@router.patch("/markets/{id}", response_model=ExpansionMarketResponse)
async def update_market(
    id: UUID,
    data: ExpansionMarketUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(ExpansionMarket).where(
            ExpansionMarket.id == id,
            ExpansionMarket.tenant_id == current_user.tenant_id,
        )
    )
    market = result.scalar_one_or_none()
    if not market:
        raise HTTPException(status_code=404, detail="Market not found")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(market, field, value)
    await db.flush()
    await db.refresh(market)
    return ExpansionMarketResponse.model_validate(market)


@router.get("/launch-console")
async def launch_console(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Expansion launch console: all markets with readiness summary."""
    q = await db.execute(
        select(ExpansionMarket)
        .where(ExpansionMarket.tenant_id == current_user.tenant_id)
        .order_by(ExpansionMarket.priority_score.desc().nullslast())
    )
    markets = q.scalars().all()

    summary = {"total": len(markets), "by_status": {}, "markets": []}
    for m in markets:
        summary["by_status"][m.status] = summary["by_status"].get(m.status, 0) + 1
        summary["markets"].append(ExpansionMarketResponse.model_validate(m).model_dump())
    return summary

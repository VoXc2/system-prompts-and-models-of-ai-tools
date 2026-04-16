"""Expansion OS — API routes for market expansion lifecycle."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional

from app.database import get_db
from app.models.expansion import ExpansionMarket
from app.schemas.sovereign import ExpansionMarketCreate, ExpansionMarketResponse

router = APIRouter(prefix="/expansion", tags=["Expansion OS — توسع"])


@router.get("/markets", response_model=list[ExpansionMarketResponse])
async def list_markets(
    status: Optional[str] = None,
    country: Optional[str] = None,
    limit: int = Query(default=50, le=200),
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    """List expansion markets."""
    q = select(ExpansionMarket)
    if status:
        q = q.where(ExpansionMarket.status == status)
    if country:
        q = q.where(ExpansionMarket.country == country)
    q = q.order_by(ExpansionMarket.priority_score.desc()).offset(offset).limit(limit)
    result = await db.execute(q)
    return result.scalars().all()


@router.post("/markets", response_model=ExpansionMarketResponse, status_code=201)
async def create_market(
    data: ExpansionMarketCreate,
    db: AsyncSession = Depends(get_db),
):
    """Add a new expansion market for evaluation."""
    market = ExpansionMarket(**data.model_dump())
    market.tenant_id = "00000000-0000-0000-0000-000000000001"
    db.add(market)
    await db.flush()
    await db.refresh(market)
    return market


@router.get("/markets/{market_id}", response_model=ExpansionMarketResponse)
async def get_market(market_id: str, db: AsyncSession = Depends(get_db)):
    """Get expansion market details."""
    result = await db.execute(select(ExpansionMarket).where(ExpansionMarket.id == market_id))
    market = result.scalar_one_or_none()
    if not market:
        raise HTTPException(status_code=404, detail="Market not found")
    return market


@router.get("/dashboard")
async def expansion_dashboard(db: AsyncSession = Depends(get_db)):
    """Expansion OS dashboard summary."""
    total = await db.execute(select(func.count(ExpansionMarket.id)))
    launched = await db.execute(
        select(func.count(ExpansionMarket.id)).where(ExpansionMarket.status == "launched")
    )
    active = await db.execute(
        select(func.count(ExpansionMarket.id)).where(ExpansionMarket.status == "active")
    )
    return {
        "total_markets": total.scalar() or 0,
        "launched": launched.scalar() or 0,
        "active": active.scalar() or 0,
        "module": "expansion_os",
        "module_ar": "نظام التوسع",
    }

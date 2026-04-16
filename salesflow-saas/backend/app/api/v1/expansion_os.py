"""Expansion OS API — Market scanning, launch readiness, actual vs forecast."""
from __future__ import annotations

from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.sovereign import ExpansionMarket, ExpansionActual

router = APIRouter(prefix="/expansion-os", tags=["Expansion OS — نظام التوسع"])


class MarketCreate(BaseModel):
    market_name_ar: str
    market_name_en: str | None = None
    country_code: str
    region: str | None = None
    tam_sar: float | None = None
    pricing_plan: dict[str, Any] | None = None
    channel_plan: dict[str, Any] | None = None
    localization_requirements: list[str] | None = None
    stop_loss_threshold: dict[str, Any] | None = None


class ActualCreate(BaseModel):
    period_label: str
    revenue_forecast_sar: float | None = None
    revenue_actual_sar: float | None = None
    leads_forecast: int | None = None
    leads_actual: int | None = None
    notes_ar: str | None = None


@router.post("/markets", status_code=status.HTTP_201_CREATED)
async def create_market(
    tenant_id: str,
    payload: MarketCreate,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    market = ExpansionMarket(
        tenant_id=tenant_id,
        market_name_ar=payload.market_name_ar,
        market_name_en=payload.market_name_en,
        country_code=payload.country_code,
        region=payload.region,
        tam_sar=payload.tam_sar,
        pricing_plan=payload.pricing_plan or {},
        channel_plan=payload.channel_plan or {},
        localization_requirements=payload.localization_requirements or [],
        stop_loss_threshold=payload.stop_loss_threshold or {},
    )
    db.add(market)
    await db.commit()
    await db.refresh(market)
    return {"id": str(market.id), "market_name_ar": market.market_name_ar, "status": market.status}


@router.get("/markets")
async def list_markets(
    tenant_id: str,
    status: str | None = None,
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    q = select(ExpansionMarket).where(ExpansionMarket.tenant_id == tenant_id)
    if status:
        q = q.where(ExpansionMarket.status == status)
    q = q.order_by(ExpansionMarket.priority_score.desc().nullslast())
    result = await db.execute(q)
    rows = result.scalars().all()
    return [
        {
            "id": str(r.id),
            "market_name_ar": r.market_name_ar,
            "market_name_en": r.market_name_en,
            "country_code": r.country_code,
            "region": r.region,
            "status": r.status,
            "priority_score": float(r.priority_score) if r.priority_score else None,
            "tam_sar": float(r.tam_sar) if r.tam_sar else None,
            "launch_readiness_score": float(r.launch_readiness_score) if r.launch_readiness_score else None,
            "launched_at": r.launched_at.isoformat() if r.launched_at else None,
        }
        for r in rows
    ]


@router.get("/markets/{market_id}/actuals")
async def market_actuals(
    market_id: str,
    tenant_id: str,
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    """فعلي مقابل متوقع — Actual vs forecast dashboard."""
    result = await db.execute(
        select(ExpansionActual).where(
            ExpansionActual.market_id == market_id,
            ExpansionActual.tenant_id == tenant_id,
        ).order_by(ExpansionActual.period_label.desc())
    )
    rows = result.scalars().all()
    return [
        {
            "id": str(r.id),
            "period_label": r.period_label,
            "revenue_forecast_sar": float(r.revenue_forecast_sar) if r.revenue_forecast_sar else None,
            "revenue_actual_sar": float(r.revenue_actual_sar) if r.revenue_actual_sar else None,
            "leads_forecast": r.leads_forecast,
            "leads_actual": r.leads_actual,
            "variance_pct": float(r.variance_pct) if r.variance_pct else None,
            "notes_ar": r.notes_ar,
        }
        for r in rows
    ]


@router.post("/markets/{market_id}/actuals", status_code=status.HTTP_201_CREATED)
async def record_actual(
    market_id: str,
    tenant_id: str,
    payload: ActualCreate,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    variance = None
    if payload.revenue_forecast_sar and payload.revenue_actual_sar and payload.revenue_forecast_sar != 0:
        variance = ((payload.revenue_actual_sar - payload.revenue_forecast_sar) / payload.revenue_forecast_sar) * 100

    actual = ExpansionActual(
        tenant_id=tenant_id,
        market_id=market_id,
        period_label=payload.period_label,
        revenue_forecast_sar=payload.revenue_forecast_sar,
        revenue_actual_sar=payload.revenue_actual_sar,
        leads_forecast=payload.leads_forecast,
        leads_actual=payload.leads_actual,
        variance_pct=round(variance, 2) if variance is not None else None,
        notes_ar=payload.notes_ar,
    )
    db.add(actual)
    await db.commit()
    await db.refresh(actual)
    return {"id": str(actual.id), "period_label": actual.period_label, "variance_pct": actual.variance_pct}

"""Corporate Development (M&A) OS API — Target sourcing, DD rooms, IC memos, offer strategy."""
from __future__ import annotations

from datetime import datetime
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.sovereign import MATarget, DDChecklist

router = APIRouter(prefix="/corporate-dev", tags=["Corporate Dev / M&A OS — التطوير المؤسسي"])


class MATargetCreate(BaseModel):
    company_name_ar: str
    company_name_en: str | None = None
    sector: str | None = None
    geography: str = "Saudi Arabia"
    strategic_rationale_ar: str | None = None
    synergy_model: dict[str, Any] | None = None
    valuation_low_sar: float | None = None
    valuation_high_sar: float | None = None


class DDItemCreate(BaseModel):
    category: str = Field(..., description="financial | legal | tech | hr | ops | regulatory")
    item_ar: str
    item_en: str | None = None
    risk_level: str = "medium"
    owner_id: str | None = None
    due_date: datetime | None = None


class DDItemUpdate(BaseModel):
    status: str
    notes_ar: str | None = None


@router.post("/targets", status_code=status.HTTP_201_CREATED)
async def create_target(
    tenant_id: str,
    payload: MATargetCreate,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """إضافة هدف استحواذ جديد — Add M&A target."""
    target = MATarget(
        tenant_id=tenant_id,
        company_name_ar=payload.company_name_ar,
        company_name_en=payload.company_name_en,
        sector=payload.sector,
        geography=payload.geography,
        strategic_rationale_ar=payload.strategic_rationale_ar,
        synergy_model=payload.synergy_model or {},
        valuation_low_sar=payload.valuation_low_sar,
        valuation_high_sar=payload.valuation_high_sar,
    )
    db.add(target)
    await db.commit()
    await db.refresh(target)
    return {"id": str(target.id), "company_name_ar": target.company_name_ar, "status": target.status}


@router.get("/targets")
async def list_targets(
    tenant_id: str,
    status: str | None = None,
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    """خط أنابيب M&A — M&A pipeline board."""
    q = select(MATarget).where(MATarget.tenant_id == tenant_id)
    if status:
        q = q.where(MATarget.status == status)
    q = q.order_by(MATarget.created_at.desc())
    result = await db.execute(q)
    rows = result.scalars().all()
    return [
        {
            "id": str(r.id),
            "company_name_ar": r.company_name_ar,
            "company_name_en": r.company_name_en,
            "sector": r.sector,
            "geography": r.geography,
            "status": r.status,
            "valuation_low_sar": float(r.valuation_low_sar) if r.valuation_low_sar else None,
            "valuation_high_sar": float(r.valuation_high_sar) if r.valuation_high_sar else None,
            "offer_price_sar": float(r.offer_price_sar) if r.offer_price_sar else None,
            "signed_at": r.signed_at.isoformat() if r.signed_at else None,
        }
        for r in rows
    ]


@router.get("/targets/{target_id}")
async def get_target(
    target_id: str,
    tenant_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    result = await db.execute(
        select(MATarget).where(MATarget.id == target_id, MATarget.tenant_id == tenant_id)
    )
    t = result.scalar_one_or_none()
    if not t:
        raise HTTPException(status_code=404, detail="M&A target not found")
    return {
        "id": str(t.id),
        "company_name_ar": t.company_name_ar,
        "company_name_en": t.company_name_en,
        "sector": t.sector,
        "geography": t.geography,
        "status": t.status,
        "strategic_rationale_ar": t.strategic_rationale_ar,
        "synergy_model": t.synergy_model,
        "valuation_low_sar": float(t.valuation_low_sar) if t.valuation_low_sar else None,
        "valuation_high_sar": float(t.valuation_high_sar) if t.valuation_high_sar else None,
        "offer_price_sar": float(t.offer_price_sar) if t.offer_price_sar else None,
        "dd_room_url": t.dd_room_url,
        "dd_access_policy": t.dd_access_policy,
        "signed_at": t.signed_at.isoformat() if t.signed_at else None,
        "closed_at": t.closed_at.isoformat() if t.closed_at else None,
    }


@router.post("/targets/{target_id}/dd-checklist", status_code=status.HTTP_201_CREATED)
async def add_dd_item(
    target_id: str,
    tenant_id: str,
    payload: DDItemCreate,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """إضافة بند فحص نافي للجهالة — Add DD checklist item."""
    item = DDChecklist(
        tenant_id=tenant_id,
        ma_target_id=target_id,
        category=payload.category,
        item_ar=payload.item_ar,
        item_en=payload.item_en,
        risk_level=payload.risk_level,
        owner_id=payload.owner_id,
        due_date=payload.due_date,
    )
    db.add(item)
    await db.commit()
    await db.refresh(item)
    return {"id": str(item.id), "status": item.status}


@router.get("/targets/{target_id}/dd-checklist")
async def get_dd_checklist(
    target_id: str,
    tenant_id: str,
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    result = await db.execute(
        select(DDChecklist).where(
            DDChecklist.ma_target_id == target_id,
            DDChecklist.tenant_id == tenant_id,
        ).order_by(DDChecklist.category, DDChecklist.created_at)
    )
    rows = result.scalars().all()
    return [
        {
            "id": str(r.id),
            "category": r.category,
            "item_ar": r.item_ar,
            "item_en": r.item_en,
            "status": r.status,
            "risk_level": r.risk_level,
            "owner_id": str(r.owner_id) if r.owner_id else None,
            "due_date": r.due_date.isoformat() if r.due_date else None,
            "notes_ar": r.notes_ar,
        }
        for r in rows
    ]


@router.patch("/dd-checklist/{item_id}")
async def update_dd_item(
    item_id: str,
    tenant_id: str,
    payload: DDItemUpdate,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    result = await db.execute(
        select(DDChecklist).where(
            DDChecklist.id == item_id,
            DDChecklist.tenant_id == tenant_id,
        )
    )
    item = result.scalar_one_or_none()
    if not item:
        raise HTTPException(status_code=404, detail="DD item not found")
    item.status = payload.status
    if payload.notes_ar:
        item.notes_ar = payload.notes_ar
    await db.commit()
    return {"id": item_id, "status": item.status}

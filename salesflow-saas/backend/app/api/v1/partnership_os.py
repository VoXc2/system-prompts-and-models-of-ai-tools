"""Partnership OS API — Partner scouting, scoring, activation, scorecards."""
from __future__ import annotations

from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.sovereign import Partner, PartnerScorecard

router = APIRouter(prefix="/partnership-os", tags=["Partnership OS — نظام الشراكات"])


class PartnerCreate(BaseModel):
    name_ar: str = Field(..., description="اسم الشريك بالعربية")
    name_en: str | None = None
    partner_type: str = "channel"
    contact_name: str | None = None
    contact_email: str | None = None
    contact_phone: str | None = None
    channel_economics: dict[str, Any] | None = None
    alliance_structure: dict[str, Any] | None = None
    term_sheet_draft: str | None = None


class PartnerStatusUpdate(BaseModel):
    status: str
    note: str | None = None


@router.post("/partners", status_code=status.HTTP_201_CREATED)
async def create_partner(
    tenant_id: str,
    payload: PartnerCreate,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """إضافة شريك جديد — Create new partner."""
    partner = Partner(
        tenant_id=tenant_id,
        name_ar=payload.name_ar,
        name_en=payload.name_en,
        partner_type=payload.partner_type,
        contact_name=payload.contact_name,
        contact_email=payload.contact_email,
        contact_phone=payload.contact_phone,
        channel_economics=payload.channel_economics or {},
        alliance_structure=payload.alliance_structure or {},
        term_sheet_draft=payload.term_sheet_draft,
    )
    db.add(partner)
    await db.commit()
    await db.refresh(partner)
    return {"id": str(partner.id), "name_ar": partner.name_ar, "status": partner.status}


@router.get("/partners")
async def list_partners(
    tenant_id: str,
    status: str | None = None,
    partner_type: str | None = None,
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    q = select(Partner).where(Partner.tenant_id == tenant_id)
    if status:
        q = q.where(Partner.status == status)
    if partner_type:
        q = q.where(Partner.partner_type == partner_type)
    q = q.order_by(Partner.strategic_fit_score.desc().nullslast())
    result = await db.execute(q)
    rows = result.scalars().all()
    return [
        {
            "id": str(r.id),
            "name_ar": r.name_ar,
            "name_en": r.name_en,
            "partner_type": r.partner_type,
            "status": r.status,
            "strategic_fit_score": float(r.strategic_fit_score) if r.strategic_fit_score else None,
            "quarterly_revenue_sar": float(r.quarterly_revenue_sar) if r.quarterly_revenue_sar else None,
            "active_deals_count": r.active_deals_count,
            "nps_score": float(r.nps_score) if r.nps_score else None,
            "activated_at": r.activated_at.isoformat() if r.activated_at else None,
        }
        for r in rows
    ]


@router.get("/partners/{partner_id}")
async def get_partner(
    partner_id: str,
    tenant_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    result = await db.execute(
        select(Partner).where(Partner.id == partner_id, Partner.tenant_id == tenant_id)
    )
    p = result.scalar_one_or_none()
    if not p:
        raise HTTPException(status_code=404, detail="Partner not found")
    return {
        "id": str(p.id),
        "name_ar": p.name_ar,
        "name_en": p.name_en,
        "partner_type": p.partner_type,
        "status": p.status,
        "strategic_fit_score": float(p.strategic_fit_score) if p.strategic_fit_score else None,
        "channel_economics": p.channel_economics,
        "alliance_structure": p.alliance_structure,
        "term_sheet_draft": p.term_sheet_draft,
        "term_sheet_approved_at": p.term_sheet_approved_at.isoformat() if p.term_sheet_approved_at else None,
        "quarterly_revenue_sar": float(p.quarterly_revenue_sar) if p.quarterly_revenue_sar else None,
        "contribution_margin_pct": float(p.contribution_margin_pct) if p.contribution_margin_pct else None,
        "active_deals_count": p.active_deals_count,
        "nps_score": float(p.nps_score) if p.nps_score else None,
        "contact_name": p.contact_name,
        "contact_email": p.contact_email,
        "contact_phone": p.contact_phone,
    }


@router.patch("/partners/{partner_id}/status")
async def update_partner_status(
    partner_id: str,
    tenant_id: str,
    payload: PartnerStatusUpdate,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    result = await db.execute(
        select(Partner).where(Partner.id == partner_id, Partner.tenant_id == tenant_id)
    )
    p = result.scalar_one_or_none()
    if not p:
        raise HTTPException(status_code=404, detail="Partner not found")
    p.status = payload.status
    await db.commit()
    return {"id": partner_id, "status": p.status}


@router.get("/partners/{partner_id}/scorecards")
async def partner_scorecards(
    partner_id: str,
    tenant_id: str,
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    result = await db.execute(
        select(PartnerScorecard).where(
            PartnerScorecard.partner_id == partner_id,
            PartnerScorecard.tenant_id == tenant_id,
        ).order_by(PartnerScorecard.period_label.desc())
    )
    rows = result.scalars().all()
    return [
        {
            "id": str(r.id),
            "period_label": r.period_label,
            "revenue_sar": float(r.revenue_sar) if r.revenue_sar else None,
            "deals_closed": r.deals_closed,
            "contribution_margin_pct": float(r.contribution_margin_pct) if r.contribution_margin_pct else None,
            "nps_score": float(r.nps_score) if r.nps_score else None,
            "notes_ar": r.notes_ar,
        }
        for r in rows
    ]

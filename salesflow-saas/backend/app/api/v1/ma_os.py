"""M&A / Corporate Development OS — API routes for acquisition lifecycle."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional

from app.database import get_db
from app.models.acquisition import AcquisitionTarget, DDStream, ValuationModel, InvestmentCommitteePack
from app.schemas.sovereign import AcquisitionTargetCreate, AcquisitionTargetResponse, DDStreamResponse

router = APIRouter(prefix="/ma", tags=["M&A OS — استحواذ"])


@router.get("/targets", response_model=list[AcquisitionTargetResponse])
async def list_targets(
    status: Optional[str] = None,
    limit: int = Query(default=50, le=200),
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    """List acquisition targets."""
    q = select(AcquisitionTarget)
    if status:
        q = q.where(AcquisitionTarget.status == status)
    q = q.order_by(AcquisitionTarget.created_at.desc()).offset(offset).limit(limit)
    result = await db.execute(q)
    return result.scalars().all()


@router.post("/targets", response_model=AcquisitionTargetResponse, status_code=201)
async def create_target(
    data: AcquisitionTargetCreate,
    db: AsyncSession = Depends(get_db),
):
    """Source a new acquisition target."""
    target = AcquisitionTarget(**data.model_dump())
    target.tenant_id = "00000000-0000-0000-0000-000000000001"
    db.add(target)
    await db.flush()
    await db.refresh(target)
    return target


@router.get("/targets/{target_id}", response_model=AcquisitionTargetResponse)
async def get_target(target_id: str, db: AsyncSession = Depends(get_db)):
    """Get acquisition target details."""
    result = await db.execute(select(AcquisitionTarget).where(AcquisitionTarget.id == target_id))
    target = result.scalar_one_or_none()
    if not target:
        raise HTTPException(status_code=404, detail="Target not found")
    return target


@router.get("/targets/{target_id}/dd", response_model=list[DDStreamResponse])
async def list_dd_streams(target_id: str, db: AsyncSession = Depends(get_db)):
    """List due diligence streams for a target."""
    q = select(DDStream).where(DDStream.target_id == target_id)
    result = await db.execute(q)
    return result.scalars().all()


@router.get("/pipeline")
async def ma_pipeline(db: AsyncSession = Depends(get_db)):
    """M&A pipeline summary."""
    total = await db.execute(select(func.count(AcquisitionTarget.id)))
    active_dd = await db.execute(
        select(func.count(AcquisitionTarget.id)).where(AcquisitionTarget.status == "dd_active")
    )
    offer_stage = await db.execute(
        select(func.count(AcquisitionTarget.id)).where(AcquisitionTarget.status == "offer_stage")
    )
    closed = await db.execute(
        select(func.count(AcquisitionTarget.id)).where(AcquisitionTarget.status == "closed")
    )
    return {
        "total_targets": total.scalar() or 0,
        "active_dd": active_dd.scalar() or 0,
        "offer_stage": offer_stage.scalar() or 0,
        "closed": closed.scalar() or 0,
        "module": "ma_corporate_dev_os",
        "module_ar": "نظام الاستحواذ والتطوير المؤسسي",
    }

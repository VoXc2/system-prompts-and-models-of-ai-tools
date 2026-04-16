"""Sovereign M&A OS: acquisition target tracking and pipeline."""

from __future__ import annotations

from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.sovereign_ma import MATarget
from app.schemas.sovereign import (
    MATargetCreate,
    MATargetResponse,
    MATargetUpdate,
)

router = APIRouter(prefix="/sovereign/ma", tags=["Sovereign M&A OS"])


@router.post("/targets", response_model=MATargetResponse, status_code=201)
async def create_target(
    data: MATargetCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    target = MATarget(
        tenant_id=current_user.tenant_id,
        assigned_to_id=current_user.id,
        **data.model_dump(exclude_none=True),
    )
    db.add(target)
    await db.flush()
    await db.refresh(target)
    return MATargetResponse.model_validate(target)


@router.get("/targets", response_model=List[MATargetResponse])
async def list_targets(
    status: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    q = select(MATarget).where(MATarget.tenant_id == current_user.tenant_id)
    if status:
        q = q.where(MATarget.status == status)
    q = q.order_by(MATarget.created_at.desc())
    result = await db.execute(q)
    return [MATargetResponse.model_validate(t) for t in result.scalars().all()]


@router.get("/targets/{id}", response_model=MATargetResponse)
async def get_target(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(MATarget).where(
            MATarget.id == id,
            MATarget.tenant_id == current_user.tenant_id,
        )
    )
    target = result.scalar_one_or_none()
    if not target:
        raise HTTPException(status_code=404, detail="M&A target not found")
    return MATargetResponse.model_validate(target)


@router.patch("/targets/{id}", response_model=MATargetResponse)
async def update_target(
    id: UUID,
    data: MATargetUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(MATarget).where(
            MATarget.id == id,
            MATarget.tenant_id == current_user.tenant_id,
        )
    )
    target = result.scalar_one_or_none()
    if not target:
        raise HTTPException(status_code=404, detail="M&A target not found")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(target, field, value)
    await db.flush()
    await db.refresh(target)
    return MATargetResponse.model_validate(target)


@router.get("/pipeline")
async def ma_pipeline(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """M&A pipeline board: targets grouped by status."""
    q = await db.execute(
        select(MATarget)
        .where(MATarget.tenant_id == current_user.tenant_id)
        .order_by(MATarget.created_at.desc())
    )
    targets = q.scalars().all()
    board: dict = {}
    for t in targets:
        board.setdefault(t.status, []).append(MATargetResponse.model_validate(t).model_dump())
    return {"pipeline": board, "total": len(targets)}


@router.get("/dd-room/{id}")
async def dd_room(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """DD room view: target details with access control check."""
    result = await db.execute(
        select(MATarget).where(
            MATarget.id == id,
            MATarget.tenant_id == current_user.tenant_id,
        )
    )
    target = result.scalar_one_or_none()
    if not target:
        raise HTTPException(status_code=404, detail="M&A target not found")

    access_list = target.dd_room_access or []
    user_email = getattr(current_user, "email", "")
    has_access = (
        str(current_user.id) in access_list
        or user_email in access_list
        or getattr(current_user, "role", "") in ("owner", "admin")
    )

    return {
        "target": MATargetResponse.model_validate(target).model_dump(),
        "has_dd_access": has_access,
        "dd_room_access": access_list if has_access else [],
        "investment_memo_url": target.investment_memo_url if has_access else None,
        "board_pack_url": target.board_pack_url if has_access else None,
    }

"""Sovereign Decision Plane: AI recommendations, contradictions, model routing."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.sovereign_decision import AIRecommendation, ContradictionRecord
from app.schemas.sovereign import (
    AIRecommendationCreate,
    AIRecommendationResponse,
    AIRecommendationUpdate,
    ContradictionRecordCreate,
    ContradictionRecordResponse,
)

router = APIRouter(prefix="/sovereign/decision", tags=["Sovereign Decision Plane"])


@router.post("/recommendations", response_model=AIRecommendationResponse, status_code=201)
async def create_recommendation(
    data: AIRecommendationCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    rec = AIRecommendation(
        tenant_id=current_user.tenant_id,
        **data.model_dump(exclude_none=True),
    )
    db.add(rec)
    await db.flush()
    await db.refresh(rec)
    return AIRecommendationResponse.model_validate(rec)


@router.get("/recommendations", response_model=List[AIRecommendationResponse])
async def list_recommendations(
    type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    offset: int = Query(0, ge=0),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    q = select(AIRecommendation).where(AIRecommendation.tenant_id == current_user.tenant_id)
    if type:
        q = q.where(AIRecommendation.recommendation_type == type)
    if status:
        q = q.where(AIRecommendation.status == status)
    q = q.order_by(AIRecommendation.created_at.desc()).offset(offset).limit(limit)
    result = await db.execute(q)
    return [AIRecommendationResponse.model_validate(r) for r in result.scalars().all()]


@router.get("/recommendations/{id}", response_model=AIRecommendationResponse)
async def get_recommendation(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(AIRecommendation).where(
            AIRecommendation.id == id,
            AIRecommendation.tenant_id == current_user.tenant_id,
        )
    )
    rec = result.scalar_one_or_none()
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    return AIRecommendationResponse.model_validate(rec)


@router.patch("/recommendations/{id}/status", response_model=AIRecommendationResponse)
async def update_recommendation_status(
    id: UUID,
    data: AIRecommendationUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(AIRecommendation).where(
            AIRecommendation.id == id,
            AIRecommendation.tenant_id == current_user.tenant_id,
        )
    )
    rec = result.scalar_one_or_none()
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")
    for field, value in data.model_dump(exclude_none=True).items():
        setattr(rec, field, value)
    if data.status in ("approved", "rejected"):
        rec.approved_by_id = current_user.id
        rec.approved_at = datetime.now(timezone.utc)
    await db.flush()
    await db.refresh(rec)
    return AIRecommendationResponse.model_validate(rec)


@router.post("/contradictions", response_model=ContradictionRecordResponse, status_code=201)
async def log_contradiction(
    data: ContradictionRecordCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    record = ContradictionRecord(
        tenant_id=current_user.tenant_id,
        **data.model_dump(exclude_none=True),
    )
    db.add(record)
    await db.flush()
    await db.refresh(record)
    return ContradictionRecordResponse.model_validate(record)


@router.get("/contradictions", response_model=List[ContradictionRecordResponse])
async def list_contradictions(
    status: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    q = select(ContradictionRecord).where(ContradictionRecord.tenant_id == current_user.tenant_id)
    if status:
        q = q.where(ContradictionRecord.contradiction_status == status)
    q = q.order_by(ContradictionRecord.created_at.desc())
    result = await db.execute(q)
    return [ContradictionRecordResponse.model_validate(r) for r in result.scalars().all()]


@router.get("/model-routing-dashboard")
async def model_routing_dashboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Model routing dashboard: recommendation counts by type, status, and model lane."""
    tid = current_user.tenant_id

    total_q = await db.execute(
        select(func.count()).select_from(AIRecommendation).where(AIRecommendation.tenant_id == tid)
    )
    total = total_q.scalar() or 0

    by_status_q = await db.execute(
        select(AIRecommendation.status, func.count())
        .where(AIRecommendation.tenant_id == tid)
        .group_by(AIRecommendation.status)
    )
    by_status = {row[0]: row[1] for row in by_status_q.all()}

    by_lane_q = await db.execute(
        select(AIRecommendation.model_lane, func.count())
        .where(AIRecommendation.tenant_id == tid)
        .group_by(AIRecommendation.model_lane)
    )
    by_lane = {row[0]: row[1] for row in by_lane_q.all()}

    contradiction_q = await db.execute(
        select(func.count()).select_from(ContradictionRecord)
        .where(ContradictionRecord.tenant_id == tid, ContradictionRecord.contradiction_status != "none")
    )
    active_contradictions = contradiction_q.scalar() or 0

    return {
        "total_recommendations": total,
        "by_status": by_status,
        "by_model_lane": by_lane,
        "active_contradictions": active_contradictions,
    }

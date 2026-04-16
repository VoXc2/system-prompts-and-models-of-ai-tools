"""Decision Plane API — Structured AI recommendations, evidence packs, HITL approvals."""
from __future__ import annotations

from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.models.sovereign import EvidencePack, SovereignDecision
from app.services.decision_plane import DecisionPlaneService

router = APIRouter(prefix="/decision-plane", tags=["Decision Plane — طبقة القرار"])


class RecommendationRequest(BaseModel):
    decision_type: str = Field(..., description="نوع القرار — e.g. ma_offer, partner_activation, market_launch")
    context: dict[str, Any] = Field(default_factory=dict)
    require_arabic: bool = True
    force_hitl: bool = False


class HITLReview(BaseModel):
    approved: bool
    note: str | None = None


@router.post("/recommend")
async def generate_recommendation(
    tenant_id: str,
    user_id: str,
    payload: RecommendationRequest,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """
    توليد توصية منظمة — Generate a structured, evidence-backed AI recommendation.
    Every recommendation includes: evidence pack, approval class, reversibility,
    sensitivity, next best action, and HITL gate if required.
    """
    svc = DecisionPlaneService(db)
    return await svc.recommend(
        tenant_id=tenant_id,
        user_id=user_id,
        decision_type=payload.decision_type,
        context=payload.context,
        require_arabic=payload.require_arabic,
        force_hitl=payload.force_hitl,
    )


@router.get("/decisions")
async def list_decisions(
    tenant_id: str,
    decision_type: str | None = None,
    hitl_pending: bool | None = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    q = select(SovereignDecision).where(SovereignDecision.tenant_id == tenant_id)
    if decision_type:
        q = q.where(SovereignDecision.decision_type == decision_type)
    if hitl_pending:
        q = q.where(
            SovereignDecision.hitl_required.is_(True),
            SovereignDecision.hitl_status == "pending",
        )
    q = q.order_by(SovereignDecision.created_at.desc()).limit(limit)
    result = await db.execute(q)
    rows = result.scalars().all()
    return [
        {
            "id": str(r.id),
            "decision_type": r.decision_type,
            "lane": r.lane,
            "model_used": r.model_used,
            "recommendation_ar": r.recommendation_ar,
            "hitl_required": r.hitl_required,
            "hitl_status": r.hitl_status,
            "schema_valid": r.schema_valid,
            "contradiction_detected": r.contradiction_detected,
            "latency_ms": r.latency_ms,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in rows
    ]


@router.post("/decisions/{decision_id}/approve")
async def approve_decision(
    decision_id: str,
    tenant_id: str,
    reviewer_id: str,
    payload: HITLReview,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """اعتماد أو رفض قرار — HITL approve/reject a pending decision."""
    svc = DecisionPlaneService(db)
    return await svc.approve_hitl(
        tenant_id=tenant_id,
        decision_id=decision_id,
        reviewer_id=reviewer_id,
        approved=payload.approved,
        note=payload.note or "",
    )


@router.get("/evidence-packs")
async def list_evidence_packs(
    tenant_id: str,
    decision_type: str | None = None,
    status: str | None = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    q = select(EvidencePack).where(EvidencePack.tenant_id == tenant_id)
    if decision_type:
        q = q.where(EvidencePack.decision_type == decision_type)
    if status:
        q = q.where(EvidencePack.status == status)
    q = q.order_by(EvidencePack.created_at.desc()).limit(limit)
    result = await db.execute(q)
    rows = result.scalars().all()
    return [
        {
            "id": str(r.id),
            "decision_type": r.decision_type,
            "title_ar": r.title_ar,
            "title_en": r.title_en,
            "approval_class": r.approval_class,
            "reversibility_class": r.reversibility_class,
            "sensitivity_level": r.sensitivity_level,
            "confidence_score": float(r.confidence_score) if r.confidence_score else None,
            "status": r.status,
            "freshness_at": r.freshness_at.isoformat() if r.freshness_at else None,
            "approved_at": r.approved_at.isoformat() if r.approved_at else None,
            "sources_count": len(r.sources or []),
            "assumptions_count": len(r.assumptions or []),
        }
        for r in rows
    ]


@router.get("/evidence-packs/{pack_id}")
async def get_evidence_pack(
    pack_id: str,
    tenant_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """عرض حزمة الأدلة — Evidence Pack Viewer."""
    result = await db.execute(
        select(EvidencePack).where(
            EvidencePack.id == pack_id,
            EvidencePack.tenant_id == tenant_id,
        )
    )
    r = result.scalar_one_or_none()
    if not r:
        raise HTTPException(status_code=404, detail="Evidence pack not found")
    return {
        "id": str(r.id),
        "decision_type": r.decision_type,
        "title_ar": r.title_ar,
        "title_en": r.title_en,
        "summary_ar": r.summary_ar,
        "sources": r.sources,
        "assumptions": r.assumptions,
        "alternatives": r.alternatives,
        "financial_model_version": r.financial_model_version,
        "freshness_at": r.freshness_at.isoformat() if r.freshness_at else None,
        "confidence_score": float(r.confidence_score) if r.confidence_score else None,
        "policy_notes": r.policy_notes,
        "approval_class": r.approval_class,
        "reversibility_class": r.reversibility_class,
        "sensitivity_level": r.sensitivity_level,
        "rollback_notes": r.rollback_notes,
        "status": r.status,
        "approved_at": r.approved_at.isoformat() if r.approved_at else None,
    }


@router.get("/pending-hitl")
async def pending_hitl(
    tenant_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """قرارات تنتظر الاعتماد البشري — All pending HITL decisions."""
    svc = DecisionPlaneService(db)
    pending = await svc.list_pending_hitl(tenant_id)
    return {
        "label_ar": "اعتماد بشري معلق",
        "pending_count": len(pending),
        "decisions": pending,
    }

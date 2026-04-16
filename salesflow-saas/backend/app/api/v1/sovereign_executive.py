"""Sovereign Executive/Board OS: dashboard, approvals, risk, evidence packs."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User
from app.models.sovereign_decision import AIRecommendation, ContradictionRecord
from app.models.sovereign_execution import DurableWorkflow
from app.models.sovereign_trust import PolicyEvaluation, ComplianceMapping
from app.models.sovereign_partnership import Partner
from app.models.sovereign_ma import MATarget
from app.models.sovereign_expansion import ExpansionMarket
from app.models.sovereign_pmi import PMIProgram
from app.models.sovereign_connector import ConnectorDefinition
from app.models.sovereign_evidence import EvidencePack
from app.schemas.sovereign import (
    EvidencePackCreate,
    EvidencePackResponse,
    EvidencePackUpdate,
    SovereignDashboardSummary,
)

router = APIRouter(prefix="/sovereign/executive", tags=["Sovereign Executive/Board OS"])


class EvidencePackStatusUpdate(BaseModel):
    status: str


@router.get("/dashboard", response_model=SovereignDashboardSummary)
async def executive_dashboard(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Executive room dashboard: aggregated counts from all sovereign planes."""
    tid = current_user.tenant_id

    rec_q = await db.execute(
        select(func.count()).select_from(AIRecommendation).where(AIRecommendation.tenant_id == tid)
    )
    pending_q = await db.execute(
        select(func.count()).select_from(AIRecommendation).where(
            AIRecommendation.tenant_id == tid, AIRecommendation.status == "pending"
        )
    )
    wf_q = await db.execute(
        select(func.count()).select_from(DurableWorkflow).where(
            DurableWorkflow.tenant_id == tid, DurableWorkflow.status == "running"
        )
    )
    partner_q = await db.execute(
        select(func.count()).select_from(Partner).where(
            Partner.tenant_id == tid, Partner.status == "active"
        )
    )
    ma_q = await db.execute(
        select(func.count()).select_from(MATarget).where(MATarget.tenant_id == tid)
    )
    exp_q = await db.execute(
        select(func.count()).select_from(ExpansionMarket).where(ExpansionMarket.tenant_id == tid)
    )
    pmi_q = await db.execute(
        select(func.count()).select_from(PMIProgram).where(PMIProgram.tenant_id == tid)
    )
    viol_q = await db.execute(
        select(func.count()).select_from(PolicyEvaluation).where(
            PolicyEvaluation.tenant_id == tid, PolicyEvaluation.evaluation_result == "violation"
        )
    )
    contra_q = await db.execute(
        select(func.count()).select_from(ContradictionRecord).where(
            ContradictionRecord.tenant_id == tid,
            ContradictionRecord.contradiction_status != "none",
        )
    )
    ep_q = await db.execute(
        select(func.count()).select_from(EvidencePack).where(
            EvidencePack.tenant_id == tid, EvidencePack.status == "assembling"
        )
    )

    return SovereignDashboardSummary(
        total_recommendations=rec_q.scalar() or 0,
        pending_approvals=pending_q.scalar() or 0,
        active_workflows=wf_q.scalar() or 0,
        active_partners=partner_q.scalar() or 0,
        ma_pipeline_count=ma_q.scalar() or 0,
        expansion_markets=exp_q.scalar() or 0,
        pmi_programs=pmi_q.scalar() or 0,
        policy_violations=viol_q.scalar() or 0,
        contradiction_alerts=contra_q.scalar() or 0,
        evidence_packs_pending=ep_q.scalar() or 0,
    )


@router.get("/approval-center")
async def approval_center(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Approval center: pending approvals across all sovereign tracks."""
    tid = current_user.tenant_id

    pending_recs_q = await db.execute(
        select(AIRecommendation).where(
            AIRecommendation.tenant_id == tid,
            AIRecommendation.status == "pending",
        ).order_by(AIRecommendation.created_at.desc()).limit(50)
    )
    pending_recs = pending_recs_q.scalars().all()

    pending_eps_q = await db.execute(
        select(EvidencePack).where(
            EvidencePack.tenant_id == tid,
            EvidencePack.status == "pending_approval",
        ).order_by(EvidencePack.created_at.desc()).limit(50)
    )
    pending_eps = pending_eps_q.scalars().all()

    return {
        "pending_recommendations": [
            {"id": str(r.id), "title": r.title, "type": r.recommendation_type, "created_at": r.created_at.isoformat() if r.created_at else None}
            for r in pending_recs
        ],
        "pending_evidence_packs": [
            {"id": str(e.id), "title": e.title, "pack_type": e.pack_type, "created_at": e.created_at.isoformat() if e.created_at else None}
            for e in pending_eps
        ],
        "total_pending": len(pending_recs) + len(pending_eps),
    }


@router.get("/risk-board")
async def risk_board(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Risk board: violations, contradictions, and high-risk compliance items."""
    tid = current_user.tenant_id

    violations_q = await db.execute(
        select(PolicyEvaluation).where(
            PolicyEvaluation.tenant_id == tid,
            PolicyEvaluation.evaluation_result == "violation",
        ).order_by(PolicyEvaluation.created_at.desc()).limit(20)
    )
    violations = violations_q.scalars().all()

    contradictions_q = await db.execute(
        select(ContradictionRecord).where(
            ContradictionRecord.tenant_id == tid,
            ContradictionRecord.contradiction_status != "none",
        ).order_by(ContradictionRecord.created_at.desc()).limit(20)
    )
    contradictions = contradictions_q.scalars().all()

    high_risk_q = await db.execute(
        select(ComplianceMapping).where(
            ComplianceMapping.tenant_id == tid,
            ComplianceMapping.risk_level == "high",
        )
    )
    high_risk = high_risk_q.scalars().all()

    return {
        "violations": [
            {"id": str(v.id), "action_type": v.action_type, "violation_details": v.violation_details, "created_at": v.created_at.isoformat() if v.created_at else None}
            for v in violations
        ],
        "contradictions": [
            {"id": str(c.id), "intended_action": c.intended_action, "status": c.contradiction_status, "created_at": c.created_at.isoformat() if c.created_at else None}
            for c in contradictions
        ],
        "high_risk_compliance": [
            {"id": str(m.id), "framework": m.framework, "control_name": m.control_name, "status": m.status}
            for m in high_risk
        ],
    }


# ── Evidence Packs ────────────────────────────────────────────

@router.get("/evidence-packs", response_model=List[EvidencePackResponse])
async def list_evidence_packs(
    type: Optional[str] = Query(None),
    status: Optional[str] = Query(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    q = select(EvidencePack).where(EvidencePack.tenant_id == current_user.tenant_id)
    if type:
        q = q.where(EvidencePack.pack_type == type)
    if status:
        q = q.where(EvidencePack.status == status)
    q = q.order_by(EvidencePack.created_at.desc())
    result = await db.execute(q)
    return [EvidencePackResponse.model_validate(e) for e in result.scalars().all()]


@router.post("/evidence-packs", response_model=EvidencePackResponse, status_code=201)
async def create_evidence_pack(
    data: EvidencePackCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    ep = EvidencePack(
        tenant_id=current_user.tenant_id,
        assembled_by_id=current_user.id,
        **data.model_dump(exclude_none=True),
    )
    db.add(ep)
    await db.flush()
    await db.refresh(ep)
    return EvidencePackResponse.model_validate(ep)


@router.get("/evidence-packs/{id}", response_model=EvidencePackResponse)
async def get_evidence_pack(
    id: UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(EvidencePack).where(
            EvidencePack.id == id,
            EvidencePack.tenant_id == current_user.tenant_id,
        )
    )
    ep = result.scalar_one_or_none()
    if not ep:
        raise HTTPException(status_code=404, detail="Evidence pack not found")
    return EvidencePackResponse.model_validate(ep)


@router.patch("/evidence-packs/{id}/status", response_model=EvidencePackResponse)
async def update_evidence_pack_status(
    id: UUID,
    data: EvidencePackStatusUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(EvidencePack).where(
            EvidencePack.id == id,
            EvidencePack.tenant_id == current_user.tenant_id,
        )
    )
    ep = result.scalar_one_or_none()
    if not ep:
        raise HTTPException(status_code=404, detail="Evidence pack not found")
    ep.status = data.status
    if data.status == "approved":
        ep.approved_by_id = current_user.id
        ep.approved_at = datetime.now(timezone.utc)
    await db.flush()
    await db.refresh(ep)
    return EvidencePackResponse.model_validate(ep)


# ── Actual vs Forecast ────────────────────────────────────────

@router.get("/actual-vs-forecast")
async def actual_vs_forecast(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Actual vs forecast dashboard: aggregated from expansion markets."""
    tid = current_user.tenant_id
    q = await db.execute(
        select(ExpansionMarket).where(ExpansionMarket.tenant_id == tid)
    )
    markets = q.scalars().all()

    data = []
    for m in markets:
        avf = m.actual_vs_forecast or {}
        data.append({
            "market_id": str(m.id),
            "market_name": m.market_name,
            "market_name_ar": m.market_name_ar,
            "country_code": m.country_code,
            "status": m.status,
            "actual_vs_forecast": avf,
        })

    return {"markets": data, "total": len(data)}

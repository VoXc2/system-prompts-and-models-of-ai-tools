"""Executive / Board OS — API routes for executive surfaces and governance."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional

from app.database import get_db
from app.models.executive import (
    ExecutiveApproval, BoardMemo, PolicyViolation,
    RiskHeatmapEntry, ForecastEntry, ComplianceMatrix,
    ModelRoutingLog, ToolVerificationEntry,
)
from app.schemas.sovereign import (
    ExecutiveApprovalCreate, ExecutiveApprovalResponse,
    BoardMemoCreate, BoardMemoResponse,
    PolicyViolationResponse, RiskHeatmapResponse,
    ForecastResponse, ComplianceMatrixResponse,
)

router = APIRouter(prefix="/executive", tags=["Executive OS — القيادة التنفيذية"])


# ── Approval Center ─────────────────────────────────────────────

@router.get("/approvals", response_model=list[ExecutiveApprovalResponse])
async def list_approvals(
    status: Optional[str] = None,
    approval_class: Optional[str] = None,
    limit: int = Query(default=50, le=200),
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    """Approval Center — list pending and historical approvals."""
    q = select(ExecutiveApproval)
    if status:
        q = q.where(ExecutiveApproval.status == status)
    if approval_class:
        q = q.where(ExecutiveApproval.approval_class == approval_class)
    q = q.order_by(ExecutiveApproval.created_at.desc()).offset(offset).limit(limit)
    result = await db.execute(q)
    return result.scalars().all()


@router.post("/approvals", response_model=ExecutiveApprovalResponse, status_code=201)
async def create_approval(
    data: ExecutiveApprovalCreate,
    db: AsyncSession = Depends(get_db),
):
    """Request executive approval for a decision."""
    approval = ExecutiveApproval(**data.model_dump())
    approval.tenant_id = "00000000-0000-0000-0000-000000000001"
    approval.requested_by_id = "00000000-0000-0000-0000-000000000001"
    db.add(approval)
    await db.flush()
    await db.refresh(approval)
    return approval


@router.patch("/approvals/{approval_id}/decide")
async def decide_approval(
    approval_id: str,
    decision: str = Query(..., regex="^(approved|rejected)$"),
    db: AsyncSession = Depends(get_db),
):
    """Approve or reject a pending approval."""
    result = await db.execute(select(ExecutiveApproval).where(ExecutiveApproval.id == approval_id))
    approval = result.scalar_one_or_none()
    if not approval:
        raise HTTPException(status_code=404, detail="Approval not found")
    if approval.status != "pending":
        raise HTTPException(status_code=400, detail="Approval already decided")
    approval.status = decision
    from datetime import datetime, timezone
    approval.decided_at = datetime.now(timezone.utc)
    return {"id": str(approval.id), "status": approval.status, "decided_at": approval.decided_at}


# ── Board Memos ─────────────────────────────────────────────────

@router.get("/memos", response_model=list[BoardMemoResponse])
async def list_memos(
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """Board memo repository."""
    q = select(BoardMemo)
    if status:
        q = q.where(BoardMemo.status == status)
    q = q.order_by(BoardMemo.created_at.desc())
    result = await db.execute(q)
    return result.scalars().all()


@router.post("/memos", response_model=BoardMemoResponse, status_code=201)
async def create_memo(data: BoardMemoCreate, db: AsyncSession = Depends(get_db)):
    """Create a board-ready memo."""
    memo = BoardMemo(**data.model_dump())
    memo.tenant_id = "00000000-0000-0000-0000-000000000001"
    db.add(memo)
    await db.flush()
    await db.refresh(memo)
    return memo


# ── Policy Violations ───────────────────────────────────────────

@router.get("/violations", response_model=list[PolicyViolationResponse])
async def list_violations(
    status: Optional[str] = None,
    severity: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """Policy violations board."""
    q = select(PolicyViolation)
    if status:
        q = q.where(PolicyViolation.status == status)
    if severity:
        q = q.where(PolicyViolation.severity == severity)
    q = q.order_by(PolicyViolation.created_at.desc())
    result = await db.execute(q)
    return result.scalars().all()


# ── Risk Heatmap ────────────────────────────────────────────────

@router.get("/risk-heatmap", response_model=list[RiskHeatmapResponse])
async def risk_heatmap(db: AsyncSession = Depends(get_db)):
    """Live risk heatmap."""
    q = select(RiskHeatmapEntry).where(
        RiskHeatmapEntry.status == "active"
    ).order_by(RiskHeatmapEntry.score.desc())
    result = await db.execute(q)
    return result.scalars().all()


# ── Forecast vs Actual ──────────────────────────────────────────

@router.get("/forecast", response_model=list[ForecastResponse])
async def forecast_vs_actual(
    period: Optional[str] = None,
    category: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """Actual vs Forecast dashboard data."""
    q = select(ForecastEntry)
    if period:
        q = q.where(ForecastEntry.period == period)
    if category:
        q = q.where(ForecastEntry.category == category)
    q = q.order_by(ForecastEntry.period.desc())
    result = await db.execute(q)
    return result.scalars().all()


# ── Saudi Compliance Matrix ─────────────────────────────────────

@router.get("/compliance-matrix", response_model=list[ComplianceMatrixResponse])
async def compliance_matrix(
    framework: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    """Saudi Compliance Matrix (PDPL, NCA, NIST AI RMF, OWASP LLM)."""
    q = select(ComplianceMatrix)
    if framework:
        q = q.where(ComplianceMatrix.framework == framework)
    q = q.order_by(ComplianceMatrix.framework, ComplianceMatrix.control_id)
    result = await db.execute(q)
    return result.scalars().all()


# ── Model Routing Dashboard ─────────────────────────────────────

@router.get("/model-routing")
async def model_routing_dashboard(
    limit: int = Query(default=100, le=500),
    db: AsyncSession = Depends(get_db),
):
    """Model routing performance dashboard."""
    q = select(ModelRoutingLog).order_by(ModelRoutingLog.created_at.desc()).limit(limit)
    result = await db.execute(q)
    logs = result.scalars().all()
    return [
        {
            "id": str(log.id),
            "task_class": log.task_class,
            "selected_model": log.selected_model,
            "latency_ms": log.latency_ms,
            "success": log.success,
            "schema_adherence": log.schema_adherence,
            "arabic_quality_score": log.arabic_quality_score,
            "cost_usd": float(log.cost_usd) if log.cost_usd else None,
            "created_at": log.created_at,
        }
        for log in logs
    ]


# ── Tool Verification Ledger ───────────────────────────────────

@router.get("/tool-ledger")
async def tool_verification_ledger(db: AsyncSession = Depends(get_db)):
    """Tool verification ledger — all registered tools and their health."""
    q = select(ToolVerificationEntry).order_by(ToolVerificationEntry.tool_name)
    result = await db.execute(q)
    entries = result.scalars().all()
    return [
        {
            "id": str(e.id),
            "tool_id": e.tool_id,
            "tool_name": e.tool_name,
            "tool_name_ar": e.tool_name_ar,
            "version": e.version,
            "verified": e.verified,
            "health_status": e.health_status,
            "last_verified_at": e.last_verified_at,
        }
        for e in entries
    ]


# ── Connector Health Board ──────────────────────────────────────

@router.get("/connector-health")
async def connector_health():
    """Connector Health Board — live status of all integrations."""
    from app.planes.data.connector_registry import CONNECTOR_REGISTRY
    return [
        {
            "connector_id": c.connector_id,
            "name": c.name,
            "name_ar": c.name_ar,
            "type": c.connector_type.value,
            "version": c.version,
            "status": c.status.value,
            "error_count_24h": c.error_count_24h,
        }
        for c in CONNECTOR_REGISTRY
    ]


# ── Executive Room Dashboard ────────────────────────────────────

@router.get("/room")
async def executive_room(db: AsyncSession = Depends(get_db)):
    """Executive Room — unified command center view."""
    pending_approvals = await db.execute(
        select(func.count(ExecutiveApproval.id)).where(ExecutiveApproval.status == "pending")
    )
    open_violations = await db.execute(
        select(func.count(PolicyViolation.id)).where(PolicyViolation.status == "open")
    )
    active_risks = await db.execute(
        select(func.count(RiskHeatmapEntry.id)).where(RiskHeatmapEntry.status == "active")
    )
    return {
        "pending_approvals": pending_approvals.scalar() or 0,
        "open_violations": open_violations.scalar() or 0,
        "active_risks": active_risks.scalar() or 0,
        "module": "executive_board_os",
        "module_ar": "غرفة القيادة التنفيذية",
        "surfaces": [
            {"id": "approval_center", "name_ar": "مركز الاعتماد"},
            {"id": "evidence_pack_viewer", "name_ar": "عارض حزم الأدلة"},
            {"id": "risk_heatmap", "name_ar": "خريطة المخاطر الحرارية"},
            {"id": "violations_board", "name_ar": "لوحة المخالفات"},
            {"id": "forecast_dashboard", "name_ar": "الفعلي مقابل المتوقع"},
            {"id": "compliance_matrix", "name_ar": "مصفوفة الامتثال السعودية"},
            {"id": "model_routing", "name_ar": "لوحة توجيه النماذج"},
            {"id": "tool_ledger", "name_ar": "سجل التحقق من الأدوات"},
            {"id": "connector_health", "name_ar": "صحة الموصلات"},
        ],
    }

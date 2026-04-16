"""Executive Room API — Board packs, approval center, risk heatmap, actual vs forecast."""
from __future__ import annotations

from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.database import get_db
from app.models.sovereign import BoardPack, PolicyViolation, SovereignDecision
from app.models.compat import default_uuid

router = APIRouter(prefix="/executive-room", tags=["Executive Room — الغرفة التنفيذية"])


# ─── Schemas ──────────────────────────────────────────────────────

class BoardPackCreate(BaseModel):
    title_ar: str = Field(..., description="عنوان الحزمة بالعربية")
    title_en: str | None = None
    pack_type: str = Field(..., description="board_memo | risk_heatmap | actual_vs_forecast | pipeline_review | approval_center")
    period_label: str | None = None
    content_ar: str | None = None
    structured_data: dict[str, Any] | None = None
    approval_items: list[dict] | None = None
    risk_heatmap: dict[str, Any] | None = None


class BoardPackReview(BaseModel):
    approved: bool
    note: str | None = None


# ─── Endpoints ────────────────────────────────────────────────────

@router.get("/dashboard")
async def executive_dashboard(
    tenant_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """
    مركز القيادة التنفيذية — Executive Command Center.
    Returns aggregated KPIs for board-level situational awareness.
    """
    # Policy violations summary
    violations_result = await db.execute(
        select(func.count(PolicyViolation.id)).where(
            PolicyViolation.tenant_id == tenant_id,
            PolicyViolation.resolved.is_(False),
        )
    )
    open_violations = violations_result.scalar() or 0

    critical_violations = await db.execute(
        select(func.count(PolicyViolation.id)).where(
            PolicyViolation.tenant_id == tenant_id,
            PolicyViolation.resolved.is_(False),
            PolicyViolation.severity == "critical",
        )
    )
    critical_count = critical_violations.scalar() or 0

    # Pending HITL decisions
    hitl_result = await db.execute(
        select(func.count(SovereignDecision.id)).where(
            SovereignDecision.tenant_id == tenant_id,
            SovereignDecision.hitl_required.is_(True),
            SovereignDecision.hitl_status == "pending",
        )
    )
    pending_hitl = hitl_result.scalar() or 0

    # Board packs
    packs_result = await db.execute(
        select(func.count(BoardPack.id)).where(
            BoardPack.tenant_id == tenant_id,
        )
    )
    total_packs = packs_result.scalar() or 0

    return {
        "labels": {
            "ar": "لوحة القيادة التنفيذية",
            "en": "Executive Dashboard",
        },
        "kpis": {
            "open_policy_violations": open_violations,
            "critical_violations": critical_count,
            "pending_approvals": pending_hitl,
            "board_packs_total": total_packs,
        },
        "alerts": [
            {"type": "policy_violation", "count": critical_count, "label_ar": "انتهاكات حرجة تحتاج مراجعة"}
            if critical_count > 0 else None,
            {"type": "pending_approvals", "count": pending_hitl, "label_ar": "قرارات تنتظر الاعتماد"}
            if pending_hitl > 0 else None,
        ],
    }


@router.post("/board-packs", status_code=status.HTTP_201_CREATED)
async def create_board_pack(
    tenant_id: str,
    created_by_id: str,
    payload: BoardPackCreate,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """إنشاء حزمة مجلس إدارة جديدة — Create new board pack."""
    pack = BoardPack(
        tenant_id=tenant_id,
        title_ar=payload.title_ar,
        title_en=payload.title_en,
        pack_type=payload.pack_type,
        period_label=payload.period_label,
        content_ar=payload.content_ar,
        structured_data=payload.structured_data or {},
        approval_items=payload.approval_items or [],
        risk_heatmap=payload.risk_heatmap or {},
        created_by_id=created_by_id,
    )
    db.add(pack)
    await db.commit()
    await db.refresh(pack)
    return {"id": str(pack.id), "status": pack.status, "title_ar": pack.title_ar}


@router.get("/board-packs")
async def list_board_packs(
    tenant_id: str,
    pack_type: str | None = None,
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    """قائمة حزم المجلس — List board packs."""
    q = select(BoardPack).where(BoardPack.tenant_id == tenant_id)
    if pack_type:
        q = q.where(BoardPack.pack_type == pack_type)
    q = q.order_by(BoardPack.created_at.desc()).limit(50)
    result = await db.execute(q)
    rows = result.scalars().all()
    return [
        {
            "id": str(r.id),
            "title_ar": r.title_ar,
            "title_en": r.title_en,
            "pack_type": r.pack_type,
            "period_label": r.period_label,
            "status": r.status,
            "policy_violations_count": r.policy_violations_count,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in rows
    ]


@router.get("/board-packs/{pack_id}")
async def get_board_pack(
    pack_id: str,
    tenant_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    result = await db.execute(
        select(BoardPack).where(
            BoardPack.id == pack_id,
            BoardPack.tenant_id == tenant_id,
        )
    )
    pack = result.scalar_one_or_none()
    if not pack:
        raise HTTPException(status_code=404, detail="Board pack not found")
    return {
        "id": str(pack.id),
        "title_ar": pack.title_ar,
        "title_en": pack.title_en,
        "pack_type": pack.pack_type,
        "period_label": pack.period_label,
        "content_ar": pack.content_ar,
        "structured_data": pack.structured_data,
        "approval_items": pack.approval_items,
        "risk_heatmap": pack.risk_heatmap,
        "status": pack.status,
        "policy_violations_count": pack.policy_violations_count,
        "approved_at": pack.approved_at.isoformat() if pack.approved_at else None,
        "published_at": pack.published_at.isoformat() if pack.published_at else None,
    }


@router.post("/approval-center")
async def approval_center(
    tenant_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """مركز الاعتماد — returns all items pending approval across all planes."""
    from app.services.decision_plane import DecisionPlaneService
    svc = DecisionPlaneService(db)
    pending = await svc.list_pending_hitl(tenant_id)
    return {
        "label_ar": "مركز الاعتماد",
        "label_en": "Approval Center",
        "pending_decisions": pending,
        "total_pending": len(pending),
    }

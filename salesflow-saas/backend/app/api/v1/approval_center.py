"""Approval Center API — live approval queue with SLA tracking."""

from datetime import datetime, timezone

from fastapi import APIRouter, Depends
from pydantic import BaseModel as PydanticBase
from typing import Any, Dict, Optional

router = APIRouter(prefix="/approval-center", tags=["Approval Center"])


class ApprovalAction(PydanticBase):
    note: Optional[str] = None


async def _get_db():
    from app.database import get_db
    async for session in get_db():
        yield session


def _serialize_approval(row) -> Dict[str, Any]:
    payload = row.payload if isinstance(row.payload, dict) else {}
    sla = payload.get("_dealix_sla", {}) if isinstance(payload.get("_dealix_sla"), dict) else {}
    return {
        "id": str(row.id), "channel": row.channel, "resource_type": row.resource_type,
        "resource_id": str(row.resource_id), "status": row.status,
        "priority": sla.get("priority", "normal"), "category": payload.get("category", "general"),
        "escalation_level": int(sla.get("escalation_level", 0)),
        "escalation_label_ar": sla.get("escalation_label_ar", ""),
        "age_hours": sla.get("age_hours", 0), "note": row.note,
        "requested_by": str(row.requested_by_id) if row.requested_by_id else None,
        "created_at": row.created_at.isoformat() if row.created_at else None,
    }


@router.get("/")
async def list_approvals(
    tenant_id: str = "00000000-0000-0000-0000-000000000000",
    status: Optional[str] = "pending",
    db=Depends(_get_db),
) -> Dict[str, Any]:
    from sqlalchemy import select
    from app.models.operations import ApprovalRequest
    stmt = select(ApprovalRequest).where(ApprovalRequest.tenant_id == tenant_id)
    if status:
        stmt = stmt.where(ApprovalRequest.status == status)
    stmt = stmt.order_by(ApprovalRequest.created_at.asc())
    result = await db.execute(stmt)
    rows = list(result.scalars().all())
    return {"approvals": [_serialize_approval(r) for r in rows], "total": len(rows)}


@router.get("/stats")
async def approval_stats(
    tenant_id: str = "00000000-0000-0000-0000-000000000000",
    db=Depends(_get_db),
) -> Dict[str, Any]:
    from sqlalchemy import select, func
    from app.models.operations import ApprovalRequest
    rows = (await db.execute(
        select(ApprovalRequest.payload).where(ApprovalRequest.tenant_id == tenant_id, ApprovalRequest.status == "pending")
    )).scalars().all()
    compliant = warning = breach = 0
    for p in rows:
        sla = (p or {}).get("_dealix_sla", {}) if isinstance(p, dict) else {}
        level = int(sla.get("escalation_level", 0)) if isinstance(sla, dict) else 0
        if level == 0: compliant += 1
        elif level == 1: warning += 1
        else: breach += 1
    return {"total_pending": len(rows), "sla_compliant": compliant, "sla_warning": warning, "sla_breach": breach}


@router.get("/my-pending")
async def my_pending_approvals(
    tenant_id: str = "00000000-0000-0000-0000-000000000000",
    db=Depends(_get_db),
) -> Dict[str, Any]:
    from sqlalchemy import select
    from app.models.operations import ApprovalRequest
    result = await db.execute(
        select(ApprovalRequest).where(ApprovalRequest.tenant_id == tenant_id, ApprovalRequest.status == "pending").order_by(ApprovalRequest.created_at.asc())
    )
    rows = list(result.scalars().all())
    return {"approvals": [_serialize_approval(r) for r in rows], "total": len(rows)}


@router.post("/{approval_id}/approve")
async def approve(approval_id: str, body: ApprovalAction, db=Depends(_get_db)) -> Dict[str, Any]:
    from sqlalchemy import select
    from app.models.operations import ApprovalRequest
    row = (await db.execute(select(ApprovalRequest).where(ApprovalRequest.id == approval_id))).scalar_one_or_none()
    if not row:
        return {"id": approval_id, "status": "not_found"}
    row.status = "approved"
    row.reviewed_at = datetime.now(timezone.utc)
    row.note = body.note
    await db.commit()
    return {"id": approval_id, "status": "approved", "note": body.note}


@router.post("/{approval_id}/reject")
async def reject(approval_id: str, body: ApprovalAction, db=Depends(_get_db)) -> Dict[str, Any]:
    from sqlalchemy import select
    from app.models.operations import ApprovalRequest
    row = (await db.execute(select(ApprovalRequest).where(ApprovalRequest.id == approval_id))).scalar_one_or_none()
    if not row:
        return {"id": approval_id, "status": "not_found"}
    row.status = "rejected"
    row.reviewed_at = datetime.now(timezone.utc)
    row.note = body.note
    await db.commit()
    return {"id": approval_id, "status": "rejected", "note": body.note}


@router.post("/{approval_id}/escalate")
async def escalate(approval_id: str, body: ApprovalAction) -> Dict[str, Any]:
    return {"id": approval_id, "status": "escalated", "note": body.note}

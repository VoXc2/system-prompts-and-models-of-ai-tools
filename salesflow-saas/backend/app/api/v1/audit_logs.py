"""Audit logs API — compliance and security trail."""
from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.api.v1.deps import get_current_user, get_db, require_role
from app.models.audit_log import AuditLog

router = APIRouter()


@router.get("")
async def list_audit_logs(
    action: Optional[str] = None,
    entity_type: Optional[str] = None,
    user_id: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    current_user: dict = Depends(require_role("owner", "admin")),
    db: AsyncSession = Depends(get_db),
):
    tenant_id = current_user["tenant_id"]
    query = select(AuditLog).where(AuditLog.tenant_id == tenant_id)

    if action:
        query = query.where(AuditLog.action == action)
    if entity_type:
        query = query.where(AuditLog.entity_type == entity_type)
    if user_id:
        query = query.where(AuditLog.user_id == user_id)

    total_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(total_q)).scalar() or 0

    query = query.order_by(AuditLog.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    items = result.scalars().all()

    return {"items": [_serialize(a) for a in items], "total": total}


def _serialize(a):
    return {
        "id": str(a.id),
        "action": a.action,
        "entity_type": getattr(a, "entity_type", None),
        "entity_id": str(a.entity_id) if getattr(a, "entity_id", None) else None,
        "user_id": str(a.user_id) if getattr(a, "user_id", None) else None,
        "changes": getattr(a, "changes", None),
        "ip_address": getattr(a, "ip_address", None),
        "created_at": a.created_at.isoformat() if a.created_at else None,
    }

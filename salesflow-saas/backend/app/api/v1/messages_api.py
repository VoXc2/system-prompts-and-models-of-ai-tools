"""Messages API — view and manage outgoing messages across channels."""
from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.api.v1.deps import get_current_user, get_db
from app.models.message import Message

router = APIRouter()


@router.get("")
async def list_messages(
    channel: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    tenant_id = current_user["tenant_id"]
    query = select(Message).where(Message.tenant_id == tenant_id)

    if channel:
        query = query.where(Message.channel == channel)
    if status:
        query = query.where(Message.status == status)

    total_q = select(func.count()).select_from(query.subquery())
    total = (await db.execute(total_q)).scalar() or 0

    query = query.order_by(Message.created_at.desc()).offset(skip).limit(limit)
    result = await db.execute(query)
    items = result.scalars().all()

    return {"items": [_serialize(m) for m in items], "total": total}


@router.get("/scheduled")
async def list_scheduled(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    tenant_id = current_user["tenant_id"]
    query = (
        select(Message)
        .where(Message.tenant_id == tenant_id, Message.status == "pending")
        .order_by(Message.created_at.asc())
        .limit(100)
    )
    result = await db.execute(query)
    items = result.scalars().all()
    return {"items": [_serialize(m) for m in items]}


def _serialize(m):
    return {
        "id": str(m.id),
        "lead_id": str(m.lead_id) if getattr(m, "lead_id", None) else None,
        "channel": getattr(m, "channel", None),
        "content": getattr(m, "content", None),
        "status": m.status,
        "sent_at": m.sent_at.isoformat() if getattr(m, "sent_at", None) else None,
        "created_at": m.created_at.isoformat() if m.created_at else None,
    }

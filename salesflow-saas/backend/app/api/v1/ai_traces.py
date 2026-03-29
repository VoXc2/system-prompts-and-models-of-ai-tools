"""AI Traces API — governance dashboard for all AI calls."""
from fastapi import APIRouter, Depends
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.api.v1.deps import get_current_user, get_db
from app.models.ai_trace import AITrace

router = APIRouter()


@router.get("/traces")
async def list_traces(
    provider: Optional[str] = None,
    status: Optional[str] = None,
    skip: int = 0,
    limit: int = 50,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(AITrace).order_by(AITrace.created_at.desc())

    if provider:
        query = query.where(AITrace.provider == provider)
    if status:
        query = query.where(AITrace.status == status)
    # AITrace may not be tenant-scoped (global governance), but filter if tenant_id exists
    if hasattr(AITrace, "tenant_id"):
        query = query.where(AITrace.tenant_id == current_user["tenant_id"])

    query = query.offset(skip).limit(limit)
    result = await db.execute(query)
    items = result.scalars().all()

    return {"items": [_serialize(t) for t in items]}


@router.get("/traces/stats")
async def trace_stats(
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    base = select(AITrace)
    if hasattr(AITrace, "tenant_id"):
        base = base.where(AITrace.tenant_id == current_user["tenant_id"])

    # Total calls
    total = (await db.execute(select(func.count()).select_from(base.subquery()))).scalar() or 0

    # Total cost
    cost_q = select(func.coalesce(func.sum(AITrace.cost_usd), 0.0))
    if hasattr(AITrace, "tenant_id"):
        cost_q = cost_q.where(AITrace.tenant_id == current_user["tenant_id"])
    total_cost = float((await db.execute(cost_q)).scalar() or 0)

    # Total tokens
    tokens_q = select(func.coalesce(func.sum(AITrace.total_tokens), 0))
    if hasattr(AITrace, "tenant_id"):
        tokens_q = tokens_q.where(AITrace.tenant_id == current_user["tenant_id"])
    total_tokens = int((await db.execute(tokens_q)).scalar() or 0)

    # Average latency
    latency_q = select(func.coalesce(func.avg(AITrace.latency_ms), 0))
    if hasattr(AITrace, "tenant_id"):
        latency_q = latency_q.where(AITrace.tenant_id == current_user["tenant_id"])
    avg_latency = float((await db.execute(latency_q)).scalar() or 0)

    # Error count
    errors_q = select(func.count()).where(AITrace.status == "error")
    if hasattr(AITrace, "tenant_id"):
        errors_q = errors_q.where(AITrace.tenant_id == current_user["tenant_id"])
    error_count = int((await db.execute(errors_q)).scalar() or 0)

    return {
        "total_calls": total,
        "total_cost_usd": round(total_cost, 4),
        "total_tokens": total_tokens,
        "avg_latency_ms": round(avg_latency, 1),
        "error_count": error_count,
        "error_rate": round(error_count / max(total, 1) * 100, 1),
    }


def _serialize(t):
    return {
        "id": str(t.id),
        "agent_type": getattr(t, "agent_type", None),
        "action": getattr(t, "action", None),
        "status": t.status,
        "provider": t.provider,
        "model": t.model,
        "temperature": getattr(t, "temperature", None),
        "input_tokens": t.input_tokens,
        "output_tokens": t.output_tokens,
        "total_tokens": t.total_tokens,
        "cost_usd": float(t.cost_usd) if t.cost_usd else 0,
        "latency_ms": t.latency_ms,
        "error_message": getattr(t, "error_message", None),
        "created_at": t.created_at.isoformat() if t.created_at else None,
    }

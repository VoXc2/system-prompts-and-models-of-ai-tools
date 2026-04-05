"""
Central Brain API — additive routes; existing /leads, /deals, etc. unchanged.

Requires JWT (tenant-scoped). Health/metrics exempt when DEALIX_INTERNAL_API_TOKEN is set (see middleware).
"""

from __future__ import annotations

from typing import Any, Literal, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_tenant, get_current_user
from app.brain import brain_health_snapshot, ingest_event, list_agent_profiles
from app.brain.observability import snapshot as metrics_snapshot
from app.brain.profiles import AGENT_PROFILES
from app.brain.skills.registry import SKILL_DEFINITIONS
from app.brain.types import MemoryTier
from app.database import get_db
from app.models.brain_runtime import BrainAgentSession
from app.models.tenant import Tenant
from app.models.user import User
from app.workers.brain_tasks import brain_dispatch_agent_chain

router = APIRouter(prefix="/brain", tags=["🧠 Central Brain"])


class BrainEventRequest(BaseModel):
    event_type: str = Field(..., min_length=1, max_length=200)
    payload: dict[str, Any] = Field(default_factory=dict)
    correlation_id: Optional[str] = None
    source: str = "brain_api"
    memory_tier: Literal["short_term", "long_term", "agent", "system", "user"] = "system"
    dispatch_celery: bool = False
    lead_id: Optional[str] = None
    conversation_id: Optional[str] = None


@router.get("/health")
async def brain_health() -> dict[str, Any]:
    return brain_health_snapshot()


@router.get("/metrics")
async def brain_metrics() -> dict[str, Any]:
    return {"brain_metrics": metrics_snapshot()}


@router.get("/agents")
async def list_agents() -> dict[str, Any]:
    return {"agents": list_agent_profiles()}


@router.get("/skills")
async def list_skills() -> dict[str, Any]:
    return {
        "skills": [
            {
                "key": s.key,
                "description": s.description,
                "risk": s.risk.value,
                "required_permissions": list(s.required_permissions),
                "max_retries": s.max_retries,
                "timeout_seconds": s.timeout_seconds,
            }
            for s in SKILL_DEFINITIONS.values()
        ]
    }


@router.get("/profiles/{agent_key}")
async def get_profile(agent_key: str) -> dict[str, Any]:
    p = AGENT_PROFILES.get(agent_key)
    if not p:
        raise HTTPException(404, detail="unknown_agent")
    return {
        "key": p.key,
        "name": p.name,
        "name_ar": p.name_ar,
        "role": p.role,
        "responsibilities": list(p.responsibilities),
        "skills": list(p.skills),
        "memory_access": list(p.memory_access),
        "permissions": list(p.permissions),
        "behavior_rules": list(p.behavior_rules),
        "personality": p.personality,
        "execution_frequency": p.execution_frequency,
        "priority": p.priority,
    }


@router.post("/events")
async def post_brain_event(
    body: BrainEventRequest,
    db: AsyncSession = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
    user: User = Depends(get_current_user),
) -> dict[str, Any]:
    try:
        tier = MemoryTier(body.memory_tier)
    except ValueError as exc:
        raise HTTPException(422, detail="invalid memory_tier") from exc

    uid: UUID | None = user.id if tier == MemoryTier.USER else None
    result = await ingest_event(
        db,
        tenant_id=tenant.id,
        event_type=body.event_type,
        payload=body.payload,
        source=body.source,
        correlation_id=body.correlation_id,
        memory_tier=tier,
        user_id=uid,
    )
    if result.get("status") == "rate_limited":
        raise HTTPException(429, detail=result.get("detail", "rate_limited"))

    if body.dispatch_celery:
        brain_dispatch_agent_chain.delay(
            str(tenant.id),
            body.event_type,
            body.payload,
            lead_id=body.lead_id,
            conversation_id=body.conversation_id,
        )
        result["celery_dispatched"] = True
    return result


@router.get("/sessions")
async def list_brain_sessions(
    db: AsyncSession = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
    limit: int = 20,
) -> dict[str, Any]:
    q = await db.execute(
        select(BrainAgentSession)
        .where(BrainAgentSession.tenant_id == tenant.id)
        .order_by(desc(BrainAgentSession.created_at))
        .limit(min(limit, 100))
    )
    rows = q.scalars().all()
    return {
        "sessions": [
            {
                "id": str(r.id),
                "agent_key": r.agent_key,
                "state": r.state,
                "correlation_id": r.correlation_id,
                "created_at": r.created_at.isoformat() if r.created_at else None,
                "completed_at": r.completed_at.isoformat() if r.completed_at else None,
            }
            for r in rows
        ]
    }

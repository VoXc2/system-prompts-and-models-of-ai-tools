"""
Revenue Lead Engine — internal API (scoring, routing, ICP, learning).

Lawful B2B signals only; stakeholder rows are role templates, not fabricated persons.
"""

from __future__ import annotations

from typing import Any, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_tenant, require_role
from app.config import get_settings
from app.database import IS_SQLITE, get_db
from app.models.lead import Lead
from app.models.lead_engine import (
    LeadEngineICPProfile,
    LeadEngineRoutingDecision,
    LeadEngineScoreSnapshot,
    LeadEngineSourceEvent,
)
from app.models.tenant import Tenant
from app.models.user import User
from app.services.lead_engine.icp import DEFAULT_ICP_TEMPLATES
from app.services.lead_engine.orchestrator import record_outcome, recompute_lead

router = APIRouter(prefix="/lead-engine", tags=["Lead Engine"])
_role = require_role("owner", "admin", "manager")


def _lead_pk(lead_id: UUID) -> UUID | str:
    """SQLite stores UUIDs as VARCHAR; bind str to avoid aiosqlite UUID binding errors."""
    return str(lead_id) if IS_SQLITE else lead_id


def _gate() -> None:
    if not get_settings().DEALIX_LEAD_ENGINE_ENABLED:
        raise HTTPException(503, detail="Lead engine disabled")


class SourceEventIn(BaseModel):
    lead_id: Optional[UUID] = None
    source_system: str = Field(..., min_length=2, max_length=80)
    acquisition_method: str = Field(..., min_length=2, max_length=120)
    confidence: int = Field(70, ge=0, le=100)
    legal_basis: str = Field("contractual_vendor", max_length=80)
    dedup_key: Optional[str] = None
    payload: dict[str, Any] = Field(default_factory=dict)


class OutcomeIn(BaseModel):
    lead_id: Optional[UUID] = None
    event_type: str = Field(..., pattern="^(won|lost|no_response|meeting_booked|disqualified|duplicate)$")
    payload: dict[str, Any] = Field(default_factory=dict)


@router.post("/recompute/{lead_id}")
async def post_recompute(
    lead_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(_role),
) -> dict[str, Any]:
    _gate()
    lead = await db.get(Lead, _lead_pk(lead_id))
    if not lead or str(lead.tenant_id) != str(user.tenant_id):
        raise HTTPException(404, detail="lead_not_found")
    result = await recompute_lead(db, tenant_id=user.tenant_id, lead=lead)
    await db.commit()
    return result


@router.get("/intel/{lead_id}")
async def get_intel(
    lead_id: UUID,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(_role),
) -> dict[str, Any]:
    _gate()
    lid = _lead_pk(lead_id)
    q = await db.execute(
        select(LeadEngineScoreSnapshot)
        .where(LeadEngineScoreSnapshot.lead_id == lid, LeadEngineScoreSnapshot.tenant_id == user.tenant_id)
        .order_by(desc(LeadEngineScoreSnapshot.created_at))
        .limit(1)
    )
    snap = q.scalars().first()
    q2 = await db.execute(
        select(LeadEngineRoutingDecision)
        .where(LeadEngineRoutingDecision.lead_id == lid, LeadEngineRoutingDecision.tenant_id == user.tenant_id)
        .order_by(desc(LeadEngineRoutingDecision.created_at))
        .limit(1)
    )
    route = q2.scalars().first()
    return {
        "score": snap.total_score if snap else None,
        "priority_band": snap.priority_band if snap else None,
        "dimensions": snap.dimension_scores if snap else None,
        "reasons": snap.reason_codes if snap else [],
        "routing": {
            "motion": route.motion if route else None,
            "playbook_key": route.playbook_key if route else None,
        }
        if route
        else None,
    }


@router.get("/summary")
async def get_summary(
    db: AsyncSession = Depends(get_db),
    user: User = Depends(_role),
    limit: int = 40,
) -> dict[str, Any]:
    _gate()
    q = await db.execute(
        select(LeadEngineScoreSnapshot, Lead.id, Lead.name)
        .join(Lead, Lead.id == LeadEngineScoreSnapshot.lead_id)
        .where(
            LeadEngineScoreSnapshot.tenant_id == user.tenant_id,
            Lead.tenant_id == user.tenant_id,
        )
        .order_by(desc(LeadEngineScoreSnapshot.total_score))
        .limit(min(limit, 200))
    )
    rows = q.all()
    return {
        "top": [
            {
                "lead_id": str(lid),
                "name": name,
                "score": s.total_score,
                "band": s.priority_band,
            }
            for s, lid, name in rows
        ]
    }


@router.post("/icp/seed-defaults")
async def seed_icp(
    db: AsyncSession = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
    _auth: User = Depends(_role),
) -> dict[str, Any]:
    _gate()
    n = 0
    for t in DEFAULT_ICP_TEMPLATES:
        existing = await db.execute(
            select(LeadEngineICPProfile).where(
                LeadEngineICPProfile.tenant_id == tenant.id, LeadEngineICPProfile.slug == t["slug"]
            )
        )
        if existing.scalar_one_or_none():
            continue
        db.add(
            LeadEngineICPProfile(
                tenant_id=tenant.id,
                slug=t["slug"],
                name_ar=t["name_ar"],
                name_en=t.get("name_en"),
                config_json=t["config_json"],
                is_active=True,
            )
        )
        n += 1
    await db.commit()
    return {"profiles_created": n}


@router.post("/source-events")
async def post_source_event(
    body: SourceEventIn,
    db: AsyncSession = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
    _auth: User = Depends(_role),
) -> dict[str, Any]:
    _gate()
    row = LeadEngineSourceEvent(
        tenant_id=tenant.id,
        lead_id=str(body.lead_id) if body.lead_id and IS_SQLITE else body.lead_id,
        source_system=body.source_system,
        acquisition_method=body.acquisition_method,
        confidence=body.confidence,
        legal_basis=body.legal_basis,
        dedup_key=body.dedup_key,
        raw_payload=body.payload,
        status="ingested",
    )
    db.add(row)
    await db.commit()
    await db.refresh(row)
    return {"id": str(row.id), "status": row.status}


@router.post("/learning/outcome")
async def post_learning(
    body: OutcomeIn,
    db: AsyncSession = Depends(get_db),
    tenant: Tenant = Depends(get_current_tenant),
    _auth: User = Depends(_role),
) -> dict[str, Any]:
    _gate()
    await record_outcome(db, tenant_id=tenant.id, lead_id=body.lead_id, event_type=body.event_type, payload=body.payload)
    await db.commit()
    return {"status": "recorded"}

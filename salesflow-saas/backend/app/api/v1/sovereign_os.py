"""Sovereign OS control center and governed action contracts."""

from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_optional_user
from app.config import get_settings
from app.database import get_db
from app.models.user import User
from app.services.audit_service import count_audits_since
from app.services.operations_hub import count_events_since, count_pending_approvals
from app.services.sovereign_os import (
    GovernedActionRequest,
    build_control_center_snapshot,
    evaluate_governed_action,
    list_governed_action_policies,
    list_operating_surfaces,
    readiness_definition,
)

router = APIRouter(prefix="/sovereign-os", tags=["Sovereign OS"])
settings = get_settings()


@router.get("/control-center")
async def control_center(
    db: AsyncSession = Depends(get_db),
    user: Optional[User] = Depends(get_optional_user),
):
    """Unified operating picture across decision/execution/trust/data/operating planes."""
    runtime = {"demo_mode": True, "pending_approvals": 0, "domain_events_24h": 0, "audit_events_24h": 0}
    if user:
        runtime = {
            "demo_mode": False,
            "tenant_id": str(user.tenant_id),
            "pending_approvals": await count_pending_approvals(db, user.tenant_id),
            "domain_events_24h": await count_events_since(db, user.tenant_id, hours=24),
            "audit_events_24h": await count_audits_since(db, user.tenant_id, hours=24),
        }
    snapshot = build_control_center_snapshot(settings=settings, runtime=runtime)
    return snapshot.model_dump()


@router.get("/governed-actions")
async def governed_actions_catalog():
    """Catalog of action policies (auto, approval-gated, blocked)."""
    items = [policy.model_dump() for policy in list_governed_action_policies()]
    return {"count": len(items), "items": items}


@router.post("/governed-actions/evaluate")
async def evaluate_action(body: GovernedActionRequest):
    """Evaluate one action against approval/reversibility/sensitivity policy classes."""
    decision = evaluate_governed_action(body)
    return decision.model_dump()


@router.get("/readiness-definition")
async def enterprise_readiness_definition():
    """Machine-readable enterprise readiness definition for sovereign operations."""
    criteria = [item.model_dump() for item in readiness_definition()]
    surfaces = [item.model_dump() for item in list_operating_surfaces()]
    return {
        "criteria_count": len(criteria),
        "surface_count": len(surfaces),
        "criteria": criteria,
        "surfaces": surfaces,
    }

"""
Strategic Dashboard API — Dealix Sovereign Growth OS
════════════════════════════════════════════════════
Board-level executive endpoints for the Sovereign Growth Intelligence layer.
"""
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from app.database import get_db
from app.api.deps import get_current_user
from app.models.user import User

router = APIRouter()


@router.get("/brief")
async def get_executive_brief(
    period: str = Query("monthly", description="daily|weekly|monthly|quarterly"),
    current_user: User = Depends(get_current_user),
):
    """Generate a board-level strategic brief by invoking the Sovereign Growth Agent."""
    from app.agents.strategic.sovereign_growth import SovereignGrowthAgent

    agent = SovereignGrowthAgent()
    result = await agent.execute({
        "tenant_id": current_user.tenant_id,
        "reporting_period": period,
    })
    return result


@router.get("/events")
async def list_strategic_events(
    domain: Optional[str] = Query(None, description="partnership|ma|growth|governance|execution"),
    limit: int = Query(50, ge=1, le=500),
    current_user: User = Depends(get_current_user),
):
    """List recent strategic events, optionally filtered by domain."""
    from app.agents.strategic.events import get_strategic_event_bus, EventDomain

    bus = get_strategic_event_bus()
    domain_enum = EventDomain(domain) if domain else None
    events = bus.get_history(domain_enum, current_user.tenant_id, limit)
    return {
        "total": len(events),
        "events": [e.model_dump(mode="json") for e in events],
    }


@router.get("/pending-approvals")
async def list_pending_approvals(
    current_user: User = Depends(get_current_user),
):
    """List all strategic events awaiting human approval (HITL)."""
    from app.agents.strategic.events import get_strategic_event_bus

    bus = get_strategic_event_bus()
    pending = bus.get_pending_approvals(current_user.tenant_id)
    return {
        "total": len(pending),
        "items": [e.model_dump(mode="json") for e in pending],
    }


@router.post("/approve/{event_id}")
async def approve_event(
    event_id: str,
    decision: str = Query(..., description="approved|denied"),
    notes: str = Query(""),
    current_user: User = Depends(get_current_user),
):
    """Approve or deny a pending strategic event (HITL checkpoint)."""
    from app.agents.strategic.events import (
        get_strategic_event_bus, GovernanceEvent, GovernanceEventType,
    )

    bus = get_strategic_event_bus()
    event_type = (
        GovernanceEventType.APPROVAL_GRANTED.value
        if decision == "approved"
        else GovernanceEventType.APPROVAL_DENIED.value
    )

    gov_event = GovernanceEvent(
        tenant_id=current_user.tenant_id,
        event_type=event_type,
        agent_name="human",
        confidence=1.0,
        decided_by=current_user.email if hasattr(current_user, "email") else str(current_user.id),
        decision=decision,
        payload={"original_event_id": event_id, "notes": notes},
    )
    await bus.publish(gov_event)

    return {
        "status": decision,
        "event_id": event_id,
        "governance_event_id": str(gov_event.id),
    }


@router.get("/audit-log")
async def get_audit_log(
    limit: int = Query(100, ge=1, le=1000),
    current_user: User = Depends(get_current_user),
):
    """Retrieve the governance audit log."""
    from app.services.governance_engine import get_governance_engine

    engine = get_governance_engine()
    entries = engine.get_audit_log(current_user.tenant_id, limit)
    return {
        "total": len(entries),
        "entries": [e.model_dump(mode="json") for e in entries],
    }


@router.get("/pipeline")
async def get_growth_pipeline(
    current_user: User = Depends(get_current_user),
):
    """Aggregate revenue pipeline across partnerships, M&A, and expansion."""
    from app.agents.strategic.events import get_strategic_event_bus, EventDomain

    bus = get_strategic_event_bus()
    tenant = current_user.tenant_id

    partnerships = bus.get_history(EventDomain.PARTNERSHIP, tenant)
    ma = bus.get_history(EventDomain.MA, tenant)
    growth = bus.get_history(EventDomain.GROWTH, tenant)

    partnership_rev = sum(
        getattr(e, "estimated_revenue_impact_sar", 0) or 0
        for e in partnerships
    )
    ma_rev = sum(
        getattr(e, "synergy_estimate_sar", 0) or 0
        for e in ma
    )
    expansion_rev = sum(
        getattr(e, "expected_revenue_sar", 0) or 0
        for e in growth
    )

    return {
        "partnerships": {"events": len(partnerships), "pipeline_sar": partnership_rev},
        "ma": {"events": len(ma), "pipeline_sar": ma_rev},
        "expansion": {"events": len(growth), "pipeline_sar": expansion_rev},
        "total_pipeline_sar": partnership_rev + ma_rev + expansion_rev,
    }


@router.get("/kpis")
async def get_strategic_kpis(
    current_user: User = Depends(get_current_user),
):
    """Key performance indicators for the Sovereign Growth OS."""
    from app.agents.strategic.events import get_strategic_event_bus, EventDomain, ExecutionEventType

    bus = get_strategic_event_bus()
    tenant = current_user.tenant_id
    all_events = bus.get_history(tenant_id=tenant, limit=9999)
    pending = bus.get_pending_approvals(tenant)
    execution = bus.get_history(EventDomain.EXECUTION, tenant)

    sla_breaches = [e for e in execution if e.event_type == ExecutionEventType.SLA_BREACHED.value]
    initiatives = [e for e in execution if e.event_type == ExecutionEventType.INITIATIVE_CREATED.value]

    return {
        "total_events": len(all_events),
        "pending_decisions": len(pending),
        "active_initiatives": len(initiatives),
        "sla_breaches": len(sla_breaches),
        "events_by_domain": {
            d.value: len([e for e in all_events if e.domain == d])
            for d in EventDomain
        },
    }

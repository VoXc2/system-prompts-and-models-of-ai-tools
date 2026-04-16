"""Trust Plane API — Policy violations, tool verification ledger, contradiction engine."""
from __future__ import annotations

from typing import Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database import get_db
from app.services.trust_plane import TrustPlaneService
from app.services.contradiction_engine import ContradictionEngine
from app.models.sovereign import ToolVerificationLedger

router = APIRouter(prefix="/trust-plane", tags=["Trust Plane — طبقة الثقة"])


class GateActionRequest(BaseModel):
    user_id: str
    role: str
    action: str
    approval_class: str = "B"
    resource_type: str = ""
    resource_id: str | None = None


class ViolationRecord(BaseModel):
    violation_type: str
    severity: str = "medium"
    description_ar: str
    resource_type: str = ""
    resource_id: str | None = None
    triggered_by_id: str | None = None
    policy_ref: str = ""
    remediation_ar: str = ""


class ToolCallRecord(BaseModel):
    agent_role: str
    tool_name: str
    intended_action: str
    claimed_action: str
    actual_tool_call: dict[str, Any]
    side_effects: list[Any] | None = None
    correlation_id: str | None = None
    trace_id: str | None = None
    span_id: str | None = None
    latency_ms: int | None = None
    outcome: str = "success"


class ContradictionResolve(BaseModel):
    resolution_notes: str
    false_positive: bool = False


@router.post("/gate-action")
async def gate_action(
    tenant_id: str,
    payload: GateActionRequest,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """بوابة الإجراء — Evaluate if an action is allowed by policy + authorization."""
    svc = TrustPlaneService(db)
    return await svc.gate_action(
        tenant_id=tenant_id,
        user_id=payload.user_id,
        role=payload.role,
        action=payload.action,
        approval_class=payload.approval_class,
        resource_type=payload.resource_type,
        resource_id=payload.resource_id,
    )


@router.post("/violations", status_code=status.HTTP_201_CREATED)
async def record_violation(
    tenant_id: str,
    payload: ViolationRecord,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    svc = TrustPlaneService(db)
    violation_id = await svc.record_violation(
        tenant_id=tenant_id,
        violation_type=payload.violation_type,
        severity=payload.severity,
        description_ar=payload.description_ar,
        resource_type=payload.resource_type,
        resource_id=payload.resource_id,
        triggered_by_id=payload.triggered_by_id,
        policy_ref=payload.policy_ref,
        remediation_ar=payload.remediation_ar,
    )
    return {"id": violation_id}


@router.get("/violations")
async def list_violations(
    tenant_id: str,
    resolved: bool = False,
    severity: str | None = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    """لوحة انتهاكات السياسة — Policy violations board."""
    svc = TrustPlaneService(db)
    return await svc.list_violations(tenant_id, resolved=resolved, severity=severity, limit=limit)


@router.post("/violations/{violation_id}/resolve")
async def resolve_violation(
    violation_id: str,
    tenant_id: str,
    resolver_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    svc = TrustPlaneService(db)
    return await svc.resolve_violation(tenant_id, violation_id, resolver_id)


@router.post("/tool-ledger", status_code=status.HTTP_201_CREATED)
async def record_tool_call(
    tenant_id: str,
    payload: ToolCallRecord,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """سجل التحقق من الأدوات — Record tool execution in verification ledger."""
    engine = ContradictionEngine(db)
    ledger, contradiction = await engine.record_tool_call(
        tenant_id=tenant_id,
        agent_role=payload.agent_role,
        tool_name=payload.tool_name,
        intended_action=payload.intended_action,
        claimed_action=payload.claimed_action,
        actual_tool_call=payload.actual_tool_call,
        side_effects=payload.side_effects,
        correlation_id=payload.correlation_id,
        trace_id=payload.trace_id,
        span_id=payload.span_id,
        latency_ms=payload.latency_ms,
        outcome=payload.outcome,
    )
    return {
        "ledger_id": str(ledger.id),
        "contradiction_id": str(contradiction.id) if contradiction else None,
        "contradiction_detected": contradiction is not None,
        "contradiction_type": contradiction.contradiction_type if contradiction else None,
    }


@router.get("/tool-ledger")
async def list_tool_ledger(
    tenant_id: str,
    agent_role: str | None = None,
    tool_name: str | None = None,
    limit: int = 50,
    db: AsyncSession = Depends(get_db),
) -> list[dict[str, Any]]:
    q = select(ToolVerificationLedger).where(
        ToolVerificationLedger.tenant_id == tenant_id,
    )
    if agent_role:
        q = q.where(ToolVerificationLedger.agent_role == agent_role)
    if tool_name:
        q = q.where(ToolVerificationLedger.tool_name == tool_name)
    q = q.order_by(ToolVerificationLedger.created_at.desc()).limit(limit)
    result = await db.execute(q)
    rows = result.scalars().all()
    return [
        {
            "id": str(r.id),
            "agent_role": r.agent_role,
            "tool_name": r.tool_name,
            "contradiction_status": r.contradiction_status,
            "outcome": r.outcome,
            "correlation_id": r.correlation_id,
            "trace_id": r.trace_id,
            "latency_ms": r.latency_ms,
            "created_at": r.created_at.isoformat() if r.created_at else None,
        }
        for r in rows
    ]


@router.get("/contradictions")
async def contradiction_dashboard(
    tenant_id: str,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    """لوحة التناقضات — Contradiction dashboard."""
    engine = ContradictionEngine(db)
    return await engine.get_dashboard(tenant_id)


@router.post("/contradictions/{contradiction_id}/resolve")
async def resolve_contradiction(
    contradiction_id: str,
    tenant_id: str,
    payload: ContradictionResolve,
    db: AsyncSession = Depends(get_db),
) -> dict[str, Any]:
    engine = ContradictionEngine(db)
    return await engine.resolve(
        tenant_id, contradiction_id, payload.resolution_notes, payload.false_positive
    )

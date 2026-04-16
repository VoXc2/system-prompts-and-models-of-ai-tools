"""Sovereign OS APIs: approval center, commitments, verification ledger."""

from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional
from uuid import UUID, uuid4

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user, get_optional_user, require_role
from app.database import get_db
from app.models.operations import ApprovalRequest, DomainEvent
from app.models.user import User
from app.services.operations_hub import emit_domain_event
from app.services.tool_receipts import (
    PolicyDecisionType,
    ToolReceipt,
    VerificationVerdict,
    pre_execution_policy,
    receipt_store,
    trust_analytics,
)

router = APIRouter(prefix="/sovereign", tags=["Sovereign OS"])


class DomainName(str, Enum):
    SALES = "sales"
    PARTNERSHIP = "partnership"
    MNA = "mna"
    EXPANSION = "expansion"
    PMI = "pmi"
    EXECUTIVE = "executive"


class ApprovalClass(str, Enum):
    A0 = "A0"
    A1 = "A1"
    A2 = "A2"
    A3 = "A3"


class ReversibilityClass(str, Enum):
    R0 = "R0"
    R1 = "R1"
    R2 = "R2"
    R3 = "R3"


class SensitivityClass(str, Enum):
    S0 = "S0"
    S1 = "S1"
    S2 = "S2"
    S3 = "S3"


class WorkflowState(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    WAITING_APPROVAL = "waiting_approval"
    BLOCKED = "blocked"
    RETRYING = "retrying"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class ExecutionStatus(str, Enum):
    SUCCESS = "success"
    FAILED = "failed"
    BLOCKED = "blocked"


class LedgerPolicyDecision(str, Enum):
    ALLOW = "allow"
    DENY = "deny"
    NEEDS_APPROVAL = "needs_approval"


class ApprovalCreateRequest(BaseModel):
    domain: DomainName
    decision_type: str = Field(min_length=3)
    channel: str = "email"
    resource_type: str = "sovereign_decision"
    resource_id: Optional[UUID] = None
    approval_class: ApprovalClass
    reversibility_class: ReversibilityClass
    sensitivity_class: SensitivityClass
    policy_refs: List[str] = Field(default_factory=list)
    evidence_pack_id: str = Field(min_length=6)
    notes: Optional[str] = Field(default=None, max_length=5000)
    trace_id: Optional[str] = Field(default=None, min_length=8)
    correlation_id: Optional[str] = Field(default=None, min_length=8)


class ApprovalResolveRequest(BaseModel):
    approve: bool
    note: Optional[str] = Field(default=None, max_length=2000)
    trace_id: Optional[str] = Field(default=None, min_length=8)
    correlation_id: Optional[str] = Field(default=None, min_length=8)


class WorkflowCommitmentUpsertRequest(BaseModel):
    workflow_commitment_id: Optional[str] = Field(default=None, min_length=8)
    domain: DomainName
    workflow_type: str = Field(min_length=3)
    state: WorkflowState
    owner: str = Field(min_length=3)
    depends_on: List[str] = Field(default_factory=list)
    sla_hours: int = Field(ge=1)
    escalation_after_hours: Optional[int] = Field(default=None, ge=1)
    requires_durable_runtime: bool
    approval_request_id: Optional[str] = Field(default=None, min_length=8)
    policy_refs: List[str] = Field(default_factory=list)
    evidence_pack_id: Optional[str] = Field(default=None, min_length=6)
    trace_id: Optional[str] = Field(default=None, min_length=8)
    correlation_id: Optional[str] = Field(default=None, min_length=8)


class ToolReceiptCreateRequest(BaseModel):
    tool_name: str = Field(min_length=2)
    tool_operation: str = Field(min_length=2)
    execution_status: ExecutionStatus
    policy_decision: LedgerPolicyDecision
    policy_refs: List[str] = Field(default_factory=list)
    approval_request_id: Optional[str] = Field(default=None, min_length=8)
    input_hash: Optional[str] = Field(default=None, min_length=16)
    output_hash: Optional[str] = Field(default=None, min_length=16)
    evidence_pack_id: Optional[str] = Field(default=None, min_length=6)
    error_message: Optional[str] = Field(default=None, max_length=2000)
    verified_at: Optional[datetime] = None
    trace_id: Optional[str] = Field(default=None, min_length=8)
    correlation_id: Optional[str] = Field(default=None, min_length=8)
    cost_estimate: float = Field(default=0.0, ge=0.0)


def _utc_now() -> datetime:
    return datetime.now(timezone.utc)


def _approval_payload(row: ApprovalRequest) -> Dict[str, Any]:
    payload = row.payload if isinstance(row.payload, dict) else {}
    return {
        "approval_id": str(row.id),
        "approval_request_id": str(row.id),
        "tenant_id": str(row.tenant_id),
        "domain": payload.get("domain"),
        "decision_type": payload.get("decision_type"),
        "channel": row.channel,
        "resource_type": row.resource_type,
        "resource_id": str(row.resource_id),
        "approval_class": payload.get("approval_class"),
        "reversibility_class": payload.get("reversibility_class"),
        "sensitivity_class": payload.get("sensitivity_class"),
        "policy_refs": payload.get("policy_refs", []),
        "evidence_pack_id": payload.get("evidence_pack_id"),
        "trace_id": payload.get("trace_id"),
        "correlation_id": payload.get("correlation_id"),
        "status": row.status,
        "requested_by_id": str(row.requested_by_id),
        "requested_at": row.created_at.isoformat() if row.created_at else None,
        "reviewed_by_id": str(row.reviewed_by_id) if row.reviewed_by_id else None,
        "reviewed_at": row.reviewed_at.isoformat() if row.reviewed_at else None,
        "note": row.note,
        "notes": payload.get("notes"),
    }


def _ensure_trace(value: Optional[str]) -> str:
    return value or f"trace-{uuid4().hex}"


def _ensure_correlation(value: Optional[str]) -> str:
    return value or f"corr-{uuid4().hex}"


async def _list_workflow_commitments(
    db: AsyncSession,
    tenant_id: UUID,
    limit: int = 500,
) -> List[Dict[str, Any]]:
    result = await db.execute(
        select(DomainEvent)
        .where(
            DomainEvent.tenant_id == tenant_id,
            DomainEvent.event_type == "sovereign.workflow_commitment.upserted",
        )
        .order_by(DomainEvent.created_at.desc())
        .limit(limit)
    )
    latest: Dict[str, Dict[str, Any]] = {}
    for row in result.scalars().all():
        payload = row.payload if isinstance(row.payload, dict) else {}
        commitment_id = payload.get("workflow_commitment_id")
        if not commitment_id or commitment_id in latest:
            continue
        latest[commitment_id] = payload
    return list(latest.values())


def _policy_decision_to_receipt(value: LedgerPolicyDecision) -> PolicyDecisionType:
    if value == LedgerPolicyDecision.ALLOW:
        return PolicyDecisionType.ALLOW
    if value == LedgerPolicyDecision.DENY:
        return PolicyDecisionType.BLOCK
    return PolicyDecisionType.HOLD


def _receipt_verdict(
    execution_status: ExecutionStatus,
    policy_decision: LedgerPolicyDecision,
) -> VerificationVerdict:
    if execution_status == ExecutionStatus.BLOCKED or policy_decision == LedgerPolicyDecision.DENY:
        return VerificationVerdict.BLOCKED
    if execution_status == ExecutionStatus.FAILED:
        return VerificationVerdict.CONTRADICTED
    if policy_decision == LedgerPolicyDecision.NEEDS_APPROVAL:
        return VerificationVerdict.PARTIALLY_VERIFIED
    return VerificationVerdict.VERIFIED


@router.get("/snapshot")
async def sovereign_snapshot(user: Optional[User] = Depends(get_optional_user)):
    if not user:
        return {
            "demo_mode": True,
            "surfaces": {
                "approval_center": "available",
                "workflow_commitments": "available",
                "tool_verification_ledger": "available",
            },
            "contracts": {
                "approval_request": "active",
                "workflow_commitment": "active",
                "tool_verification_receipt": "active",
            },
        }
    return {
        "demo_mode": False,
        "tenant_id": str(user.tenant_id),
        "surfaces": {
            "approval_center": "live",
            "workflow_commitments": "live",
            "tool_verification_ledger": "live",
        },
        "contracts": {
            "approval_request": "active",
            "workflow_commitment": "active",
            "tool_verification_receipt": "active",
        },
    }


@router.post("/approvals")
async def create_approval(
    body: ApprovalCreateRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if not body.policy_refs:
        raise HTTPException(status_code=422, detail="policy_refs must include at least one policy")

    trace_id = _ensure_trace(body.trace_id)
    correlation_id = _ensure_correlation(body.correlation_id)
    payload = {
        "domain": body.domain.value,
        "decision_type": body.decision_type,
        "approval_class": body.approval_class.value,
        "reversibility_class": body.reversibility_class.value,
        "sensitivity_class": body.sensitivity_class.value,
        "policy_refs": body.policy_refs,
        "evidence_pack_id": body.evidence_pack_id,
        "notes": body.notes,
        "trace_id": trace_id,
        "correlation_id": correlation_id,
    }
    row = ApprovalRequest(
        tenant_id=user.tenant_id,
        channel=body.channel,
        resource_type=body.resource_type,
        resource_id=body.resource_id or uuid4(),
        payload=payload,
        status="pending",
        requested_by_id=user.id,
    )
    db.add(row)
    await db.flush()
    await emit_domain_event(
        db,
        tenant_id=user.tenant_id,
        event_type="sovereign.approval.requested",
        payload={
            "approval_id": str(row.id),
            "decision_type": body.decision_type,
            "approval_class": body.approval_class.value,
        },
        source="api",
        correlation_id=correlation_id,
    )
    return _approval_payload(row)


@router.get("/approvals")
async def list_approvals(
    status: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("owner", "admin", "manager")),
):
    query = select(ApprovalRequest).where(ApprovalRequest.tenant_id == user.tenant_id)
    if status:
        query = query.where(ApprovalRequest.status == status)
    query = query.order_by(ApprovalRequest.created_at.desc()).limit(200)
    result = await db.execute(query)
    items = [_approval_payload(row) for row in result.scalars().all()]
    return {"items": items, "count": len(items)}


@router.put("/approvals/{approval_id}/resolve")
async def resolve_approval(
    approval_id: UUID,
    body: ApprovalResolveRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("owner", "admin", "manager")),
):
    result = await db.execute(
        select(ApprovalRequest).where(
            ApprovalRequest.id == approval_id,
            ApprovalRequest.tenant_id == user.tenant_id,
        )
    )
    row = result.scalar_one_or_none()
    if not row:
        raise HTTPException(status_code=404, detail="Approval not found")
    if row.status != "pending":
        raise HTTPException(status_code=400, detail="Approval is not pending")

    row.status = "approved" if body.approve else "rejected"
    row.reviewed_by_id = user.id
    row.reviewed_at = _utc_now()
    row.note = body.note
    await db.flush()
    await emit_domain_event(
        db,
        tenant_id=user.tenant_id,
        event_type="sovereign.approval.resolved",
        payload={
            "approval_id": str(row.id),
            "status": row.status,
            "trace_id": body.trace_id,
            "correlation_id": body.correlation_id,
        },
        source="api",
        correlation_id=body.correlation_id,
    )
    return _approval_payload(row)


@router.put("/approvals/{approval_id}")
async def resolve_approval_legacy(
    approval_id: UUID,
    body: ApprovalResolveRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("owner", "admin", "manager")),
):
    return await resolve_approval(approval_id=approval_id, body=body, db=db, user=user)


@router.post("/workflow-commitments")
async def upsert_workflow_commitment(
    body: WorkflowCommitmentUpsertRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("owner", "admin", "manager")),
):
    workflow_commitment_id = body.workflow_commitment_id or f"wfc-{uuid4().hex}"
    trace_id = _ensure_trace(body.trace_id)
    correlation_id = _ensure_correlation(body.correlation_id)
    existing_items = await _list_workflow_commitments(db, user.tenant_id, limit=1000)
    existing = next(
        (x for x in existing_items if x.get("workflow_commitment_id") == workflow_commitment_id),
        None,
    )
    now_iso = _utc_now().isoformat()
    payload = body.model_dump()
    payload["workflow_commitment_id"] = workflow_commitment_id
    payload["domain"] = body.domain.value
    payload["state"] = body.state.value
    payload["trace_id"] = trace_id
    payload["correlation_id"] = correlation_id
    payload["tenant_id"] = str(user.tenant_id)
    payload["updated_by"] = str(user.id)
    payload["updated_at"] = now_iso
    payload["created_at"] = (existing or {}).get("created_at", now_iso)

    await emit_domain_event(
        db,
        tenant_id=user.tenant_id,
        event_type="sovereign.workflow_commitment.upserted",
        payload=payload,
        source="api",
        correlation_id=correlation_id,
    )
    return payload


@router.get("/workflow-commitments")
async def list_workflow_commitments(
    domain: Optional[DomainName] = None,
    state: Optional[WorkflowState] = None,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("owner", "admin", "manager")),
):
    items = await _list_workflow_commitments(db, user.tenant_id, limit=max(limit * 5, 200))
    if domain:
        items = [x for x in items if x.get("domain") == domain.value]
    if state:
        items = [x for x in items if x.get("state") == state.value]
    items = sorted(items, key=lambda x: x.get("updated_at") or "", reverse=True)[:limit]
    return {"items": items, "count": len(items)}


@router.post("/tool-verification-ledger/receipts")
async def create_tool_receipt(
    body: ToolReceiptCreateRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("owner", "admin", "manager")),
):
    trace_id = _ensure_trace(body.trace_id)
    correlation_id = _ensure_correlation(body.correlation_id)
    policy_eval = pre_execution_policy.evaluate(
        body.tool_name,
        {"count": 1},
        {
            "role": user.role,
            "session_id": correlation_id,
            "user_id": str(user.id),
            "has_consent": True,
        },
    )
    verdict = _receipt_verdict(body.execution_status, body.policy_decision)
    receipt = ToolReceipt(
        run_id=trace_id,
        session_id=correlation_id,
        agent_id=str(user.id),
        tool_name=body.tool_name,
        parameters={"operation": body.tool_operation},
        execution_result=body.execution_status.value,
        policy_decision=_policy_decision_to_receipt(body.policy_decision),
        verification_verdict=verdict,
        cost_estimate=body.cost_estimate,
        tenant_id=str(user.tenant_id),
    )
    if body.error_message:
        receipt.execution_result = f"{receipt.execution_result}: {body.error_message}"
    receipt_id = receipt_store.store(receipt)

    payload = body.model_dump(mode="json")
    payload["receipt_id"] = receipt_id
    payload["trace_id"] = trace_id
    payload["correlation_id"] = correlation_id
    payload["verification_verdict"] = verdict.value
    payload["tenant_id"] = str(user.tenant_id)
    payload["policy_alignment"] = {
        "runtime_decision": body.policy_decision.value,
        "pre_execution_decision": policy_eval.decision.value,
    }
    payload["verified_at"] = (body.verified_at or _utc_now()).isoformat()

    await emit_domain_event(
        db,
        tenant_id=user.tenant_id,
        event_type="sovereign.tool_receipt.recorded",
        payload=payload,
        source="api",
        correlation_id=correlation_id,
    )
    return payload


@router.get("/tool-verification-ledger/receipts")
async def list_tool_receipts(
    tool_name: Optional[str] = None,
    execution_status: Optional[ExecutionStatus] = None,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("owner", "admin", "manager")),
):
    result = await db.execute(
        select(DomainEvent)
        .where(
            DomainEvent.tenant_id == user.tenant_id,
            DomainEvent.event_type == "sovereign.tool_receipt.recorded",
        )
        .order_by(DomainEvent.created_at.desc())
        .limit(max(limit * 3, 300))
    )
    items: List[Dict[str, Any]] = []
    for row in result.scalars().all():
        payload = row.payload if isinstance(row.payload, dict) else {}
        if tool_name and payload.get("tool_name") != tool_name:
            continue
        if execution_status and payload.get("execution_status") != execution_status.value:
            continue
        items.append(payload)
        if len(items) >= limit:
            break
    return {"items": items, "count": len(items)}


@router.post("/tool-verification-ledger")
async def create_tool_receipt_legacy(
    body: ToolReceiptCreateRequest,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("owner", "admin", "manager")),
):
    return await create_tool_receipt(body=body, db=db, user=user)


@router.get("/tool-verification-ledger")
async def list_tool_receipts_legacy(
    tool_name: Optional[str] = None,
    execution_status: Optional[ExecutionStatus] = None,
    limit: int = 100,
    db: AsyncSession = Depends(get_db),
    user: User = Depends(require_role("owner", "admin", "manager")),
):
    return await list_tool_receipts(
        tool_name=tool_name,
        execution_status=execution_status,
        limit=limit,
        db=db,
        user=user,
    )


@router.get("/tool-verification-ledger/summary")
async def tool_verification_summary(
    user: User = Depends(require_role("owner", "admin", "manager")),
):
    return {
        "tenant_id": str(user.tenant_id),
        "agent_summary": trust_analytics.get_summary(agent_id=str(user.id)),
        "tenant_hint": (
            "Summary currently reflects in-process receipts for this agent session. "
            "Use /receipts endpoint for tenant-level persisted ledger entries."
        ),
    }

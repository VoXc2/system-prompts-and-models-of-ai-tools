"""Sovereign Growth, Execution & Governance OS — Unified API."""
from __future__ import annotations
from typing import Any
from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from app.services.sovereign import sovereign_os

router = APIRouter(prefix="/sovereign-os", tags=["Sovereign OS"])


class InitResponse(BaseModel):
    status: str
    planes: list[str] = []
    os_modules: list[str] = []
    workflow_definitions_registered: int = 0
    event_types_cataloged: int = 0


class DecisionCreateRequest(BaseModel):
    title: str
    title_ar: str = ""
    os_module: str
    summary: str = ""
    summary_ar: str = ""
    action: str = ""
    created_by: str = ""
    financial_impact_sar: float = 0.0
    risk_level: str = "low"


class DecisionProposeRequest(BaseModel):
    recommended_action: str
    recommended_action_ar: str = ""


class DecisionApproveRequest(BaseModel):
    approved_by: str
    evidence_pack_id: str | None = None


class WorkflowStartRequest(BaseModel):
    workflow_name: str
    tenant_id: str
    context: dict[str, Any] = Field(default_factory=dict)


class StepApprovalRequest(BaseModel):
    step_id: str
    approved_by: str
    evidence_pack_id: str | None = None


class StepRejectRequest(BaseModel):
    step_id: str
    rejected_by: str
    reason: str = ""


class PolicyEvalRequest(BaseModel):
    action: str
    actor: dict[str, Any] = Field(default_factory=dict)
    resource: dict[str, Any] = Field(default_factory=dict)
    context: dict[str, Any] | None = None


class EvidenceAssembleRequest(BaseModel):
    decision_ref: str
    items: list[dict[str, Any]] = Field(default_factory=list)
    assembled_by: str
    approval_class: str = "R0_AUTO"


class EventEmitRequest(BaseModel):
    event_type: str
    source: str
    data: dict[str, Any] = Field(default_factory=dict)
    tenant_id: str = ""
    os_module: str = ""


# ── System ─────────────────────────────────────────────────────

@router.post("/initialize", response_model=InitResponse)
async def initialize_os():
    result = sovereign_os.initialize()
    return InitResponse(**result)


@router.get("/status")
async def os_status():
    return {
        "initialized": sovereign_os._initialized,
        "planes": ["decision", "execution", "trust", "data", "operating"],
        "os_modules": sovereign_os.OS_MODULES,
    }


# ── Decision Plane ─────────────────────────────────────────────

@router.post("/decisions")
async def create_decision(req: DecisionCreateRequest):
    from app.planes.decision.structured_decision import DecisionImpact
    decision = sovereign_os.create_decision(
        title=req.title,
        os_module=req.os_module,
        created_by=req.created_by,
        title_ar=req.title_ar,
        summary=req.summary,
        summary_ar=req.summary_ar,
        action=req.action,
        impact=DecisionImpact(financial_sar=req.financial_impact_sar, risk_level=req.risk_level),
    )
    return decision.model_dump()


@router.post("/decisions/{decision_id}/propose")
async def propose_decision(decision_id: str, req: DecisionProposeRequest):
    decision = sovereign_os.propose_decision(decision_id, req.recommended_action, req.recommended_action_ar)
    return decision.model_dump()


@router.post("/decisions/{decision_id}/approve")
async def approve_decision(decision_id: str, req: DecisionApproveRequest):
    decision = sovereign_os.approve_decision(decision_id, req.approved_by, req.evidence_pack_id)
    return decision.model_dump()


@router.get("/decisions")
async def list_decisions(os_module: str = Query(default="")):
    if os_module:
        decisions = sovereign_os.decision_engine.list_by_module(os_module)
    else:
        decisions = list(sovereign_os.decision_engine._decisions.values())
    return [d.model_dump() for d in decisions]


@router.get("/decisions/pending")
async def list_pending_decisions():
    decisions = sovereign_os.decision_engine.list_pending()
    return [d.model_dump() for d in decisions]


# ── Execution Plane ────────────────────────────────────────────

@router.post("/workflows/start")
async def start_workflow(req: WorkflowStartRequest):
    instance = sovereign_os.start_workflow(req.workflow_name, req.tenant_id, req.context)
    return instance.model_dump()


@router.post("/workflows/{instance_id}/approve")
async def approve_step(instance_id: str, req: StepApprovalRequest):
    instance = sovereign_os.approve_workflow_step(instance_id, req.step_id, req.approved_by, req.evidence_pack_id)
    return instance.model_dump()


@router.post("/workflows/{instance_id}/reject")
async def reject_step(instance_id: str, req: StepRejectRequest):
    instance = sovereign_os.reject_workflow_step(instance_id, req.step_id, req.rejected_by, req.reason)
    return instance.model_dump()


@router.get("/workflows/{instance_id}")
async def get_workflow(instance_id: str):
    instance = sovereign_os.workflow_engine.get_instance(instance_id)
    if not instance:
        return {"error": "Instance not found"}
    return instance.model_dump()


@router.get("/approvals/pending")
async def pending_approvals(tenant_id: str = Query(default="")):
    return sovereign_os.list_pending_approvals(tenant_id or None)


# ── Trust Plane ────────────────────────────────────────────────

@router.post("/policy/evaluate")
async def evaluate_policy(req: PolicyEvalRequest):
    result = sovereign_os.evaluate_policy(req.action, req.actor, req.resource, req.context)
    return result.model_dump()


@router.post("/evidence/assemble")
async def assemble_evidence(req: EvidenceAssembleRequest):
    pack = sovereign_os.assemble_evidence(req.decision_ref, req.items, req.assembled_by, req.approval_class)
    return pack.model_dump()


@router.get("/compliance")
async def get_compliance(tenant_id: str = Query(default="")):
    matrix = sovereign_os.check_compliance(tenant_id)
    return matrix.model_dump()


# ── Data Plane ─────────────────────────────────────────────────

@router.post("/events/emit")
async def emit_event(req: EventEmitRequest):
    event = sovereign_os.emit_event(req.event_type, req.source, req.data, req.tenant_id, req.os_module)
    return event.model_dump()


@router.get("/events/catalog")
async def event_catalog():
    return sovereign_os.get_event_catalog()


@router.get("/events/log")
async def event_log(limit: int = Query(default=100, ge=1, le=1000)):
    return sovereign_os.get_event_log(limit)


# ── Operating / Executive ──────────────────────────────────────

@router.get("/model-routing")
async def model_routing_dashboard():
    return sovereign_os.get_model_routing_dashboard()


@router.get("/model-routing/select")
async def select_model(task_type: str = Query(...)):
    return sovereign_os.select_model(task_type)


@router.get("/executive/dashboard")
async def executive_dashboard(tenant_id: str = Query(default="default")):
    return sovereign_os.get_executive_dashboard(tenant_id)


@router.get("/executive/risk-heatmap")
async def risk_heatmap(tenant_id: str = Query(default="default")):
    return sovereign_os.get_risk_heatmap(tenant_id)


@router.get("/executive/policy-violations")
async def policy_violations(tenant_id: str = Query(default="default")):
    return sovereign_os.get_policy_violations(tenant_id)

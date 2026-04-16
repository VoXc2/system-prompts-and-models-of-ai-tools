"""Sovereign OS Service — Unified orchestration across all planes and modules."""
from __future__ import annotations
from datetime import datetime, timezone
from typing import Any

from app.planes.decision.structured_decision import (
    DecisionEngine, StructuredDecision, DecisionImpact, DecisionAlternative, decision_engine,
)
from app.planes.execution.workflow_engine import (
    DurableWorkflowEngine, WorkflowInstance, workflow_engine,
)
from app.planes.execution.workflow_definitions import register_all_workflows
from app.planes.trust.approval_classes import (
    ApprovalClass, evaluate_action, PolicyGateResult,
)
from app.planes.trust.evidence_pack import assemble_evidence_pack, EvidencePack
from app.planes.trust.policy_engine import PolicyEngine
from app.planes.trust.tool_verification import ToolVerificationLedger
from app.planes.data.event_contracts import emit_cloud_event, CloudEvent, EVENT_CATALOG
from app.planes.data.quality_gate import DataQualityGate, data_quality_gate
from app.planes.operating.release_governance import (
    ReleaseGovernance, ComplianceMatrix, release_governance,
)
from app.planes.decision.model_router import ModelRoutingFabric, model_routing_fabric


class SovereignOSService:
    """Central orchestrator for the Dealix Sovereign OS.
    
    Exposes unified methods that coordinate across Decision, Execution,
    Trust, Data, and Operating planes for all 6 OS modules:
    Sales, Partnership, M&A, Expansion, PMI, Executive.
    """

    OS_MODULES = ["sales", "partnership", "ma", "expansion", "pmi", "executive"]

    def __init__(self):
        self.decision_engine: DecisionEngine = decision_engine
        self.workflow_engine: DurableWorkflowEngine = workflow_engine
        self.policy_engine: PolicyEngine = PolicyEngine()
        self.tool_ledger: ToolVerificationLedger = ToolVerificationLedger()
        self.data_quality: DataQualityGate = data_quality_gate
        self.release_gov: ReleaseGovernance = release_governance
        self.model_router: ModelRoutingFabric = model_routing_fabric
        self._event_log: list[CloudEvent] = []
        self._initialized = False

    def initialize(self) -> dict[str, Any]:
        if self._initialized:
            return {"status": "already_initialized"}
        register_all_workflows(self.workflow_engine)
        self._initialized = True
        return {
            "status": "initialized",
            "planes": ["decision", "execution", "trust", "data", "operating"],
            "os_modules": self.OS_MODULES,
            "workflow_definitions_registered": len(self.workflow_engine._definitions),
            "event_types_cataloged": len(EVENT_CATALOG),
        }

    # ── Decision Plane ──────────────────────────────────────────

    def create_decision(
        self,
        title: str,
        os_module: str,
        created_by: str,
        **kwargs: Any,
    ) -> StructuredDecision:
        gate = evaluate_action(kwargs.get("action", ""), kwargs.get("context"))
        return self.decision_engine.create_decision(
            title=title,
            os_module=os_module,
            created_by=created_by,
            approval_class=gate.approval_class.value,
            reversibility=gate.reversibility.value,
            sensitivity=gate.sensitivity.value,
            **{k: v for k, v in kwargs.items() if k not in ("action", "context")},
        )

    def propose_decision(self, decision_id: str, recommended_action: str, recommended_action_ar: str = "") -> StructuredDecision:
        return self.decision_engine.propose(decision_id, recommended_action, recommended_action_ar)

    def approve_decision(self, decision_id: str, approved_by: str, evidence_pack_id: str | None = None) -> StructuredDecision:
        decision = self.decision_engine.approve(decision_id, approved_by, evidence_pack_id)
        self._emit("com.dealix.approval.granted", "dealix/decision-plane", {
            "decision_id": decision_id, "approved_by": approved_by,
        }, os_module=decision.os_module)
        return decision

    # ── Execution Plane ─────────────────────────────────────────

    def start_workflow(self, workflow_name: str, tenant_id: str, context: dict | None = None) -> WorkflowInstance:
        for wid, defn in self.workflow_engine._definitions.items():
            if defn.name == workflow_name:
                instance = self.workflow_engine.start_workflow(wid, tenant_id, context)
                self._emit("com.dealix.approval.requested" if instance.status.value.startswith("paused") else "com.dealix.lead.captured",
                    f"dealix/{defn.os_module}-os", {"instance_id": instance.instance_id, "workflow": workflow_name},
                    tenant_id=tenant_id, os_module=defn.os_module)
                return instance
        raise ValueError(f"Workflow '{workflow_name}' not found")

    def approve_workflow_step(self, instance_id: str, step_id: str, approved_by: str, evidence_pack_id: str | None = None) -> WorkflowInstance:
        instance = self.workflow_engine.approve_step(instance_id, step_id, approved_by, evidence_pack_id)
        self._emit("com.dealix.approval.granted", "dealix/execution-plane", {
            "instance_id": instance_id, "step_id": step_id, "approved_by": approved_by,
        }, tenant_id=instance.tenant_id)
        return instance

    def reject_workflow_step(self, instance_id: str, step_id: str, rejected_by: str, reason: str = "") -> WorkflowInstance:
        instance = self.workflow_engine.reject_step(instance_id, step_id, rejected_by, reason)
        self._emit("com.dealix.approval.denied", "dealix/execution-plane", {
            "instance_id": instance_id, "step_id": step_id, "rejected_by": rejected_by, "reason": reason,
        }, tenant_id=instance.tenant_id)
        return instance

    def list_pending_approvals(self, tenant_id: str | None = None) -> list[dict]:
        return self.workflow_engine.list_pending_approvals(tenant_id)

    # ── Trust Plane ─────────────────────────────────────────────

    def evaluate_policy(self, action: str, actor: dict, resource: dict, context: dict | None = None) -> PolicyGateResult:
        return self.policy_engine.evaluate(action, actor, resource, context)

    def assemble_evidence(self, decision_ref: str, items: list[dict], assembled_by: str, approval_class: str = "R0_AUTO") -> EvidencePack:
        pack = assemble_evidence_pack(decision_ref, items, assembled_by, approval_class)
        self._emit("com.dealix.approval.requested", "dealix/trust-plane", {
            "pack_id": pack.pack_id, "decision_ref": decision_ref,
        })
        return pack

    def check_compliance(self, tenant_id: str = "") -> ComplianceMatrix:
        return ComplianceMatrix.default_saudi_matrix(tenant_id)

    # ── Data Plane ──────────────────────────────────────────────

    def emit_event(self, event_type: str, source: str, data: dict, tenant_id: str = "", os_module: str = "") -> CloudEvent:
        return self._emit(event_type, source, data, tenant_id=tenant_id, os_module=os_module)

    def get_event_catalog(self) -> dict[str, dict[str, str]]:
        return EVENT_CATALOG

    def get_event_log(self, limit: int = 100) -> list[dict]:
        return [e.model_dump() for e in self._event_log[-limit:]]

    # ── Operating Plane ─────────────────────────────────────────

    def get_model_routing_dashboard(self) -> dict[str, Any]:
        return self.model_router.get_dashboard_data()

    def select_model(self, task_type: str) -> dict[str, Any]:
        profile = self.model_router.select_model(task_type)
        return profile.model_dump()

    # ── Executive Surface ───────────────────────────────────────

    def get_executive_dashboard(self, tenant_id: str) -> dict[str, Any]:
        pending = self.list_pending_approvals(tenant_id)
        compliance = self.check_compliance(tenant_id)
        
        return {
            "tenant_id": tenant_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "planes_status": {
                "decision": "operational",
                "execution": "operational",
                "trust": "operational",
                "data": "operational",
                "operating": "operational",
            },
            "pending_approvals": len(pending),
            "pending_approval_details": pending[:10],
            "active_decisions": len(self.decision_engine._decisions),
            "active_workflows": len([i for i in self.workflow_engine._instances.values() if i.status.value in ("running", "paused_hitl", "paused_approval")]),
            "compliance_score": compliance.overall_score,
            "pdpl_controls_implemented": sum(1 for c in compliance.pdpl_controls if c.get("status") == "implemented"),
            "pdpl_controls_total": len(compliance.pdpl_controls),
            "nca_controls_implemented": sum(1 for c in compliance.nca_ecc_controls if c.get("status") == "implemented"),
            "nca_controls_total": len(compliance.nca_ecc_controls),
            "event_log_size": len(self._event_log),
            "model_routing": self.model_router.get_dashboard_data(),
            "os_modules": {
                module: {
                    "decisions": len(self.decision_engine.list_by_module(module)),
                } for module in self.OS_MODULES
            },
        }

    def get_risk_heatmap(self, tenant_id: str) -> list[dict[str, Any]]:
        risks: list[dict[str, Any]] = []
        for inst in self.workflow_engine._instances.values():
            if inst.tenant_id != tenant_id:
                continue
            for step in inst.steps:
                if step.approval_class in ("R2_APPROVE", "R3_COMMITTEE") and step.status.value == "waiting_approval":
                    risks.append({
                        "type": "pending_high_approval",
                        "severity": "high" if step.approval_class == "R3_COMMITTEE" else "medium",
                        "instance_id": inst.instance_id,
                        "step_name": step.name,
                        "approval_class": step.approval_class,
                    })
        pending_decisions = [d for d in self.decision_engine._decisions.values() if d.status.value == "proposed"]
        for d in pending_decisions:
            if d.approval_class in ("R2_APPROVE", "R3_COMMITTEE"):
                risks.append({
                    "type": "pending_decision",
                    "severity": "high" if d.approval_class == "R3_COMMITTEE" else "medium",
                    "decision_id": d.decision_id,
                    "title": d.title,
                    "title_ar": d.title_ar,
                    "impact_sar": d.impact.financial_sar,
                })
        return risks

    def get_policy_violations(self, tenant_id: str) -> list[dict[str, Any]]:
        violations: list[dict[str, Any]] = []
        for event in self._event_log:
            if event.type == "com.dealix.policy.violated" and event.tenantid == tenant_id:
                violations.append(event.model_dump())
        return violations

    # ── Internal ────────────────────────────────────────────────

    def _emit(self, event_type: str, source: str, data: dict, **kwargs: Any) -> CloudEvent:
        event = emit_cloud_event(event_type, source, data, **kwargs)
        self._event_log.append(event)
        return event


sovereign_os = SovereignOSService()

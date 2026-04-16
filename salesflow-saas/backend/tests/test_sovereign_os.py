"""Tests for the Dealix Sovereign Growth, Execution & Governance OS."""
import pytest


# ── Trust Plane ─────────────────────────────────────────────────

class TestApprovalClasses:
    def test_r0_auto_actions_are_allowed(self):
        from app.planes.trust.approval_classes import evaluate_action, ApprovalClass
        for action in ["lead_capture", "enrichment", "scoring", "routing",
                        "follow_up", "memo_draft", "dashboard_update", "telemetry"]:
            result = evaluate_action(action)
            assert result.allowed is True
            assert result.approval_class == ApprovalClass.R0_AUTO

    def test_r2_actions_require_approval(self):
        from app.planes.trust.approval_classes import evaluate_action, ApprovalClass
        for action in ["term_sheet_send", "signature_request", "partnership_activation",
                        "market_entry_launch", "discount_override"]:
            result = evaluate_action(action)
            assert result.allowed is False
            assert result.approval_class == ApprovalClass.R2_APPROVE

    def test_r3_actions_require_committee(self):
        from app.planes.trust.approval_classes import evaluate_action, ApprovalClass
        for action in ["ma_offer_send", "closing_approval", "external_capital_commitment"]:
            result = evaluate_action(action)
            assert result.allowed is False
            assert result.approval_class == ApprovalClass.R3_COMMITTEE

    def test_unknown_action_defaults_r2(self):
        from app.planes.trust.approval_classes import evaluate_action, ApprovalClass
        result = evaluate_action("unknown_action_xyz")
        assert result.allowed is False
        assert result.approval_class == ApprovalClass.R2_APPROVE


class TestPolicyEngine:
    def test_admin_can_override(self):
        from app.planes.trust.policy_engine import PolicyEngine
        engine = PolicyEngine()
        result = engine.evaluate("ma_offer_send", {"role": "admin"}, {})
        assert result.allowed is True

    def test_ceo_can_override(self):
        from app.planes.trust.policy_engine import PolicyEngine
        engine = PolicyEngine()
        result = engine.evaluate("ma_offer_send", {"role": "ceo"}, {})
        assert result.allowed is True

    def test_analyst_cannot_send_offer(self):
        from app.planes.trust.policy_engine import PolicyEngine
        engine = PolicyEngine()
        result = engine.evaluate("ma_offer_send", {"role": "analyst"}, {})
        assert result.allowed is False

    def test_pdpl_compliance_no_consent(self):
        from app.planes.trust.policy_engine import PolicyEngine
        engine = PolicyEngine()
        result = engine.check_pdpl_compliance("personal", "marketing", False)
        assert result["compliant"] is False
        assert len(result["violations"]) > 0

    def test_pdpl_compliance_with_consent(self):
        from app.planes.trust.policy_engine import PolicyEngine
        engine = PolicyEngine()
        result = engine.check_pdpl_compliance("personal", "service_delivery", True)
        assert result["compliant"] is True

    def test_nca_compliance_restricted_abroad(self):
        from app.planes.trust.policy_engine import PolicyEngine
        engine = PolicyEngine()
        result = engine.check_nca_compliance("restricted", "outside_ksa")
        assert result["compliant"] is False


class TestEvidencePack:
    def test_assemble_creates_pack(self):
        from app.planes.trust.evidence_pack import assemble_evidence_pack
        pack = assemble_evidence_pack("decision-1", [
            {"type": "financial", "source": "erp", "content": {"amount": 100000}},
        ], "analyst@dealix.sa", "R2_APPROVE")
        assert pack.pack_id
        assert pack.decision_ref == "decision-1"
        assert len(pack.items) == 1


class TestToolVerification:
    def test_register_and_verify(self):
        from app.planes.trust.tool_verification import ToolVerificationLedger, ToolVerificationEntry
        from datetime import datetime, timezone
        ledger = ToolVerificationLedger()
        entry = ToolVerificationEntry(
            tool_id="t1", tool_name="web_search", version="1.0",
            verified_at=datetime.now(timezone.utc), verified_by="ops",
            checksum="abc123", capabilities=["search"], restrictions=[],
        )
        ledger.register(entry)
        assert ledger.verify("t1") is not None
        assert ledger.is_allowed("t1", "search") is True
        assert ledger.is_allowed("t1", "delete") is False


# ── Execution Plane ─────────────────────────────────────────────

class TestWorkflowEngine:
    def test_sales_workflow_pauses_at_approval(self):
        from app.planes.execution.workflow_engine import DurableWorkflowEngine, WorkflowStatus
        from app.planes.execution.workflow_definitions import register_all_workflows
        engine = DurableWorkflowEngine()
        register_all_workflows(engine)

        wid = None
        for k, d in engine._definitions.items():
            if d.name == "sales_lead_to_close":
                wid = k
                break
        assert wid is not None

        instance = engine.start_workflow(wid, "t1")
        assert instance.status == WorkflowStatus.PAUSED_APPROVAL
        completed = [s for s in instance.steps if s.status.value == "completed"]
        assert len(completed) == 9

    def test_approve_then_complete(self):
        from app.planes.execution.workflow_engine import DurableWorkflowEngine, WorkflowStatus, StepStatus
        from app.planes.execution.workflow_definitions import register_all_workflows
        engine = DurableWorkflowEngine()
        register_all_workflows(engine)

        wid = [k for k, d in engine._definitions.items() if d.name == "pmi_integration"][0]
        instance = engine.start_workflow(wid, "t1")
        assert instance.status == WorkflowStatus.COMPLETED

    def test_ma_workflow_requires_committee(self):
        from app.planes.execution.workflow_engine import DurableWorkflowEngine, WorkflowStatus
        from app.planes.execution.workflow_definitions import register_all_workflows
        engine = DurableWorkflowEngine()
        register_all_workflows(engine)

        wid = [k for k, d in engine._definitions.items() if d.name == "ma_acquisition"][0]
        instance = engine.start_workflow(wid, "t1")
        assert instance.status in (WorkflowStatus.PAUSED_APPROVAL, WorkflowStatus.PAUSED_HITL)
        waiting = [s for s in instance.steps if s.status.value == "waiting_approval"]
        assert len(waiting) == 1
        assert waiting[0].approval_class == "R3_COMMITTEE"

    def test_pending_approvals_list(self):
        from app.planes.execution.workflow_engine import DurableWorkflowEngine
        from app.planes.execution.workflow_definitions import register_all_workflows
        engine = DurableWorkflowEngine()
        register_all_workflows(engine)

        wid = [k for k, d in engine._definitions.items() if d.name == "sales_lead_to_close"][0]
        engine.start_workflow(wid, "t1")
        engine.start_workflow(wid, "t2")

        all_pending = engine.list_pending_approvals()
        assert len(all_pending) == 2

        t1_pending = engine.list_pending_approvals("t1")
        assert len(t1_pending) == 1


# ── Decision Plane ──────────────────────────────────────────────

class TestDecisionEngine:
    def test_decision_lifecycle(self):
        from app.planes.decision.structured_decision import DecisionEngine, DecisionStatus
        engine = DecisionEngine()
        d = engine.create_decision("Test", "sales", "user@dealix.sa")
        assert d.status == DecisionStatus.DRAFT

        engine.propose(d.decision_id, "Go ahead")
        assert d.status == DecisionStatus.PROPOSED

        engine.approve(d.decision_id, "ceo@dealix.sa")
        assert d.status == DecisionStatus.APPROVED

    def test_reject_decision(self):
        from app.planes.decision.structured_decision import DecisionEngine, DecisionStatus
        engine = DecisionEngine()
        d = engine.create_decision("Test", "ma", "user@dealix.sa")
        engine.propose(d.decision_id, "Acquire target")
        engine.reject(d.decision_id, "board@dealix.sa", "Too risky")
        assert d.status == DecisionStatus.REJECTED
        assert d.metadata.get("rejection_reason") == "Too risky"


class TestModelRouter:
    def test_strategic_task_gets_opus(self):
        from app.planes.decision.model_router import ModelRoutingFabric
        fabric = ModelRoutingFabric()
        profile = fabric.select_model("board_pack")
        assert profile.tier == "strategic"
        assert "opus" in profile.model_id.lower()

    def test_implementation_task_gets_codex(self):
        from app.planes.decision.model_router import ModelRoutingFabric
        fabric = ModelRoutingFabric()
        profile = fabric.select_model("code_generation")
        assert profile.tier == "implementation"

    def test_arabic_task_gets_groq(self):
        from app.planes.decision.model_router import ModelRoutingFabric
        fabric = ModelRoutingFabric()
        profile = fabric.select_model("arabic_nlp")
        assert profile.tier == "lightweight"


# ── Data Plane ──────────────────────────────────────────────────

class TestEventContracts:
    def test_cloud_event_creation(self):
        from app.planes.data.event_contracts import emit_cloud_event
        event = emit_cloud_event(
            "com.dealix.lead.captured", "dealix/sales-os",
            {"lead_id": "123"}, tenant_id="t1",
        )
        assert event.type == "com.dealix.lead.captured"
        assert event.specversion == "1.0"
        assert event.tenantid == "t1"

    def test_event_catalog_coverage(self):
        from app.planes.data.event_contracts import EVENT_CATALOG
        modules = {v["module"] for v in EVENT_CATALOG.values()}
        assert "sales" in modules
        assert "partnership" in modules
        assert "ma" in modules
        assert "expansion" in modules
        assert "pmi" in modules
        assert "governance" in modules


class TestDataQuality:
    def test_validate_not_null(self):
        from app.planes.data.quality_gate import DataQualityGate, QualityExpectation
        gate = DataQualityGate()
        gate.register_expectations("leads", [
            QualityExpectation(name="email_required", column="email", expectation_type="not_null"),
        ])
        report = gate.validate("leads", [{"email": "a@b.com"}, {"email": None}])
        assert report.failed == 1

    def test_validate_in_set(self):
        from app.planes.data.quality_gate import DataQualityGate, QualityExpectation
        gate = DataQualityGate()
        gate.register_expectations("deals", [
            QualityExpectation(name="valid_stage", column="stage", expectation_type="in_set",
                               parameters={"values": ["new", "negotiation", "closed_won"]}),
        ])
        report = gate.validate("deals", [
            {"stage": "new"}, {"stage": "invalid_stage"},
        ])
        assert report.failed == 1


# ── Operating Plane ─────────────────────────────────────────────

class TestReleaseGovernance:
    def test_create_prod_release_has_canary(self):
        from app.planes.operating.release_governance import ReleaseGovernance, EnvironmentType
        gov = ReleaseGovernance()
        release = gov.create_release("2.1.0", EnvironmentType.PRODUCTION, "abc123")
        assert release.canary_percentage == 10
        gate_names = [g.name for g in release.gates]
        assert "Canary Deployment" in gate_names

    def test_pass_all_gates_approves(self):
        from app.planes.operating.release_governance import ReleaseGovernance, EnvironmentType, ReleaseStatus
        gov = ReleaseGovernance()
        release = gov.create_release("2.1.0", EnvironmentType.STAGING)
        for gate in release.gates:
            gov.pass_gate(release.release_id, gate.gate_id, "ci-bot")
        assert release.status == ReleaseStatus.APPROVED


class TestComplianceMatrix:
    def test_saudi_matrix_has_all_sections(self):
        from app.planes.operating.release_governance import ComplianceMatrix
        matrix = ComplianceMatrix.default_saudi_matrix("t1")
        assert len(matrix.pdpl_controls) == 8
        assert len(matrix.nca_ecc_controls) == 6
        assert len(matrix.ai_governance_controls) == 5


# ── Sovereign OS Service ───────────────────────────────────────

class TestSovereignOSService:
    def test_initialize(self):
        from app.services.sovereign.os_service import SovereignOSService
        svc = SovereignOSService()
        result = svc.initialize()
        assert result["status"] == "initialized"
        assert len(result["planes"]) == 5
        assert len(result["os_modules"]) == 6

    def test_executive_dashboard(self):
        from app.services.sovereign.os_service import SovereignOSService
        svc = SovereignOSService()
        svc.initialize()
        dashboard = svc.get_executive_dashboard("t1")
        assert "planes_status" in dashboard
        assert "os_modules" in dashboard
        assert dashboard["planes_status"]["decision"] == "operational"

    def test_risk_heatmap(self):
        from app.services.sovereign.os_service import SovereignOSService
        svc = SovereignOSService()
        svc.initialize()
        svc.start_workflow("sales_lead_to_close", "t1")
        risks = svc.get_risk_heatmap("t1")
        assert len(risks) > 0

    def test_full_lifecycle(self):
        from app.services.sovereign.os_service import SovereignOSService
        svc = SovereignOSService()
        svc.initialize()

        decision = svc.create_decision(
            title="New market entry", os_module="expansion",
            created_by="founder@dealix.sa", action="market_entry_launch",
        )
        assert decision.approval_class == "R2_APPROVE"

        svc.propose_decision(decision.decision_id, "Enter UAE Q3")
        svc.approve_decision(decision.decision_id, "board@dealix.sa")

        instance = svc.start_workflow("expansion_market_entry", "t1")
        assert instance.status.value in ("paused_approval", "paused_hitl")

        events = svc.get_event_log()
        assert len(events) > 0

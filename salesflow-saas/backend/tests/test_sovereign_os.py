"""Tests for the Dealix Sovereign Growth, Execution & Governance OS."""

import pytest
from httpx import AsyncClient, ASGITransport
from app.main import app


@pytest.fixture
def client():
    transport = ASGITransport(app=app)
    return AsyncClient(transport=transport, base_url="http://test")


# ── Sovereign Health ────────────────────────────────────────────

@pytest.mark.asyncio
async def test_sovereign_health(client):
    async with client:
        r = await client.get("/api/v1/sovereign/health")
    assert r.status_code == 200
    data = r.json()
    assert data["status"] == "operational"
    assert "planes" in data
    for plane in ("decision", "execution", "trust", "data", "operating"):
        assert plane in data["planes"]
        assert data["planes"][plane]["status"] == "active"
    assert len(data["os_modules"]) == 6


@pytest.mark.asyncio
async def test_sovereign_manifest(client):
    async with client:
        r = await client.get("/api/v1/sovereign/manifest")
    assert r.status_code == 200
    data = r.json()
    assert "Sovereign" in data["name"]
    assert len(data["live_surfaces"]) == 18
    assert len(data["os_modules"]) == 6
    assert "auto" in data["approval_classes"]
    assert "board" in data["approval_classes"]


@pytest.mark.asyncio
async def test_event_catalog(client):
    async with client:
        r = await client.get("/api/v1/sovereign/event-catalog")
    assert r.status_code == 200
    data = r.json()
    assert data["total_events"] >= 22
    assert "dealix.sales.lead.captured" in data["events"]
    assert "dealix.ma.dd.started" in data["events"]


@pytest.mark.asyncio
async def test_automation_map(client):
    async with client:
        r = await client.get("/api/v1/sovereign/automation-map")
    assert r.status_code == 200
    data = r.json()
    assert "lead_capture" in data["fully_automated"]
    assert "send_acquisition_offer" in data["hitl_gated"]
    assert len(data["fully_automated"]) == 18
    assert len(data["hitl_gated"]) == 10


@pytest.mark.asyncio
async def test_workflow_catalog(client):
    async with client:
        r = await client.get("/api/v1/sovereign/workflows")
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 5
    types = {w["type"] for w in data}
    assert "sales_revenue_os" in types
    assert "partnership_os" in types
    assert "ma_corporate_dev_os" in types


@pytest.mark.asyncio
async def test_release_gates(client):
    async with client:
        r = await client.get("/api/v1/sovereign/release-gates")
    assert r.status_code == 200
    data = r.json()
    assert "staging" in data
    assert "production" in data


@pytest.mark.asyncio
async def test_connectors(client):
    async with client:
        r = await client.get("/api/v1/sovereign/connectors")
    assert r.status_code == 200
    data = r.json()
    assert len(data) >= 8
    ids = {c["connector_id"] for c in data}
    assert "whatsapp-business" in ids
    assert "postgres-primary" in ids


# ── Executive OS ────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_executive_room(client):
    async with client:
        r = await client.get("/api/v1/executive/room")
    assert r.status_code == 200
    data = r.json()
    assert data["module"] == "executive_board_os"
    assert len(data["surfaces"]) >= 9


@pytest.mark.asyncio
async def test_executive_connector_health(client):
    async with client:
        r = await client.get("/api/v1/executive/connector-health")
    assert r.status_code == 200
    data = r.json()
    assert len(data) >= 8


# ── Partnership OS ──────────────────────────────────────────────

@pytest.mark.asyncio
async def test_partnership_dashboard(client):
    async with client:
        r = await client.get("/api/v1/partnership/dashboard")
    assert r.status_code == 200
    data = r.json()
    assert data["module"] == "partnership_os"


@pytest.mark.asyncio
async def test_partnership_partners_list(client):
    async with client:
        r = await client.get("/api/v1/partnership/partners")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


# ── M&A OS ──────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_ma_pipeline(client):
    async with client:
        r = await client.get("/api/v1/ma/pipeline")
    assert r.status_code == 200
    data = r.json()
    assert data["module"] == "ma_corporate_dev_os"


@pytest.mark.asyncio
async def test_ma_targets_list(client):
    async with client:
        r = await client.get("/api/v1/ma/targets")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


# ── Expansion OS ────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_expansion_dashboard(client):
    async with client:
        r = await client.get("/api/v1/expansion/dashboard")
    assert r.status_code == 200
    data = r.json()
    assert data["module"] == "expansion_os"


@pytest.mark.asyncio
async def test_expansion_markets_list(client):
    async with client:
        r = await client.get("/api/v1/expansion/markets")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


# ── PMI OS ──────────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_pmi_dashboard(client):
    async with client:
        r = await client.get("/api/v1/pmi/dashboard")
    assert r.status_code == 200
    data = r.json()
    assert data["module"] == "pmi_strategic_pmo"


@pytest.mark.asyncio
async def test_pmi_programs_list(client):
    async with client:
        r = await client.get("/api/v1/pmi/programs")
    assert r.status_code == 200
    assert isinstance(r.json(), list)


# ── Planes Unit Tests ───────────────────────────────────────────

def test_guardrails_auto_allowed():
    from app.planes.decision.guardrails import is_action_auto_allowed
    assert is_action_auto_allowed("lead_capture")
    assert is_action_auto_allowed("enrichment")
    assert not is_action_auto_allowed("send_acquisition_offer")


def test_guardrails_hitl_blocking():
    from app.planes.decision.schemas import (
        StructuredDecision, DecisionContext, ApprovalClass,
        ReversibilityClass, SensitivityClass
    )
    from app.planes.decision.guardrails import evaluate_guardrails
    ctx = DecisionContext(
        trace_id="t1", correlation_id="c1", tenant_id="t",
        actor_id="a", actor_role="admin"
    )
    decision = StructuredDecision(
        decision_id="d1", context=ctx, action="send_term_sheet",
        rationale="test", rationale_ar="اختبار",
        required_approval=ApprovalClass.AUTO,
    )
    results = evaluate_guardrails(decision)
    hitl_result = [r for r in results if r.rule_id == "HITL-001"][0]
    assert not hitl_result.passed
    assert hitl_result.blocked


def test_pdpl_guardrail_blocks_without_consent():
    from app.planes.decision.schemas import (
        StructuredDecision, DecisionContext, SensitivityClass
    )
    from app.planes.decision.guardrails import evaluate_guardrails
    ctx = DecisionContext(
        trace_id="t1", correlation_id="c1", tenant_id="t",
        actor_id="a", actor_role="admin"
    )
    decision = StructuredDecision(
        decision_id="d1", context=ctx, action="enrichment",
        rationale="test", rationale_ar="اختبار",
        sensitivity=SensitivityClass.RESTRICTED,
        metadata={"pdpl_consent_verified": False},
    )
    results = evaluate_guardrails(decision)
    pdpl_result = [r for r in results if r.rule_id == "PDPL-001"][0]
    assert not pdpl_result.passed
    assert pdpl_result.blocked


def test_model_routing():
    from app.planes.decision.model_router import route_model
    r = route_model("code_implementation")
    assert "codex" in r.selected_model
    r2 = route_model("board_synthesis")
    assert "opus" in r2.selected_model
    r3 = route_model("arabic_memo")
    assert "gpt" in r3.selected_model


def test_policy_engine_financial_thresholds():
    from app.planes.trust.policy_engine import evaluate_policy, PolicyInput, PolicyVerdict
    low = evaluate_policy(PolicyInput(
        action="approve", actor_id="a", actor_role="admin",
        tenant_id="t", resource_type="deal", financial_impact_sar=5_000
    ))
    assert low.verdict == PolicyVerdict.ALLOW

    high = evaluate_policy(PolicyInput(
        action="approve", actor_id="a", actor_role="admin",
        tenant_id="t", resource_type="deal", financial_impact_sar=3_000_000
    ))
    assert high.verdict == PolicyVerdict.REQUIRE_APPROVAL


def test_cloud_event_creation():
    from app.planes.data.event_contracts import create_event
    e = create_event(
        "dealix.sales.lead.captured", "api",
        {"lead_id": "123"}, tenant_id="t1"
    )
    assert e.specversion == "1.0"
    assert e.type == "dealix.sales.lead.captured"
    assert e.tenantid == "t1"
    assert e.data["lead_id"] == "123"


def test_workflow_instance_advance():
    from app.planes.execution.workflow_engine import (
        WorkflowInstance, WorkflowStep, StepStatus, WorkflowStatus
    )
    wf = WorkflowInstance(
        tenant_id="t1", workflow_type="test",
        steps=[
            WorkflowStep(name="Step 1", name_ar="خطوة 1", order=0, status=StepStatus.COMPLETED),
            WorkflowStep(name="Step 2", name_ar="خطوة 2", order=1),
        ]
    )
    next_step = wf.advance()
    assert next_step is not None
    assert next_step.name == "Step 2"
    assert wf.current_step == 1

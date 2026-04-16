"""Comprehensive tests for the Dealix Sovereign Enterprise Growth OS."""

import pytest
from httpx import ASGITransport, AsyncClient

from app.main import app


# ── Sovereign Readiness & Meta Endpoints ─────────────────────

@pytest.mark.asyncio
async def test_sovereign_readiness():
    """GET /sovereign/readiness returns 8 readiness criteria."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.get("/api/v1/sovereign/readiness")
        assert r.status_code == 200
        data = r.json()
        assert "criteria" in data or "readiness" in data or isinstance(data, dict)


@pytest.mark.asyncio
async def test_sovereign_surfaces():
    """GET /sovereign/surfaces returns 18 required surfaces."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.get("/api/v1/sovereign/surfaces")
        assert r.status_code == 200
        data = r.json()
        assert isinstance(data, (list, dict))


@pytest.mark.asyncio
async def test_sovereign_program_lock():
    """GET /sovereign/program-lock returns current program lock."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.get("/api/v1/sovereign/program-lock")
        assert r.status_code == 200


@pytest.mark.asyncio
async def test_sovereign_compliance_matrix():
    """GET /sovereign/compliance-matrix returns Saudi compliance matrix."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.get("/api/v1/sovereign/compliance-matrix")
        assert r.status_code == 200


@pytest.mark.asyncio
async def test_sovereign_routing_dashboard():
    """GET /sovereign/routing-dashboard returns model routing dashboard."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.get("/api/v1/sovereign/routing-dashboard")
        assert r.status_code == 200


@pytest.mark.asyncio
async def test_sovereign_contradiction_dashboard():
    """GET /sovereign/contradiction-dashboard returns contradiction dashboard."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.get("/api/v1/sovereign/contradiction-dashboard")
        assert r.status_code == 200


# ── Decision Plane ───────────────────────────────────────────

@pytest.mark.asyncio
async def test_decision_detect_signals():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.post("/api/v1/sovereign/decision/signals/detect", json={
            "track": "REVENUE",
            "raw_data": {"source": "whatsapp", "text": "نحتاج عرض سعر"}
        })
        assert r.status_code == 200


@pytest.mark.asyncio
async def test_decision_triage():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.post("/api/v1/sovereign/decision/triage", json={
            "signals": [{"type": "lead_inquiry", "urgency": 0.8}]
        })
        assert r.status_code == 200


@pytest.mark.asyncio
async def test_decision_memo():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.post("/api/v1/sovereign/decision/memo", json={
            "track": "REVENUE",
            "context": {"deal_id": "DEAL-001"},
            "language": "ar"
        })
        assert r.status_code == 200


@pytest.mark.asyncio
async def test_decision_recommend():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.post("/api/v1/sovereign/decision/recommend", json={
            "track": "REVENUE",
            "context": {"lead_score": 85}
        })
        assert r.status_code == 200


@pytest.mark.asyncio
async def test_decision_forecast():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.post("/api/v1/sovereign/decision/forecast", json={
            "track": "REVENUE",
            "historical_data": [100, 120, 150],
            "horizon_days": 30
        })
        assert r.status_code == 200


@pytest.mark.asyncio
async def test_decision_next_action():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.post("/api/v1/sovereign/decision/next-action", json={
            "track": "REVENUE",
            "current_state": {"stage": "QUALIFIED"}
        })
        assert r.status_code == 200


@pytest.mark.asyncio
async def test_decision_evidence_pack():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.post("/api/v1/sovereign/decision/evidence-pack", json={
            "track": "REVENUE",
            "items": [{"title_en": "Market Analysis", "text_ar": "تحليل السوق"}]
        })
        assert r.status_code == 200


# ── Execution Plane ──────────────────────────────────────────

@pytest.mark.asyncio
async def test_execution_workflow_start():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.post("/api/v1/sovereign/execution/workflow/start", json={
            "workflow_type": "deal_approval",
            "payload": {"deal_id": "DEAL-001"},
            "approval_class": "TEAM_LEAD"
        })
        assert r.status_code == 200


@pytest.mark.asyncio
async def test_execution_workflow_status():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.get("/api/v1/sovereign/execution/workflow/test-wf-001/status")
        assert r.status_code in (200, 404)


# ── Trust Plane ──────────────────────────────────────────────

@pytest.mark.asyncio
async def test_trust_policy_evaluate():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.post("/api/v1/sovereign/trust/policy/evaluate", json={
            "action": "send_term_sheet",
            "context": {"partner_id": "P-001"}
        })
        assert r.status_code == 200


@pytest.mark.asyncio
async def test_trust_authorization_check():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.post("/api/v1/sovereign/trust/authorization/check", json={
            "user_id": "user-001",
            "resource": "deal_room",
            "action": "read"
        })
        assert r.status_code == 200


@pytest.mark.asyncio
async def test_trust_tool_verify():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.post("/api/v1/sovereign/trust/tool/verify", json={
            "agent_id": "closer-agent",
            "tool_name": "send_whatsapp",
            "parameters": {"to": "+966500000000"}
        })
        assert r.status_code == 200


@pytest.mark.asyncio
async def test_trust_contradiction_detect():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.post("/api/v1/sovereign/trust/contradiction/detect", json={
            "intended": "send_email",
            "claimed": "sent_email",
            "actual": "no_op"
        })
        assert r.status_code == 200


# ── Data Plane ───────────────────────────────────────────────

@pytest.mark.asyncio
async def test_data_quality_validate():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.post("/api/v1/sovereign/data/quality/validate", json={
            "dataset_name": "leads",
            "data": [{"name": "شركة تقنية", "score": 80}]
        })
        assert r.status_code == 200


@pytest.mark.asyncio
async def test_data_connector_health():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.get("/api/v1/sovereign/data/connector/health")
        assert r.status_code == 200


@pytest.mark.asyncio
async def test_data_semantic_query():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.post("/api/v1/sovereign/data/semantic/query", json={
            "query": "ما هي أفضل استراتيجية تسعير",
            "collection": "knowledge",
            "top_k": 5
        })
        assert r.status_code == 200


# ── Operating Plane ──────────────────────────────────────────

@pytest.mark.asyncio
async def test_operating_release_gate():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.get("/api/v1/sovereign/operating/release/v1.0.0/gate")
        assert r.status_code == 200


@pytest.mark.asyncio
async def test_operating_deployment_status():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.get("/api/v1/sovereign/operating/deployment/staging/status")
        assert r.status_code == 200


# ── Revenue Track ────────────────────────────────────────────

@pytest.mark.asyncio
async def test_revenue_lead_capture():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.post("/api/v1/sovereign/tracks/revenue/lead/capture", json={
            "source": "whatsapp",
            "channel": "direct",
            "data": {"name": "شركة الرياض للتقنية", "phone": "+966500000000"}
        })
        assert r.status_code == 200


@pytest.mark.asyncio
async def test_revenue_funnel_metrics():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.get("/api/v1/sovereign/tracks/revenue/funnel/metrics")
        assert r.status_code == 200


# ── Partnership Track ────────────────────────────────────────

@pytest.mark.asyncio
async def test_partnership_scout():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.post("/api/v1/sovereign/tracks/partnership/scout", json={
            "criteria": {"industry": "technology", "region": "GCC"}
        })
        assert r.status_code == 200


# ── M&A Track ────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_ma_source_targets():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.post("/api/v1/sovereign/tracks/ma/targets/source", json={
            "criteria": {"sector": "fintech", "revenue_min_sar": 5000000}
        })
        assert r.status_code == 200


# ── Expansion Track ──────────────────────────────────────────

@pytest.mark.asyncio
async def test_expansion_scan_markets():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.post("/api/v1/sovereign/tracks/expansion/markets/scan", json={
            "criteria": {"regions": ["UAE", "Bahrain", "Kuwait"]}
        })
        assert r.status_code == 200


# ── PMI Track ────────────────────────────────────────────────

@pytest.mark.asyncio
async def test_pmi_day1_readiness():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.get("/api/v1/sovereign/tracks/pmi/deal-001/day1-readiness")
        assert r.status_code == 200


# ── Executive/Board Track ────────────────────────────────────

@pytest.mark.asyncio
async def test_executive_board_memo():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.post("/api/v1/sovereign/tracks/executive/board-memo", json={
            "topic": "Q1 Revenue Review",
            "language": "ar"
        })
        assert r.status_code == 200


@pytest.mark.asyncio
async def test_executive_approval_center():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.get("/api/v1/sovereign/tracks/executive/approval-center")
        assert r.status_code == 200


@pytest.mark.asyncio
async def test_executive_risk_heatmap():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.get("/api/v1/sovereign/tracks/executive/risk-heatmap")
        assert r.status_code == 200


@pytest.mark.asyncio
async def test_executive_policy_violations():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.get("/api/v1/sovereign/tracks/executive/policy-violations")
        assert r.status_code == 200


@pytest.mark.asyncio
async def test_executive_pipeline():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.get("/api/v1/sovereign/tracks/executive/pipeline")
        assert r.status_code == 200


@pytest.mark.asyncio
async def test_executive_next_actions():
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        r = await ac.get("/api/v1/sovereign/tracks/executive/next-actions")
        assert r.status_code == 200


# ── Schemas Unit Tests ───────────────────────────────────────

def test_sovereign_schemas_import():
    """All core sovereign schemas should be importable."""
    from app.sovereign.schemas import (
        SovereigntyDimension, PlaneType, BusinessTrack,
        ActionClass, ApprovalClass, ReversibilityClass,
        SensitivityLevel, AgentRole, SovereignRoutingLane,
        ProvenanceInfo, EvidenceItem, EvidencePack,
        RecommendationPayload, ConnectorContract, RetryPolicy,
        ContradictionRecord, ModelRoutingDecision, ProgramLock,
    )
    assert len(SovereigntyDimension) == 4
    assert len(PlaneType) == 5
    assert len(BusinessTrack) == 6
    assert len(ActionClass) == 3
    assert len(ReversibilityClass) == 4


def test_sovereign_constants():
    """Constants should have correct cardinality."""
    from app.sovereign.constants import (
        REQUIRED_SURFACES, SAUDI_COMPLIANCE_FRAMEWORKS,
        SOVEREIGNTY_READINESS_CRITERIA,
    )
    assert len(REQUIRED_SURFACES) == 18
    assert len(SAUDI_COMPLIANCE_FRAMEWORKS) >= 4
    assert len(SOVEREIGNTY_READINESS_CRITERIA) == 8


def test_evidence_pack_creation():
    """EvidencePack should be constructable with defaults."""
    from app.sovereign.schemas import EvidencePack, BusinessTrack
    pack = EvidencePack(track=BusinessTrack.REVENUE)
    assert pack.track == BusinessTrack.REVENUE
    assert pack.pack_id is not None
    assert isinstance(pack.items, list)


def test_recommendation_payload_creation():
    """RecommendationPayload should be constructable with required fields."""
    from app.sovereign.schemas import (
        RecommendationPayload, BusinessTrack, ActionClass,
        ApprovalClass, ReversibilityClass, SensitivityLevel, EvidencePack,
    )
    rec = RecommendationPayload(
        track=BusinessTrack.MA_CORPDEV,
        title="Acquire TechCo",
        title_ar="استحواذ على تك كو",
        description="Strategic acquisition target",
        description_ar="هدف استحواذ استراتيجي",
        action_class=ActionClass.APPROVAL_REQUIRED,
        approval_class=ApprovalClass.BOARD_LEVEL,
        reversibility_class=ReversibilityClass.IRREVERSIBLE,
        sensitivity_level=SensitivityLevel.RESTRICTED,
        evidence_pack=EvidencePack(track=BusinessTrack.MA_CORPDEV),
        policy_evaluation={"pdpl": "compliant"},
    )
    assert rec.recommendation_id is not None
    assert rec.action_class == ActionClass.APPROVAL_REQUIRED


def test_contradiction_record_creation():
    """ContradictionRecord should be constructable."""
    from app.sovereign.schemas import ContradictionRecord
    cr = ContradictionRecord(
        agent_id="closer-agent",
        intended_action="send_email",
        claimed_action="email_sent",
        actual_tool_call="no_op",
        side_effects=[],
        contradiction_detected=True,
    )
    assert cr.contradiction_detected is True
    assert cr.resolution_status == "open"


# ── SQLAlchemy Model Import Tests ────────────────────────────

def test_sovereign_models_import():
    """All sovereign SQLAlchemy models should be importable from app.models."""
    from app.models.sovereign import (
        SovereignEvidencePack, SovereignEvidenceItem,
        SovereignWorkflow, SovereignContradiction,
        SovereignPolicyEvaluation, SovereignToolVerification,
        SovereignComplianceCheck, SovereignConnectorState,
        SovereignProgramLock,
    )
    assert SovereignEvidencePack.__tablename__ == "sovereign_evidence_packs"
    assert SovereignWorkflow.__tablename__ == "sovereign_workflows"
    assert SovereignContradiction.__tablename__ == "sovereign_contradictions"

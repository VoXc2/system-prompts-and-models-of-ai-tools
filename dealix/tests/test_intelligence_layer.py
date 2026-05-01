"""Tests for intelligence_layer package and router."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from api.main import create_app
from auto_client_acquisition.intelligence_layer.action_graph import build_action_graph_trace
from auto_client_acquisition.intelligence_layer.decision_memory import list_decisions, record_decision, reset_demo_memory
from auto_client_acquisition.intelligence_layer.growth_brain import build_growth_profile
from auto_client_acquisition.intelligence_layer.intel_command_feed import build_intel_command_feed
from auto_client_acquisition.intelligence_layer.mission_engine import list_mission_catalog
from auto_client_acquisition.intelligence_layer.opportunity_simulator import simulate_opportunities


def test_growth_profile_has_brain_id_and_blocked_actions() -> None:
    out = build_growth_profile(
        {"company_name": "نمو", "sector": "training", "city": "الرياض", "risk_tolerance": "low", "channels": ["email"]}
    )
    assert out["growth_brain_id"].startswith("gb_")
    assert "cold_whatsapp" in out["blocked_actions"]
    assert out["recommended_first_mission"] == "ten_in_ten_opportunities"
    assert out["tone"]


def test_intel_command_feed_unified_card_shape() -> None:
    data = build_intel_command_feed()
    for c in data["cards"]:
        assert "why_it_matters_ar" in c
        assert "buttons" in c
        assert len(c["buttons"]) <= 3
        assert "approval_required" in c


def test_intel_command_feed_distinct_from_innovation() -> None:
    data = build_intel_command_feed()
    assert data["source"] == "intelligence_layer"
    types = {c.get("type") for c in data["cards"]}
    assert "revenue_leak" in types


def test_opportunity_simulator_numeric() -> None:
    out = simulate_opportunities({"pipeline_sar": 100_000, "win_rate": 0.2})
    assert out["weighted_forecast_sar"] == 20_000.0


@pytest.fixture()
def client() -> TestClient:
    return TestClient(create_app())


def test_intelligence_bundle_optional_ten_in_ten(client: TestClient) -> None:
    r = client.post(
        "/api/v1/intelligence/bundle",
        json={
            "company": {"company_name": "تجربة", "sector": "صحة"},
            "include_ten_in_ten": True,
            "ten_in_ten": {"company": "تجربة", "sector": "صحة", "city": "الرياض"},
        },
    )
    assert r.status_code == 200
    body = r.json()
    assert "growth_profile" in body
    assert "ten_in_ten" in body
    assert isinstance(body["ten_in_ten"], dict)


def test_intelligence_command_feed_route(client: TestClient) -> None:
    r = client.get("/api/v1/intelligence/command-feed")
    assert r.status_code == 200
    assert r.json()["cards"]


def test_command_feed_demo_alias_matches_command_feed(client: TestClient) -> None:
    a = client.get("/api/v1/intelligence/command-feed").json()
    b = client.get("/api/v1/intelligence/command-feed/demo").json()
    assert a == b


def test_missions_first_10_opportunities_wraps_ten_in_ten(client: TestClient) -> None:
    r = client.post(
        "/api/v1/intelligence/missions/first-10-opportunities",
        json={"company": "أكاديمية", "sector": "training", "city": "الرياض"},
    )
    assert r.status_code == 200
    body = r.json()
    opps = body.get("opportunities")
    assert isinstance(opps, list) and len(opps) == 10


def test_growth_profile_route(client: TestClient) -> None:
    r = client.post("/api/v1/intelligence/growth-profile", json={"company_name": "X", "risk_tolerance": "high"})
    assert r.status_code == 200
    assert r.json()["growth_brain_id"].startswith("gb_")


def test_mission_catalog_includes_first_10() -> None:
    cat = list_mission_catalog()
    ids = {m["id"] for m in cat["missions"]}
    assert "first_10_opportunities" in ids


def test_action_graph_trace() -> None:
    g = build_action_graph_trace({"signal_type": "email.received"})
    assert len(g["nodes"]) >= 4
    assert any(e["from"] == "n1" for e in g["edges"])


def test_decision_memory_roundtrip() -> None:
    reset_demo_memory()
    record_decision({"decision_ar": "اعتمد مسودة", "actor": "demo"})
    lst = list_decisions(limit=5)
    assert lst["count"] >= 1


def test_intelligence_mission_catalog_route(client: TestClient) -> None:
    r = client.get("/api/v1/intelligence/missions/catalog")
    assert r.status_code == 200
    assert r.json().get("missions")


def test_intelligence_mission_detail_route(client: TestClient) -> None:
    r = client.get("/api/v1/intelligence/missions/first_10_opportunities")
    assert r.status_code == 200
    assert r.json().get("found") is True


def test_action_graph_demo_route(client: TestClient) -> None:
    r = client.post("/api/v1/intelligence/action-graph/demo", json={"signal_type": "lead_received"})
    assert r.status_code == 200
    assert r.json().get("nodes")


def test_decision_memory_routes(client: TestClient) -> None:
    reset_demo_memory()
    r1 = client.post("/api/v1/intelligence/decision-memory/record", json={"decision_ar": "تجربة", "actor": "test"})
    assert r1.status_code == 200
    r2 = client.get("/api/v1/intelligence/decision-memory/demo")
    assert r2.status_code == 200
    assert r2.json().get("count", 0) >= 1

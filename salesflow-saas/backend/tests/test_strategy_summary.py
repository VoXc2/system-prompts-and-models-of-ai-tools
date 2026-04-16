from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_strategy_summary_json():
    r = client.get("/api/v1/strategy/summary")
    assert r.status_code == 200
    data = r.json()
    assert data["product"] == "Dealix"
    assert data.get("blueprint_version")
    assert "moat_pillars" in data
    assert len(data["phases"]) >= 4
    assert "auditable_targets" in data and len(data["auditable_targets"]) >= 4
    assert "design_principles" in data and len(data["design_principles"]) >= 4
    assert "planes" in data and len(data["planes"]) == 5
    assert data.get("program_locks", {}).get("planes") == 5
    assert "mandatory_surfaces" in data and len(data["mandatory_surfaces"]) >= 10
    assert "automation_policy" in data
    assert "routing_fabric" in data
    assert "readiness_definition" in data and len(data["readiness_definition"]) >= 4
    assert data["doc_paths"].get("ultimate_execution_ar")
    assert data["doc_paths"].get("integration_master_ar")
    assert "competitive_moat" in data

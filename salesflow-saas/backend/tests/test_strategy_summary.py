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
    assert "planes" in data and len(data["planes"]) == 5
    assert "business_tracks" in data and len(data["business_tracks"]) == 6
    assert "operating_surfaces" in data and len(data["operating_surfaces"]) >= 10
    assert "program_locks" in data and data["program_locks"]["counts"]["planes"] == 5
    assert "routing_fabric" in data and len(data["routing_fabric"]["lanes"]) >= 4
    assert "readiness_definition" in data and len(data["readiness_definition"]) >= 6
    assert "design_principles" in data and len(data["design_principles"]) >= 4
    assert data["doc_paths"].get("ultimate_execution_ar")
    assert data["doc_paths"].get("integration_master_ar")
    assert data["doc_paths"].get("sovereign_operating_model_ar")
    assert data["repo_paths"].get("sovereign_doc")
    assert "competitive_moat" in data

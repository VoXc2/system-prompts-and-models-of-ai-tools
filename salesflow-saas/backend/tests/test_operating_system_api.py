import pytest


@pytest.mark.asyncio
async def test_operating_system_executive_room_contract(client):
    response = await client.get("/api/v1/operating-system/executive-room")
    assert response.status_code == 200

    payload = response.json()
    assert payload["title_en"] == "Dealix Sovereign Growth, Execution & Governance OS"
    assert payload["mode"] in ("demo", "tenant")
    assert payload["surface_coverage"]["live"] >= 1
    assert payload["system_coverage"]["live"] >= 1

    assert len(payload["planes"]) == 5
    assert {plane["id"] for plane in payload["planes"]} == {
        "decision",
        "execution",
        "trust",
        "data",
        "operating",
    }

    assert len(payload["business_systems"]) == 6
    assert any(system["id"] == "sales_revenue_os" and system["status"] == "live" for system in payload["business_systems"])
    assert any(system["id"] == "pmi_pmo_os" and system["status"] == "gap" for system in payload["business_systems"])

    assert any(surface["id"] == "executive_room" and surface["status"] == "live" for surface in payload["live_surfaces"])
    assert any(surface["id"] == "model_routing_dashboard" and surface["status"] == "gap" for surface in payload["live_surfaces"])

    assert any(item["family"] == "approval" for item in payload["decision_metadata_classes"])
    assert any(item["family"] == "reversibility" for item in payload["decision_metadata_classes"])
    assert any(item["family"] == "sensitivity" for item in payload["decision_metadata_classes"])

    assert len(payload["automation_policy"]) == 2
    assert payload["launch_gate"]["readiness_percent"] >= 0
    assert "summary_ar" in payload["launch_gate"]
    assert len(payload["next_moves"]) >= 3

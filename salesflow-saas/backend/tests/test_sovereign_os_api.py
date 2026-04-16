import pytest


@pytest.mark.asyncio
async def test_sovereign_control_center_public_demo(client):
    response = await client.get("/api/v1/sovereign-os/control-center")

    assert response.status_code == 200
    data = response.json()

    assert data["product_name"].startswith("Dealix Sovereign")
    assert data["snapshot"]["demo_mode"] is True
    assert len(data["planes"]) == 5
    assert any(room["id"] == "approval-center" for plane in data["planes"] for room in plane["rooms"])
    assert any(item["provider"] == "groq" for item in data["model_routing"])

import pytest


@pytest.mark.asyncio
async def test_operations_snapshot_public_demo(client):
    r = await client.get("/api/v1/operations/snapshot")
    assert r.status_code == 200
    data = r.json()
    assert data.get("demo_mode") is True
    assert "connectors" in data
    assert len(data["connectors"]) >= 1


@pytest.mark.asyncio
async def test_operations_command_center_public_demo(client):
    r = await client.get("/api/v1/operations/command-center")
    assert r.status_code == 200
    data = r.json()
    assert data.get("demo_mode") is True
    assert data["headline"]["system_name_ar"].startswith("Dealix Sovereign")
    assert len(data["planes"]) == 5
    assert len(data["approval_classes"]) >= 3
    assert len(data["commitment_gates"]) >= 4
    assert any(surface["slug"] == "executive-room" for surface in data["surfaces"])
    assert any(surface["slug"] == "partner-room" for surface in data["surfaces"])
    assert len(data["gaps"]) >= 1
    assert "benchmark_dimensions" in data["model_routing"]

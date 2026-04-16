import pytest
import uuid


@pytest.mark.asyncio
async def test_operations_snapshot_public_demo(client):
    r = await client.get("/api/v1/operations/snapshot")
    assert r.status_code == 200
    data = r.json()
    assert data.get("demo_mode") is True
    assert "connectors" in data
    assert len(data["connectors"]) >= 1


@pytest.mark.asyncio
async def test_command_center_authenticated_after_register(client):
    suffix = uuid.uuid4().hex[:10]
    email = f"command_center_{suffix}@dealix.test"
    password = "Dealix12345"

    register = await client.post(
        "/api/v1/auth/register",
        json={
            "company_name": f"Command Center QA {suffix}",
            "full_name": "QA User",
            "email": email,
            "password": password,
        },
    )
    assert register.status_code == 200, register.text
    token = register.json()["access_token"]

    response = await client.get(
        "/api/v1/operations/command-center",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200, response.text
    payload = response.json()
    assert payload["demo_mode"] is False
    assert payload["headline"]["operating_mode"] == "executive_command_center"
    assert any(item["slug"] == "approval-center" for item in payload["surfaces"])
    assert any(item["key"] == "sales_revenue_os" for item in payload["operating_systems"])


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

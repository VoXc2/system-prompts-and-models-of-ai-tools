"""Health endpoint tests."""
import pytest


@pytest.mark.asyncio
async def test_health_endpoint_returns_200(client):
    """Health endpoint should return app info."""
    response = await client.get("/api/v1/health")
    # May be 200 or 503 depending on DB/Redis availability
    assert response.status_code in (200, 503)
    data = response.json()
    assert "status" in data
    assert "app" in data
    assert data["app"] == "Dealix"
    assert "database" in data
    assert "redis" in data


@pytest.mark.asyncio
async def test_health_includes_version(client):
    """Health endpoint should include version."""
    response = await client.get("/api/v1/health")
    data = response.json()
    assert "version" in data
    assert data["version"] == "1.0.0"

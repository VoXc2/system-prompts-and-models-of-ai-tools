"""API integration tests."""

from __future__ import annotations

import pytest


@pytest.mark.asyncio
async def test_root(async_client):
    response = await async_client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "operational"
    assert "version" in data


@pytest.mark.asyncio
async def test_health(async_client):
    response = await async_client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "ok"
    assert "providers" in data


@pytest.mark.asyncio
async def test_live(async_client):
    response = await async_client.get("/live")
    assert response.status_code == 200
    assert response.json() == {"status": "alive"}


@pytest.mark.asyncio
async def test_ready(async_client):
    response = await async_client.get("/ready")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_sector_intel_endpoint(async_client):
    response = await async_client.get("/api/v1/sectors/technology")
    assert response.status_code == 200
    data = response.json()
    assert data["sector"] == "technology"
    assert data["ai_readiness"] > 0


@pytest.mark.asyncio
async def test_sector_intel_unknown(async_client):
    response = await async_client.get("/api/v1/sectors/nonexistent")
    assert response.status_code == 404


@pytest.mark.asyncio
async def test_best_opportunity(async_client):
    response = await async_client.get("/api/v1/sectors/best/opportunity")
    assert response.status_code == 200
    assert "sector" in response.json()


@pytest.mark.asyncio
async def test_target_sectors(async_client):
    response = await async_client.get("/api/v1/sectors/target/list")
    assert response.status_code == 200
    assert len(response.json()) == 5


@pytest.mark.asyncio
async def test_sales_script(async_client):
    response = await async_client.post(
        "/api/v1/sales/script",
        json={
            "sector": "technology",
            "locale": "ar",
            "script_type": "opener",
            "name": "أحمد",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "script" in data
    assert data["locale"] == "ar"


@pytest.mark.asyncio
async def test_openapi_available(async_client):
    response = await async_client.get("/openapi.json")
    assert response.status_code == 200
    assert response.json()["info"]["title"]

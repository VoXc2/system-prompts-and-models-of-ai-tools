"""Lead endpoint tests."""
import pytest


@pytest.mark.asyncio
async def test_leads_requires_auth(client):
    """Leads endpoint should require authentication."""
    response = await client.get("/api/v1/leads")
    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_create_lead_requires_auth(client):
    """Creating a lead should require authentication."""
    response = await client.post(
        "/api/v1/leads",
        json={"name": "Test Lead", "phone": "+966500000000"},
    )
    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_leads_with_auth(client, auth_headers):
    """Leads endpoint with valid auth should not return 401."""
    headers = {k: v for k, v in auth_headers.items() if not k.startswith("_")}
    response = await client.get("/api/v1/leads", headers=headers)
    # Should not be 401 - might be 200 or 500 if DB not available
    assert response.status_code != 401

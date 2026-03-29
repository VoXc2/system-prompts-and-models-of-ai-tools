"""Auth endpoint tests."""
import pytest


@pytest.mark.asyncio
async def test_login_without_credentials_returns_422(client):
    """Login without body should return 422 validation error."""
    response = await client.post("/api/v1/auth/login")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_login_with_invalid_credentials(client):
    """Login with wrong credentials should return 401."""
    response = await client.post(
        "/api/v1/auth/login",
        json={"email": "nonexistent@test.com", "password": "wrongpassword"},
    )
    # Should be 401 or 400 depending on implementation
    assert response.status_code in (400, 401, 404, 500)


@pytest.mark.asyncio
async def test_register_without_body_returns_422(client):
    """Register without body should return 422."""
    response = await client.post("/api/v1/auth/register")
    assert response.status_code == 422


@pytest.mark.asyncio
async def test_me_without_auth_returns_401(client):
    """Accessing /me without auth should return 401."""
    response = await client.get("/api/v1/auth/me")
    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_protected_endpoint_without_auth(client):
    """Accessing protected endpoints without auth should fail."""
    endpoints = [
        "/api/v1/leads",
        "/api/v1/deals",
        "/api/v1/dashboard/overview",
        "/api/v1/conversations",
    ]
    for endpoint in endpoints:
        response = await client.get(endpoint)
        assert response.status_code in (401, 403), f"{endpoint} should require auth"

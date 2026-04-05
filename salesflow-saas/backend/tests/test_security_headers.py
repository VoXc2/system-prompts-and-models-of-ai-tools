"""رؤوس الأمان على الاستجابات + حقل git_sha في /health عند توفر المتغير."""

import pytest


@pytest.mark.asyncio
async def test_security_headers_present_on_health(client):
    r = await client.get("/api/v1/health")
    assert r.status_code == 200
    assert r.headers.get("x-content-type-options") == "nosniff"
    assert r.headers.get("x-frame-options") == "SAMEORIGIN"


@pytest.mark.asyncio
async def test_health_includes_git_sha_when_env_set(monkeypatch, client):
    monkeypatch.setenv("DEALIX_GIT_SHA", "abc123deadbeef" * 2)
    r = await client.get("/api/v1/health")
    assert r.status_code == 200
    data = r.json()
    assert data.get("git_sha") == ("abc123deadbeef" * 2)[:40]

import pytest

from app.config import get_settings
from app.middleware.internal_api import _exempt_path


def test_internal_api_exempt_paths():
    assert _exempt_path("/api/v1/health")
    assert _exempt_path("/api/v1/agent-frameworks")
    assert _exempt_path("/api/v1/ready")
    assert _exempt_path("/api/v1/deployment-readiness")
    assert _exempt_path("/api/v1/webhooks/whatsapp")
    assert _exempt_path("/api/v1/marketing/hub")
    assert _exempt_path("/api/v1/strategy/summary")
    assert _exempt_path("/api/v1/value-proposition/")
    assert _exempt_path("/api/v1/customer-onboarding/journey")
    assert _exempt_path("/api/v1/sales-os/overview")
    assert _exempt_path("/api/v1/operations/snapshot")
    assert _exempt_path("/api/v1/affiliates/program")
    assert _exempt_path("/api/v1/affiliates/register")
    assert _exempt_path("/api/v1/affiliates/leaderboard/top")
    assert not _exempt_path("/api/v1/sales-os/quota")
    assert not _exempt_path("/api/v1/deals")


def test_strategy_marketing_exempt_only_when_public(monkeypatch):
    monkeypatch.setenv("DEALIX_PUBLIC_STRATEGY_MARKETING", "false")
    get_settings.cache_clear()
    assert not _exempt_path("/api/v1/strategy/summary")
    assert not _exempt_path("/api/v1/marketing/hub")
    monkeypatch.setenv("DEALIX_PUBLIC_STRATEGY_MARKETING", "true")
    get_settings.cache_clear()
    assert _exempt_path("/api/v1/strategy/summary")
    assert _exempt_path("/api/v1/marketing/hub")


@pytest.mark.asyncio
async def test_value_proposition_public_json(client):
    r = await client.get("/api/v1/value-proposition/")
    assert r.status_code == 200
    data = r.json()
    assert "pillars" in data
    assert len(data["pillars"]) >= 4
    assert data["pillars"][0]["title_ar"]

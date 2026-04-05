"""Brain OS + Upgrade Director — smoke and launch gates."""

from __future__ import annotations

import pytest

from app.services.upgrade_director.snapshot import collect_local_dependency_snapshot


def test_local_dependency_snapshot_readable():
    snap = collect_local_dependency_snapshot()
    assert "backend_root" in snap
    assert isinstance(snap.get("requirements_pins", {}), dict)


@pytest.mark.launch
@pytest.mark.asyncio
async def test_brain_health_public(client):
    r = await client.get("/api/v1/brain/health")
    assert r.status_code == 200, r.text
    body = r.json()
    assert "component" in body or "agent_framework" in body


@pytest.mark.launch
@pytest.mark.asyncio
async def test_brain_agent_registry_public(client):
    r = await client.get("/api/v1/brain/agents")
    assert r.status_code == 200
    agents = r.json().get("agents", [])
    assert len(agents) >= 8
    keys = {a["key"] for a in agents}
    assert "lead_qualification" in keys
    assert "monitoring" in keys


@pytest.mark.launch
@pytest.mark.asyncio
async def test_brain_skills_registry(client):
    r = await client.get("/api/v1/brain/skills")
    assert r.status_code == 200
    skills = r.json().get("skills", [])
    assert len(skills) >= 5


@pytest.mark.asyncio
async def test_upgrade_director_hourly_disabled_without_env():
    from app.workers.upgrade_director_tasks import upgrade_director_hourly_tick

    out = upgrade_director_hourly_tick()
    assert out.get("status") == "disabled"

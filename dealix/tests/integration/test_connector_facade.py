"""Integration test for ConnectorFacade retry + audit."""

from __future__ import annotations

import asyncio

import pytest

from dealix.connectors import ConnectorFacade, ConnectorPolicy


@pytest.mark.asyncio
async def test_facade_retries_then_succeeds():
    calls = {"n": 0}

    async def flaky(payload):
        calls["n"] += 1
        if calls["n"] < 2:
            raise RuntimeError("temporary failure")
        return {"ok": True, "echo": payload}

    facade = ConnectorFacade(policies={"test": ConnectorPolicy(max_retries=3, backoff_base=0.01)})
    r = await facade.call("test", "echo", flaky, payload={"hello": "world"})
    assert r.ok
    assert r.attempts == 2
    assert r.data["echo"]["hello"] == "world"


@pytest.mark.asyncio
async def test_facade_gives_up_after_max_retries():
    async def always_fails(payload):
        raise RuntimeError("persistent failure")

    facade = ConnectorFacade(policies={"test": ConnectorPolicy(max_retries=2, backoff_base=0.01)})
    r = await facade.call("test", "op", always_fails, payload={})
    assert not r.ok
    assert "persistent" in (r.error or "")


@pytest.mark.asyncio
async def test_facade_policy_disable():
    facade = ConnectorFacade(policies={"test": ConnectorPolicy(allow=False)})
    r = await facade.call("test", "op", lambda p: asyncio.sleep(0), payload=None)
    assert not r.ok
    assert r.error == "connector_disabled_by_policy"

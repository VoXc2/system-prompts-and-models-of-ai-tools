"""Tests for D0 Launch Hardening modules — DLQ, PostHog, Circuit Breaker, Pricing."""

import asyncio
import json
import time
import pytest


# ── DLQ Tests ────────────────────────────────────────────────────


class FakeRedis:
    """Minimal async Redis mock for DLQ tests."""

    def __init__(self):
        self._data: dict[str, list[str]] = {}

    async def rpush(self, key: str, value: str) -> int:
        self._data.setdefault(key, []).append(value)
        return len(self._data[key])

    async def lpop(self, key: str) -> str | None:
        lst = self._data.get(key, [])
        return lst.pop(0) if lst else None

    async def lrange(self, key: str, start: int, end: int) -> list[str]:
        lst = self._data.get(key, [])
        return lst[start : end + 1]

    async def llen(self, key: str) -> int:
        return len(self._data.get(key, []))

    async def delete(self, key: str) -> int:
        removed = len(self._data.pop(key, []))
        return removed

    async def scan(self, cursor: int, match: str = "*", count: int = 100):
        keys = [k for k in self._data if k.startswith(match.replace("*", ""))]
        return (0, keys)


@pytest.fixture
def fake_redis():
    return FakeRedis()


@pytest.mark.asyncio
async def test_dlq_push_and_peek(fake_redis):
    from app.services.dlq import DeadLetterQueue

    dlq = DeadLetterQueue(redis_client=fake_redis)
    entry_id = await dlq.push("webhooks", {"url": "/test"}, "timeout error")
    assert entry_id is not None

    entries = await dlq.peek("webhooks")
    assert len(entries) == 1
    assert entries[0].queue == "webhooks"
    assert entries[0].error == "timeout error"


@pytest.mark.asyncio
async def test_dlq_depth(fake_redis):
    from app.services.dlq import DeadLetterQueue

    dlq = DeadLetterQueue(redis_client=fake_redis)
    await dlq.push("webhooks", {"a": 1}, "err1")
    await dlq.push("webhooks", {"b": 2}, "err2")
    assert await dlq.depth("webhooks") == 2


@pytest.mark.asyncio
async def test_dlq_drain_success(fake_redis):
    from app.services.dlq import DeadLetterQueue

    dlq = DeadLetterQueue(redis_client=fake_redis)
    await dlq.push("webhooks", {"x": 1}, "err")

    async def handler(payload):
        pass  # success

    result = await dlq.drain("webhooks", handler)
    assert result["processed"] == 1
    assert result["succeeded"] == 1
    assert result["re_queued"] == 0
    assert await dlq.depth("webhooks") == 0


@pytest.mark.asyncio
async def test_dlq_drain_retry(fake_redis):
    from app.services.dlq import DeadLetterQueue

    dlq = DeadLetterQueue(redis_client=fake_redis)
    await dlq.push("webhooks", {"x": 1}, "err", max_retries=3)

    async def handler(payload):
        raise RuntimeError("still broken")

    result = await dlq.drain("webhooks", handler, batch_size=1)
    assert result["processed"] == 1
    assert result["re_queued"] == 1
    assert await dlq.depth("webhooks") == 1


@pytest.mark.asyncio
async def test_dlq_drain_dead(fake_redis):
    from app.services.dlq import DeadLetterQueue

    dlq = DeadLetterQueue(redis_client=fake_redis)
    await dlq.push("webhooks", {"x": 1}, "err", attempt=4, max_retries=5)

    async def handler(payload):
        raise RuntimeError("permanent failure")

    result = await dlq.drain("webhooks", handler)
    assert result["dead"] == 1
    assert await dlq.depth("webhooks") == 0


@pytest.mark.asyncio
async def test_dlq_purge(fake_redis):
    from app.services.dlq import DeadLetterQueue

    dlq = DeadLetterQueue(redis_client=fake_redis)
    await dlq.push("old", {"x": 1}, "err")
    await dlq.push("old", {"x": 2}, "err")
    purged = await dlq.purge("old")
    assert purged == 2
    assert await dlq.depth("old") == 0


@pytest.mark.asyncio
async def test_dlq_all_queues(fake_redis):
    from app.services.dlq import DeadLetterQueue

    dlq = DeadLetterQueue(redis_client=fake_redis)
    await dlq.push("webhooks", {}, "e")
    await dlq.push("payments", {}, "e")
    await dlq.push("payments", {}, "e")
    queues = await dlq.all_queues()
    assert queues.get("webhooks") == 1
    assert queues.get("payments") == 2


# ── PostHog Tests ────────────────────────────────────────────────


def test_posthog_disabled_without_key():
    from app.services.posthog_client import PostHogClient

    client = PostHogClient(api_key="")
    assert not client._enabled


@pytest.mark.asyncio
async def test_posthog_skip_when_disabled():
    from app.services.posthog_client import PostHogClient, FunnelEvent

    client = PostHogClient(api_key="")
    result = await client.capture("user-1", FunnelEvent.LEAD_CAPTURED)
    assert result is False


def test_posthog_enabled_with_key():
    from app.services.posthog_client import PostHogClient

    client = PostHogClient(api_key="phc_test123")
    assert client._enabled


def test_funnel_events_values():
    from app.services.posthog_client import FunnelEvent

    assert FunnelEvent.LANDING_VIEW.value == "landing_view"
    assert FunnelEvent.DEAL_WON.value == "deal_won"
    assert FunnelEvent.PAYMENT_SUCCEEDED.value == "payment_succeeded"
    assert len(FunnelEvent) >= 10


# ── Circuit Breaker Tests ────────────────────────────────────────


def test_circuit_breaker_starts_closed():
    from app.utils.circuit_breaker import CircuitBreaker

    cb = CircuitBreaker("test")
    assert cb.state.value == "closed"


def test_circuit_breaker_opens_on_threshold():
    from app.utils.circuit_breaker import CircuitBreaker

    cb = CircuitBreaker("test", failure_threshold=3)
    cb.record_failure()
    cb.record_failure()
    assert cb.state.value == "closed"
    cb.record_failure()
    assert cb.state.value == "open"


@pytest.mark.asyncio
async def test_circuit_breaker_fails_fast_when_open():
    from app.utils.circuit_breaker import CircuitBreaker, CircuitOpenError

    cb = CircuitBreaker("test", failure_threshold=1)
    cb.record_failure()
    assert cb.state.value == "open"

    async def dummy():
        return "ok"

    with pytest.raises(CircuitOpenError):
        await cb.call(dummy)


def test_circuit_breaker_resets_on_success():
    from app.utils.circuit_breaker import CircuitBreaker

    cb = CircuitBreaker("test", failure_threshold=3)
    cb.record_failure()
    cb.record_failure()
    cb.record_success()
    assert cb._failure_count == 0
    assert cb.state.value == "closed"


def test_circuit_breaker_registry():
    from app.utils.circuit_breaker import CircuitBreakerRegistry

    reg = CircuitBreakerRegistry()
    cb1 = reg.get("hubspot")
    cb2 = reg.get("hubspot")
    assert cb1 is cb2
    cb3 = reg.get("calendly")
    assert cb3 is not cb1
    states = reg.all_states()
    assert "hubspot" in states
    assert "calendly" in states


# ── Pricing Tests ────────────────────────────────────────────────


@pytest.mark.asyncio
async def test_pricing_plans_endpoint():
    from fastapi.testclient import TestClient
    from app.api.v1.pricing import router
    from fastapi import FastAPI

    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)

    resp = client.get("/pricing/plans")
    assert resp.status_code == 200
    data = resp.json()
    assert "plans" in data
    assert len(data["plans"]) >= 3
    assert data["currency"] == "SAR"

    starter = next(p for p in data["plans"] if p["id"] == "starter")
    assert starter["price_sar"] == 990
    assert "features_ar" in starter


@pytest.mark.asyncio
async def test_pricing_plan_by_id():
    from fastapi.testclient import TestClient
    from app.api.v1.pricing import router
    from fastapi import FastAPI

    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)

    resp = client.get("/pricing/plans/growth")
    assert resp.status_code == 200
    assert resp.json()["plan"]["id"] == "growth"

    resp404 = client.get("/pricing/plans/nonexistent")
    assert resp404.status_code == 404


@pytest.mark.asyncio
async def test_checkout_no_moyasar_key():
    from fastapi.testclient import TestClient
    from app.api.v1.pricing import router
    from fastapi import FastAPI

    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)

    resp = client.post(
        "/pricing/checkout",
        json={
            "plan_id": "starter",
            "customer_name": "Test User",
            "customer_email": "test@example.com",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "checkout_unavailable"


@pytest.mark.asyncio
async def test_checkout_enterprise_contact_sales():
    from fastapi.testclient import TestClient
    from app.api.v1.pricing import router
    from fastapi import FastAPI

    app = FastAPI()
    app.include_router(router)
    client = TestClient(app)

    resp = client.post(
        "/pricing/checkout",
        json={
            "plan_id": "enterprise",
            "customer_name": "Corp",
            "customer_email": "ceo@corp.sa",
        },
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "contact_sales"

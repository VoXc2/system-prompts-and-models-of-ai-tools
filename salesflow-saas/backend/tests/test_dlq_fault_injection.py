"""DLQ Fault Injection Tests — verify failure paths work correctly.

These tests simulate real failure scenarios:
1. Webhook handler crashes → entry lands in DLQ
2. DLQ drain retries and succeeds on second attempt
3. DLQ drain exhausts retries → entry marked dead
4. Circuit breaker opens after repeated failures
5. Circuit breaker recovers after timeout
"""

import pytest
import time


class FakeRedis:
    def __init__(self):
        self._data: dict[str, list[str]] = {}

    async def rpush(self, key, value):
        self._data.setdefault(key, []).append(value)
        return len(self._data[key])

    async def lpop(self, key):
        lst = self._data.get(key, [])
        return lst.pop(0) if lst else None

    async def lrange(self, key, start, end):
        return self._data.get(key, [])[start : end + 1]

    async def llen(self, key):
        return len(self._data.get(key, []))

    async def delete(self, key):
        return len(self._data.pop(key, []))

    async def scan(self, cursor, match="*", count=100):
        keys = [k for k in self._data if k.startswith(match.replace("*", ""))]
        return (0, keys)


@pytest.mark.asyncio
async def test_webhook_crash_lands_in_dlq():
    """Simulate: Moyasar webhook handler throws → payload goes to DLQ."""
    from app.services.dlq import DeadLetterQueue

    dlq = DeadLetterQueue(redis_client=FakeRedis())
    webhook_payload = {
        "type": "payment_paid",
        "data": {"id": "pay_test_123", "amount": 99000},
    }

    try:
        raise ConnectionError("DB connection lost during webhook processing")
    except ConnectionError as exc:
        await dlq.push("moyasar_webhooks", webhook_payload, str(exc))

    assert await dlq.depth("moyasar_webhooks") == 1
    entries = await dlq.peek("moyasar_webhooks")
    assert entries[0].payload["data"]["id"] == "pay_test_123"
    assert "DB connection lost" in entries[0].error


@pytest.mark.asyncio
async def test_dlq_drain_succeeds_on_second_attempt():
    """Simulate: first retry fails, second succeeds."""
    from app.services.dlq import DeadLetterQueue

    dlq = DeadLetterQueue(redis_client=FakeRedis())
    await dlq.push("hubspot_sync", {"lead_id": "abc"}, "timeout", max_retries=5)

    call_count = 0

    async def flaky_handler(payload):
        nonlocal call_count
        call_count += 1
        if call_count == 1:
            raise TimeoutError("HubSpot timeout")

    # First drain: fails, re-queues
    r1 = await dlq.drain("hubspot_sync", flaky_handler, batch_size=1)
    assert r1["re_queued"] == 1

    # Second drain: succeeds
    r2 = await dlq.drain("hubspot_sync", flaky_handler, batch_size=1)
    assert r2["succeeded"] == 1
    assert await dlq.depth("hubspot_sync") == 0


@pytest.mark.asyncio
async def test_dlq_exhausts_retries_marks_dead():
    """Simulate: permanent failure exhausts all retries."""
    from app.services.dlq import DeadLetterQueue

    dlq = DeadLetterQueue(redis_client=FakeRedis())
    await dlq.push("calendly_webhooks", {"event": "booked"}, "err", attempt=4, max_retries=5)

    async def always_fail(payload):
        raise RuntimeError("Calendly API permanently broken")

    result = await dlq.drain("calendly_webhooks", always_fail, batch_size=1)
    assert result["dead"] == 1
    assert result["re_queued"] == 0
    assert await dlq.depth("calendly_webhooks") == 0


@pytest.mark.asyncio
async def test_circuit_breaker_opens_and_recovers():
    """Simulate: HubSpot fails 3x → circuit opens → recovers after timeout."""
    from app.utils.circuit_breaker import CircuitBreaker, CircuitOpenError

    cb = CircuitBreaker("hubspot_api", failure_threshold=3, recovery_timeout=0.1)

    # 3 failures → opens
    for _ in range(3):
        cb.record_failure()
    assert cb.state.value == "open"

    # Fails fast when open
    async def hubspot_call():
        return {"contacts": []}

    with pytest.raises(CircuitOpenError):
        await cb.call(hubspot_call)

    # Wait for recovery timeout
    time.sleep(0.15)

    # Should be half-open now → probe succeeds → closes
    result = await cb.call(hubspot_call)
    assert result == {"contacts": []}
    assert cb.state.value == "closed"


@pytest.mark.asyncio
async def test_circuit_breaker_stays_open_on_probe_failure():
    """Simulate: probe call also fails → stays open."""
    from app.utils.circuit_breaker import CircuitBreaker

    cb = CircuitBreaker("moyasar_api", failure_threshold=2, recovery_timeout=0.1)
    cb.record_failure()
    cb.record_failure()
    assert cb.state.value == "open"

    time.sleep(0.15)  # allow half-open

    async def still_broken():
        raise ConnectionError("Moyasar still down")

    with pytest.raises(ConnectionError):
        await cb.call(still_broken)

    assert cb.state.value == "open"


@pytest.mark.asyncio
async def test_multi_queue_dlq_isolation():
    """Verify different queues don't interfere with each other."""
    from app.services.dlq import DeadLetterQueue

    redis = FakeRedis()
    dlq = DeadLetterQueue(redis_client=redis)

    await dlq.push("webhooks", {"src": "webhook"}, "err1")
    await dlq.push("webhooks", {"src": "webhook2"}, "err2")
    await dlq.push("payments", {"src": "payment"}, "err3")

    assert await dlq.depth("webhooks") == 2
    assert await dlq.depth("payments") == 1

    await dlq.purge("webhooks")
    assert await dlq.depth("webhooks") == 0
    assert await dlq.depth("payments") == 1  # untouched

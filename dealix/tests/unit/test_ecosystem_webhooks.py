"""Smoke tests for the Ecosystem layer — outbound webhook dispatcher."""

from __future__ import annotations

import json
import time

import pytest

from auto_client_acquisition.ecosystem.webhook_dispatcher import (
    EVENT_TYPES,
    MAX_ATTEMPTS,
    RETRY_SCHEDULE_SECONDS,
    DeliveryResult,
    WebhookSubscription,
    deliver_once,
    dispatch,
    make_event,
    matching_subscriptions,
    next_retry_delay,
    serialize_envelope,
    should_retry,
    sign_payload,
    verify_signature,
)


# ── Event taxonomy ────────────────────────────────────────────────
def test_event_types_includes_core_events():
    assert "lead.created" in EVENT_TYPES
    assert "deal.won" in EVENT_TYPES
    assert "payment.received" in EVENT_TYPES
    assert "churn.predicted" in EVENT_TYPES


def test_event_types_no_duplicates():
    assert len(EVENT_TYPES) == len(set(EVENT_TYPES))


# ── Event creation ────────────────────────────────────────────────
def test_make_event_assigns_unique_ids():
    e1 = make_event(event_type="lead.created", customer_id="c1", payload={})
    e2 = make_event(event_type="lead.created", customer_id="c1", payload={})
    assert e1.event_id != e2.event_id
    assert e1.event_id.startswith("evt_")


def test_event_envelope_has_expected_keys():
    e = make_event(event_type="deal.won", customer_id="c1", payload={"a": 1})
    env = e.envelope()
    for key in ("id", "type", "customer_id", "timestamp", "api_version", "data"):
        assert key in env


# ── HMAC signing — round trip ─────────────────────────────────────
def test_sign_then_verify_round_trip():
    secret = "whsec_test_abc123"
    body = b'{"hello":"world"}'
    ts = int(time.time())
    header = sign_payload(secret=secret, body=body, timestamp=ts)
    ok, err = verify_signature(secret=secret, signature_header=header, body=body)
    assert ok is True
    assert err is None


def test_verify_rejects_wrong_secret():
    body = b"x"
    ts = int(time.time())
    header = sign_payload(secret="real", body=body, timestamp=ts)
    ok, err = verify_signature(secret="wrong", signature_header=header, body=body)
    assert ok is False
    assert err == "signature_mismatch"


def test_verify_rejects_stale_timestamp():
    body = b"x"
    old_ts = int(time.time()) - 3600  # 1h old
    header = sign_payload(secret="s", body=body, timestamp=old_ts)
    ok, err = verify_signature(secret="s", signature_header=header, body=body)
    assert ok is False
    assert err == "stale_signature"


def test_verify_rejects_malformed_header():
    ok, err = verify_signature(secret="s", signature_header="garbage", body=b"x")
    assert ok is False


# ── Retry policy ──────────────────────────────────────────────────
def test_retry_schedule_increases():
    """Backoff must be non-decreasing."""
    for i in range(len(RETRY_SCHEDULE_SECONDS) - 1):
        assert RETRY_SCHEDULE_SECONDS[i] <= RETRY_SCHEDULE_SECONDS[i + 1]


def test_next_retry_returns_none_at_max():
    assert next_retry_delay(MAX_ATTEMPTS) is None


def test_should_retry_5xx():
    assert should_retry(500, None) is True
    assert should_retry(503, None) is True


def test_should_retry_429():
    assert should_retry(429, None) is True


def test_should_retry_408():
    assert should_retry(408, None) is True


def test_should_not_retry_4xx_clienterror():
    """4xx (except 408/429) means subscriber bug — don't retry."""
    assert should_retry(400, None) is False
    assert should_retry(401, None) is False
    assert should_retry(404, None) is False


def test_should_not_retry_2xx():
    assert should_retry(200, None) is False
    assert should_retry(204, None) is False


def test_should_retry_network_error():
    assert should_retry(None, "connection refused") is True


# ── Subscription filtering ────────────────────────────────────────
def test_matching_subscriptions_filters_by_customer():
    subs = [
        WebhookSubscription("c1", "https://a.example", "s1", events=()),
        WebhookSubscription("c2", "https://b.example", "s2", events=()),
    ]
    out = matching_subscriptions(
        subscriptions=subs, event_type="lead.created", customer_id="c1"
    )
    assert len(out) == 1
    assert out[0].customer_id == "c1"


def test_empty_events_means_subscribe_to_all():
    subs = [WebhookSubscription("c1", "https://a", "s", events=())]
    out = matching_subscriptions(
        subscriptions=subs, event_type="ANY_EVENT", customer_id="c1"
    )
    assert len(out) == 1


def test_specific_events_filter_excludes_others():
    subs = [
        WebhookSubscription("c1", "https://a", "s", events=("deal.won",)),
    ]
    out = matching_subscriptions(
        subscriptions=subs, event_type="lead.created", customer_id="c1"
    )
    assert out == []


def test_disabled_subscription_excluded():
    subs = [
        WebhookSubscription("c1", "https://a", "s", events=(), enabled=False),
    ]
    out = matching_subscriptions(
        subscriptions=subs, event_type="lead.created", customer_id="c1"
    )
    assert out == []


# ── Pluggable transport — testable without HTTP ───────────────────
def test_deliver_once_with_fake_transport():
    captured = {}

    def fake_transport(url, body, headers):
        captured["url"] = url
        captured["body"] = body
        captured["headers"] = headers
        return DeliveryResult(status_code=200, duration_ms=50)

    sub = WebhookSubscription("c1", "https://hook.example", "secret", events=())
    evt = make_event(event_type="lead.created", customer_id="c1", payload={"x": 1})
    d = deliver_once(subscription=sub, event=evt, transport=fake_transport)

    assert d.success is True
    assert d.status_code == 200
    assert d.duration_ms == 50
    # Required headers
    assert captured["headers"]["Dealix-Event-Id"] == evt.event_id
    assert captured["headers"]["Dealix-Event-Type"] == "lead.created"
    assert captured["headers"]["Dealix-Signature"].startswith("t=")


def test_deliver_signature_verifies_at_destination():
    """The signature emitted must be verifiable using the same secret on the receiver side."""
    captured = {}

    def fake_transport(url, body, headers):
        captured["body"] = body
        captured["headers"] = headers
        return DeliveryResult(status_code=200, duration_ms=10)

    secret = "whsec_xyz"
    sub = WebhookSubscription("c1", "https://hook", secret, events=())
    evt = make_event(event_type="deal.won", customer_id="c1", payload={"a": 1})
    deliver_once(subscription=sub, event=evt, transport=fake_transport)

    ok, err = verify_signature(
        secret=secret,
        signature_header=captured["headers"]["Dealix-Signature"],
        body=captured["body"],
    )
    assert ok is True, f"verification should succeed, got error: {err}"


def test_dispatch_summary_counts_delivered_vs_failed():
    def transport_alternates(url, body, headers):
        if "good" in url:
            return DeliveryResult(status_code=200, duration_ms=20)
        return DeliveryResult(status_code=500, duration_ms=5)

    subs = [
        WebhookSubscription("c1", "https://good.example", "s1", events=()),
        WebhookSubscription("c1", "https://bad.example", "s2", events=()),
    ]
    evt = make_event(event_type="lead.created", customer_id="c1", payload={})
    summary = dispatch(subscriptions=subs, event=evt, transport=transport_alternates)
    assert summary.matched == 2
    assert summary.delivered == 1
    assert summary.failed == 1


# ── Stable serialization ──────────────────────────────────────────
def test_serialize_envelope_is_stable():
    e1 = make_event(event_type="x", customer_id="c", payload={"b": 2, "a": 1}, now=1)
    e2 = make_event(event_type="x", customer_id="c", payload={"a": 1, "b": 2}, now=1)
    # event_ids differ but payload serialization is sort-keyed
    s1 = serialize_envelope(e1)
    s2 = serialize_envelope(e2)
    # Strip event_id portion to compare structure
    s1_dict = json.loads(s1)
    s2_dict = json.loads(s2)
    assert s1_dict["data"] == s2_dict["data"]

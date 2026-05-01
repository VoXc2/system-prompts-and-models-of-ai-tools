"""
Outbound webhook dispatcher — Scale tier ecosystem play.

Customers register webhook endpoints, we POST events with HMAC signing.
Each event is signed with HMAC-SHA256(secret, payload) — verifiable on
receipt without sharing the secret.

Pure functions: building, signing, retry policy decisions.
Network I/O is pluggable via a `transport` callable so this module is testable
without httpx in the import path.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import time
import uuid
from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

# ── Event taxonomy — what Dealix emits to subscribed customers ─────
EVENT_TYPES: tuple[str, ...] = (
    "lead.created",
    "lead.qualified",
    "lead.disqualified",
    "lead.enriched",
    "draft.created",
    "draft.approved",
    "draft.sent",
    "reply.received",
    "reply.classified",
    "demo.booked",
    "demo.held",
    "deal.created",
    "deal.won",
    "deal.lost",
    "payment.received",
    "health.changed",
    "churn.predicted",
    "qbr.generated",
    "pulse.published",
)


@dataclass(frozen=True)
class WebhookSubscription:
    """A customer's registered webhook endpoint."""

    customer_id: str
    endpoint_url: str
    secret: str  # used to sign payloads — customer verifies on receipt
    events: tuple[str, ...] = ()  # empty = subscribe to all
    enabled: bool = True
    created_at: int = 0  # unix ts


@dataclass
class WebhookDelivery:
    """Single delivery attempt record (immutable per attempt)."""

    delivery_id: str
    event_id: str
    event_type: str
    customer_id: str
    endpoint_url: str
    attempt: int
    status_code: int | None = None
    success: bool = False
    error: str | None = None
    duration_ms: int | None = None
    timestamp: int = 0
    request_signature: str = ""


@dataclass
class WebhookEvent:
    """Outbound event envelope."""

    event_id: str
    event_type: str
    customer_id: str
    payload: dict[str, Any]
    timestamp: int
    api_version: str = "v1"

    def envelope(self) -> dict[str, Any]:
        return {
            "id": self.event_id,
            "type": self.event_type,
            "customer_id": self.customer_id,
            "timestamp": self.timestamp,
            "api_version": self.api_version,
            "data": self.payload,
        }


# ── Helpers ────────────────────────────────────────────────────────
def make_event(
    *,
    event_type: str,
    customer_id: str,
    payload: dict[str, Any],
    now: int | None = None,
) -> WebhookEvent:
    """Build a new event envelope with a deterministic id."""
    ts = now or int(time.time())
    eid = f"evt_{uuid.uuid4().hex[:24]}"
    return WebhookEvent(
        event_id=eid,
        event_type=event_type,
        customer_id=customer_id,
        payload=payload,
        timestamp=ts,
    )


def sign_payload(*, secret: str, body: bytes, timestamp: int) -> str:
    """
    Compute HMAC-SHA256 signature in Stripe-like format:
        t=<unix_ts>,v1=<hex_hmac>

    Customer side verifies by recomputing HMAC over `f"{t}.{body}"`.
    Replay window: customer should reject if |now - t| > 5 minutes.
    """
    msg = f"{timestamp}.".encode() + body
    digest = hmac.new(secret.encode("utf-8"), msg, hashlib.sha256).hexdigest()
    return f"t={timestamp},v1={digest}"


def serialize_envelope(event: WebhookEvent) -> bytes:
    """Stable JSON serialization for signing."""
    return json.dumps(event.envelope(), separators=(",", ":"), sort_keys=True).encode("utf-8")


# ── Retry policy — exponential backoff with jitter cap ─────────────
RETRY_SCHEDULE_SECONDS: tuple[int, ...] = (
    0,        # immediate
    30,       # 30s later
    300,      # 5min
    1800,     # 30min
    21600,    # 6h
    86400,    # 24h — last attempt
)
MAX_ATTEMPTS = len(RETRY_SCHEDULE_SECONDS)


def next_retry_delay(attempt: int) -> int | None:
    """Return seconds until next retry, or None if exhausted."""
    if attempt < 0 or attempt >= MAX_ATTEMPTS:
        return None
    return RETRY_SCHEDULE_SECONDS[attempt]


def should_retry(status_code: int | None, error: str | None) -> bool:
    """
    Retryable conditions:
    - Network error (no status_code)
    - 5xx server error
    - 408 Request Timeout
    - 429 Too Many Requests

    Non-retryable:
    - 2xx success
    - 4xx client error (subscriber bug — they need to fix their endpoint)
    """
    if status_code is None:
        return True  # network error
    if 200 <= status_code < 300:
        return False  # success
    if status_code in (408, 429):
        return True
    if 500 <= status_code < 600:
        return True
    return False


# ── Subscription filtering ─────────────────────────────────────────
def matching_subscriptions(
    *, subscriptions: list[WebhookSubscription], event_type: str, customer_id: str
) -> list[WebhookSubscription]:
    """Filter subscriptions by customer + event-type + enabled flag."""
    out = []
    for sub in subscriptions:
        if not sub.enabled:
            continue
        if sub.customer_id != customer_id:
            continue
        if sub.events and event_type not in sub.events:
            continue
        out.append(sub)
    return out


# ── Delivery — pluggable transport for testability ─────────────────
@dataclass
class DeliveryResult:
    """Returned by transport callable — testable without HTTP."""

    status_code: int | None = None
    error: str | None = None
    duration_ms: int = 0


TransportCallable = Callable[[str, bytes, dict[str, str]], DeliveryResult]


def _default_transport(url: str, body: bytes, headers: dict[str, str]) -> DeliveryResult:
    """Real HTTP transport — gated import to keep module testable."""
    try:
        import httpx
    except Exception as exc:  # pragma: no cover
        return DeliveryResult(error=f"httpx_import_failed: {exc}", duration_ms=0)
    started = time.monotonic()
    try:
        with httpx.Client(timeout=10.0, follow_redirects=False) as client:
            resp = client.post(url, content=body, headers=headers)
            duration = int((time.monotonic() - started) * 1000)
            return DeliveryResult(status_code=resp.status_code, duration_ms=duration)
    except Exception as exc:
        duration = int((time.monotonic() - started) * 1000)
        return DeliveryResult(error=str(exc)[:200], duration_ms=duration)


def deliver_once(
    *,
    subscription: WebhookSubscription,
    event: WebhookEvent,
    attempt: int = 1,
    transport: TransportCallable | None = None,
    extra_headers: dict[str, str] | None = None,
) -> WebhookDelivery:
    """One delivery attempt — pure logic + pluggable transport."""
    body = serialize_envelope(event)
    signature = sign_payload(secret=subscription.secret, body=body, timestamp=event.timestamp)
    headers = {
        "Content-Type": "application/json",
        "User-Agent": "Dealix-Webhooks/1.0",
        "Dealix-Event-Id": event.event_id,
        "Dealix-Event-Type": event.event_type,
        "Dealix-Signature": signature,
        "Dealix-Delivery-Attempt": str(attempt),
    }
    if extra_headers:
        headers.update(extra_headers)
    t = transport or _default_transport
    res = t(subscription.endpoint_url, body, headers)
    return WebhookDelivery(
        delivery_id=f"dlv_{uuid.uuid4().hex[:24]}",
        event_id=event.event_id,
        event_type=event.event_type,
        customer_id=subscription.customer_id,
        endpoint_url=subscription.endpoint_url,
        attempt=attempt,
        status_code=res.status_code,
        success=bool(res.status_code and 200 <= res.status_code < 300),
        error=res.error,
        duration_ms=res.duration_ms,
        timestamp=int(time.time()),
        request_signature=signature,
    )


# ── Convenience: dispatch to all matching subscriptions ────────────
@dataclass
class DispatchSummary:
    event_id: str
    event_type: str
    customer_id: str
    matched: int
    delivered: int
    failed: int
    deliveries: list[WebhookDelivery] = field(default_factory=list)


def dispatch(
    *,
    subscriptions: list[WebhookSubscription],
    event: WebhookEvent,
    transport: TransportCallable | None = None,
) -> DispatchSummary:
    """Dispatch event to matching subscriptions (single attempt each)."""
    matched = matching_subscriptions(
        subscriptions=subscriptions,
        event_type=event.event_type,
        customer_id=event.customer_id,
    )
    deliveries: list[WebhookDelivery] = []
    delivered = failed = 0
    for sub in matched:
        d = deliver_once(subscription=sub, event=event, attempt=1, transport=transport)
        deliveries.append(d)
        if d.success:
            delivered += 1
        else:
            failed += 1
    return DispatchSummary(
        event_id=event.event_id,
        event_type=event.event_type,
        customer_id=event.customer_id,
        matched=len(matched),
        delivered=delivered,
        failed=failed,
        deliveries=deliveries,
    )


# ── Verification helpers — published in our docs for customers ─────
def verify_signature(
    *, secret: str, signature_header: str, body: bytes, max_age_seconds: int = 300
) -> tuple[bool, str | None]:
    """
    Verify a Dealix-Signature header on the receiving side.

    Returns (is_valid, error_message_or_none).
    Customers will copy this snippet into their handler.
    """
    if not signature_header or "," not in signature_header:
        return False, "malformed_header"
    parts = dict(p.split("=", 1) for p in signature_header.split(",") if "=" in p)
    try:
        ts = int(parts.get("t", "0"))
    except ValueError:
        return False, "bad_timestamp"
    sig = parts.get("v1", "")
    if not sig:
        return False, "missing_v1"

    # Replay protection
    if abs(int(time.time()) - ts) > max_age_seconds:
        return False, "stale_signature"

    expected = hmac.new(
        secret.encode("utf-8"),
        f"{ts}.".encode() + body,
        hashlib.sha256,
    ).hexdigest()
    if not hmac.compare_digest(expected, sig):
        return False, "signature_mismatch"
    return True, None

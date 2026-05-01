"""
Ecosystem router — outbound webhooks platform.

Scale tier customers register HTTPS endpoints, Dealix POSTs HMAC-signed
events when matching activity occurs. This is the API/webhooks ecosystem
play that converts Dealix from a vertical SaaS into a Saudi B2B platform.

Endpoints:
    POST   /api/v1/ecosystem/webhooks                    — register endpoint
    GET    /api/v1/ecosystem/webhooks                    — list customer's subs
    GET    /api/v1/ecosystem/webhooks/{sub_id}           — get one
    PATCH  /api/v1/ecosystem/webhooks/{sub_id}           — toggle/update events
    DELETE /api/v1/ecosystem/webhooks/{sub_id}           — remove
    POST   /api/v1/ecosystem/webhooks/{sub_id}/test      — fire test event
    POST   /api/v1/ecosystem/events/emit                 — internal: emit event
    GET    /api/v1/ecosystem/deliveries                  — recent delivery log
    GET    /api/v1/ecosystem/event-types                 — list available events

Security:
- Each subscription gets its own HMAC secret (returned ONCE at creation).
- Customers verify signatures using `Dealix-Signature` header (Stripe-format).
- Failed deliveries auto-disable subscription after 20 consecutive failures.
"""

from __future__ import annotations

import logging
import secrets
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import APIRouter, Body, HTTPException, Query
from sqlalchemy import desc, select

from auto_client_acquisition.ecosystem.webhook_dispatcher import (
    EVENT_TYPES,
    WebhookSubscription,
    dispatch,
    make_event,
)
from db.models import WebhookDeliveryRecord, WebhookSubscriptionRecord
from db.session import async_session_factory

router = APIRouter(prefix="/api/v1/ecosystem", tags=["ecosystem"])
log = logging.getLogger(__name__)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _scrub_secret(record: WebhookSubscriptionRecord) -> dict[str, Any]:
    """Return subscription dict without the secret (one-time-shown only)."""
    return {
        "id": record.id,
        "customer_id": record.customer_id,
        "endpoint_url": record.endpoint_url,
        "events": list(record.events or []),
        "description": record.description,
        "enabled": record.enabled,
        "last_delivery_at": record.last_delivery_at.isoformat()
        if record.last_delivery_at
        else None,
        "last_status_code": record.last_status_code,
        "consecutive_failures": record.consecutive_failures,
        "created_at": record.created_at.isoformat() if record.created_at else None,
    }


async def _safe_commit(session) -> bool:
    try:
        await session.commit()
        return True
    except Exception as exc:  # pragma: no cover
        await session.rollback()
        log.warning("ecosystem_commit_failed: %s", exc)
        return False


# ── List allowed event types ───────────────────────────────────────
@router.get("/event-types")
async def list_event_types() -> dict[str, Any]:
    """Discovery endpoint — list every event type Dealix can emit."""
    descriptions = {
        "lead.created": "New lead recorded in the system.",
        "lead.qualified": "Lead passed ICP + qualification gates.",
        "lead.disqualified": "Lead rejected by qualifier (low fit).",
        "lead.enriched": "Lead enrichment completed — phone/email/company fields populated.",
        "draft.created": "Outbound draft (email/LinkedIn/WhatsApp) generated.",
        "draft.approved": "Human approved the draft for send.",
        "draft.sent": "Draft was sent through provider chain.",
        "reply.received": "Inbound reply received and persisted.",
        "reply.classified": "Reply classified — intent/sentiment/next-action set.",
        "demo.booked": "Prospect booked a demo via Calendly/portal.",
        "demo.held": "Demo confirmed completed.",
        "deal.created": "Deal record created (post-demo).",
        "deal.won": "Deal closed-won.",
        "deal.lost": "Deal closed-lost.",
        "payment.received": "Moyasar/Stripe webhook confirmed payment.",
        "health.changed": "Customer health bucket changed (healthy/at_risk/critical).",
        "churn.predicted": "Churn-prediction model flagged customer.",
        "qbr.generated": "Quarterly Business Review created for customer.",
        "pulse.published": "Saudi B2B Pulse monthly report published.",
    }
    return {
        "count": len(EVENT_TYPES),
        "events": [
            {"type": t, "description": descriptions.get(t, "")} for t in EVENT_TYPES
        ],
        "signature_format": "t=<unix>,v1=<hmac_hex>",
        "headers_emitted": [
            "Dealix-Event-Id",
            "Dealix-Event-Type",
            "Dealix-Signature",
            "Dealix-Delivery-Attempt",
        ],
        "verification_doc": "/docs#tag/ecosystem",
    }


# ── Register a webhook subscription ────────────────────────────────
@router.post("/webhooks")
async def create_subscription(
    customer_id: str = Body(..., embed=True),
    endpoint_url: str = Body(..., embed=True),
    events: list[str] = Body(default_factory=list, embed=True),
    description: str | None = Body(default=None, embed=True),
) -> dict[str, Any]:
    """
    Register a new webhook endpoint.

    Returns the secret ONCE — we never return it again. Customer must store it
    securely. If lost, they must rotate by deleting + creating a new subscription.
    """
    if not endpoint_url.startswith(("https://", "http://localhost")):
        raise HTTPException(
            status_code=400,
            detail="endpoint_url must be HTTPS (localhost allowed for dev only)",
        )

    invalid = [e for e in events if e not in EVENT_TYPES]
    if invalid:
        raise HTTPException(
            status_code=400,
            detail=f"unknown event types: {invalid}. See GET /event-types",
        )

    sub_id = f"whk_{uuid.uuid4().hex[:24]}"
    secret = f"whsec_{secrets.token_urlsafe(32)}"

    record = WebhookSubscriptionRecord(
        id=sub_id,
        customer_id=customer_id,
        endpoint_url=endpoint_url,
        secret=secret,
        events=list(events),
        description=description,
        enabled=True,
    )

    try:
        async with async_session_factory() as session:
            session.add(record)
            ok = await _safe_commit(session)
            if not ok:
                return {
                    "skipped_db_unreachable": True,
                    "would_create": _scrub_secret(record),
                    "secret": secret,  # still return for offline-mode demo
                }
    except Exception as exc:
        log.warning("create_subscription_failed: %s", exc)
        return {"error": str(exc)[:200], "skipped": True}

    return {
        "id": sub_id,
        "customer_id": customer_id,
        "endpoint_url": endpoint_url,
        "events": list(events) or "all",
        "description": description,
        "secret": secret,  # ⚠️ ONLY shown once — store securely
        "secret_warning": "Save this secret now — it will never be shown again.",
        "verification_example_python": (
            "import hmac, hashlib\n"
            "def verify(secret, sig_header, body):\n"
            "    parts = dict(p.split('=',1) for p in sig_header.split(','))\n"
            "    expected = hmac.new(\n"
            "        secret.encode(), f\"{parts['t']}.\".encode()+body, hashlib.sha256\n"
            "    ).hexdigest()\n"
            "    return hmac.compare_digest(expected, parts['v1'])"
        ),
    }


# ── List subscriptions ─────────────────────────────────────────────
@router.get("/webhooks")
async def list_subscriptions(
    customer_id: str = Query(...),
    enabled_only: bool = Query(default=False),
) -> dict[str, Any]:
    """List all subscriptions for a customer."""
    try:
        async with async_session_factory() as session:
            stmt = select(WebhookSubscriptionRecord).where(
                WebhookSubscriptionRecord.customer_id == customer_id
            )
            if enabled_only:
                stmt = stmt.where(WebhookSubscriptionRecord.enabled.is_(True))
            stmt = stmt.order_by(desc(WebhookSubscriptionRecord.created_at))
            rows = (await session.execute(stmt)).scalars().all()
            return {
                "customer_id": customer_id,
                "count": len(rows),
                "subscriptions": [_scrub_secret(r) for r in rows],
            }
    except Exception as exc:
        log.warning("list_subscriptions_failed: %s", exc)
        return {"customer_id": customer_id, "skipped_db_unreachable": True, "error": str(exc)[:200]}


# ── Get one ────────────────────────────────────────────────────────
@router.get("/webhooks/{sub_id}")
async def get_subscription(sub_id: str) -> dict[str, Any]:
    try:
        async with async_session_factory() as session:
            row = await session.get(WebhookSubscriptionRecord, sub_id)
            if not row:
                raise HTTPException(status_code=404, detail="subscription not found")
            return _scrub_secret(row)
    except HTTPException:
        raise
    except Exception as exc:
        log.warning("get_subscription_failed: %s", exc)
        return {"id": sub_id, "skipped_db_unreachable": True}


# ── Update enabled / events ────────────────────────────────────────
@router.patch("/webhooks/{sub_id}")
async def update_subscription(
    sub_id: str,
    enabled: bool | None = Body(default=None, embed=True),
    events: list[str] | None = Body(default=None, embed=True),
    description: str | None = Body(default=None, embed=True),
) -> dict[str, Any]:
    if events is not None:
        invalid = [e for e in events if e not in EVENT_TYPES]
        if invalid:
            raise HTTPException(status_code=400, detail=f"unknown events: {invalid}")

    try:
        async with async_session_factory() as session:
            row = await session.get(WebhookSubscriptionRecord, sub_id)
            if not row:
                raise HTTPException(status_code=404, detail="subscription not found")
            if enabled is not None:
                row.enabled = enabled
                if enabled:
                    row.consecutive_failures = 0
            if events is not None:
                row.events = list(events)
            if description is not None:
                row.description = description
            row.updated_at = _utcnow()
            await _safe_commit(session)
            return _scrub_secret(row)
    except HTTPException:
        raise
    except Exception as exc:
        log.warning("update_subscription_failed: %s", exc)
        return {"id": sub_id, "skipped_db_unreachable": True}


# ── Delete ─────────────────────────────────────────────────────────
@router.delete("/webhooks/{sub_id}")
async def delete_subscription(sub_id: str) -> dict[str, Any]:
    try:
        async with async_session_factory() as session:
            row = await session.get(WebhookSubscriptionRecord, sub_id)
            if not row:
                raise HTTPException(status_code=404, detail="subscription not found")
            await session.delete(row)
            await _safe_commit(session)
            return {"id": sub_id, "deleted": True}
    except HTTPException:
        raise
    except Exception as exc:
        log.warning("delete_subscription_failed: %s", exc)
        return {"id": sub_id, "skipped_db_unreachable": True}


# ── Test fire — dry-run dispatch with synthetic payload ────────────
@router.post("/webhooks/{sub_id}/test")
async def test_subscription(
    sub_id: str,
    event_type: str = Body(default="lead.created", embed=True),
) -> dict[str, Any]:
    """Send a synthetic test event to verify the customer's endpoint."""
    if event_type not in EVENT_TYPES:
        raise HTTPException(status_code=400, detail=f"unknown event type: {event_type}")

    try:
        async with async_session_factory() as session:
            row = await session.get(WebhookSubscriptionRecord, sub_id)
            if not row:
                raise HTTPException(status_code=404, detail="subscription not found")
            sub = WebhookSubscription(
                customer_id=row.customer_id,
                endpoint_url=row.endpoint_url,
                secret=row.secret,
                events=tuple(row.events or ()),
                enabled=row.enabled,
            )
            evt = make_event(
                event_type=event_type,
                customer_id=row.customer_id,
                payload={
                    "test": True,
                    "note": "Synthetic event from POST /webhooks/{id}/test",
                    "fields": {"company_name": "Test Co.", "fit_score": 0.78},
                },
            )
            summary = dispatch(subscriptions=[sub], event=evt)
            # Persist the delivery
            for d in summary.deliveries:
                session.add(
                    WebhookDeliveryRecord(
                        id=d.delivery_id,
                        subscription_id=sub_id,
                        customer_id=d.customer_id,
                        event_id=d.event_id,
                        event_type=d.event_type,
                        attempt=d.attempt,
                        endpoint_url=d.endpoint_url,
                        status_code=d.status_code,
                        success=d.success,
                        error=d.error,
                        duration_ms=d.duration_ms,
                        request_signature=d.request_signature,
                        payload=evt.envelope(),
                    )
                )
                row.last_delivery_at = _utcnow()
                row.last_status_code = d.status_code
                if d.success:
                    row.consecutive_failures = 0
                else:
                    row.consecutive_failures += 1
                    if row.consecutive_failures >= 20:
                        row.enabled = False
            await _safe_commit(session)
            return {
                "test_event": evt.event_id,
                "matched": summary.matched,
                "delivered": summary.delivered,
                "failed": summary.failed,
                "deliveries": [
                    {
                        "status_code": d.status_code,
                        "success": d.success,
                        "duration_ms": d.duration_ms,
                        "error": d.error,
                    }
                    for d in summary.deliveries
                ],
            }
    except HTTPException:
        raise
    except Exception as exc:
        log.warning("test_subscription_failed: %s", exc)
        return {"id": sub_id, "skipped_db_unreachable": True, "error": str(exc)[:200]}


# ── Internal: emit event to all matching subs ──────────────────────
@router.post("/events/emit")
async def emit_event(
    customer_id: str = Body(..., embed=True),
    event_type: str = Body(..., embed=True),
    payload: dict[str, Any] = Body(default_factory=dict, embed=True),
) -> dict[str, Any]:
    """
    Internal endpoint — emits an event to all matching subscriptions for the customer.

    In production this is called by deal/lead/payment routers after state changes.
    Exposed via API so any internal worker (cron, background task) can fire events
    without having to import the dispatcher.
    """
    if event_type not in EVENT_TYPES:
        raise HTTPException(status_code=400, detail=f"unknown event type: {event_type}")

    try:
        async with async_session_factory() as session:
            stmt = select(WebhookSubscriptionRecord).where(
                WebhookSubscriptionRecord.customer_id == customer_id,
                WebhookSubscriptionRecord.enabled.is_(True),
            )
            rows = (await session.execute(stmt)).scalars().all()
            subs = [
                WebhookSubscription(
                    customer_id=r.customer_id,
                    endpoint_url=r.endpoint_url,
                    secret=r.secret,
                    events=tuple(r.events or ()),
                    enabled=r.enabled,
                )
                for r in rows
            ]
            evt = make_event(
                event_type=event_type, customer_id=customer_id, payload=payload
            )
            summary = dispatch(subscriptions=subs, event=evt)
            row_by_endpoint = {r.endpoint_url: r for r in rows}
            for d in summary.deliveries:
                session.add(
                    WebhookDeliveryRecord(
                        id=d.delivery_id,
                        subscription_id=row_by_endpoint[d.endpoint_url].id,
                        customer_id=d.customer_id,
                        event_id=d.event_id,
                        event_type=d.event_type,
                        attempt=d.attempt,
                        endpoint_url=d.endpoint_url,
                        status_code=d.status_code,
                        success=d.success,
                        error=d.error,
                        duration_ms=d.duration_ms,
                        request_signature=d.request_signature,
                        payload=evt.envelope(),
                    )
                )
                src = row_by_endpoint[d.endpoint_url]
                src.last_delivery_at = _utcnow()
                src.last_status_code = d.status_code
                if d.success:
                    src.consecutive_failures = 0
                else:
                    src.consecutive_failures += 1
                    if src.consecutive_failures >= 20:
                        src.enabled = False
            await _safe_commit(session)
            return {
                "event_id": evt.event_id,
                "event_type": event_type,
                "customer_id": customer_id,
                "matched": summary.matched,
                "delivered": summary.delivered,
                "failed": summary.failed,
            }
    except Exception as exc:
        log.warning("emit_event_failed: %s", exc)
        return {
            "event_type": event_type,
            "customer_id": customer_id,
            "skipped_db_unreachable": True,
            "error": str(exc)[:200],
        }


# ── Recent deliveries — debug/replay ───────────────────────────────
@router.get("/deliveries")
async def list_deliveries(
    customer_id: str = Query(...),
    limit: int = Query(default=50, ge=1, le=500),
    success_only: bool = Query(default=False),
    failed_only: bool = Query(default=False),
) -> dict[str, Any]:
    if success_only and failed_only:
        raise HTTPException(status_code=400, detail="cannot filter for both success and failed")

    try:
        async with async_session_factory() as session:
            stmt = (
                select(WebhookDeliveryRecord)
                .where(WebhookDeliveryRecord.customer_id == customer_id)
                .order_by(desc(WebhookDeliveryRecord.created_at))
                .limit(limit)
            )
            if success_only:
                stmt = stmt.where(WebhookDeliveryRecord.success.is_(True))
            elif failed_only:
                stmt = stmt.where(WebhookDeliveryRecord.success.is_(False))
            rows = (await session.execute(stmt)).scalars().all()
            return {
                "customer_id": customer_id,
                "count": len(rows),
                "deliveries": [
                    {
                        "id": r.id,
                        "subscription_id": r.subscription_id,
                        "event_id": r.event_id,
                        "event_type": r.event_type,
                        "attempt": r.attempt,
                        "endpoint_url": r.endpoint_url,
                        "status_code": r.status_code,
                        "success": r.success,
                        "error": r.error,
                        "duration_ms": r.duration_ms,
                        "created_at": r.created_at.isoformat() if r.created_at else None,
                    }
                    for r in rows
                ],
            }
    except Exception as exc:
        log.warning("list_deliveries_failed: %s", exc)
        return {"customer_id": customer_id, "skipped_db_unreachable": True}


# ── Stats — for customer dashboard ─────────────────────────────────
@router.get("/stats")
async def ecosystem_stats(
    customer_id: str = Query(...),
    period_days: int = Query(default=7, ge=1, le=90),
) -> dict[str, Any]:
    """Per-customer ecosystem stats — useful for portal display."""
    cutoff = _utcnow() - timedelta(days=period_days)
    try:
        async with async_session_factory() as session:
            stmt = select(WebhookDeliveryRecord).where(
                WebhookDeliveryRecord.customer_id == customer_id,
                WebhookDeliveryRecord.created_at >= cutoff,
            )
            rows = (await session.execute(stmt)).scalars().all()
            total = len(rows)
            ok = sum(1 for r in rows if r.success)
            fail = total - ok
            by_event: dict[str, dict[str, int]] = {}
            for r in rows:
                bucket = by_event.setdefault(
                    r.event_type, {"total": 0, "success": 0, "failed": 0}
                )
                bucket["total"] += 1
                if r.success:
                    bucket["success"] += 1
                else:
                    bucket["failed"] += 1
            sub_stmt = select(WebhookSubscriptionRecord).where(
                WebhookSubscriptionRecord.customer_id == customer_id
            )
            subs = (await session.execute(sub_stmt)).scalars().all()
            avg_latency = (
                int(sum(r.duration_ms or 0 for r in rows) / total)
                if total
                else None
            )
            return {
                "customer_id": customer_id,
                "period_days": period_days,
                "subscriptions": {
                    "total": len(subs),
                    "enabled": sum(1 for s in subs if s.enabled),
                    "disabled": sum(1 for s in subs if not s.enabled),
                },
                "deliveries": {
                    "total": total,
                    "success": ok,
                    "failed": fail,
                    "success_rate": round(ok / total, 4) if total else 0.0,
                    "avg_latency_ms": avg_latency,
                },
                "by_event_type": by_event,
            }
    except Exception as exc:
        log.warning("ecosystem_stats_failed: %s", exc)
        return {"customer_id": customer_id, "skipped_db_unreachable": True}

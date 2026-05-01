"""Admin endpoints — cost dashboard, cache stats."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field

from api.deps import get_approval_gate
from dealix.caching.cache_stats import get_global_stats
from dealix.governance import ApprovalDecision
from dealix.observability.cost_tracker import CostTracker
from dealix.reliability.dlq import (
    CRM_SYNC_DLQ,
    DLQ,
    ENRICHMENT_DLQ,
    OUTBOUND_DLQ,
    WEBHOOKS_DLQ,
)

router = APIRouter(prefix="/api/v1/admin", tags=["admin"])

_tracker = CostTracker()


@router.get("/costs")
async def costs(
    window_hours: int = Query(24, ge=1, le=720),
    group_by: str = Query("model", regex="^(model|provider|task)$"),
) -> dict[str, Any]:
    """Aggregate LLM spend over the last N hours."""
    since = datetime.now(UTC) - timedelta(hours=window_hours)
    entries = _tracker.query_window(since=since)

    total_usd = sum(e.cost_usd for e in entries)
    total_in = sum(e.input_tokens for e in entries)
    total_out = sum(e.output_tokens for e in entries)
    total_cached = sum(getattr(e, "cached_tokens", 0) for e in entries)

    groups: dict[str, dict[str, float]] = {}
    for e in entries:
        key = getattr(e, group_by, "unknown") or "unknown"
        g = groups.setdefault(str(key), {"usd": 0.0, "calls": 0, "in": 0, "out": 0})
        g["usd"] += e.cost_usd
        g["calls"] += 1
        g["in"] += e.input_tokens
        g["out"] += e.output_tokens

    return {
        "window_hours": window_hours,
        "group_by": group_by,
        "totals": {
            "usd": round(total_usd, 4),
            "calls": len(entries),
            "input_tokens": total_in,
            "output_tokens": total_out,
            "cached_tokens": total_cached,
            "cache_hit_ratio": round(total_cached / total_in, 3) if total_in else 0.0,
        },
        "by_group": {k: {**v, "usd": round(v["usd"], 4)} for k, v in groups.items()},
    }


@router.get("/cache/stats")
async def cache_stats() -> dict[str, Any]:
    """Semantic cache hit/miss stats."""
    return get_global_stats()


@router.get("/dlq/stats")
async def dlq_stats() -> dict[str, Any]:
    """Dead-letter queue depth and last errors across all queues."""
    return {q: DLQ(q).stats() for q in (WEBHOOKS_DLQ, OUTBOUND_DLQ, ENRICHMENT_DLQ, CRM_SYNC_DLQ)}


@router.get("/dlq/{queue}/peek")
async def dlq_peek(queue: str, n: int = Query(10, ge=1, le=100)) -> dict[str, Any]:
    """Inspect the first N items in a DLQ without removing them."""
    dlq = DLQ(queue)
    items = dlq.peek(n=n)
    return {
        "queue": queue,
        "returned": len(items),
        "depth": dlq.depth(),
        "items": [
            {
                "id": it.id,
                "source": it.source,
                "error": it.error,
                "attempts": it.attempts,
                "first_seen_at": it.first_seen_at,
                "last_attempt_at": it.last_attempt_at,
                "payload_keys": (list(it.payload.keys()) if isinstance(it.payload, dict) else []),
            }
            for it in items
        ],
    }


@router.post("/dlq/{queue}/drain")
async def dlq_drain(queue: str, limit: int = Query(10, ge=1, le=100)) -> dict[str, Any]:
    """Remove up to `limit` items from a DLQ. Caller is responsible for replay.
    Returns drained items for operator inspection / manual retry.
    """
    dlq = DLQ(queue)
    items = dlq.drain(limit=limit)
    return {
        "queue": queue,
        "drained": len(items),
        "remaining": dlq.depth(),
        "items": [
            {"id": it.id, "source": it.source, "payload": it.payload, "error": it.error}
            for it in items
        ],
    }


# ── Approvals Gate ──────────────────────────────────────────────


class ApprovalRequestIn(BaseModel):
    action: str = Field(..., min_length=1, max_length=128)
    payload: dict = Field(default_factory=dict)
    risk_score: float = Field(0.0, ge=0.0, le=1.0)
    requested_by: str = Field("admin", max_length=128)


class ApprovalDecisionIn(BaseModel):
    approved: bool
    decided_by: str = Field(..., min_length=1, max_length=128)
    note: str = Field("", max_length=1024)


def _approval_to_dict(req) -> dict[str, Any]:
    return {
        "id": req.id,
        "action": req.action,
        "payload": req.payload,
        "risk_score": req.risk_score,
        "requested_by": req.requested_by,
        "requested_at": req.requested_at,
        "status": req.status.value,
        "reason": req.reason,
        "decided_by": req.decided_by,
        "decided_at": req.decided_at,
        "expires_at": req.expires_at,
    }


@router.get("/approvals/stats")
async def approvals_stats() -> dict[str, Any]:
    gate = await get_approval_gate()
    return await gate.stats()


@router.get("/approvals/pending")
async def approvals_pending(limit: int = Query(50, ge=1, le=200)) -> dict[str, Any]:
    gate = await get_approval_gate()
    items = await gate.list_pending(limit=limit)
    return {"count": len(items), "items": [_approval_to_dict(r) for r in items]}


@router.post("/approvals/request")
async def approvals_request(body: ApprovalRequestIn) -> dict[str, Any]:
    gate = await get_approval_gate()
    req = await gate.request(
        action=body.action,
        payload=body.payload,
        risk_score=body.risk_score,
        requested_by=body.requested_by,
    )
    return _approval_to_dict(req)


@router.get("/approvals/{request_id}")
async def approvals_get(request_id: str) -> dict[str, Any]:
    gate = await get_approval_gate()
    req = await gate.get(request_id)
    if not req:
        raise HTTPException(status_code=404, detail="approval request not found")
    return _approval_to_dict(req)


@router.post("/approvals/{request_id}/decide")
async def approvals_decide(request_id: str, body: ApprovalDecisionIn) -> dict[str, Any]:
    gate = await get_approval_gate()
    decision = ApprovalDecision(
        request_id=request_id,
        approved=body.approved,
        decided_by=body.decided_by,
        note=body.note,
    )
    req = await gate.decide(decision)
    if not req:
        raise HTTPException(status_code=404, detail="approval request not found")
    return _approval_to_dict(req)


@router.get("/sentry-check")
async def sentry_check() -> dict[str, str]:
    """Trigger a Sentry test error — verify DSN is live.
    Call once post-deploy, then remove from production routes if paranoid.
    """
    import os

    try:
        import sentry_sdk  # type: ignore

        sentry_sdk.capture_message(
            "Dealix sentry-check ping",
            level="info",
        )
        return {"status": "sent", "dsn_configured": str(bool(os.getenv("SENTRY_DSN")))}
    except Exception:  # pragma: no cover
        return {"status": "error", "error": "sentry_check_failed"}

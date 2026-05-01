"""Unit tests for ApprovalGate — fake Redis, no network."""

from __future__ import annotations

import time

import pytest

from dealix.governance.approvals import (
    OUTBOUND_THRESHOLD,
    PENDING_TTL_SECONDS,
    RISK_THRESHOLD,
    ApprovalDecision,
    ApprovalGate,
    ApprovalStatus,
)


class FakeRedis:
    """Minimal in-memory Redis compatible with ApprovalGate's async calls."""

    def __init__(self) -> None:
        self.kv: dict[str, str] = {}
        self.z: dict[str, dict[str, float]] = {}
        self.expiries: dict[str, float] = {}

    async def set(self, key: str, value: str, ex: int | None = None) -> None:
        self.kv[key] = value
        if ex:
            self.expiries[key] = time.time() + ex

    async def get(self, key: str) -> str | None:
        if key in self.expiries and time.time() > self.expiries[key]:
            self.kv.pop(key, None)
            return None
        return self.kv.get(key)

    async def zadd(self, key: str, mapping: dict[str, float]) -> int:
        bucket = self.z.setdefault(key, {})
        added = 0
        for member, score in mapping.items():
            if member not in bucket:
                added += 1
            bucket[member] = score
        return added

    async def zrem(self, key: str, *members: str) -> int:
        bucket = self.z.get(key, {})
        removed = 0
        for m in members:
            if m in bucket:
                bucket.pop(m)
                removed += 1
        return removed

    async def zrevrange(self, key: str, start: int, end: int) -> list[str]:
        bucket = self.z.get(key, {})
        ordered = sorted(bucket.items(), key=lambda kv: kv[1], reverse=True)
        # end is inclusive in Redis; Python slice end is exclusive.
        return [m for m, _ in ordered[start : end + 1]]

    async def zcard(self, key: str) -> int:
        return len(self.z.get(key, {}))


@pytest.fixture
def gate() -> ApprovalGate:
    return ApprovalGate(FakeRedis())


@pytest.mark.asyncio
async def test_auto_approves_below_thresholds(gate: ApprovalGate) -> None:
    req = await gate.request(
        action="enrichment_task",
        payload={"recipients": 5},
        risk_score=0.1,
    )
    assert req.status == ApprovalStatus.AUTO_APPROVED


@pytest.mark.asyncio
async def test_requires_approval_when_action_critical(gate: ApprovalGate) -> None:
    req = await gate.request(
        action="outbound_email_campaign",
        payload={"recipients": 3},
        risk_score=0.0,
    )
    assert req.status == ApprovalStatus.PENDING
    assert "CRITICAL_ACTIONS" in req.reason


@pytest.mark.asyncio
async def test_requires_approval_over_recipient_threshold(gate: ApprovalGate) -> None:
    req = await gate.request(
        action="notify",
        payload={"recipients": OUTBOUND_THRESHOLD + 1},
    )
    assert req.status == ApprovalStatus.PENDING
    assert "recipients" in req.reason


@pytest.mark.asyncio
async def test_requires_approval_over_risk_threshold(gate: ApprovalGate) -> None:
    req = await gate.request(
        action="enrichment_task",
        payload={},
        risk_score=RISK_THRESHOLD + 0.01,
    )
    assert req.status == ApprovalStatus.PENDING
    assert "risk_score" in req.reason


@pytest.mark.asyncio
async def test_requires_approval_over_amount(gate: ApprovalGate) -> None:
    req = await gate.request(action="refund", payload={"amount_sar": 10000})
    assert req.status == ApprovalStatus.PENDING


@pytest.mark.asyncio
async def test_decide_approve(gate: ApprovalGate) -> None:
    req = await gate.request(action="outbound_email_campaign", payload={"recipients": 100})
    assert req.status == ApprovalStatus.PENDING

    decided = await gate.decide(
        ApprovalDecision(request_id=req.id, approved=True, decided_by="sami", note="ok")
    )
    assert decided is not None
    assert decided.status == ApprovalStatus.APPROVED
    assert decided.decided_by == "sami"
    stats = await gate.stats()
    assert stats["pending"] == 0


@pytest.mark.asyncio
async def test_decide_reject(gate: ApprovalGate) -> None:
    req = await gate.request(action="outbound_whatsapp_broadcast", payload={"recipients": 200})
    decided = await gate.decide(
        ApprovalDecision(request_id=req.id, approved=False, decided_by="sami")
    )
    assert decided.status == ApprovalStatus.REJECTED


@pytest.mark.asyncio
async def test_decide_idempotent(gate: ApprovalGate) -> None:
    req = await gate.request(action="outbound_email_campaign", payload={"recipients": 100})
    await gate.decide(ApprovalDecision(request_id=req.id, approved=True, decided_by="sami"))
    # second decide should NOT change status
    second = await gate.decide(
        ApprovalDecision(request_id=req.id, approved=False, decided_by="sami2")
    )
    assert second.status == ApprovalStatus.APPROVED
    assert second.decided_by == "sami"


@pytest.mark.asyncio
async def test_list_pending_excludes_decided(gate: ApprovalGate) -> None:
    r1 = await gate.request(action="outbound_email_campaign", payload={"recipients": 100})
    r2 = await gate.request(action="outbound_email_campaign", payload={"recipients": 200})
    await gate.decide(ApprovalDecision(request_id=r1.id, approved=True, decided_by="sami"))
    pending = await gate.list_pending()
    ids = {r.id for r in pending}
    assert r1.id not in ids
    assert r2.id in ids


@pytest.mark.asyncio
async def test_expires_after_ttl(gate: ApprovalGate) -> None:
    req = await gate.request(action="outbound_email_campaign", payload={"recipients": 100})
    # fast-forward by mutating expires_at on the stored record
    key = gate._key(req.id)
    raw = await gate.r.get(key)
    import json as _json

    d = _json.loads(raw)
    d["expires_at"] = time.time() - 10
    await gate.r.set(key, _json.dumps(d), ex=PENDING_TTL_SECONDS + 3600)

    refreshed = await gate.get(req.id)
    assert refreshed.status == ApprovalStatus.EXPIRED


@pytest.mark.asyncio
async def test_get_returns_none_for_unknown(gate: ApprovalGate) -> None:
    assert await gate.get("does-not-exist") is None

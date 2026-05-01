"""
Approvals Gate — حاجز موافقة بشرية على العمليات الخارجية عالية المخاطر.

الاستخدام:
    gate = ApprovalGate(redis_client)
    req = await gate.request(
        action="outbound_email_campaign",
        payload={"recipients": 500, "template": "cold_outreach_v2"},
        risk_score=0.8,
        requested_by="lead_engine",
    )
    if req.status == "auto_approved":
        execute()
    else:
        # ينتظر موافقة الأدمن عبر POST /admin/approvals/{id}/decide
        pending()

قواعد الحاجز:
- أي outbound > OUTBOUND_THRESHOLD (افتراضي 50 مستلم) → موافقة مطلوبة
- أي risk_score >= 0.7 → موافقة مطلوبة
- أي action في CRITICAL_ACTIONS → موافقة مطلوبة حتى لو < threshold
- TTL على الطلب المعلق = 24 ساعة، بعدها يرفض تلقائياً
"""

from __future__ import annotations

import json
import time
import uuid
from dataclasses import asdict, dataclass
from enum import StrEnum
from typing import Any

import redis.asyncio as redis

OUTBOUND_THRESHOLD = 50  # عدد المستلمين الذي فوقه نطلب موافقة
RISK_THRESHOLD = 0.7
PENDING_TTL_SECONDS = 24 * 60 * 60  # 24h

CRITICAL_ACTIONS = frozenset(
    {
        "outbound_email_campaign",
        "outbound_whatsapp_broadcast",
        "outbound_sms_broadcast",
        "crm_bulk_update",
        "crm_bulk_delete",
        "pricing_change",
        "refund_issue",
        "production_config_change",
    }
)


class ApprovalStatus(StrEnum):
    PENDING = "pending"
    AUTO_APPROVED = "auto_approved"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"


@dataclass
class ApprovalRequest:
    id: str
    action: str
    payload: dict[str, Any]
    risk_score: float
    requested_by: str
    requested_at: float
    status: ApprovalStatus
    reason: str = ""
    decided_by: str = ""
    decided_at: float | None = None
    expires_at: float = 0.0

    def to_json(self) -> str:
        d = asdict(self)
        d["status"] = self.status.value
        return json.dumps(d, ensure_ascii=False)

    @classmethod
    def from_json(cls, raw: str) -> ApprovalRequest:
        d = json.loads(raw)
        d["status"] = ApprovalStatus(d["status"])
        return cls(**d)


@dataclass
class ApprovalDecision:
    request_id: str
    approved: bool
    decided_by: str
    note: str = ""


class ApprovalGate:
    """واجهة Redis-backed لإدارة طلبات الموافقة."""

    KEY_PREFIX = "dealix:approvals"
    PENDING_INDEX = "dealix:approvals:pending"

    def __init__(self, redis_client: redis.Redis):
        self.r = redis_client

    def _key(self, request_id: str) -> str:
        return f"{self.KEY_PREFIX}:{request_id}"

    # ---------- helpers ----------
    def _evaluate(
        self,
        action: str,
        payload: dict[str, Any],
        risk_score: float,
    ) -> tuple[bool, str]:
        """يرجع (يحتاج_موافقة, سبب)."""
        if action in CRITICAL_ACTIONS:
            return True, f"action '{action}' in CRITICAL_ACTIONS"
        if risk_score >= RISK_THRESHOLD:
            return True, f"risk_score {risk_score:.2f} >= {RISK_THRESHOLD}"
        recipients = int(payload.get("recipients", 0) or 0)
        if recipients > OUTBOUND_THRESHOLD:
            return True, f"recipients {recipients} > {OUTBOUND_THRESHOLD}"
        amount_sar = float(payload.get("amount_sar", 0) or 0)
        if amount_sar >= 5000:
            return True, f"amount_sar {amount_sar} >= 5000"
        return False, "auto-approved: below all thresholds"

    # ---------- API ----------
    async def request(
        self,
        action: str,
        payload: dict[str, Any],
        risk_score: float = 0.0,
        requested_by: str = "system",
    ) -> ApprovalRequest:
        needs_approval, reason = self._evaluate(action, payload, risk_score)
        now = time.time()
        req = ApprovalRequest(
            id=str(uuid.uuid4()),
            action=action,
            payload=payload,
            risk_score=risk_score,
            requested_by=requested_by,
            requested_at=now,
            status=(ApprovalStatus.PENDING if needs_approval else ApprovalStatus.AUTO_APPROVED),
            reason=reason,
            expires_at=now + PENDING_TTL_SECONDS,
        )
        await self.r.set(
            self._key(req.id),
            req.to_json(),
            ex=PENDING_TTL_SECONDS + 3600,  # نحتفظ ساعة إضافية للـ audit
        )
        if needs_approval:
            await self.r.zadd(self.PENDING_INDEX, {req.id: now})
        return req

    async def get(self, request_id: str) -> ApprovalRequest | None:
        raw = await self.r.get(self._key(request_id))
        if not raw:
            return None
        if isinstance(raw, bytes):
            raw = raw.decode("utf-8")
        req = ApprovalRequest.from_json(raw)
        # انتهاء تلقائي
        if req.status == ApprovalStatus.PENDING and time.time() > req.expires_at:
            req.status = ApprovalStatus.EXPIRED
            await self._persist(req)
            await self.r.zrem(self.PENDING_INDEX, req.id)
        return req

    async def list_pending(self, limit: int = 50) -> list[ApprovalRequest]:
        ids = await self.r.zrevrange(self.PENDING_INDEX, 0, limit - 1)
        out: list[ApprovalRequest] = []
        for rid in ids:
            if isinstance(rid, bytes):
                rid = rid.decode("utf-8")
            req = await self.get(rid)
            if req and req.status == ApprovalStatus.PENDING:
                out.append(req)
        return out

    async def decide(self, decision: ApprovalDecision) -> ApprovalRequest | None:
        req = await self.get(decision.request_id)
        if not req:
            return None
        if req.status != ApprovalStatus.PENDING:
            return req  # idempotent — لا نغيّر قرار سابق
        req.status = ApprovalStatus.APPROVED if decision.approved else ApprovalStatus.REJECTED
        req.decided_by = decision.decided_by
        req.decided_at = time.time()
        if decision.note:
            req.reason = f"{req.reason} | decision_note: {decision.note}"
        await self._persist(req)
        await self.r.zrem(self.PENDING_INDEX, req.id)
        return req

    async def _persist(self, req: ApprovalRequest) -> None:
        await self.r.set(
            self._key(req.id),
            req.to_json(),
            ex=PENDING_TTL_SECONDS + 3600,
        )

    async def stats(self) -> dict[str, int]:
        pending = await self.r.zcard(self.PENDING_INDEX)
        return {"pending": int(pending or 0)}

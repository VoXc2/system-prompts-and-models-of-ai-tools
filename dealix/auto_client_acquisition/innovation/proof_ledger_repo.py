"""مستودع Proof Ledger — عمليات DB غير متزامنة."""

from __future__ import annotations

import uuid
from datetime import datetime, timedelta
from core._py_compat import UTC
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from db.models import ProofLedgerEventRecord


def _iso_utc(dt: datetime | None) -> str:
    if not dt:
        return ""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=UTC)
    return dt.isoformat()


def _new_pl_id() -> str:
    return f"pl_{uuid.uuid4().hex[:20]}"


async def proof_ledger_append(
    session: AsyncSession,
    *,
    tenant_id: str,
    event_type: str,
    revenue_influenced_sar_estimate: float,
    notes_ar: str,
    extra: dict[str, Any] | None = None,
) -> dict[str, Any]:
    rec = ProofLedgerEventRecord(
        id=_new_pl_id(),
        tenant_id=tenant_id or "default",
        event_type=event_type,
        revenue_influenced_sar_estimate=float(revenue_influenced_sar_estimate),
        notes_ar=notes_ar or "",
        extra_json=extra or {},
    )
    session.add(rec)
    await session.flush()
    return {
        "id": rec.id,
        "tenant_id": rec.tenant_id,
        "event_type": rec.event_type,
        "revenue_influenced_sar_estimate": rec.revenue_influenced_sar_estimate,
        "notes_ar": rec.notes_ar,
        "extra_json": rec.extra_json,
        "created_at": _iso_utc(rec.created_at),
    }


async def proof_ledger_list(
    session: AsyncSession,
    *,
    tenant_id: str,
    limit: int = 100,
) -> list[dict[str, Any]]:
    q = (
        select(ProofLedgerEventRecord)
        .where(ProofLedgerEventRecord.tenant_id == tenant_id)
        .order_by(ProofLedgerEventRecord.created_at.desc())
        .limit(min(max(limit, 1), 500))
    )
    result = await session.execute(q)
    rows = result.scalars().all()
    out: list[dict[str, Any]] = []
    for r in rows:
        out.append(
            {
                "id": r.id,
                "event_type": r.event_type,
                "ts": _iso_utc(r.created_at),
                "revenue_influenced_sar_estimate": r.revenue_influenced_sar_estimate,
                "notes_ar": r.notes_ar,
                "extra_json": r.extra_json,
            }
        )
    return out


async def proof_ledger_weekly_report(
    session: AsyncSession,
    *,
    tenant_id: str,
) -> dict[str, Any]:
    since = datetime.now(tz=UTC) - timedelta(days=7)
    q = select(
        func.count(ProofLedgerEventRecord.id),
        func.coalesce(func.sum(ProofLedgerEventRecord.revenue_influenced_sar_estimate), 0.0),
    ).where(
        ProofLedgerEventRecord.tenant_id == tenant_id,
        ProofLedgerEventRecord.created_at >= since,
    )
    result = await session.execute(q)
    row = result.one()
    count, total_est = int(row[0] or 0), float(row[1] or 0.0)
    return {
        "tenant_id": tenant_id,
        "window_days": 7,
        "event_count": count,
        "revenue_influenced_sar_estimate_sum": total_est,
        "disclaimer_ar": "تقديرات تشغيلية فقط — ليست إيرادات محققة أو مؤكدة محاسبياً.",
    }

"""
Customer Success router — health scores, QBRs, and Saudi B2B Pulse.

Endpoints:
    POST /api/v1/customer-success/health/{customer_id}    — compute health score
    GET  /api/v1/customer-success/at-risk                 — list at-risk customers
    POST /api/v1/customer-success/qbr/{customer_id}       — generate QBR (md + json)
    GET  /api/v1/customer-success/benchmarks/{sector}     — sector percentiles
    POST /api/v1/customer-success/compare/{customer_id}   — customer vs sector
    GET  /api/v1/customer-success/saudi-b2b-pulse         — public monthly report

Privacy: benchmarks use min cohort = 5 (re-identification guard).
"""

from __future__ import annotations

import logging
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import APIRouter, Body, HTTPException
from sqlalchemy import func, select

from auto_client_acquisition.customer_success.benchmarks import (
    MIN_COHORT_SIZE, compare_customer, compute_sector_benchmark, saudi_b2b_pulse,
)
from auto_client_acquisition.customer_success.health_score import compute_health
from auto_client_acquisition.customer_success.qbr_generator import generate_qbr
from db.models import (
    AccountRecord, CustomerRecord, EmailSendLog, GmailDraftRecord,
    LeadScoreRecord, LinkedInDraftRecord,
)
from db.session import async_session_factory

router = APIRouter(prefix="/api/v1/customer-success", tags=["customer-success"])
log = logging.getLogger(__name__)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


# ── Health score for one customer ─────────────────────────────────
@router.post("/health/{customer_id}")
async def compute_customer_health(customer_id: str) -> dict[str, Any]:
    """Compute live health score for a customer using last-30d signals."""
    cutoff_30d = _utcnow() - timedelta(days=30)

    async with async_session_factory() as session:
        try:
            cust = (await session.execute(
                select(CustomerRecord).where(CustomerRecord.id == customer_id)
            )).scalar_one_or_none()
            if not cust:
                raise HTTPException(404, "customer_not_found")

            drafts_created = int((await session.execute(
                select(func.count()).select_from(GmailDraftRecord).where(
                    GmailDraftRecord.created_at >= cutoff_30d,
                )
            )).scalar() or 0)
            drafts_sent = int((await session.execute(
                select(func.count()).select_from(GmailDraftRecord).where(
                    GmailDraftRecord.created_at >= cutoff_30d,
                    GmailDraftRecord.status == "sent",
                )
            )).scalar() or 0)
            replies = int((await session.execute(
                select(func.count()).select_from(EmailSendLog).where(
                    EmailSendLog.reply_received_at >= cutoff_30d,
                )
            )).scalar() or 0)
            total_drafts = int((await session.execute(
                select(func.count()).select_from(GmailDraftRecord)
            )).scalar() or 0)
        except HTTPException:
            raise
        except Exception as exc:  # noqa: BLE001
            return {"status": "skipped_db_unreachable", "error": str(exc)}

    days_since_login = (
        (_utcnow() - cust.updated_at).days
        if cust.updated_at else 0
    )

    score = compute_health(
        customer_id=customer_id,
        logins_last_30d=max(0, 22 - days_since_login),
        drafts_approved_last_30d=drafts_sent,
        replies_acted_on_last_30d=replies,
        demos_booked_last_30d=int(cust.daily_report_sent or 0) // 5,
        deals_stage_progressed_last_30d=drafts_sent // 5,
        paid_customers_last_30d=1 if cust.onboarding_status != "kickoff_pending" else 0,
        pipeline_value_sar=drafts_sent * 5000,  # rough estimate
        channels_enabled=2,  # default 2 (Gmail + LinkedIn)
        integrations_connected=1,
        sectors_targeted=1,
        total_drafts_lifetime=total_drafts,
        nps=cust.nps_score,
        support_tickets_open=0,
        days_since_last_login=days_since_login,
        billing_failures=0,
    )
    return score.to_dict()


@router.get("/at-risk")
async def list_at_risk_customers() -> dict[str, Any]:
    """Return all customers in at_risk or critical buckets."""
    async with async_session_factory() as session:
        try:
            customers = (await session.execute(select(CustomerRecord))).scalars().all()
        except Exception as exc:  # noqa: BLE001
            return {"status": "skipped_db_unreachable", "error": str(exc), "items": []}

    at_risk: list[dict[str, Any]] = []
    for c in customers:
        # Simplified: pull the full health score per customer
        days_idle = (_utcnow() - c.updated_at).days if c.updated_at else 0
        score = compute_health(
            customer_id=c.id,
            logins_last_30d=max(0, 22 - days_idle),
            nps=c.nps_score,
            days_since_last_login=days_idle,
            drafts_approved_last_30d=0,  # TODO query per customer
        )
        if score.bucket in {"at_risk", "critical"}:
            at_risk.append(score.to_dict())

    return {
        "count": len(at_risk),
        "customers": sorted(at_risk, key=lambda x: x["overall"]),
        "next_action": "Reach out to critical bucket within 24 hours.",
    }


# ── QBR generator ─────────────────────────────────────────────────
@router.post("/qbr/{customer_id}")
async def generate_customer_qbr(customer_id: str, body: dict[str, Any] = Body(default={})) -> dict[str, Any]:
    """Generate a Quarterly Business Review for a customer (default: last 30 days)."""
    period_days = int(body.get("period_days") or 30)
    cutoff = _utcnow() - timedelta(days=period_days)

    async with async_session_factory() as session:
        try:
            cust = (await session.execute(
                select(CustomerRecord).where(CustomerRecord.id == customer_id)
            )).scalar_one_or_none()
            if not cust:
                raise HTTPException(404, "customer_not_found")

            emails_sent = int((await session.execute(
                select(func.count()).select_from(EmailSendLog).where(
                    EmailSendLog.sent_at >= cutoff,
                    EmailSendLog.status == "sent",
                )
            )).scalar() or 0)
            emails_replied = int((await session.execute(
                select(func.count()).select_from(EmailSendLog).where(
                    EmailSendLog.reply_received_at >= cutoff,
                )
            )).scalar() or 0)
            emails_bounced = int((await session.execute(
                select(func.count()).select_from(EmailSendLog).where(
                    EmailSendLog.status == "bounced",
                    EmailSendLog.updated_at >= cutoff,
                )
            )).scalar() or 0)
            drafts_created = int((await session.execute(
                select(func.count()).select_from(GmailDraftRecord).where(
                    GmailDraftRecord.created_at >= cutoff,
                )
            )).scalar() or 0)
            drafts_sent = int((await session.execute(
                select(func.count()).select_from(GmailDraftRecord).where(
                    GmailDraftRecord.created_at >= cutoff,
                    GmailDraftRecord.status == "sent",
                )
            )).scalar() or 0)
            linkedin_drafts = int((await session.execute(
                select(func.count()).select_from(LinkedInDraftRecord).where(
                    LinkedInDraftRecord.created_at >= cutoff,
                )
            )).scalar() or 0)
            linkedin_sent = int((await session.execute(
                select(func.count()).select_from(LinkedInDraftRecord).where(
                    LinkedInDraftRecord.created_at >= cutoff,
                    LinkedInDraftRecord.status == "sent",
                )
            )).scalar() or 0)
        except HTTPException:
            raise
        except Exception as exc:  # noqa: BLE001
            return {"status": "skipped_db_unreachable", "error": str(exc)}

    # Health score
    days_idle = (_utcnow() - cust.updated_at).days if cust.updated_at else 0
    health = compute_health(
        customer_id=customer_id,
        logins_last_30d=max(0, 22 - days_idle),
        drafts_approved_last_30d=drafts_sent,
        replies_acted_on_last_30d=emails_replied,
        nps=cust.nps_score, days_since_last_login=days_idle,
        total_drafts_lifetime=drafts_created,
    )

    qbr = generate_qbr(
        customer_id=customer_id,
        customer_name=cust.company_id or customer_id,
        period_days=period_days,
        emails_sent=emails_sent, emails_replied=emails_replied,
        emails_bounced=emails_bounced,
        drafts_created=drafts_created, drafts_sent=drafts_sent,
        linkedin_drafts=linkedin_drafts, linkedin_sent=linkedin_sent,
        health_overall=health.overall, health_bucket=health.bucket,
        current_plan=cust.plan,
    )

    return {
        "qbr": qbr.to_dict(),
        "markdown": qbr.to_markdown(),
        "health": health.to_dict(),
    }


# ── Sector benchmarks (private to subscribers) ────────────────────
@router.get("/benchmarks/{sector}")
async def get_sector_benchmarks(sector: str, metric: str = "reply_rate") -> dict[str, Any]:
    """Sector percentiles. Requires >=5 customers in sector for privacy."""
    cutoff_30d = _utcnow() - timedelta(days=30)
    async with async_session_factory() as session:
        try:
            accounts = (await session.execute(
                select(AccountRecord).where(AccountRecord.sector == sector)
            )).scalars().all()
            account_ids = [a.id for a in accounts]
            if not account_ids:
                return {"status": "no_data", "sector": sector}

            sends = (await session.execute(
                select(EmailSendLog).where(
                    EmailSendLog.account_id.in_(account_ids),
                    EmailSendLog.sent_at >= cutoff_30d,
                )
            )).scalars().all()
        except Exception as exc:  # noqa: BLE001
            return {"status": "skipped_db_unreachable", "error": str(exc)}

    # Group by account_id, compute reply rates
    by_account: dict[str, dict[str, int]] = defaultdict(lambda: {"sent": 0, "replied": 0})
    for s in sends:
        by_account[s.account_id]["sent"] += 1
        if s.reply_received_at:
            by_account[s.account_id]["replied"] += 1

    if metric == "reply_rate":
        values = [
            (v["replied"] / max(1, v["sent"])) * 100
            for v in by_account.values() if v["sent"] >= 5
        ]
    elif metric == "send_volume":
        values = [v["sent"] for v in by_account.values()]
    else:
        return {"status": "unknown_metric", "sector": sector, "metric": metric,
                "valid_metrics": ["reply_rate", "send_volume"]}

    bench = compute_sector_benchmark(sector, metric, values)
    if bench is None:
        return {
            "status": "cohort_too_small",
            "sector": sector, "metric": metric,
            "min_required": MIN_COHORT_SIZE, "current": len(values),
            "note": "Privacy guard: need ≥5 active customers in this sector.",
        }
    return {"status": "ok", "benchmark": bench.to_dict()}


@router.post("/compare/{customer_id}")
async def compare_to_sector(customer_id: str, body: dict[str, Any] = Body(default={})) -> dict[str, Any]:
    """Where does this customer rank in their sector cohort?"""
    metric = str(body.get("metric") or "reply_rate")
    cutoff_30d = _utcnow() - timedelta(days=30)

    async with async_session_factory() as session:
        try:
            cust = (await session.execute(
                select(CustomerRecord).where(CustomerRecord.id == customer_id)
            )).scalar_one_or_none()
            if not cust or not cust.company_id:
                return {"status": "customer_or_company_not_found"}

            company = (await session.execute(
                select(AccountRecord).where(AccountRecord.id == cust.company_id)
            )).scalar_one_or_none()
            if not company:
                return {"status": "company_not_found"}

            sector = company.sector or "unknown"
            peers = (await session.execute(
                select(AccountRecord).where(AccountRecord.sector == sector)
            )).scalars().all()
            peer_ids = [a.id for a in peers]

            sends = (await session.execute(
                select(EmailSendLog).where(
                    EmailSendLog.account_id.in_(peer_ids),
                    EmailSendLog.sent_at >= cutoff_30d,
                )
            )).scalars().all()
        except Exception as exc:  # noqa: BLE001
            return {"status": "skipped_db_unreachable", "error": str(exc)}

    by_acc: dict[str, dict[str, int]] = defaultdict(lambda: {"sent": 0, "replied": 0})
    for s in sends:
        by_acc[s.account_id]["sent"] += 1
        if s.reply_received_at:
            by_acc[s.account_id]["replied"] += 1
    sector_values = [
        (v["replied"] / max(1, v["sent"])) * 100
        for v in by_acc.values() if v["sent"] >= 5
    ]
    customer_stats = by_acc.get(cust.company_id, {"sent": 0, "replied": 0})
    customer_value = (
        (customer_stats["replied"] / max(1, customer_stats["sent"])) * 100
    )
    cmp = compare_customer(
        customer_id=customer_id, sector=sector, metric=metric,
        customer_value=customer_value, sector_values=sector_values,
    )
    if cmp is None:
        return {"status": "cohort_too_small", "min_required": MIN_COHORT_SIZE}
    return cmp.to_dict()


# ── Saudi B2B Pulse (public, monthly) ─────────────────────────────
@router.get("/saudi-b2b-pulse")
async def get_saudi_b2b_pulse() -> dict[str, Any]:
    """Public anonymized monthly report — works as a free lead magnet."""
    cutoff_30d = _utcnow() - timedelta(days=30)
    async with async_session_factory() as session:
        try:
            accounts = (await session.execute(select(AccountRecord))).scalars().all()
            sector_to_ids: dict[str, list[str]] = defaultdict(list)
            for a in accounts:
                sector_to_ids[a.sector or "unknown"].append(a.id)

            all_sends = (await session.execute(
                select(EmailSendLog).where(EmailSendLog.sent_at >= cutoff_30d)
            )).scalars().all()
            by_acc: dict[str, dict[str, int]] = defaultdict(lambda: {"sent": 0, "replied": 0})
            for s in all_sends:
                by_acc[s.account_id]["sent"] += 1
                if s.reply_received_at:
                    by_acc[s.account_id]["replied"] += 1
        except Exception as exc:  # noqa: BLE001
            return {"status": "skipped_db_unreachable", "error": str(exc)}

    sector_data: dict[str, dict[str, list[float]]] = {}
    for sector, ids in sector_to_ids.items():
        if len(ids) < MIN_COHORT_SIZE:
            continue
        reply_rates = [
            (by_acc[i]["replied"] / max(1, by_acc[i]["sent"])) * 100
            for i in ids if by_acc[i]["sent"] >= 5
        ]
        send_volumes = [by_acc[i]["sent"] for i in ids]
        if reply_rates or send_volumes:
            sector_data[sector] = {}
            if reply_rates:
                sector_data[sector]["reply_rate"] = reply_rates
            if send_volumes:
                sector_data[sector]["send_volume"] = [float(s) for s in send_volumes]

    return saudi_b2b_pulse(sector_data=sector_data)

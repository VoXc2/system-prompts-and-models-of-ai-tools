"""
Email send router — Gmail OAuth send + status + replies sync.

Endpoints:
    POST /api/v1/email/connect/gmail        — return OAuth setup checklist
    POST /api/v1/email/send-approved        — send a single approved row
    POST /api/v1/email/send-batch           — send a batch of up to BATCH_SIZE rows
    GET  /api/v1/email/status               — Gmail config + today counts
    POST /api/v1/email/replies/sync         — manual reply ingestion (until Pub/Sub)
"""

from __future__ import annotations

import logging
import os
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import APIRouter, Body, HTTPException
from sqlalchemy import func, select

from auto_client_acquisition.email.compliance import (
    append_opt_out_line,
    check_outreach,
    get_batch_interval_seconds,
    get_batch_size,
    get_daily_limit,
)
from auto_client_acquisition.email.gmail_send import (
    get_oauth_setup_instructions,
    is_configured as gmail_is_configured,
    send_email,
)
from auto_client_acquisition.email.reply_classifier import classify_reply
from db.models import (
    AccountRecord,
    ContactRecord,
    EmailSendLog,
    OutreachQueueRecord,
    SuppressionRecord,
)
from db.session import async_session_factory

router = APIRouter(prefix="/api/v1/email", tags=["email"])
log = logging.getLogger(__name__)


def _new_id(prefix: str = "") -> str:
    return f"{prefix}{uuid.uuid4().hex[:24]}" if prefix else uuid.uuid4().hex[:24]


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


@router.post("/connect/gmail")
async def connect_gmail() -> dict[str, Any]:
    """Returns the exact 8-step OAuth setup Sami runs once locally."""
    if gmail_is_configured():
        return {"status": "already_configured", "sender_email": os.getenv("GMAIL_SENDER_EMAIL", "")}
    return {"status": "needs_setup", **get_oauth_setup_instructions()}


@router.get("/status")
async def email_status() -> dict[str, Any]:
    today_start = _utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    async with async_session_factory() as session:
        try:
            sent_today = int((await session.execute(
                select(func.count()).select_from(EmailSendLog).where(
                    EmailSendLog.status == "sent",
                    EmailSendLog.sent_at >= today_start,
                )
            )).scalar() or 0)
            queued = int((await session.execute(
                select(func.count()).select_from(OutreachQueueRecord).where(
                    OutreachQueueRecord.status.in_(["queued", "approved"])
                )
            )).scalar() or 0)
        except Exception as exc:  # noqa: BLE001
            return {"status": "skipped_db_unreachable", "error": str(exc)}

    return {
        "gmail_configured": gmail_is_configured(),
        "sender_email": os.getenv("GMAIL_SENDER_EMAIL") or "(unset)",
        "limits": {
            "daily_email_limit": get_daily_limit(),
            "batch_size": get_batch_size(),
            "batch_interval_minutes": get_batch_interval_seconds() // 60,
        },
        "sent_today": sent_today,
        "remaining_today": max(0, get_daily_limit() - sent_today),
        "approval_queue_size": queued,
    }


async def _gather_compliance_inputs(
    *, to_email: str, account_id: str | None
) -> dict[str, Any]:
    """Pull suppression + contact + recent-send state needed for compliance gate."""
    async with async_session_factory() as session:
        sup_emails: set[str] = set()
        sup_domains: set[str] = set()
        contact_opt_out = False
        bounced_before = False
        risk_score = 0.0
        allowed_use = "business_contact_research_only"
        try:
            sup_rows = (await session.execute(select(SuppressionRecord))).scalars().all()
            for r in sup_rows:
                if r.email: sup_emails.add(r.email.lower())
                if r.domain: sup_domains.add(r.domain.lower())

            if account_id:
                acc = (await session.execute(
                    select(AccountRecord).where(AccountRecord.id == account_id)
                )).scalar_one_or_none()
                if acc:
                    allowed_use = (acc.extra or {}).get("allowed_use") or allowed_use
                    if (acc.risk_level or "").lower() == "high":
                        risk_score = 80.0

                contacts = (await session.execute(
                    select(ContactRecord).where(ContactRecord.account_id == account_id)
                )).scalars().all()
                for c in contacts:
                    if c.email and c.email.lower() == to_email.lower() and c.opt_out:
                        contact_opt_out = True

            bounce_log = (await session.execute(
                select(EmailSendLog).where(
                    EmailSendLog.to_email == to_email,
                    EmailSendLog.status == "bounced",
                ).limit(1)
            )).scalar_one_or_none()
            if bounce_log:
                bounced_before = True

            today_start = _utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
            sent_today_count = int((await session.execute(
                select(func.count()).select_from(EmailSendLog).where(
                    EmailSendLog.status == "sent",
                    EmailSendLog.sent_at >= today_start,
                )
            )).scalar() or 0)

            # Last batch timestamp
            last = (await session.execute(
                select(EmailSendLog.sent_at).where(
                    EmailSendLog.status == "sent"
                ).order_by(EmailSendLog.sent_at.desc()).limit(1)
            )).scalar_one_or_none()
            seconds_since_last = None
            if last is not None:
                seconds_since_last = (_utcnow() - last).total_seconds()
        except Exception as exc:  # noqa: BLE001
            log.warning("compliance_gather_failed err=%s", exc)
            return {"db_error": str(exc)}

    return {
        "sup_emails": sup_emails,
        "sup_domains": sup_domains,
        "contact_opt_out": contact_opt_out,
        "bounced_before": bounced_before,
        "risk_score": risk_score,
        "allowed_use": allowed_use,
        "sent_today_count": sent_today_count,
        "seconds_since_last_batch": seconds_since_last,
    }


@router.post("/send-approved")
async def send_approved(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """
    Send a single approved row. Body:
        to_email (required)
        subject (required)
        body_plain (required)
        account_id (optional)
        queue_id (optional — if from outreach_queue, marks as sent on success)
        sequence_step (default 0)
        force (default False — skips DB compliance, NEVER skips Gmail config check)
    """
    to_email = str(body.get("to_email") or "").strip()
    subject = str(body.get("subject") or "").strip()
    body_plain = str(body.get("body_plain") or "").strip()
    if not to_email or not subject or not body_plain:
        raise HTTPException(400, "to_email/subject/body_plain required")

    account_id = body.get("account_id")
    queue_id = body.get("queue_id")
    seq_step = int(body.get("sequence_step") or 0)

    if not gmail_is_configured():
        return {"status": "blocked_compliance",
                "reasons": ["gmail_not_configured"],
                "next_action": "POST /api/v1/email/connect/gmail"}

    # Compliance gate
    inputs = await _gather_compliance_inputs(to_email=to_email, account_id=account_id)
    if inputs.get("db_error"):
        return {"status": "skipped_db_unreachable", "error": inputs["db_error"]}

    chk = check_outreach(
        to_email=to_email,
        contact_opt_out=inputs["contact_opt_out"],
        risk_score=inputs["risk_score"],
        allowed_use=inputs["allowed_use"],
        suppression_emails=inputs["sup_emails"],
        suppression_domains=inputs["sup_domains"],
        bounced_before=inputs["bounced_before"],
        sent_today_count=inputs["sent_today_count"],
        sent_in_current_batch=0,
        seconds_since_last_batch=inputs.get("seconds_since_last_batch"),
    )
    if not chk.allowed:
        # Persist a compliance-blocked log row
        async with async_session_factory() as session:
            session.add(EmailSendLog(
                id=_new_id("es_"),
                account_id=account_id, queue_id=queue_id,
                to_email=to_email, subject=subject[:500],
                body_preview=body_plain[:500],
                sender_email=os.getenv("GMAIL_SENDER_EMAIL", ""),
                status="blocked_compliance",
                sequence_step=seq_step,
                compliance_check=chk.to_dict(),
            ))
            try:
                await session.commit()
            except Exception:
                await session.rollback()
        return {"status": "blocked_compliance", "reasons": chk.blocked_reasons}

    # Append opt-out line and send
    final_body = append_opt_out_line(body_plain)
    result = await send_email(
        to_email=to_email,
        subject=subject,
        body_plain=final_body,
        sender_name=body.get("sender_name") or "Sami | Dealix",
    )

    # Persist log
    async with async_session_factory() as session:
        log_row = EmailSendLog(
            id=_new_id("es_"),
            account_id=account_id, queue_id=queue_id,
            to_email=to_email, subject=subject[:500],
            body_preview=final_body[:500],
            sender_email=os.getenv("GMAIL_SENDER_EMAIL", ""),
            status="sent" if result.status == "ok" else "failed",
            gmail_message_id=result.gmail_message_id,
            sent_at=_utcnow() if result.status == "ok" else None,
            sequence_step=seq_step,
            compliance_check=chk.to_dict(),
            bounce_reason=result.error if result.status != "ok" else None,
        )
        session.add(log_row)
        if queue_id and result.status == "ok":
            qr = (await session.execute(
                select(OutreachQueueRecord).where(OutreachQueueRecord.id == queue_id)
            )).scalar_one_or_none()
            if qr:
                qr.status = "sent"
                qr.sent_at = _utcnow()
        try:
            await session.commit()
        except Exception as exc:  # noqa: BLE001
            await session.rollback()
            return {"status": "commit_failed", "send_status": result.status, "error": str(exc)}

    return {
        "status": result.status,
        "gmail_message_id": result.gmail_message_id,
        "send_log_id": log_row.id,
        "error": result.error,
    }


@router.post("/send-batch")
async def send_batch(body: dict[str, Any] = Body(default={})) -> dict[str, Any]:
    """
    Send up to BATCH_SIZE approved rows from the outreach queue.
    Body:
        max: int (default = EMAIL_BATCH_SIZE)
        only_status: 'approved' (default) — skips 'queued' which still need approval
    """
    max_n = int(body.get("max") or get_batch_size())
    only_status = str(body.get("only_status") or "approved")
    if max_n < 1 or max_n > 50:
        raise HTTPException(400, "max_out_of_range: 1..50")

    if not gmail_is_configured():
        return {"status": "blocked", "reason": "gmail_not_configured",
                "next_action": "POST /api/v1/email/connect/gmail"}

    sent: list[dict[str, Any]] = []
    blocked: list[dict[str, Any]] = []

    async with async_session_factory() as session:
        try:
            rows = (await session.execute(
                select(OutreachQueueRecord).where(
                    OutreachQueueRecord.status == only_status,
                    OutreachQueueRecord.channel.in_(["email", "email_warm", "email_followup"]),
                ).limit(max_n)
            )).scalars().all()
        except Exception as exc:  # noqa: BLE001
            return {"status": "skipped_db_unreachable", "error": str(exc)}

    for r in rows:
        # Need to fetch contact email for the account
        async with async_session_factory() as s2:
            try:
                contact = (await s2.execute(
                    select(ContactRecord).where(
                        ContactRecord.account_id == r.lead_id,
                        ContactRecord.email.is_not(None),
                        ContactRecord.opt_out == False,  # noqa: E712
                    ).limit(1)
                )).scalar_one_or_none()
                acc = (await s2.execute(
                    select(AccountRecord).where(AccountRecord.id == r.lead_id)
                )).scalar_one_or_none()
            except Exception as exc:  # noqa: BLE001
                blocked.append({"queue_id": r.id, "reason": f"db: {exc}"})
                continue

        if not contact or not contact.email:
            blocked.append({"queue_id": r.id, "reason": "no_contact_email"})
            continue

        subject = f"Dealix — تجربة تأهيل عملاء لـ {(acc.company_name if acc else 'فريقكم')[:60]}"

        send_result = await send_approved.__wrapped__({} if False else {
            "to_email": contact.email,
            "subject": subject,
            "body_plain": r.message,
            "account_id": r.lead_id,
            "queue_id": r.id,
            "sequence_step": 0,
        }) if False else None  # FastAPI doesn't expose __wrapped__; we re-call helper inline

        # Inline send instead of recursive HTTP-style call
        import asyncio as _asyncio
        send_payload = {
            "to_email": contact.email,
            "subject": subject,
            "body_plain": r.message,
            "account_id": r.lead_id,
            "queue_id": r.id,
            "sequence_step": 0,
        }
        try:
            send_result = await send_approved(send_payload)
        except HTTPException as he:
            blocked.append({"queue_id": r.id, "reason": f"http: {he.detail}"})
            continue

        if send_result.get("status") == "ok":
            sent.append({"queue_id": r.id, "to": contact.email,
                         "gmail_message_id": send_result.get("gmail_message_id")})
        else:
            blocked.append({
                "queue_id": r.id, "to": contact.email,
                "status": send_result.get("status"),
                "reasons": send_result.get("reasons") or [send_result.get("error")],
            })

    return {
        "status": "ok",
        "sent_count": len(sent),
        "blocked_count": len(blocked),
        "sent": sent,
        "blocked": blocked,
        "limits": {
            "batch_size": get_batch_size(),
            "daily_limit": get_daily_limit(),
        },
    }


@router.post("/replies/sync")
async def replies_sync(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """
    Manual reply ingestion endpoint (until Gmail Pub/Sub is wired).
    Body:
        to_email: original recipient (the prospect)
        from_email: sender of the reply (their address)
        subject: reply subject
        text: reply body
        original_send_log_id: optional
    """
    text = str(body.get("text") or "").strip()
    from_email = str(body.get("from_email") or "").strip().lower()
    if not text or not from_email:
        raise HTTPException(400, "from_email and text required")

    classification = await classify_reply(text)

    async with async_session_factory() as session:
        try:
            log_row = None
            if body.get("original_send_log_id"):
                log_row = (await session.execute(
                    select(EmailSendLog).where(EmailSendLog.id == body["original_send_log_id"])
                )).scalar_one_or_none()
            if log_row is None:
                # Find by recipient = from_email of reply
                log_row = (await session.execute(
                    select(EmailSendLog).where(
                        EmailSendLog.to_email == from_email,
                        EmailSendLog.status == "sent",
                    ).order_by(EmailSendLog.sent_at.desc()).limit(1)
                )).scalar_one_or_none()
            if log_row:
                log_row.status = "replied"
                log_row.reply_classification = classification.category
                log_row.reply_received_at = _utcnow()

            # If unsubscribe → add to suppression
            if classification.category == "unsubscribe":
                session.add(SuppressionRecord(
                    id=_new_id("sup_"),
                    email=from_email, phone=None, domain=None,
                    reason="opt_out_via_reply",
                ))
            await session.commit()
        except Exception as exc:  # noqa: BLE001
            await session.rollback()
            return {"status": "skipped_db_unreachable", "error": str(exc),
                    "classification": classification.to_dict()}

    return {
        "status": "ok",
        "classification": classification.to_dict(),
        "matched_send_log": getattr(log_row, "id", None) if log_row else None,
    }

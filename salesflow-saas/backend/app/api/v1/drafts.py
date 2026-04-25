"""Draft Queue API — review, approve, send, track outreach drafts.

All outreach starts as drafts. Sami reviews in dashboard, approves
batch, then system sends via existing Celery tasks.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional
from uuid import uuid4

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger("dealix.drafts")

router = APIRouter(prefix="/drafts", tags=["Draft Queue"])


async def _get_db():
    from app.database import get_db
    async for session in get_db():
        yield session


class DraftFilter(BaseModel):
    status: Optional[str] = "draft"
    channel: Optional[str] = None
    batch_id: Optional[str] = None
    sector: Optional[str] = None
    limit: int = 50


class ApproveBatchRequest(BaseModel):
    batch_id: str


class LogReplyRequest(BaseModel):
    reply_text: str


class EditDraftRequest(BaseModel):
    subject: Optional[str] = None
    body: Optional[str] = None
    channel: Optional[str] = None
    contact_email: Optional[str] = None
    contact_phone: Optional[str] = None


@router.get("/")
async def list_drafts(
    status: Optional[str] = Query("draft"),
    channel: Optional[str] = Query(None),
    batch_id: Optional[str] = Query(None),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(_get_db),
) -> Dict[str, Any]:
    from app.models.outreach_draft import OutreachDraft

    stmt = select(OutreachDraft)
    if status:
        stmt = stmt.where(OutreachDraft.status == status)
    if channel:
        stmt = stmt.where(OutreachDraft.channel == channel)
    if batch_id:
        stmt = stmt.where(OutreachDraft.batch_id == batch_id)
    stmt = stmt.order_by(OutreachDraft.created_at.desc()).limit(limit)

    result = await db.execute(stmt)
    rows = list(result.scalars().all())
    return {
        "drafts": [r.to_dict() for r in rows],
        "count": len(rows),
        "filter": {"status": status, "channel": channel, "batch_id": batch_id},
    }


@router.get("/stats")
async def draft_stats(db: AsyncSession = Depends(_get_db)) -> Dict[str, Any]:
    from app.models.outreach_draft import OutreachDraft

    result = await db.execute(
        select(OutreachDraft.status, func.count(OutreachDraft.id))
        .group_by(OutreachDraft.status)
    )
    counts = {row[0]: row[1] for row in result.all()}
    return {
        "total": sum(counts.values()),
        "draft": counts.get("draft", 0),
        "approved": counts.get("approved", 0),
        "sent": counts.get("sent", 0),
        "replied": counts.get("replied", 0),
        "opted_out": counts.get("opted_out", 0),
        "bounced": counts.get("bounced", 0),
        "skipped": counts.get("skipped", 0),
    }


@router.get("/{draft_id}")
async def get_draft(draft_id: str, db: AsyncSession = Depends(_get_db)) -> Dict[str, Any]:
    from app.models.outreach_draft import OutreachDraft

    result = await db.execute(
        select(OutreachDraft).where(OutreachDraft.id == draft_id)
    )
    draft = result.scalar_one_or_none()
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")
    d = draft.to_dict()
    d["body"] = draft.body
    d["followup_2d"] = draft.followup_2d
    d["followup_5d"] = draft.followup_5d
    d["call_script"] = draft.call_script
    return d


@router.post("/{draft_id}/approve")
async def approve_draft(draft_id: str, db: AsyncSession = Depends(_get_db)) -> Dict[str, Any]:
    from app.models.outreach_draft import OutreachDraft

    result = await db.execute(
        select(OutreachDraft).where(OutreachDraft.id == draft_id)
    )
    draft = result.scalar_one_or_none()
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")
    if draft.status != "draft":
        return {"id": str(draft.id), "status": draft.status, "message": "already processed"}

    draft.status = "approved"
    draft.approved_at = datetime.now(timezone.utc)
    await db.commit()
    return {"id": str(draft.id), "status": "approved"}


@router.post("/approve-batch")
async def approve_batch(
    req: ApproveBatchRequest, db: AsyncSession = Depends(_get_db)
) -> Dict[str, Any]:
    from app.models.outreach_draft import OutreachDraft

    result = await db.execute(
        update(OutreachDraft)
        .where(OutreachDraft.batch_id == req.batch_id, OutreachDraft.status == "draft")
        .values(status="approved", approved_at=datetime.now(timezone.utc))
    )
    await db.commit()
    return {"batch_id": req.batch_id, "approved_count": result.rowcount}


@router.post("/{draft_id}/send")
async def send_draft(draft_id: str, db: AsyncSession = Depends(_get_db)) -> Dict[str, Any]:
    from app.models.outreach_draft import OutreachDraft

    result = await db.execute(
        select(OutreachDraft).where(OutreachDraft.id == draft_id)
    )
    draft = result.scalar_one_or_none()
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")
    if draft.status not in ("approved", "draft"):
        return {"id": str(draft.id), "status": draft.status, "message": "not sendable"}

    send_result = {"channel": draft.channel, "status": "pending"}

    if draft.channel == "email" and draft.contact_email:
        try:
            from app.integrations.email_sender import send_email
            r = await send_email(draft.contact_email, draft.subject, draft.body)
            send_result = {"channel": "email", "status": "sent", "result": r}
        except Exception as exc:
            send_result = {"channel": "email", "status": "failed", "error": str(exc)[:200]}

    elif draft.channel == "whatsapp" and draft.contact_phone:
        try:
            from app.integrations.whatsapp import send_whatsapp_message
            r = await send_whatsapp_message(draft.contact_phone, draft.body)
            send_result = {"channel": "whatsapp", "status": "sent", "result": r}
        except Exception as exc:
            send_result = {"channel": "whatsapp", "status": "failed", "error": str(exc)[:200]}

    elif draft.channel == "sms" and draft.contact_phone:
        try:
            from app.integrations.sms import send_sms
            r = await send_sms(draft.contact_phone, draft.body)
            send_result = {"channel": "sms", "status": "sent", "result": r}
        except Exception as exc:
            send_result = {"channel": "sms", "status": "failed", "error": str(exc)[:200]}

    elif draft.channel == "linkedin":
        send_result = {
            "channel": "linkedin",
            "status": "manual_required",
            "message": "Copy the message and send manually on LinkedIn",
        }

    if send_result.get("status") == "sent":
        draft.status = "sent"
        draft.sent_at = datetime.now(timezone.utc)
    elif send_result.get("status") == "failed":
        draft.next_action = f"send_failed: {send_result.get('error', '')[:100]}"

    await db.commit()
    return {"id": str(draft.id), **send_result}


@router.post("/{draft_id}/skip")
async def skip_draft(draft_id: str, db: AsyncSession = Depends(_get_db)) -> Dict[str, Any]:
    from app.models.outreach_draft import OutreachDraft

    result = await db.execute(
        select(OutreachDraft).where(OutreachDraft.id == draft_id)
    )
    draft = result.scalar_one_or_none()
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")
    draft.status = "skipped"
    await db.commit()
    return {"id": str(draft.id), "status": "skipped"}


@router.patch("/{draft_id}")
async def edit_draft(
    draft_id: str, req: EditDraftRequest, db: AsyncSession = Depends(_get_db)
) -> Dict[str, Any]:
    from app.models.outreach_draft import OutreachDraft

    result = await db.execute(
        select(OutreachDraft).where(OutreachDraft.id == draft_id)
    )
    draft = result.scalar_one_or_none()
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")
    if draft.status != "draft":
        raise HTTPException(status_code=400, detail="Can only edit drafts, not sent/approved")

    for field, value in req.model_dump(exclude_none=True).items():
        setattr(draft, field, value)
    await db.commit()
    return {"id": str(draft.id), "status": "edited", "updated_fields": list(req.model_dump(exclude_none=True).keys())}


@router.post("/{draft_id}/log-reply")
async def log_reply(
    draft_id: str, req: LogReplyRequest, db: AsyncSession = Depends(_get_db)
) -> Dict[str, Any]:
    from app.models.outreach_draft import OutreachDraft
    from app.api.v1.automation import classify_reply, ClassifyReplyRequest

    result = await db.execute(
        select(OutreachDraft).where(OutreachDraft.id == draft_id)
    )
    draft = result.scalar_one_or_none()
    if not draft:
        raise HTTPException(status_code=404, detail="Draft not found")

    classification = await classify_reply(
        ClassifyReplyRequest(
            reply_text=req.reply_text,
            company=draft.company,
            original_sector=draft.sector,
        )
    )

    draft.status = "replied"
    draft.replied_at = datetime.now(timezone.utc)
    draft.reply_text = req.reply_text
    draft.reply_category = classification["category"]
    draft.next_action = classification["next_action"]

    if classification["category"] == "unsubscribe":
        draft.status = "opted_out"
        draft.next_action = "suppressed — no further contact"

    await db.commit()

    return {
        "id": str(draft.id),
        "reply_category": classification["category"],
        "suggested_response": classification["suggested_response"],
        "next_action": classification["next_action"],
        "auto_reply_allowed": classification["auto_reply_allowed"],
    }

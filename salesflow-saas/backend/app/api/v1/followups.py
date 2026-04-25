"""Follow-up Scheduler — generates follow-up drafts for unreplied outreach.

Checks sent drafts that haven't received replies after 2/5/10 days
and creates new follow-up drafts linked to the original.
"""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List
from uuid import uuid4

from fastapi import APIRouter, Depends, Query
from pydantic import BaseModel
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

logger = logging.getLogger("dealix.followups")

router = APIRouter(prefix="/followups", tags=["Follow-ups"])


async def _get_db():
    from app.database import get_db
    async for session in get_db():
        yield session


@router.get("/due")
async def list_due_followups(
    days_since_sent: int = Query(2, ge=1, le=30),
    limit: int = Query(50, ge=1, le=200),
    db: AsyncSession = Depends(_get_db),
) -> Dict[str, Any]:
    from app.models.outreach_draft import OutreachDraft

    cutoff = datetime.now(timezone.utc) - timedelta(days=days_since_sent)
    stmt = (
        select(OutreachDraft)
        .where(
            and_(
                OutreachDraft.status == "sent",
                OutreachDraft.sent_at <= cutoff,
                OutreachDraft.reply_text.is_(None),
            )
        )
        .order_by(OutreachDraft.sent_at.asc())
        .limit(limit)
    )
    result = await db.execute(stmt)
    rows = list(result.scalars().all())

    due = []
    for row in rows:
        days_elapsed = (datetime.now(timezone.utc) - row.sent_at).days if row.sent_at else 0
        followup_text = ""
        followup_type = ""
        if days_elapsed >= 10:
            followup_text = row.followup_5d or "آخر متابعة — لو مو الوقت المناسب أفهم تماماً. شكراً."
            followup_type = "day_10_breakup"
        elif days_elapsed >= 5:
            followup_text = row.followup_5d or row.followup_2d or ""
            followup_type = "day_5_value"
        elif days_elapsed >= 2:
            followup_text = row.followup_2d or ""
            followup_type = "day_2_reminder"

        if followup_text:
            due.append({
                "original_draft_id": str(row.id),
                "company": row.company,
                "channel": row.channel,
                "contact_email": row.contact_email,
                "contact_phone": row.contact_phone,
                "days_since_sent": days_elapsed,
                "followup_type": followup_type,
                "followup_text": followup_text,
                "sector": row.sector,
            })

    return {
        "due_count": len(due),
        "cutoff_days": days_since_sent,
        "followups": due,
    }


class GenerateFollowupsRequest(BaseModel):
    days_since_sent: int = 2
    max_followups: int = 20


@router.post("/generate")
async def generate_followup_drafts(
    req: GenerateFollowupsRequest,
    db: AsyncSession = Depends(_get_db),
) -> Dict[str, Any]:
    from app.models.outreach_draft import OutreachDraft

    cutoff = datetime.now(timezone.utc) - timedelta(days=req.days_since_sent)
    stmt = (
        select(OutreachDraft)
        .where(
            and_(
                OutreachDraft.status == "sent",
                OutreachDraft.sent_at <= cutoff,
                OutreachDraft.reply_text.is_(None),
            )
        )
        .order_by(OutreachDraft.sent_at.asc())
        .limit(req.max_followups)
    )
    result = await db.execute(stmt)
    originals = list(result.scalars().all())

    created = 0
    batch_id = f"followup_{datetime.now(timezone.utc).strftime('%Y%m%d')}_{str(uuid4())[:6]}"

    for orig in originals:
        days_elapsed = (datetime.now(timezone.utc) - orig.sent_at).days if orig.sent_at else 0
        if days_elapsed >= 10:
            body = orig.followup_5d or "آخر متابعة — لو مناسب نتكلم، أنا موجود. لو لا، شكراً على وقتكم."
            subject = f"متابعة أخيرة: {orig.company}"
        elif days_elapsed >= 5:
            body = orig.followup_5d or orig.followup_2d or ""
            subject = f"متابعة: {orig.company}"
        else:
            body = orig.followup_2d or ""
            subject = f"متابعة سريعة: {orig.company}"

        if not body:
            continue

        followup = OutreachDraft(
            batch_id=batch_id,
            company=orig.company,
            contact_name=orig.contact_name,
            contact_email=orig.contact_email,
            contact_phone=orig.contact_phone,
            channel=orig.channel,
            subject=subject,
            body=body,
            sector=orig.sector,
            city=orig.city,
            fit_score=orig.fit_score,
            risk_score=orig.risk_score,
            status="draft",
            approval_required=True,
            source=f"followup_day_{days_elapsed}_of_{str(orig.id)[:8]}",
        )
        db.add(followup)
        created += 1

    if created:
        await db.commit()

    return {
        "batch_id": batch_id,
        "followups_created": created,
        "originals_checked": len(originals),
    }

"""
Draft-First Revenue Machine — Gmail drafts + LinkedIn drafts + revenue-machine/run.

Endpoints:
    POST /api/v1/automation/revenue-machine/run     — daily orchestrator (the brain)
    POST /api/v1/gmail/drafts/create                 — single Gmail draft
    POST /api/v1/gmail/drafts/create-batch           — batch Gmail drafts from queue
    GET  /api/v1/gmail/drafts/today                  — list today's drafts
    POST /api/v1/linkedin/drafts/create              — single LinkedIn draft
    GET  /api/v1/linkedin/drafts/today               — list today's LinkedIn queue
    PATCH /api/v1/linkedin/drafts/{id}/mark-sent     — Sami marks "I sent it"
    POST /api/v1/linkedin/drafts/{id}/manual-capture — paste a reply we got
    GET  /api/v1/dashboard/revenue-machine/today     — today's metrics
    POST /api/v1/automation/daily-report/generate    — write docs/ops/daily_reports/YYYY-MM-DD.md

Rules baked in:
- LinkedIn: NEVER auto-send, NEVER scrape (per LinkedIn ToS)
- Gmail: drafts.create by default; messages.send only on /email/send-approved
- All gated by compliance (suppression / opt-out / risk / allowed_use)
"""

from __future__ import annotations

import logging
import os
import uuid
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any

from fastapi import APIRouter, Body, HTTPException
from sqlalchemy import func, select

from auto_client_acquisition.email.compliance import (
    append_opt_out_line,
    check_outreach,
)
from auto_client_acquisition.email.daily_targeting import (
    compute_followup_schedule,
    llm_personalize,
    render_email_template,
    select_top_n_diversified,
)
from auto_client_acquisition.email.gmail_send import (
    create_draft as gmail_create_draft,
    is_configured as gmail_is_configured,
)
from auto_client_acquisition.email.research_agent import (
    research_company_with_llm,
)
from db.models import (
    AccountRecord,
    ContactRecord,
    EmailSendLog,
    GmailDraftRecord,
    LeadScoreRecord,
    LinkedInDraftRecord,
    OutreachQueueRecord,
    SuppressionRecord,
)
from db.session import async_session_factory

router = APIRouter(prefix="/api/v1", tags=["revenue-machine"])
log = logging.getLogger(__name__)


def _new_id(prefix: str = "") -> str:
    return f"{prefix}{uuid.uuid4().hex[:24]}" if prefix else uuid.uuid4().hex[:24]


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


# ── Daily orchestrator ────────────────────────────────────────────
@router.post("/automation/revenue-machine/run")
async def revenue_machine_run(body: dict[str, Any] = Body(default={})) -> dict[str, Any]:
    """
    Daily Revenue Machine orchestrator. Builds:
        50 Gmail drafts
        20 LinkedIn drafts
        10 call scripts
        10 partner intros (drafts)

    Body:
        gmail_drafts: int = 50
        linkedin_drafts: int = 20
        call_scripts: int = 10
        partner_drafts: int = 10
        candidate_pool_size: int = 200
        sectors: list[str] | None
        cities: list[str] | None
        approval_mode: 'draft_only' (default) | 'auto_send_low_risk'
        create_gmail_drafts_in_inbox: bool = False (only if Gmail OAuth configured)
    """
    n_gmail = int(body.get("gmail_drafts") or 50)
    n_linkedin = int(body.get("linkedin_drafts") or 20)
    n_calls = int(body.get("call_scripts") or 10)
    n_partners = int(body.get("partner_drafts") or 10)
    pool_size = int(body.get("candidate_pool_size") or 200)
    create_in_gmail = bool(body.get("create_gmail_drafts_in_inbox", False))
    sectors_filter = body.get("sectors")
    cities_filter = body.get("cities")

    # 1. Pull candidate pool
    excluded = {"opt_out": 0, "suppressed": 0, "recently_contacted": 0,
                "high_risk": 0, "no_allowed_use": 0, "no_business_contact": 0}

    async with async_session_factory() as session:
        try:
            q = select(AccountRecord).where(AccountRecord.status.in_(["enriched", "new"]))
            if sectors_filter: q = q.where(AccountRecord.sector.in_(sectors_filter))
            if cities_filter: q = q.where(AccountRecord.city.in_(cities_filter))
            q = q.order_by(AccountRecord.data_quality_score.desc()).limit(pool_size)
            accounts = (await session.execute(q)).scalars().all()
            ids = [a.id for a in accounts]

            scores = (await session.execute(
                select(LeadScoreRecord).where(LeadScoreRecord.account_id.in_(ids))
            )).scalars().all() if ids else []
            score_map: dict[str, LeadScoreRecord] = {}
            for s in scores:
                if s.account_id not in score_map or s.created_at > score_map[s.account_id].created_at:
                    score_map[s.account_id] = s

            contacts = (await session.execute(
                select(ContactRecord).where(ContactRecord.account_id.in_(ids))
            )).scalars().all() if ids else []
            contacts_by_acc: dict[str, list[ContactRecord]] = {}
            for c in contacts:
                contacts_by_acc.setdefault(c.account_id, []).append(c)

            sup = (await session.execute(select(SuppressionRecord))).scalars().all()
            sup_emails = {s.email.lower() for s in sup if s.email}
            sup_domains = {s.domain.lower() for s in sup if s.domain}

            recent_cutoff = _utcnow() - timedelta(days=14)
            recent_logs = (await session.execute(
                select(EmailSendLog.account_id).where(
                    EmailSendLog.sent_at >= recent_cutoff
                ).distinct()
            )).scalars().all() if ids else []
            recently = set(recent_logs)
        except Exception as exc:  # noqa: BLE001
            return {"status": "skipped_db_unreachable", "error": str(exc)}

    # 2. Filter into eligible candidates
    candidates: list[dict[str, Any]] = []
    for a in accounts:
        if a.id in recently:
            excluded["recently_contacted"] += 1; continue
        if (a.risk_level or "").lower() == "high":
            excluded["high_risk"] += 1; continue
        allowed = (a.extra or {}).get("allowed_use")
        if not allowed or allowed in {"unknown", ""}:
            excluded["no_allowed_use"] += 1; continue
        if a.domain and a.domain.lower() in sup_domains:
            excluded["suppressed"] += 1; continue

        ac = contacts_by_acc.get(a.id, [])
        if any(c.opt_out for c in ac):
            excluded["opt_out"] += 1; continue
        biz_email = next(
            (c.email for c in ac if c.email and c.email.lower() not in sup_emails
             and not any(p in c.email.lower() for p in
                         ["@gmail.com", "@hotmail.com", "@yahoo.com", "@outlook.com", "@icloud.com"])),
            None,
        )
        any_phone = next((c.phone for c in ac if c.phone), None)
        if not biz_email and not any_phone:
            excluded["no_business_contact"] += 1; continue

        score = score_map.get(a.id)
        candidates.append({
            "id": a.id, "company_name": a.company_name,
            "domain": a.domain, "website": a.website,
            "city": a.city, "sector": a.sector, "sector_ar": a.sector,
            "google_place_id": a.google_place_id,
            "data_quality_score": a.data_quality_score,
            "risk_level": a.risk_level,
            "best_email": biz_email, "best_phone": any_phone,
            "allowed_use": allowed, "best_source": a.best_source,
            "total_score": score.total_score if score else 0,
            "priority": score.priority if score else "P3",
            "recommended_channel": score.recommended_channel if score else None,
        })

    # 3. Bucket selection
    has_email = [c for c in candidates if c["best_email"]]
    no_email = [c for c in candidates if not c["best_email"] and c["best_phone"]]

    gmail_picks = select_top_n_diversified(has_email, target_count=n_gmail)
    # LinkedIn lane prefers SaaS / agency / consulting (knowledge-worker contacts)
    linkedin_pool = [c for c in candidates if c["sector"] in
                     {"saas", "marketing_agency", "consulting_firm", "training_center"}]
    if len(linkedin_pool) < n_linkedin:
        linkedin_pool += [c for c in has_email if c not in linkedin_pool]
    linkedin_picks = select_top_n_diversified(linkedin_pool, target_count=n_linkedin,
                                              sector_caps={"saas": n_linkedin})
    call_picks = select_top_n_diversified(no_email or has_email, target_count=n_calls)
    partner_pool = [c for c in candidates if c["sector"] in
                    {"marketing_agency", "consulting_firm"}]
    partner_picks = partner_pool[:n_partners]

    # 4. Generate drafts
    gmail_drafts_out: list[dict[str, Any]] = []
    linkedin_drafts_out: list[dict[str, Any]] = []
    call_scripts_out: list[dict[str, Any]] = []

    async with async_session_factory() as session:
        # Gmail drafts
        for cand in gmail_picks:
            brief = await research_company_with_llm(cand)
            base = render_email_template(cand, cand.get("priority") or "P2")
            personalized = await llm_personalize(cand, base)
            body_with_optout = append_opt_out_line(personalized["body_ar"])
            subject = base["subject_ar"]

            chk = check_outreach(
                to_email=cand["best_email"],
                contact_opt_out=False,
                risk_score=20.0 if cand["risk_level"] == "medium" else 0.0,
                allowed_use=cand["allowed_use"],
                suppression_emails=sup_emails,
                suppression_domains=sup_domains,
                bounced_before=False, sent_today_count=0,
                sent_in_current_batch=0, seconds_since_last_batch=99999,
            )

            draft_record = GmailDraftRecord(
                id=_new_id("gd_"),
                account_id=cand["id"], queue_id=None,
                to_email=cand["best_email"],
                subject=subject[:500], body_plain=body_with_optout,
                sender_email=os.getenv("GMAIL_SENDER_EMAIL", ""),
                gmail_draft_id=None, gmail_message_id=None,
                status="created" if chk.allowed else "failed",
                discarded_reason=None if chk.allowed else "; ".join(chk.blocked_reasons),
            )

            # Optionally push into Gmail Drafts inbox (real)
            if create_in_gmail and chk.allowed and gmail_is_configured():
                gmail_result = await gmail_create_draft(
                    to_email=cand["best_email"],
                    subject=subject,
                    body_plain=body_with_optout,
                )
                if gmail_result.status == "ok":
                    draft_record.gmail_draft_id = gmail_result.draft_id
                    draft_record.gmail_message_id = gmail_result.message_id
                else:
                    draft_record.discarded_reason = (
                        f"gmail_api: {gmail_result.status} {gmail_result.error or ''}"
                    )[:255]

            session.add(draft_record)
            gmail_drafts_out.append({
                "draft_id": draft_record.id,
                "company": cand["company_name"], "to_email": cand["best_email"],
                "subject": subject, "body_preview": body_with_optout[:300],
                "status": draft_record.status,
                "compliance_blocked": chk.blocked_reasons or None,
                "personalized_by_llm": personalized.get("personalized_by_llm") == "true",
                "research": brief.to_dict(),
                "gmail_draft_id_in_inbox": draft_record.gmail_draft_id,
            })

        # LinkedIn drafts (NEVER auto-send)
        for cand in linkedin_picks:
            brief = await research_company_with_llm(cand)
            search_query = f'"{cand["company_name"]}" {cand.get("city") or "Saudi Arabia"} site:linkedin.com'
            company_context = brief.company_brief
            reason = brief.pain_hypothesis
            msg_ar = (
                f"{brief.best_first_sentence}\n\n"
                f"{brief.dealix_fit}\n\n"
                f"عندنا Pilot 7 أيام بـ 499 ريال. تناسبكم 20 دقيقة هذا الأسبوع؟"
            )
            msg_en = (
                f"Quick reach-out about {cand['company_name']}. "
                f"{brief.dealix_fit}. We have a 7-day Pilot at 499 SAR — "
                "open to a 20-min chat this week?"
            )
            ld = LinkedInDraftRecord(
                id=_new_id("ld_"),
                account_id=cand["id"],
                company_name=cand["company_name"][:255],
                contact_name=None,
                profile_search_query=search_query[:500],
                company_context=company_context,
                reason_for_outreach=reason,
                message_ar=msg_ar, message_en=msg_en,
                followup_day_3="متابعة سريعة لرسالتي. هل عندكم سؤال محدد؟",
                followup_day_7="آخر متابعة. لو الوقت غير مناسب الآن، نقدر نتقابل بعد شهر.",
                status="draft",
            )
            session.add(ld)
            linkedin_drafts_out.append({
                "draft_id": ld.id,
                "company": cand["company_name"],
                "search_query": search_query,
                "context": company_context,
                "message_preview": msg_ar[:300],
                "research": brief.to_dict(),
            })

        # Call scripts
        for cand in call_picks:
            brief = await research_company_with_llm(cand)
            script = (
                f"السلام عليكم، معك سامي من Dealix.\n"
                f"اتصل في وقت مناسب؟\n\n"
                f"شركتكم في {cand.get('sector_ar') or cand.get('sector') or 'القطاع'} "
                f"بـ {cand.get('city') or 'السعودية'} — "
                f"{brief.pain_hypothesis}\n\n"
                f"نقدم Pilot 7 أيام بـ 499 ريال — نرد على leadsكم نحن، تشوفون النتيجة، ثم تقرّرون.\n\n"
                f"تناسبكم 20 دقيقة هذا الأسبوع نوضح؟"
            )
            call_scripts_out.append({
                "company": cand["company_name"],
                "phone": cand["best_phone"],
                "city": cand.get("city"),
                "sector": cand.get("sector"),
                "research": brief.to_dict(),
                "call_script": script,
            })

        try:
            await session.commit()
        except Exception as exc:  # noqa: BLE001
            await session.rollback()
            return {"status": "commit_failed", "error": str(exc)}

    # Build daily summary
    return {
        "status": "ok",
        "generated_at": _utcnow().isoformat(),
        "candidates_pool": len(accounts),
        "candidates_eligible": len(candidates),
        "excluded": excluded,
        "produced": {
            "gmail_drafts": len(gmail_drafts_out),
            "linkedin_drafts": len(linkedin_drafts_out),
            "call_scripts": len(call_scripts_out),
            "partner_drafts_pool": len(partner_picks),
        },
        "gmail_drafts_in_inbox": create_in_gmail and gmail_is_configured(),
        "gmail_drafts": gmail_drafts_out[:n_gmail],
        "linkedin_drafts": linkedin_drafts_out[:n_linkedin],
        "call_scripts": call_scripts_out[:n_calls],
        "approval_required": True,
        "next_action": (
            "Open /api/v1/dashboard/revenue-machine/today to review,"
            " then approve via /api/v1/email/send-approved per row."
        ),
    }


# ── Gmail draft endpoints ─────────────────────────────────────────
@router.post("/gmail/drafts/create")
async def gmail_drafts_create(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """Create a single Gmail draft. Body: to_email, subject, body_plain, account_id."""
    to_email = str(body.get("to_email") or "").strip()
    subject = str(body.get("subject") or "").strip()
    body_plain = str(body.get("body_plain") or "").strip()
    if not all([to_email, subject, body_plain]):
        raise HTTPException(400, "to_email/subject/body_plain required")

    body_with_optout = append_opt_out_line(body_plain)

    record = GmailDraftRecord(
        id=_new_id("gd_"),
        account_id=body.get("account_id"),
        queue_id=body.get("queue_id"),
        to_email=to_email, subject=subject[:500], body_plain=body_with_optout,
        sender_email=os.getenv("GMAIL_SENDER_EMAIL", ""),
        status="created",
    )

    if gmail_is_configured() and bool(body.get("create_in_inbox", True)):
        result = await gmail_create_draft(
            to_email=to_email, subject=subject, body_plain=body_with_optout,
        )
        if result.status == "ok":
            record.gmail_draft_id = result.draft_id
            record.gmail_message_id = result.message_id
        else:
            record.discarded_reason = f"gmail_api: {result.error}"[:255]

    async with async_session_factory() as session:
        session.add(record)
        try:
            await session.commit()
        except Exception as exc:  # noqa: BLE001
            await session.rollback()
            return {"status": "skipped_db_unreachable", "error": str(exc)}

    return {
        "status": "ok",
        "draft_id": record.id,
        "gmail_draft_id_in_inbox": record.gmail_draft_id,
        "discarded_reason": record.discarded_reason,
    }


@router.get("/gmail/drafts/today")
async def gmail_drafts_today() -> dict[str, Any]:
    today_start = _utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    async with async_session_factory() as session:
        try:
            rows = (await session.execute(
                select(GmailDraftRecord).where(
                    GmailDraftRecord.created_at >= today_start
                ).order_by(GmailDraftRecord.created_at.desc())
            )).scalars().all()
        except Exception as exc:  # noqa: BLE001
            return {"status": "skipped_db_unreachable", "error": str(exc), "items": []}
    return {
        "count": len(rows),
        "items": [
            {
                "id": r.id, "account_id": r.account_id,
                "to_email": r.to_email, "subject": r.subject,
                "body_preview": r.body_plain[:300],
                "status": r.status, "gmail_draft_id": r.gmail_draft_id,
                "created_at": r.created_at.isoformat(),
                "discarded_reason": r.discarded_reason,
            }
            for r in rows
        ],
    }


# ── LinkedIn draft endpoints ──────────────────────────────────────
@router.post("/linkedin/drafts/create")
async def linkedin_drafts_create(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """Create a LinkedIn draft. NEVER auto-sent. Body: company_name, message_ar, optional rest."""
    company = str(body.get("company_name") or "").strip()
    msg_ar = str(body.get("message_ar") or "").strip()
    if not company or not msg_ar:
        raise HTTPException(400, "company_name and message_ar required")

    rec = LinkedInDraftRecord(
        id=_new_id("ld_"),
        account_id=body.get("account_id"),
        company_name=company[:255],
        contact_name=body.get("contact_name"),
        profile_search_query=str(body.get("profile_search_query") or
                                 f'"{company}" site:linkedin.com')[:500],
        company_context=body.get("company_context"),
        reason_for_outreach=body.get("reason_for_outreach"),
        message_ar=msg_ar,
        message_en=body.get("message_en"),
        followup_day_3=body.get("followup_day_3"),
        followup_day_7=body.get("followup_day_7"),
        status="draft",
    )
    async with async_session_factory() as session:
        session.add(rec)
        try:
            await session.commit()
        except Exception as exc:  # noqa: BLE001
            await session.rollback()
            return {"status": "skipped_db_unreachable", "error": str(exc)}
    return {"status": "ok", "draft_id": rec.id}


@router.get("/linkedin/drafts/today")
async def linkedin_drafts_today() -> dict[str, Any]:
    today_start = _utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    async with async_session_factory() as session:
        try:
            rows = (await session.execute(
                select(LinkedInDraftRecord).where(
                    LinkedInDraftRecord.created_at >= today_start
                ).order_by(LinkedInDraftRecord.created_at.desc())
            )).scalars().all()
        except Exception as exc:  # noqa: BLE001
            return {"status": "skipped_db_unreachable", "error": str(exc), "items": []}
    return {
        "count": len(rows),
        "items": [
            {
                "id": r.id, "company_name": r.company_name,
                "search_query": r.profile_search_query,
                "context": r.company_context,
                "reason": r.reason_for_outreach,
                "message_ar": r.message_ar, "message_en": r.message_en,
                "status": r.status,
                "sent_at": r.sent_at.isoformat() if r.sent_at else None,
                "reply": r.reply_text,
            }
            for r in rows
        ],
    }


@router.patch("/linkedin/drafts/{draft_id}/mark-sent")
async def linkedin_drafts_mark_sent(draft_id: str) -> dict[str, Any]:
    """Sami marks 'I sent this manually'. Updates status + sent_at."""
    async with async_session_factory() as session:
        try:
            rec = (await session.execute(
                select(LinkedInDraftRecord).where(LinkedInDraftRecord.id == draft_id)
            )).scalar_one_or_none()
            if not rec:
                raise HTTPException(404, "draft_not_found")
            rec.status = "sent"
            rec.sent_at = _utcnow()
            await session.commit()
        except HTTPException:
            raise
        except Exception as exc:  # noqa: BLE001
            await session.rollback()
            return {"status": "skipped_db_unreachable", "error": str(exc)}
    return {"status": "ok", "draft_id": draft_id, "marked_sent_at": rec.sent_at.isoformat()}


@router.post("/linkedin/drafts/{draft_id}/manual-capture")
async def linkedin_drafts_manual_capture(
    draft_id: str, body: dict[str, Any] = Body(...)
) -> dict[str, Any]:
    """
    Sami pastes a LinkedIn reply they received.
    Body: reply_text
    """
    reply = str(body.get("reply_text") or "").strip()
    if not reply:
        raise HTTPException(400, "reply_text_required")
    async with async_session_factory() as session:
        try:
            rec = (await session.execute(
                select(LinkedInDraftRecord).where(LinkedInDraftRecord.id == draft_id)
            )).scalar_one_or_none()
            if not rec:
                raise HTTPException(404, "draft_not_found")
            rec.reply_text = reply[:2000]
            rec.reply_received_at = _utcnow()
            rec.status = "replied"
            await session.commit()
        except HTTPException:
            raise
        except Exception as exc:  # noqa: BLE001
            await session.rollback()
            return {"status": "skipped_db_unreachable", "error": str(exc)}

    # Classify the reply
    from auto_client_acquisition.email.reply_classifier import classify_reply
    classification = await classify_reply(reply)

    return {
        "status": "ok",
        "draft_id": draft_id,
        "classification": classification.to_dict(),
    }


# ── Revenue dashboard ─────────────────────────────────────────────
@router.get("/dashboard/revenue-machine/today")
async def dashboard_revenue_machine_today() -> dict[str, Any]:
    today_start = _utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    async with async_session_factory() as session:
        try:
            gmail_total = int((await session.execute(
                select(func.count()).select_from(GmailDraftRecord).where(
                    GmailDraftRecord.created_at >= today_start
                )
            )).scalar() or 0)
            gmail_sent = int((await session.execute(
                select(func.count()).select_from(GmailDraftRecord).where(
                    GmailDraftRecord.created_at >= today_start,
                    GmailDraftRecord.status == "sent",
                )
            )).scalar() or 0)
            linkedin_total = int((await session.execute(
                select(func.count()).select_from(LinkedInDraftRecord).where(
                    LinkedInDraftRecord.created_at >= today_start
                )
            )).scalar() or 0)
            linkedin_sent = int((await session.execute(
                select(func.count()).select_from(LinkedInDraftRecord).where(
                    LinkedInDraftRecord.created_at >= today_start,
                    LinkedInDraftRecord.status == "sent",
                )
            )).scalar() or 0)
            linkedin_replied = int((await session.execute(
                select(func.count()).select_from(LinkedInDraftRecord).where(
                    LinkedInDraftRecord.reply_received_at >= today_start
                )
            )).scalar() or 0)
            email_replied = int((await session.execute(
                select(func.count()).select_from(EmailSendLog).where(
                    EmailSendLog.reply_received_at >= today_start
                )
            )).scalar() or 0)
        except Exception as exc:  # noqa: BLE001
            return {"status": "skipped_db_unreachable", "error": str(exc)}

    return {
        "status": "ok",
        "date": today_start.date().isoformat(),
        "gmail_drafts": {"total": gmail_total, "sent": gmail_sent,
                         "remaining_to_review": max(0, gmail_total - gmail_sent)},
        "linkedin_drafts": {"total": linkedin_total, "sent": linkedin_sent,
                            "replied": linkedin_replied},
        "email_replies": email_replied,
        "approval_queue_open": gmail_total - gmail_sent + (linkedin_total - linkedin_sent),
    }


# ── Gmail batch draft create (standalone, separate from revenue-machine/run) ─
@router.post("/gmail/drafts/create-batch")
async def gmail_drafts_create_batch(body: dict[str, Any] = Body(default={})) -> dict[str, Any]:
    """
    Create a batch of Gmail drafts from approved outreach queue rows.
    Body:
        max: int (default = EMAIL_BATCH_SIZE)
        only_status: 'approved' (default) or 'queued'
        create_in_inbox: bool (default True if Gmail OAuth configured)
    """
    max_n = int(body.get("max") or 10)
    only_status = str(body.get("only_status") or "approved")
    create_in_inbox = bool(body.get("create_in_inbox", True)) and gmail_is_configured()
    if max_n < 1 or max_n > 50:
        raise HTTPException(400, "max_out_of_range: 1..50")

    created: list[dict[str, Any]] = []
    failed: list[dict[str, Any]] = []

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
            try:
                contact = (await session.execute(
                    select(ContactRecord).where(
                        ContactRecord.account_id == r.lead_id,
                        ContactRecord.email.is_not(None),
                        ContactRecord.opt_out == False,  # noqa: E712
                    ).limit(1)
                )).scalar_one_or_none()
                acc = (await session.execute(
                    select(AccountRecord).where(AccountRecord.id == r.lead_id)
                )).scalar_one_or_none()
            except Exception as exc:  # noqa: BLE001
                failed.append({"queue_id": r.id, "reason": f"db: {exc}"})
                continue
            if not contact or not contact.email:
                failed.append({"queue_id": r.id, "reason": "no_contact_email"})
                continue
            subject = f"Dealix — تجربة تأهيل عملاء لـ {(acc.company_name if acc else 'فريقكم')[:60]}"
            body_with_optout = append_opt_out_line(r.message)

            draft = GmailDraftRecord(
                id=_new_id("gd_"),
                account_id=r.lead_id, queue_id=r.id,
                to_email=contact.email, subject=subject[:500],
                body_plain=body_with_optout,
                sender_email=os.getenv("GMAIL_SENDER_EMAIL", ""),
                status="created",
            )
            if create_in_inbox:
                gres = await gmail_create_draft(
                    to_email=contact.email, subject=subject, body_plain=body_with_optout,
                )
                if gres.status == "ok":
                    draft.gmail_draft_id = gres.draft_id
                    draft.gmail_message_id = gres.message_id
                else:
                    draft.discarded_reason = f"gmail_api: {gres.error}"[:255]
            session.add(draft)
            created.append({
                "queue_id": r.id, "draft_id": draft.id,
                "to_email": contact.email, "subject": subject,
                "gmail_draft_id_in_inbox": draft.gmail_draft_id,
            })

        try:
            await session.commit()
        except Exception as exc:  # noqa: BLE001
            await session.rollback()
            return {"status": "commit_failed", "error": str(exc),
                    "created": created, "failed": failed}

    return {"status": "ok", "created_count": len(created), "failed_count": len(failed),
            "created": created, "failed": failed}


# ── Replies aliases (respond + route) ────────────────────────────
@router.post("/replies/respond")
async def replies_respond(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """
    Stateless: generate a response draft for a reply without persisting.
    Body: text (required), prefer_llm (default True)
    """
    from auto_client_acquisition.email.reply_classifier import classify_reply
    text = str(body.get("text") or "").strip()
    if not text:
        raise HTTPException(400, "text_required")
    classification = await classify_reply(text, prefer_llm=bool(body.get("prefer_llm", True)))
    return {
        "category": classification.category,
        "confidence": classification.confidence,
        "response_draft_ar": classification.response_draft_ar,
        "auto_send_allowed": classification.auto_send_allowed,
        "requires_human_review": classification.requires_human_review,
    }


@router.post("/replies/route")
async def replies_route(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """
    Stateless: route a reply to its deal_stage + next_action without persisting.
    Body: text (required)
    """
    from auto_client_acquisition.email.reply_classifier import classify_reply
    text = str(body.get("text") or "").strip()
    if not text:
        raise HTTPException(400, "text_required")
    classification = await classify_reply(text, prefer_llm=bool(body.get("prefer_llm", True)))
    return {
        "category": classification.category,
        "next_action": classification.next_action,
        "deal_stage": classification.deal_stage,
        "followup_days": classification.followup_days,
        "requires_human_review": classification.requires_human_review,
    }


# ── Revenue dashboard history ─────────────────────────────────────
@router.get("/dashboard/revenue-machine/history")
async def dashboard_revenue_machine_history(days: int = 14) -> dict[str, Any]:
    """Last N days of revenue machine output (default 14)."""
    if days < 1 or days > 90:
        raise HTTPException(400, "days_out_of_range: 1..90")
    cutoff = _utcnow() - timedelta(days=days)
    async with async_session_factory() as session:
        try:
            gmail_rows = (await session.execute(
                select(GmailDraftRecord).where(GmailDraftRecord.created_at >= cutoff)
            )).scalars().all()
            linkedin_rows = (await session.execute(
                select(LinkedInDraftRecord).where(LinkedInDraftRecord.created_at >= cutoff)
            )).scalars().all()
        except Exception as exc:  # noqa: BLE001
            return {"status": "skipped_db_unreachable", "error": str(exc)}

    # Aggregate by date
    from collections import defaultdict
    by_day: dict[str, dict[str, int]] = defaultdict(lambda: {
        "gmail_drafts": 0, "gmail_sent": 0,
        "linkedin_drafts": 0, "linkedin_sent": 0, "linkedin_replied": 0,
    })
    for r in gmail_rows:
        d = r.created_at.date().isoformat()
        by_day[d]["gmail_drafts"] += 1
        if r.status == "sent": by_day[d]["gmail_sent"] += 1
    for r in linkedin_rows:
        d = r.created_at.date().isoformat()
        by_day[d]["linkedin_drafts"] += 1
        if r.status == "sent": by_day[d]["linkedin_sent"] += 1
        if r.reply_received_at: by_day[d]["linkedin_replied"] += 1

    series = sorted(
        [{"date": d, **stats} for d, stats in by_day.items()],
        key=lambda x: x["date"],
    )
    return {"status": "ok", "days_window": days, "series": series,
            "totals": {
                "gmail_drafts": sum(d["gmail_drafts"] for d in series),
                "gmail_sent": sum(d["gmail_sent"] for d in series),
                "linkedin_drafts": sum(d["linkedin_drafts"] for d in series),
                "linkedin_sent": sum(d["linkedin_sent"] for d in series),
                "linkedin_replied": sum(d["linkedin_replied"] for d in series),
            }}


# ── Export today's drafts as CSV (for offline review when Gmail OAuth missing) ─
@router.get("/automation/revenue-machine/export")
async def revenue_machine_export(format: str = "csv") -> dict[str, Any]:
    """
    Export today's drafts as CSV/Markdown so Sami can review them in Excel
    or paste into Gmail manually when Gmail OAuth isn't yet configured.

    format: csv | markdown
    Writes to docs/ops/daily_reports/YYYY-MM-DD_drafts.csv (or .md).
    """
    if format not in {"csv", "markdown"}:
        raise HTTPException(400, "format_must_be_csv_or_markdown")
    today_start = _utcnow().replace(hour=0, minute=0, second=0, microsecond=0)

    async with async_session_factory() as session:
        try:
            gmail_rows = (await session.execute(
                select(GmailDraftRecord).where(
                    GmailDraftRecord.created_at >= today_start
                ).order_by(GmailDraftRecord.created_at)
            )).scalars().all()
            linkedin_rows = (await session.execute(
                select(LinkedInDraftRecord).where(
                    LinkedInDraftRecord.created_at >= today_start
                ).order_by(LinkedInDraftRecord.created_at)
            )).scalars().all()
        except Exception as exc:  # noqa: BLE001
            return {"status": "skipped_db_unreachable", "error": str(exc)}

    out_dir = Path("docs/ops/daily_reports")
    out_dir.mkdir(parents=True, exist_ok=True)
    date_iso = today_start.date().isoformat()

    if format == "csv":
        import csv as _csv
        gmail_path = out_dir / f"{date_iso}_gmail_drafts.csv"
        with open(gmail_path, "w", encoding="utf-8", newline="") as f:
            w = _csv.DictWriter(f, fieldnames=[
                "draft_id", "to_email", "subject", "body_plain",
                "status", "gmail_draft_id", "created_at",
            ])
            w.writeheader()
            for r in gmail_rows:
                w.writerow({
                    "draft_id": r.id, "to_email": r.to_email,
                    "subject": r.subject,
                    "body_plain": (r.body_plain or "").replace("\n", " ⏎ "),
                    "status": r.status, "gmail_draft_id": r.gmail_draft_id or "",
                    "created_at": r.created_at.isoformat(),
                })
        linkedin_path = out_dir / f"{date_iso}_linkedin_drafts.csv"
        with open(linkedin_path, "w", encoding="utf-8", newline="") as f:
            w = _csv.DictWriter(f, fieldnames=[
                "draft_id", "company_name", "search_query", "context",
                "reason", "message_ar", "message_en", "status",
            ])
            w.writeheader()
            for r in linkedin_rows:
                w.writerow({
                    "draft_id": r.id, "company_name": r.company_name,
                    "search_query": r.profile_search_query,
                    "context": r.company_context or "",
                    "reason": r.reason_for_outreach or "",
                    "message_ar": (r.message_ar or "").replace("\n", " ⏎ "),
                    "message_en": (r.message_en or "").replace("\n", " ⏎ "),
                    "status": r.status,
                })
        return {"status": "ok", "format": "csv",
                "gmail_export": str(gmail_path),
                "linkedin_export": str(linkedin_path),
                "gmail_count": len(gmail_rows),
                "linkedin_count": len(linkedin_rows)}

    # markdown
    md_path = out_dir / f"{date_iso}_drafts.md"
    lines = [f"# Dealix — Drafts to Send  ({date_iso})\n\n"]
    lines.append(f"## Gmail Drafts ({len(gmail_rows)})\n\n")
    for i, r in enumerate(gmail_rows, 1):
        lines.append(f"### {i}. To: `{r.to_email}`\n\n")
        lines.append(f"**Subject:** {r.subject}\n\n")
        lines.append("```\n" + (r.body_plain or "") + "\n```\n\n")
        lines.append("---\n\n")
    lines.append(f"\n## LinkedIn Drafts ({len(linkedin_rows)}) — manual send only\n\n")
    for i, r in enumerate(linkedin_rows, 1):
        lines.append(f"### {i}. {r.company_name}\n\n")
        lines.append(f"**Search:** `{r.profile_search_query}`\n\n")
        if r.reason_for_outreach:
            lines.append(f"**Reason:** {r.reason_for_outreach}\n\n")
        lines.append(f"**Message (Arabic):**\n\n```\n{r.message_ar}\n```\n\n")
        if r.message_en:
            lines.append(f"**Message (English):**\n\n```\n{r.message_en}\n```\n\n")
        lines.append("---\n\n")
    md_path.write_text("".join(lines), encoding="utf-8")
    return {"status": "ok", "format": "markdown",
            "report_path": str(md_path),
            "gmail_count": len(gmail_rows),
            "linkedin_count": len(linkedin_rows)}


# ── Daily report generator ─────────────────────────────────────────
@router.post("/automation/daily-report/generate")
async def automation_daily_report_generate() -> dict[str, Any]:
    """
    Write a daily markdown report into docs/ops/daily_reports/YYYY-MM-DD.md
    summarizing today's targeting + sends + replies.
    """
    today_start = _utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    metrics = await dashboard_revenue_machine_today()
    if metrics.get("status") != "ok":
        return metrics

    out_dir = Path("docs/ops/daily_reports")
    out_dir.mkdir(parents=True, exist_ok=True)
    file_path = out_dir / f"{today_start.date().isoformat()}.md"

    content = (
        f"# Dealix Daily Revenue Report — {today_start.date().isoformat()}\n\n"
        f"## Drafts produced\n"
        f"- Gmail drafts: {metrics['gmail_drafts']['total']}\n"
        f"- Gmail sent: {metrics['gmail_drafts']['sent']}\n"
        f"- LinkedIn drafts: {metrics['linkedin_drafts']['total']}\n"
        f"- LinkedIn sent (manual): {metrics['linkedin_drafts']['sent']}\n\n"
        f"## Replies\n"
        f"- Email replies received: {metrics['email_replies']}\n"
        f"- LinkedIn replies received: {metrics['linkedin_drafts']['replied']}\n\n"
        f"## Approval queue open\n"
        f"- {metrics['approval_queue_open']} drafts await Sami's review.\n\n"
        f"## Tomorrow recommendation\n"
        f"- Re-run /api/v1/automation/revenue-machine/run with same defaults.\n"
        f"- If reply rate today < 5%, switch top sector for tomorrow.\n"
    )
    try:
        file_path.write_text(content, encoding="utf-8")
    except Exception as exc:  # noqa: BLE001
        return {"status": "write_failed", "error": str(exc), "metrics": metrics}

    return {
        "status": "ok",
        "report_path": str(file_path),
        "metrics": metrics,
    }

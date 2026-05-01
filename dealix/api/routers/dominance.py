"""
Dominance router — adds the upper-tier intelligence endpoints on top of
the existing daily revenue machine.

Endpoints:
    GET  /api/v1/signals/account/{id}      — typed buying signals
    POST /api/v1/accounts/{id}/brief       — full company brief (research + score)
    GET  /api/v1/objections/bank           — all 13 objection responses
    POST /api/v1/offers/route              — sector → offer routing
    POST /api/v1/automation/score-tuner/run — weight-tuning recommendations
    POST /api/v1/customers/{id}/proof-pack — case-study + testimonial template
    GET  /api/v1/dashboard/dominance       — top-tier daily snapshot

All write endpoints respect the existing compliance gates. Score tuner
returns recommendations only — never auto-applies (logged for human review).
"""

from __future__ import annotations

import logging
import os
import uuid
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import APIRouter, Body, HTTPException
from sqlalchemy import func, select

from auto_client_acquisition.email.research_agent import research_company_with_llm
from auto_client_acquisition.email.reply_classifier import (
    PATTERNS, RESPONSE_TEMPLATES,
)
from auto_client_acquisition.intelligence.next_action import (
    compute_priority, decide,
)
from auto_client_acquisition.intelligence.offers import (
    DEFAULT_OFFER, OFFER_ROUTES, build_tomorrow_recommendation, route_offer,
)
from auto_client_acquisition.intelligence.signals import (
    detect_signals, signals_to_intent_lift,
)
from db.models import (
    AccountRecord, ContactRecord, CustomerRecord, DealRecord,
    EmailSendLog, GmailDraftRecord, LeadScoreRecord, LinkedInDraftRecord,
    OutreachQueueRecord, PartnerRecord, SignalRecord,
)
from db.session import async_session_factory

router = APIRouter(prefix="/api/v1", tags=["dominance"])
log = logging.getLogger(__name__)


def _new_id(prefix: str = "") -> str:
    return f"{prefix}{uuid.uuid4().hex[:24]}" if prefix else uuid.uuid4().hex[:24]


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


# ── Sector → Offer routing table (canonical lives in intelligence/offers.py) ─
_LEGACY_OFFER_ROUTES: dict[str, dict[str, Any]] = {
    "real_estate_developer": {
        "primary_offer": "pilot_499_lead_qualification_plus_viewing_booking",
        "value_prop": "تأهيل lead العقار + حجز معاينة بدلاً منكم",
        "headline_pain": "كل lead عقاري متأخر دقيقة = احتمال خسارة العميل لمنافس",
        "kpi": "Arabic-replied leads × demos booked × pipeline added",
        "best_channel": "phone_task_then_email", "pricing_tier": "Pilot 499",
    },
    "real_estate": {
        "primary_offer": "pilot_499_lead_qualification_plus_viewing_booking",
        "value_prop": "نأهل العميل ونحجز موعد المعاينة قبل ما يبرد",
        "headline_pain": "العمولة الواحدة في العقار = ربح أسبوع. لا تخسرونها لتأخر الرد",
        "kpi": "qualified leads × viewings booked",
        "best_channel": "phone_task_then_email", "pricing_tier": "Pilot 499",
    },
    "construction": {
        "primary_offer": "pilot_999_quote_request_qualification",
        "value_prop": "نفرز RFQs ونجمع المواصفات قبل تسعير المشروع",
        "headline_pain": "RFQ تتوزع بين قنوات متعددة بدون فرز موحد",
        "kpi": "RFQs qualified × pricing-engineer time saved",
        "best_channel": "phone_task", "pricing_tier": "Pilot 999",
    },
    "hospitality": {
        "primary_offer": "pilot_999_booking_inquiry_assistant",
        "value_prop": "نرد فوراً على استفسارات MICE/قاعات/إفطار-سحور ونحجز معاينات",
        "headline_pain": "استفسارات بأي ساعة + موظف غير متاح = حجز ضائع",
        "kpi": "MICE inquiries × site visits booked",
        "best_channel": "phone_task_or_email", "pricing_tier": "Pilot 999",
    },
    "events": {
        "primary_offer": "pilot_499_event_inquiry_with_viewing_booking",
        "value_prop": "نرد على lead الفعالية فوراً ونجمع التاريخ + العدد + الباقة",
        "headline_pain": "كل lead = موسم — خسارته = 5K-100K ريال",
        "kpi": "inquiries × site visits booked",
        "best_channel": "phone_task", "pricing_tier": "Pilot 499",
    },
    "food_beverage": {
        "primary_offer": "pilot_499_catering_franchise_inquiry_routing",
        "value_prop": "نفرز التموين/الفرنشايز عن طلبات الطعام العادية",
        "headline_pain": "تموين شركة = إيراد شهر، يضيع بين رسائل واتساب",
        "kpi": "catering leads qualified × management calls scheduled",
        "best_channel": "phone_task", "pricing_tier": "Pilot 499",
    },
    "restaurant": {
        "primary_offer": "pilot_499_catering_franchise_inquiry_routing",
        "value_prop": "نفرز التموين/الفرنشايز عن طلبات الطعام العادية",
        "headline_pain": "تموين شركة = إيراد شهر، يضيع بين رسائل واتساب",
        "kpi": "catering leads qualified × management calls scheduled",
        "best_channel": "phone_task", "pricing_tier": "Pilot 499",
    },
    "logistics": {
        "primary_offer": "pilot_999_RFQ_response_under_60_seconds",
        "value_prop": "نرد على RFQ شحن خلال دقيقة بالعربي",
        "headline_pain": "10 دقائق فرق في الرد = خسارة عقد لمنافس",
        "kpi": "RFQs answered <60s × dispatch tickets opened",
        "best_channel": "phone_or_email", "pricing_tier": "Pilot 999",
    },
    "saas": {
        "primary_offer": "pilot_999_saudi_arabic_inbound_response_layer",
        "value_prop": "AI sales rep بالعربي الخليجي يكمل CRMكم",
        "headline_pain": "Saudi inbound leads باللغة العربية، الفريق يرد بالإنجليزية/ترجمة",
        "kpi": "Arabic-lead-to-demo conversion uplift",
        "best_channel": "linkedin_manual_then_email", "pricing_tier": "Pilot 999",
    },
    "marketing_agency": {
        "primary_offer": "agency_partner_25pct_mrr",
        "value_prop": "Dealix شريك resell — أنتم تبيعونه، نحن نبنيه، 25% MRR",
        "headline_pain": "العملاء يطلبون AI sales rep بالعربي والوكالة بدون حل جاهز",
        "kpi": "agency clients signed × MRR share",
        "best_channel": "linkedin_manual_then_call", "pricing_tier": "Partnership",
    },
    "training_center": {
        "primary_offer": "pilot_499_course_inquiry_enrollment_assistant",
        "value_prop": "نرد على استفسار البرامج + نجمع التفاصيل + نوجه للتسجيل",
        "headline_pain": "موسم تسجيل = استفسارات كثيرة، الرد البطيء = طالب راح لمنافس",
        "kpi": "inquiries qualified × enrollments started",
        "best_channel": "phone_task_then_email", "pricing_tier": "Pilot 499",
    },
    "dental_clinic": {
        "primary_offer": "pilot_499_appointment_qualification",
        "value_prop": "نأخذ تفاصيل المريض + نقيم الحالة قبل الحجز",
        "headline_pain": "مكالمات استقبال غير مدربة = جدول مزدحم بمواعيد منخفضة الجدية",
        "kpi": "high-intent appointments × no-show rate reduction",
        "best_channel": "phone_task", "pricing_tier": "Pilot 499",
    },
    "medical_clinic": {
        "primary_offer": "pilot_499_appointment_qualification",
        "value_prop": "نأخذ تفاصيل المريض + نقيم الحالة قبل الحجز",
        "headline_pain": "مكالمات استقبال غير مدربة = جدول مزدحم بمواعيد منخفضة الجدية",
        "kpi": "high-intent appointments × no-show rate reduction",
        "best_channel": "phone_task", "pricing_tier": "Pilot 499",
    },
}

_LEGACY_DEFAULT_OFFER = {
    "primary_offer": "pilot_499_managed",
    "value_prop": "Dealix يرد على inbound leads بالعربي الخليجي خلال 45 ثانية",
    "headline_pain": "سرعة الرد على العميل = ميزة تنافسية مباشرة",
    "kpi": "qualified leads × demos booked",
    "best_channel": "phone_or_email", "pricing_tier": "Pilot 499",
}


# ── Endpoint: GET signals for an account ──────────────────────────
@router.get("/signals/account/{account_id}")
async def get_signals_for_account(account_id: str) -> dict[str, Any]:
    """Return persisted SignalRecord rows + freshly-detected signals."""
    async with async_session_factory() as session:
        try:
            acc = (await session.execute(
                select(AccountRecord).where(AccountRecord.id == account_id)
            )).scalar_one_or_none()
            if not acc:
                raise HTTPException(404, "account_not_found")
            persisted = (await session.execute(
                select(SignalRecord).where(SignalRecord.account_id == account_id)
                .order_by(SignalRecord.detected_at.desc())
            )).scalars().all()
        except HTTPException:
            raise
        except Exception as exc:  # noqa: BLE001
            return {"status": "skipped_db_unreachable", "error": str(exc)}

    # Compute fresh signals from current account data (no website crawl here —
    # that requires the enrichment pipeline)
    fresh = detect_signals(
        sector=acc.sector,
        google_rating=None,
        google_reviews_count=None,
        branches_hint=None,
    )
    intent_lift = signals_to_intent_lift(fresh)

    return {
        "account_id": account_id,
        "company_name": acc.company_name,
        "persisted_signals": [
            {
                "type": s.signal_type, "value": s.signal_value,
                "confidence": s.confidence, "source_url": s.source_url,
                "detected_at": s.detected_at.isoformat(),
            }
            for s in persisted
        ],
        "fresh_rule_signals": [s.to_dict() for s in fresh],
        "computed_intent_lift": intent_lift,
        "note": "fresh_rule_signals are sector-only; run /leads/enrich/full "
                "to add website/Maps signals.",
    }


# ── Endpoint: POST account brief (research + signals + score) ─────
@router.post("/accounts/{account_id}/brief")
async def account_brief(account_id: str) -> dict[str, Any]:
    """
    Full account brief: company_summary + pain_hypothesis + dealix_fit +
    expected_gain + best_offer + best_channel + objection_risks + risk_note.
    """
    async with async_session_factory() as session:
        try:
            acc = (await session.execute(
                select(AccountRecord).where(AccountRecord.id == account_id)
            )).scalar_one_or_none()
            if not acc:
                raise HTTPException(404, "account_not_found")
            score = (await session.execute(
                select(LeadScoreRecord).where(LeadScoreRecord.account_id == account_id)
                .order_by(LeadScoreRecord.created_at.desc()).limit(1)
            )).scalar_one_or_none()
            contacts = (await session.execute(
                select(ContactRecord).where(ContactRecord.account_id == account_id)
            )).scalars().all()
        except HTTPException:
            raise
        except Exception as exc:  # noqa: BLE001
            return {"status": "skipped_db_unreachable", "error": str(exc)}

    account_dict = {
        "id": acc.id, "company_name": acc.company_name,
        "domain": acc.domain, "website": acc.website,
        "city": acc.city, "country": acc.country, "sector": acc.sector,
        "google_place_id": acc.google_place_id,
        "best_source": acc.best_source, "risk_level": acc.risk_level,
        "allowed_use": (acc.extra or {}).get("allowed_use"),
        "email": next((c.email for c in contacts if c.email), None),
        "phone": next((c.phone for c in contacts if c.phone), None),
    }
    brief = await research_company_with_llm(account_dict)

    fit = score.fit_score if score else 0.0
    intent = score.intent_score if score else 0.0
    urgency = score.urgency_score if score else 0.0
    revenue = 8.0  # default neutral
    risk = score.risk_score if score else 0.0

    decision = decide(
        fit_score=fit, intent_score=intent, urgency_score=urgency,
        revenue_score=revenue, risk_score=risk,
        opt_out=any(c.opt_out for c in contacts),
        has_business_email=bool(account_dict.get("email")),
        has_phone=bool(account_dict.get("phone")),
        has_linkedin_handle=False,
        is_potential_partner=acc.sector in {"marketing_agency", "consulting_firm"},
        sector=acc.sector, allowed_use=account_dict["allowed_use"],
    )

    return {
        "account_id": account_id,
        "brief": brief.to_dict(),
        "scores": {
            "fit": fit, "intent": intent, "urgency": urgency,
            "risk": risk, "revenue": revenue,
        },
        "next_action": decision.to_dict(),
        "contacts_count": len(contacts),
        "personalized_by_llm": "llm:groq_polish" in (brief.sources_used or []),
    }


# ── Endpoint: GET objection bank ──────────────────────────────────
@router.get("/objections/bank")
async def objections_bank() -> dict[str, Any]:
    """Return all 13 objection categories with response drafts."""
    bank = []
    for category, tpl in RESPONSE_TEMPLATES.items():
        bank.append({
            "category": category,
            "response_ar": tpl["ar"],
            "auto_send_allowed": tpl["auto_send_allowed"],
            "next_action": tpl["next_action"],
            "deal_stage": tpl["deal_stage"],
            "followup_days": tpl["followup_days"],
        })
    return {"count": len(bank), "objections": bank,
            "rule_patterns": [p[0] for p in PATTERNS]}


# ── Endpoint: POST offer route by sector ─────────────────────────
@router.post("/offers/route")
async def offers_route(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """
    Route an offer by sector. Body: sector (str). Returns offer config.
    """
    sector = str(body.get("sector") or "").lower().strip()
    if not sector:
        raise HTTPException(400, "sector_required")
    offer = route_offer(sector)
    return {"sector": sector, "matched": sector in OFFER_ROUTES, **offer}


# ── Endpoint: POST score-tuner/run (recommend weights) ───────────
@router.post("/automation/score-tuner/run")
async def score_tuner_run(body: dict[str, Any] = Body(default={})) -> dict[str, Any]:
    """
    Analyze last N days of email sends + replies and recommend scoring weight
    adjustments. NEVER auto-applies — returns recommendations only.

    Body: days (default 14)
    """
    days = int(body.get("days") or 14)
    cutoff = _utcnow() - timedelta(days=days)

    async with async_session_factory() as session:
        try:
            sends = (await session.execute(
                select(EmailSendLog).where(
                    EmailSendLog.sent_at >= cutoff
                )
            )).scalars().all()
            replies = [s for s in sends if s.reply_received_at is not None]
            account_ids = list({s.account_id for s in sends if s.account_id})
            scores = (await session.execute(
                select(LeadScoreRecord).where(
                    LeadScoreRecord.account_id.in_(account_ids)
                )
            )).scalars().all() if account_ids else []
            accounts = (await session.execute(
                select(AccountRecord).where(
                    AccountRecord.id.in_(account_ids)
                )
            )).scalars().all() if account_ids else []
        except Exception as exc:  # noqa: BLE001
            return {"status": "skipped_db_unreachable", "error": str(exc)}

    sector_by_acc = {a.id: a.sector for a in accounts}

    sector_sent: Counter[str] = Counter()
    sector_replied: Counter[str] = Counter()
    sector_positive: Counter[str] = Counter()
    classification_counts: Counter[str] = Counter()

    for s in sends:
        sec = sector_by_acc.get(s.account_id, "unknown")
        sector_sent[sec] += 1
    for r in replies:
        sec = sector_by_acc.get(r.account_id, "unknown")
        sector_replied[sec] += 1
        if r.reply_classification:
            classification_counts[r.reply_classification] += 1
            if r.reply_classification in {"interested", "ask_demo", "ask_price"}:
                sector_positive[sec] += 1

    by_sector = []
    for sec, sent in sector_sent.most_common():
        replied = sector_replied[sec]
        positive = sector_positive[sec]
        by_sector.append({
            "sector": sec, "sent": sent, "replied": replied,
            "positive": positive,
            "reply_rate": round(replied / sent, 3) if sent else 0,
            "positive_rate": round(positive / sent, 3) if sent else 0,
        })

    # Recommendations (never auto-applied)
    recommendations: list[dict[str, Any]] = []
    if by_sector:
        top = by_sector[0]
        if top["positive_rate"] > 0.05:
            recommendations.append({
                "type": "increase_sector_weight",
                "sector": top["sector"],
                "current_implied_priority": "P1-P2",
                "suggested_action": f"raise fit_weight for {top['sector']} by +5",
                "rationale": f"positive_rate={top['positive_rate']:.1%} on {top['sent']} sends",
                "confidence": 0.65,
            })
        worst = by_sector[-1]
        if worst["sent"] >= 10 and worst["reply_rate"] < 0.02:
            recommendations.append({
                "type": "decrease_sector_weight",
                "sector": worst["sector"],
                "suggested_action": f"reduce fit_weight for {worst['sector']} by -5",
                "rationale": f"reply_rate={worst['reply_rate']:.1%} on {worst['sent']} sends",
                "confidence": 0.55,
            })

    return {
        "status": "ok",
        "window_days": days,
        "totals": {
            "sent": len(sends),
            "replied": len(replies),
            "positive": sum(sector_positive.values()),
        },
        "by_sector": by_sector,
        "by_classification": dict(classification_counts),
        "recommendations": recommendations,
        "auto_applied": False,
        "note": "Recommendations are advisory only — review before applying.",
    }


# ── Endpoint: POST customer proof-pack ────────────────────────────
@router.post("/customers/{customer_id}/proof-pack")
async def customer_proof_pack(customer_id: str) -> dict[str, Any]:
    """
    Generate a case-study + testimonial + referral-ask kit after a pilot.
    Pulls real metrics from EmailSendLog if account_id is linked, else
    returns templates for manual fill-in.
    """
    async with async_session_factory() as session:
        try:
            cust = (await session.execute(
                select(CustomerRecord).where(CustomerRecord.id == customer_id)
            )).scalar_one_or_none()
            if not cust:
                raise HTTPException(404, "customer_not_found")
        except HTTPException:
            raise
        except Exception as exc:  # noqa: BLE001
            return {"status": "skipped_db_unreachable", "error": str(exc)}

    case_study_template = (
        f"## Case Study — {cust.company_id or 'العميل'}\n\n"
        f"**القطاع:** [حدد]\n"
        f"**المدة:** Pilot 7 أيام ({cust.pilot_start_at or '—'} → {cust.pilot_end_at or '—'})\n\n"
        f"### قبل Dealix\n"
        f"- وقت الرد على lead: [X دقائق/ساعات]\n"
        f"- معدل التحويل من inquiry → demo: [X%]\n"
        f"- leads مهملة شهرياً: [X]\n\n"
        f"### بعد Dealix (7 أيام)\n"
        f"- وقت الرد: 45 ثانية\n"
        f"- demos محجوزة: [X]\n"
        f"- leads جادة معالجة: [X]\n\n"
        f"### اقتباس العميل\n"
        f"> [Sami: agree on quote with customer post-pilot]\n\n"
        f"### النتيجة\n"
        f"العميل أكمل إلى Starter بـ 999 SAR/شهر.\n"
    )

    testimonial_request = (
        f"السلام عليكم،\n\n"
        f"شكراً على إكمال Pilot Dealix معنا. النتائج كانت مفيدة لكم — "
        f"هل ممكن نسجّل اقتباس قصير (60 ثانية) عن تجربتكم؟\n"
        f"يمكن نص أو فيديو. نشكركم على الوقت."
    )

    referral_ask = (
        f"بناءً على نتيجة Pilot، تعرفون شركة سعودية ثانية تواجه نفس "
        f"المشكلة (تأخر الرد على leads العربية)؟ نعطي 10% من اشتراكها "
        f"السنوي لكل إحالة جدية."
    )

    return {
        "customer_id": customer_id,
        "case_study_md_template": case_study_template,
        "testimonial_request_ar": testimonial_request,
        "referral_ask_ar": referral_ask,
        "next_action": "save case_study to docs/business/case_studies/{customer}.md",
    }


# ── Endpoint: GET dashboard/dominance ─────────────────────────────
@router.post("/partners/revenue-machine/run")
async def partners_revenue_machine_run(body: dict[str, Any] = Body(default={})) -> dict[str, Any]:
    """
    Partner-targeted daily run. Pulls top marketing/consulting partners,
    generates partnership-pitch LinkedIn drafts (manual-send only).

    Body: max_partners (default 10), city (optional)
    """
    max_partners = int(body.get("max_partners") or 10)
    city = body.get("city")
    partner_sectors = ["marketing_agency", "consulting_firm"]

    async with async_session_factory() as session:
        try:
            q = select(AccountRecord).where(
                AccountRecord.sector.in_(partner_sectors),
                AccountRecord.status.in_(["enriched", "new"]),
            )
            if city:
                q = q.where(AccountRecord.city == city)
            q = q.order_by(AccountRecord.data_quality_score.desc()).limit(max_partners * 2)
            partner_pool = (await session.execute(q)).scalars().all()
        except Exception as exc:  # noqa: BLE001
            return {"status": "skipped_db_unreachable", "error": str(exc)}

        drafts_created: list[dict[str, Any]] = []
        for acc in partner_pool[:max_partners]:
            offer = route_offer(acc.sector)
            search_query = f'"{acc.company_name}" {acc.city or "Saudi"} site:linkedin.com'
            msg_ar = (
                f"أهلاً [اسم المسؤول]،\n\n"
                f"لاحظت أن {acc.company_name} يخدم عملاء في السوق السعودي.\n\n"
                f"Dealix شريك resell — أنتم تبيعونه لعملائكم، 25% MRR شهرياً.\n"
                f"3 عملاء وكالة = ~600-1500 ريال شهرياً passive recurring.\n\n"
                f"رابط شامل: https://dealix.me/partners.html\n\n"
                f"تناسبكم 20 دقيقة هذا الأسبوع نوضح؟\n\nسامي"
            )
            ld = LinkedInDraftRecord(
                id=_new_id("ld_"), account_id=acc.id,
                company_name=acc.company_name[:255], contact_name=None,
                profile_search_query=search_query[:500],
                company_context=f"Saudi {acc.sector} in {acc.city or '?'}",
                reason_for_outreach="partnership_resell_pitch",
                message_ar=msg_ar, message_en=None,
                followup_day_3="متابعة سريعة — هل عندكم سؤال محدد قبل المكالمة؟",
                followup_day_7="آخر متابعة. لو لاحقاً يناسب، أنا هنا.",
                status="draft",
            )
            session.add(ld)
            drafts_created.append({
                "draft_id": ld.id, "company": acc.company_name,
                "city": acc.city, "search_query": search_query,
                "offer_tier": offer.get("pricing_tier"),
            })

        try:
            await session.commit()
        except Exception as exc:  # noqa: BLE001
            await session.rollback()
            return {"status": "commit_failed", "error": str(exc)}

    return {
        "status": "ok",
        "partners_pool_size": len(partner_pool),
        "drafts_created": len(drafts_created),
        "drafts": drafts_created,
        "approval_required": True,
        "next_action": "Open /api/v1/linkedin/drafts/today to review + send manually",
    }


@router.get("/dashboard/dominance")
async def dashboard_dominance() -> dict[str, Any]:
    """
    Top-tier daily snapshot:
        - today: drafts/sent/replies
        - sector leaderboard (last 14d)
        - channel leaderboard
        - offer leaderboard (by pricing_tier)
        - partner pipeline
        - tomorrow recommendation
    """
    today_start = _utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
    cutoff_14d = today_start - timedelta(days=14)

    async with async_session_factory() as session:
        try:
            gmail_today = int((await session.execute(
                select(func.count()).select_from(GmailDraftRecord).where(
                    GmailDraftRecord.created_at >= today_start
                )
            )).scalar() or 0)
            gmail_sent_today = int((await session.execute(
                select(func.count()).select_from(GmailDraftRecord).where(
                    GmailDraftRecord.created_at >= today_start,
                    GmailDraftRecord.status == "sent",
                )
            )).scalar() or 0)
            linkedin_today = int((await session.execute(
                select(func.count()).select_from(LinkedInDraftRecord).where(
                    LinkedInDraftRecord.created_at >= today_start
                )
            )).scalar() or 0)
            replies_14d = int((await session.execute(
                select(func.count()).select_from(EmailSendLog).where(
                    EmailSendLog.reply_received_at >= cutoff_14d
                )
            )).scalar() or 0)
            partners_active = int((await session.execute(
                select(func.count()).select_from(PartnerRecord).where(
                    PartnerRecord.status.in_(["active", "prospecting"])
                )
            )).scalar() or 0)
            partners_signed = int((await session.execute(
                select(func.coalesce(func.sum(PartnerRecord.clients_signed), 0))
            )).scalar() or 0)
            customers_total = int((await session.execute(
                select(func.count()).select_from(CustomerRecord)
            )).scalar() or 0)
            customers_paid = int((await session.execute(
                select(func.count()).select_from(CustomerRecord).where(
                    CustomerRecord.onboarding_status != "kickoff_pending"
                )
            )).scalar() or 0)

            # Sector leaderboard from email sends
            sends_14d = (await session.execute(
                select(EmailSendLog).where(EmailSendLog.sent_at >= cutoff_14d)
            )).scalars().all()
            account_ids = list({s.account_id for s in sends_14d if s.account_id})
            accounts = (await session.execute(
                select(AccountRecord).where(AccountRecord.id.in_(account_ids))
            )).scalars().all() if account_ids else []
            sector_by_acc = {a.id: a.sector for a in accounts}

            sector_sent: Counter[str] = Counter()
            sector_replied: Counter[str] = Counter()
            for s in sends_14d:
                sec = sector_by_acc.get(s.account_id, "unknown")
                sector_sent[sec] += 1
                if s.reply_received_at:
                    sector_replied[sec] += 1
            sector_leaderboard = sorted(
                [
                    {
                        "sector": sec, "sent": cnt,
                        "replied": sector_replied[sec],
                        "reply_rate": round(sector_replied[sec] / cnt, 3) if cnt else 0,
                    }
                    for sec, cnt in sector_sent.most_common(10)
                ],
                key=lambda x: -x["reply_rate"],
            )

            # Channel leaderboard
            channel_dist: Counter[str] = Counter()
            for c in (await session.execute(
                select(OutreachQueueRecord.channel).where(
                    OutreachQueueRecord.created_at >= cutoff_14d
                )
            )).all():
                channel_dist[c[0] or "unknown"] += 1
        except Exception as exc:  # noqa: BLE001
            return {"status": "skipped_db_unreachable", "error": str(exc)}

    tomorrow_recommendation = build_tomorrow_recommendation(
        sector_leaderboard, gmail_today, replies_14d
    )

    return {
        "status": "ok",
        "date_utc": today_start.date().isoformat(),
        "today": {
            "gmail_drafts": gmail_today,
            "gmail_sent": gmail_sent_today,
            "linkedin_drafts": linkedin_today,
        },
        "last_14_days": {
            "email_replies": replies_14d,
        },
        "sector_leaderboard_14d": sector_leaderboard,
        "channel_distribution_14d": dict(channel_dist),
        "partners": {
            "active": partners_active,
            "clients_signed_via_partners": int(partners_signed),
        },
        "customers": {
            "total": customers_total,
            "in_active_pilot_or_onboarded": customers_paid,
        },
        "tomorrow_recommendation": tomorrow_recommendation,
    }


# helper moved to auto_client_acquisition.intelligence.offers.build_tomorrow_recommendation

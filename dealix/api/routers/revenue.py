"""
Revenue motion endpoints — fills gaps demanded by the operator playbook.

Endpoints:
    POST /api/v1/leads/score                 — alias for prospect score on a lead body
    POST /api/v1/negotiation/respond         — generate negotiation reply (rule-based + LLM)
    POST /api/v1/customers/daily-report      — log a daily delivery report for a customer
    POST /api/v1/partners/outreach           — log partner outreach attempt
    POST /api/v1/partners/deal               — log partner-sourced deal

All endpoints honor `_safe_commit` for graceful DB-unreachable handling and
respect approval_required=True for any outbound message generation.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Body, HTTPException
from sqlalchemy import select

from auto_client_acquisition.pipelines.scoring import (
    compute_data_quality,
    compute_lead_score,
)
from db.models import (
    CustomerRecord,
    PartnerRecord,
    TaskRecord,
)
from db.session import async_session_factory

router = APIRouter(prefix="/api/v1", tags=["revenue"])
log = logging.getLogger(__name__)


def _new_id(prefix: str = "") -> str:
    suffix = uuid.uuid4().hex[:24]
    return f"{prefix}{suffix}" if prefix else suffix


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


# ── Score alias on /leads namespace ───────────────────────────────
@router.post("/leads/score")
async def score_lead_body(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """
    Score a lead body without persisting. Mirror of prospect/score for /leads namespace.
    Body: any account-shaped dict — minimum: company_name + (domain | phone | email).
    """
    if not body.get("company_name"):
        raise HTTPException(400, "company_name_required")
    score = compute_lead_score(body, signals=body.get("signals") or [], technologies=body.get("technologies") or [])
    dq, dq_reasons = compute_data_quality(body)
    return {
        "company_name": body.get("company_name"),
        "score": {
            "fit": score.fit, "intent": score.intent, "urgency": score.urgency,
            "risk": score.risk, "total": score.total, "priority": score.priority,
            "recommended_channel": score.recommended_channel, "reason": score.reason,
        },
        "data_quality": {"score": dq, "reasons": dq_reasons},
    }


# ── Negotiation respond ───────────────────────────────────────────
NEGOTIATION_TEMPLATES_AR = {
    "price_objection": (
        "أفهم القلق على السعر — Pilot 7 أيام بـ 499 ريال هو أرخص طريقة "
        "تشوف نتيجة قبل أي التزام. لو ما اقتنعتم نرجع المبلغ كامل."
    ),
    "feature_missing": (
        "هذي ميزة في طريقها ضمن خطة Q3. الآن نقدر نعمل workaround يدوي خلال "
        "الـ pilot — تناسبكم نسلمه كذا ونضيف الميزة لاحقاً؟"
    ),
    "timing_objection": (
        "متفهم. الـ pilot 7 أيام فقط، نشغله بدون تدخل من فريقكم. "
        "تبدؤون متى يناسبكم — هذا الأسبوع أو الأسبوع القادم؟"
    ),
    "trust_objection": (
        "صحيح، Dealix شركة جديدة. عشان كذا الـ pilot 499 ريال + استرجاع كامل. "
        "أنتم تجربون قبل أي التزام. تناسبكم نبدأ الاثنين؟"
    ),
    "competitor_comparison": (
        "Dealix الوحيد بالعربي الخليجي + متوافق PDPL + Mada. "
        "البقية إما إنجليزية أو ترجمة آلية. تبون نقارن جانب-جانب على lead حقيقي؟"
    ),
    "decision_maker_unavailable": (
        "ممتاز. نرسل لكم one-pager + رابط Calendly تشاركونه مع المسؤول، "
        "ونرجع نتابع بعد 3 أيام. أرسلها لإيميلكم؟"
    ),
}


@router.post("/negotiation/respond")
async def negotiation_respond(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """
    Generate a negotiation response.
    Body:
        objection_type: one of price_objection / feature_missing / timing_objection /
                        trust_objection / competitor_comparison / decision_maker_unavailable
        company_name: optional, used to personalize
        custom_context: optional, free-text the rep wants Dealix to address
    """
    obj_type = str(body.get("objection_type") or "").strip()
    company = str(body.get("company_name") or "العميل").strip()
    custom = str(body.get("custom_context") or "").strip()

    if obj_type not in NEGOTIATION_TEMPLATES_AR:
        return {
            "status": "unknown_objection",
            "valid_types": list(NEGOTIATION_TEMPLATES_AR.keys()),
            "hint": "Pick one of the valid objection_type values, OR pass custom_context.",
        }

    base = NEGOTIATION_TEMPLATES_AR[obj_type]
    response = f"{company}، {base}"
    if custom:
        response += f"\n\nبخصوص ما ذكرتم: {custom[:300]}"
    return {
        "objection_type": obj_type,
        "response_ar": response,
        "approval_required": True,
        "send_status": "queued_for_human_approval",
        "channel_policy": "human_final_send_only_during_first_30_days",
    }


# ── Customer daily report ─────────────────────────────────────────
@router.post("/customers/daily-report")
async def customers_daily_report(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """
    Log a daily delivery report for a customer.
    Body: customer_id, date, leads_handled, demos_booked, response_time_avg_seconds,
          notes, customer_quote_optional
    """
    customer_id = str(body.get("customer_id") or "").strip()
    if not customer_id:
        raise HTTPException(400, "customer_id_required")
    leads_handled = int(body.get("leads_handled") or 0)
    demos_booked = int(body.get("demos_booked") or 0)
    response_avg = float(body.get("response_time_avg_seconds") or 0)
    notes = str(body.get("notes") or "")[:1000]

    # Persist as a TaskRecord with task_type=daily_report so it's auditable
    async with async_session_factory() as session:
        try:
            task = TaskRecord(
                id=_new_id("dr_"),
                lead_id=None,
                deal_id=None,
                task_type="daily_report",
                status="done",
                owner="auto",
                notes=(
                    f"customer_id={customer_id} | "
                    f"date={body.get('date') or _utcnow().date().isoformat()} | "
                    f"leads_handled={leads_handled} | demos_booked={demos_booked} | "
                    f"avg_response={response_avg}s\n{notes}"
                )[:5000],
                completed_at=_utcnow(),
            )
            session.add(task)
            try:
                await session.commit()
            except Exception as exc:  # noqa: BLE001
                await session.rollback()
                return {"status": "skipped_db_unreachable", "error": str(exc)}
        except Exception as exc:  # noqa: BLE001
            return {"status": "skipped_db_unreachable", "error": str(exc)}

    # Optional: bump customer record metric counters
    async with async_session_factory() as session:
        try:
            cust = (await session.execute(
                select(CustomerRecord).where(CustomerRecord.id == customer_id)
            )).scalar_one_or_none()
            if cust:
                cust.daily_report_sent = (cust.daily_report_sent or 0) + 1
                cust.updated_at = _utcnow()
                await session.commit()
        except Exception:
            pass

    return {
        "status": "logged",
        "customer_id": customer_id,
        "metrics": {
            "leads_handled": leads_handled,
            "demos_booked": demos_booked,
            "response_time_avg_seconds": response_avg,
        },
    }


# ── Partner outreach + deal ───────────────────────────────────────
@router.post("/partners/outreach")
async def partners_outreach(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """
    Log a partner-outreach attempt.
    Body: partner_id, channel, message_summary, next_action, next_action_at
    """
    partner_id = str(body.get("partner_id") or "").strip()
    if not partner_id:
        raise HTTPException(400, "partner_id_required")
    channel = str(body.get("channel") or "manual")[:32]
    message = str(body.get("message_summary") or "")[:1000]
    next_action = str(body.get("next_action") or "follow_up")[:64]

    async with async_session_factory() as session:
        try:
            partner = (await session.execute(
                select(PartnerRecord).where(PartnerRecord.id == partner_id)
            )).scalar_one_or_none()
            if not partner:
                return {"status": "partner_not_found", "id": partner_id}
            partner.next_action = next_action
            partner.notes = ((partner.notes or "") + f"\n[{_utcnow().isoformat()}] outreach via {channel}: {message[:300]}")[:5000]
            partner.updated_at = _utcnow()
            try:
                await session.commit()
            except Exception as exc:  # noqa: BLE001
                await session.rollback()
                return {"status": "commit_failed", "error": str(exc)}
        except Exception as exc:  # noqa: BLE001
            return {"status": "skipped_db_unreachable", "error": str(exc)}

    return {
        "status": "logged",
        "partner_id": partner_id,
        "channel": channel,
        "next_action": next_action,
        "approval_required": True,
        "send_status": "queued_for_human_approval",
    }


@router.post("/partners/deal")
async def partners_deal(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """
    Log a partner-sourced deal.
    Body: partner_id, customer_company, deal_value_sar, mrr_share_pct (optional)
    """
    partner_id = str(body.get("partner_id") or "").strip()
    customer = str(body.get("customer_company") or "").strip()
    deal_value = float(body.get("deal_value_sar") or 0)
    if not partner_id or not customer:
        raise HTTPException(400, "partner_id_and_customer_company_required")

    async with async_session_factory() as session:
        try:
            partner = (await session.execute(
                select(PartnerRecord).where(PartnerRecord.id == partner_id)
            )).scalar_one_or_none()
            if not partner:
                return {"status": "partner_not_found", "id": partner_id}

            # Increment partner's clients_signed counter
            partner.clients_signed = (partner.clients_signed or 0) + 1
            partner.updated_at = _utcnow()
            # Append context to partner notes (DealRecord requires lead FK; skip
            # creating a real Deal until customer has a corresponding LeadRecord)
            partner.notes = ((partner.notes or "") + (
                f"\n[{_utcnow().isoformat()}] partner_deal logged: "
                f"customer={customer} value_sar={deal_value} "
                f"mrr_share_pct={body.get('mrr_share_pct')}"
            ))[:5000]
            try:
                await session.commit()
            except Exception as exc:  # noqa: BLE001
                await session.rollback()
                return {"status": "commit_failed", "error": str(exc)}
        except Exception as exc:  # noqa: BLE001
            return {"status": "skipped_db_unreachable", "error": str(exc)}

    return {
        "status": "deal_logged",
        "partner_id": partner_id,
        "customer_company": customer,
        "deal_value_sar": deal_value,
        "partner_total_clients": partner.clients_signed,
        "note": "Deal record created in partner.notes audit trail; "
                "create a LeadRecord first if you need a full DealRecord row.",
    }

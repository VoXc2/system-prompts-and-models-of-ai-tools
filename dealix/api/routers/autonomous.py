"""
Autonomous Revenue Operator endpoints — conversations, deals, tasks, dashboard.

Production-safe additive endpoints. Does NOT modify existing /leads or /prospect routes.
"""

from __future__ import annotations

import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import APIRouter, Body, HTTPException
from sqlalchemy import select, func

from db.models import ConversationRecord, DealRecord, LeadRecord, TaskRecord
from db.session import async_session_factory

router = APIRouter(prefix="/api/v1", tags=["autonomous"])
log = logging.getLogger(__name__)


def _new_id(prefix: str = "rec") -> str:
    return f"{prefix}_{uuid.uuid4().hex[:16]}"


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


async def _safe_commit(session, obj_to_add=None) -> bool:
    """Try to add+commit; return True on success, False if DB unreachable."""
    try:
        if obj_to_add is not None:
            session.add(obj_to_add)
        await session.commit()
        return True
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning("db_unreachable_skip: %s", str(e)[:120])
        try:
            await session.rollback()
        except Exception:
            pass
        return False


# ── Conversations ───────────────────────────────────────────────

@router.post("/conversations")
async def create_conversation(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """
    Log an inbound message + outbound auto-response.
    Body: {lead_id?, channel, sender, inbound_message, outbound_response?,
           classification?, next_action?, escalation_required?, auto_sent?}
    """
    channel = str(body.get("channel") or "").strip().lower()
    inbound = str(body.get("inbound_message") or "").strip()
    if not channel or not inbound:
        raise HTTPException(status_code=400, detail="channel_and_inbound_required")

    rec_id = _new_id("conv")
    async with async_session_factory()() as session:
        rec = ConversationRecord(
            id=rec_id,
            lead_id=str(body.get("lead_id")) if body.get("lead_id") else None,
            channel=channel,
            sender=str(body.get("sender") or "") or None,
            inbound_message=inbound[:8000],
            outbound_response=str(body.get("outbound_response") or "")[:8000] or None,
            classification=str(body.get("classification") or "") or None,
            sentiment=str(body.get("sentiment") or "") or None,
            next_action=str(body.get("next_action") or "") or None,
            escalation_required=bool(body.get("escalation_required", False)),
            auto_sent=bool(body.get("auto_sent", False)),
        )
        ok = await _safe_commit(session, rec)

    return {"id": rec_id, "status": "logged" if ok else "skipped_db_unreachable", "created_at": _utcnow().isoformat()}


@router.get("/conversations")
async def list_conversations(
    lead_id: str | None = None,
    channel: str | None = None,
    limit: int = 20,
) -> dict[str, Any]:
    limit = max(1, min(100, limit))
    async with async_session_factory()() as session:
        stmt = select(ConversationRecord).order_by(ConversationRecord.created_at.desc()).limit(limit)
        if lead_id:
            stmt = stmt.where(ConversationRecord.lead_id == lead_id)
        if channel:
            stmt = stmt.where(ConversationRecord.channel == channel.lower())
        result = await session.execute(stmt)
        rows = result.scalars().all()
        return {
            "count": len(rows),
            "items": [
                {
                    "id": r.id,
                    "lead_id": r.lead_id,
                    "channel": r.channel,
                    "sender": r.sender,
                    "inbound_message": r.inbound_message[:300],
                    "outbound_response": (r.outbound_response or "")[:300],
                    "classification": r.classification,
                    "next_action": r.next_action,
                    "escalation_required": r.escalation_required,
                    "auto_sent": r.auto_sent,
                    "created_at": r.created_at.isoformat() if r.created_at else None,
                }
                for r in rows
            ],
        }


# ── Deals (POST + PATCH) ────────────────────────────────────────

@router.post("/deals")
async def create_deal(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """
    Create a deal record (e.g., when prospect verbally agrees + invoice issued).
    Body: {lead_id, stage?, amount?, currency?, hubspot_deal_id?}
    """
    lead_id = str(body.get("lead_id") or "").strip()
    if not lead_id:
        raise HTTPException(status_code=400, detail="lead_id_required")

    deal_id = _new_id("deal")
    async with async_session_factory()() as session:
        deal = DealRecord(
            id=deal_id,
            lead_id=lead_id,
            hubspot_deal_id=body.get("hubspot_deal_id") or None,
            hubspot_contact_id=body.get("hubspot_contact_id") or None,
            amount=float(body.get("amount") or 0.0),
            currency=str(body.get("currency") or "SAR"),
            stage=str(body.get("stage") or "new"),
        )
        ok = await _safe_commit(session, deal)
    return {"id": deal_id, "stage": "new", "status": "ok" if ok else "skipped_db_unreachable", "created_at": _utcnow().isoformat()}


@router.patch("/deals/{deal_id}")
async def update_deal(deal_id: str, body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """
    Update deal stage/amount/payment_status. Common path: payment_requested → paid.
    Body: any subset of {stage, amount, currency}
    """
    async with async_session_factory()() as session:
        result = await session.execute(select(DealRecord).where(DealRecord.id == deal_id))
        deal = result.scalar_one_or_none()
        if not deal:
            raise HTTPException(status_code=404, detail="deal_not_found")
        if "stage" in body:
            deal.stage = str(body["stage"])
        if "amount" in body:
            deal.amount = float(body["amount"])
        if "currency" in body:
            deal.currency = str(body["currency"])
        if "hubspot_deal_id" in body:
            deal.hubspot_deal_id = str(body["hubspot_deal_id"]) or None
        await session.commit()
    return {"id": deal_id, "stage": deal.stage, "updated_at": _utcnow().isoformat()}


@router.get("/deals")
async def list_deals(stage: str | None = None, limit: int = 20) -> dict[str, Any]:
    limit = max(1, min(100, limit))
    async with async_session_factory()() as session:
        stmt = select(DealRecord).order_by(DealRecord.created_at.desc()).limit(limit)
        if stage:
            stmt = stmt.where(DealRecord.stage == stage)
        result = await session.execute(stmt)
        rows = result.scalars().all()
        return {
            "count": len(rows),
            "items": [
                {
                    "id": r.id,
                    "lead_id": r.lead_id,
                    "stage": r.stage,
                    "amount": r.amount,
                    "currency": r.currency,
                    "created_at": r.created_at.isoformat() if r.created_at else None,
                }
                for r in rows
            ],
        }


# ── Tasks ───────────────────────────────────────────────────────

@router.post("/tasks")
async def create_task(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """
    Schedule a follow-up task.
    Body: {lead_id?, deal_id?, task_type, due_at?(iso), notes?, owner?}
    """
    task_type = str(body.get("task_type") or "follow_up").strip()
    if not task_type:
        raise HTTPException(status_code=400, detail="task_type_required")

    due_at = _utcnow() + timedelta(days=2)  # default +2d
    if body.get("due_at"):
        try:
            due_at = datetime.fromisoformat(str(body["due_at"]).replace("Z", "+00:00"))
        except Exception:
            pass

    task_id = _new_id("task")
    async with async_session_factory()() as session:
        task = TaskRecord(
            id=task_id,
            lead_id=body.get("lead_id") or None,
            deal_id=body.get("deal_id") or None,
            task_type=task_type,
            due_at=due_at,
            status="pending",
            owner=str(body.get("owner") or "auto"),
            notes=str(body.get("notes") or "") or None,
        )
        session.add(task)
        await session.commit()
    return {"id": task_id, "status": "pending", "due_at": due_at.isoformat()}


@router.patch("/tasks/{task_id}")
async def update_task(task_id: str, body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    async with async_session_factory()() as session:
        result = await session.execute(select(TaskRecord).where(TaskRecord.id == task_id))
        task = result.scalar_one_or_none()
        if not task:
            raise HTTPException(status_code=404, detail="task_not_found")
        if "status" in body:
            task.status = str(body["status"])
            if task.status == "done":
                task.completed_at = _utcnow()
        if "notes" in body:
            task.notes = str(body["notes"])[:2000]
        if "due_at" in body:
            try:
                task.due_at = datetime.fromisoformat(str(body["due_at"]).replace("Z", "+00:00"))
            except Exception:
                pass
        await session.commit()
    return {"id": task_id, "status": task.status}


@router.get("/tasks")
async def list_tasks(status: str = "pending", limit: int = 20) -> dict[str, Any]:
    limit = max(1, min(100, limit))
    async with async_session_factory()() as session:
        result = await session.execute(
            select(TaskRecord)
            .where(TaskRecord.status == status)
            .order_by(TaskRecord.due_at.asc())
            .limit(limit)
        )
        rows = result.scalars().all()
        return {
            "count": len(rows),
            "items": [
                {
                    "id": r.id,
                    "lead_id": r.lead_id,
                    "deal_id": r.deal_id,
                    "task_type": r.task_type,
                    "due_at": r.due_at.isoformat() if r.due_at else None,
                    "status": r.status,
                    "owner": r.owner,
                    "notes": r.notes,
                }
                for r in rows
            ],
        }


# ── Dashboard metrics ───────────────────────────────────────────

@router.get("/dashboard/metrics")
async def dashboard_metrics() -> dict[str, Any]:
    """
    Public/internal dashboard summary — counts + top of pipeline.
    Resilient: if a table doesn't exist yet, returns 0 for that metric.
    """
    async def _count(session, stmt):
        try:
            r = await session.execute(stmt)
            return int(r.scalar() or 0)
        except Exception as e:
            log.warning("dashboard_query_skip: %s", str(e)[:120])
            return 0

    async def _sum(session, stmt):
        try:
            r = await session.execute(stmt)
            return float(r.scalar() or 0.0)
        except Exception as e:
            log.warning("dashboard_query_skip: %s", str(e)[:120])
            return 0.0

    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)

    async with async_session_factory()() as session:
        leads_total = await _count(session, select(func.count()).select_from(LeadRecord))
        leads_new = await _count(session, select(func.count()).select_from(LeadRecord).where(LeadRecord.status == "new"))
        leads_qualified = await _count(session, select(func.count()).select_from(LeadRecord).where(LeadRecord.status == "qualified"))
        leads_won = await _count(session, select(func.count()).select_from(LeadRecord).where(LeadRecord.status == "won"))

        deals_total = await _count(session, select(func.count()).select_from(DealRecord))
        deals_paid_count = await _count(session, select(func.count()).select_from(DealRecord).where(DealRecord.stage == "paid"))
        revenue_paid = await _sum(session, select(func.coalesce(func.sum(DealRecord.amount), 0.0)).where(DealRecord.stage == "paid"))

        conversations_total = await _count(session, select(func.count()).select_from(ConversationRecord))
        conversations_today = await _count(session, select(func.count()).select_from(ConversationRecord).where(ConversationRecord.created_at >= today_start))

        tasks_pending = await _count(session, select(func.count()).select_from(TaskRecord).where(TaskRecord.status == "pending"))
        tasks_overdue = await _count(session, select(func.count()).select_from(TaskRecord).where(TaskRecord.status == "pending", TaskRecord.due_at < _utcnow()))

    return {
        "as_of": _utcnow().isoformat(),
        "leads": {
            "total": int(leads_total),
            "new": int(leads_new),
            "qualified": int(leads_qualified),
            "won": int(leads_won),
        },
        "deals": {
            "total": int(deals_total),
            "paid": int(deals_paid_count),
            "revenue_sar_paid": float(revenue_paid),
        },
        "conversations": {
            "total": int(conversations_total),
            "today": int(conversations_today),
        },
        "tasks": {
            "pending": int(tasks_pending),
            "overdue": int(tasks_overdue),
        },
    }


from db.models import CompanyRecord, CustomerRecord, OutreachQueueRecord, PartnerRecord


# ── Companies (subscriber intake) ───────────────────────────────

@router.post("/companies/intake")
async def company_intake(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """
    Onboard a Dealix subscriber. Builds full GTM profile (ICP, channel plan, offer ladder).
    Body: {name, website, industry, country, products, target_customer_type, ...}
    """
    name = str(body.get("name") or "").strip()
    if not name:
        raise HTTPException(status_code=400, detail="company_name_required")

    # Auto-derived ICP/channel/offer based on industry (deterministic — no LLM)
    industry = (body.get("industry") or "").lower()
    icp_profile = {
        "best_segments": _segments_for(industry),
        "buying_triggers": ["high lead volume", "WhatsApp inbound", "CRM in use", "hiring sales"],
        "decision_makers": ["CEO", "Founder", "Head of Growth", "Sales Director"],
    }
    channel_plan = {
        "primary": "WhatsApp + email + form",
        "secondary": ["LinkedIn manual", "SMS warm only"],
        "auto_send_allowed": ["form", "email", "whatsapp_inbound", "sms_inbound"],
        "human_required": ["linkedin", "investor", "high_value_enterprise"],
    }
    offer_ladder = {
        "free_audit": "20-min audit",
        "pilot": "1 SAR × 7 days",
        "starter": "999 SAR/mo",
        "growth": "2,999 SAR/mo",
        "scale": "7,999 SAR/mo",
        "agency_partner": "Setup 3-15K + 20-30% MRR",
    }
    automation_policy = {
        "default": "auto_inbound + human_approval_outbound",
        "linkedin": "human_final_send_only",
        "whatsapp_cold": "blocked",
        "email_cold": "low_volume_with_optout",
    }

    rec_id = _new_id("co")
    db_status = "ok"
    async with async_session_factory()() as session:
        rec = CompanyRecord(
            id=rec_id,
            name=name,
            website=body.get("website") or None,
            industry=industry or None,
            country=body.get("country") or "Saudi Arabia",
            city=body.get("city") or None,
            products=body.get("products") or None,
            target_customer_type=body.get("target_customer_type") or None,
            average_deal_value=float(body.get("average_deal_value") or 0) or None,
            sales_cycle_length_days=float(body.get("sales_cycle_length_days") or 0) or None,
            current_lead_sources=body.get("current_lead_sources") or None,
            current_crm=body.get("current_crm") or None,
            booking_link=body.get("booking_link") or None,
            sales_team_email=body.get("sales_team_email") or None,
            whatsapp_number=body.get("whatsapp_number") or None,
            tone_of_voice=body.get("tone_of_voice") or "professional_khaliji",
            languages=body.get("languages") or "ar,en",
            success_metric=body.get("success_metric") or None,
            icp_profile=icp_profile,
            channel_plan=channel_plan,
            offer_ladder=offer_ladder,
            automation_policy=automation_policy,
        )
        ok = await _safe_commit(session, rec)
        db_status = "ok" if ok else "skipped_db_unreachable"

    return {
        "id": rec_id,
        "name": name,
        "db_status": db_status,
        "icp_profile": icp_profile,
        "channel_plan": channel_plan,
        "offer_ladder": offer_ladder,
        "automation_policy": automation_policy,
        "status": "active",
    }


def _segments_for(industry: str) -> list[str]:
    industry = (industry or "").lower()
    if "saas" in industry:
        return ["Saudi B2B SaaS 20-200 employees", "Founders/Heads of Growth", "Companies with HubSpot/Calendly/CRM"]
    if "ecom" in industry or "retail" in industry:
        return ["Salla/Zid merchants 1K+ orders/mo", "WhatsApp-heavy stores", "B2B distributors"]
    if "real estate" in industry or "proptech" in industry:
        return ["Real estate brokers", "Property developers", "Wasit platforms"]
    if "f&b" in industry or "restaurant" in industry:
        return ["Restaurant chains 5+ locations", "F&B franchises", "Cloud kitchens"]
    if "agency" in industry or "marketing" in industry:
        return ["Saudi B2B clients of agency", "Marketing agencies w/ retainer model"]
    return ["Saudi B2B 50-500 employees with inbound leads", "Companies with response-time pain"]


# ── Channels policy ─────────────────────────────────────────────

@router.post("/channels/policy")
async def channel_policy(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """
    Decide if a planned outreach action can auto-send or needs human approval.
    Body: {channel, opportunity_type?, risk_level?, lead_value_sar?}
    """
    channel = str(body.get("channel") or "").lower()
    opp = str(body.get("opportunity_type") or "").upper()
    risk = str(body.get("risk_level") or "LOW").upper()
    value = float(body.get("lead_value_sar") or 0)

    auto_send = True
    human_required = False
    risk_reason = []

    if channel == "linkedin":
        auto_send = False
        human_required = True
        risk_reason.append("LinkedIn ToS — no auto-send ever")
    if channel == "whatsapp_cold":
        auto_send = False
        human_required = True
        risk_reason.append("PDPL + Meta policy — cold WhatsApp blocked")
    if channel == "email" and not body.get("opt_out_included"):
        risk_reason.append("Email needs opt-out footer for compliance")
    if opp == "INVESTOR_OR_ADVISOR":
        auto_send = False
        human_required = True
        risk_reason.append("Investor outreach requires human")
    if risk in ("HIGH", "BLOCKED"):
        auto_send = False
        human_required = True
        risk_reason.append(f"Risk level {risk}")
    if value >= 50000:
        auto_send = False
        human_required = True
        risk_reason.append("High-value enterprise — human review")

    return {
        "channel": channel,
        "auto_send_allowed": auto_send,
        "human_approval_required": human_required,
        "risk_reasons": risk_reason or ["LOW risk — proceed"],
        "recommended_action": "AUTO_SEND" if auto_send else "QUEUE_FOR_HUMAN",
    }


# ── Outreach queue ──────────────────────────────────────────────

@router.post("/outreach/queue")
async def queue_outreach(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """Add an outreach item to queue (one-by-one human-final-send model for restricted channels)."""
    channel = str(body.get("channel") or "").lower()
    message = str(body.get("message") or "").strip()
    if not channel or not message:
        raise HTTPException(status_code=400, detail="channel_and_message_required")

    rec_id = _new_id("queue")
    async with async_session_factory()() as session:
        rec = OutreachQueueRecord(
            id=rec_id,
            lead_id=body.get("lead_id") or None,
            channel=channel,
            message=message[:5000],
            approval_required=bool(body.get("approval_required", channel == "linkedin")),
            status="queued",
            risk_reason=body.get("risk_reason") or None,
        )
        session.add(rec)
        await session.commit()
    return {"id": rec_id, "status": "queued", "channel": channel}


@router.patch("/outreach/queue/{queue_id}")
async def update_queue_item(queue_id: str, body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    async with async_session_factory()() as session:
        result = await session.execute(select(OutreachQueueRecord).where(OutreachQueueRecord.id == queue_id))
        rec = result.scalar_one_or_none()
        if not rec:
            raise HTTPException(status_code=404, detail="queue_item_not_found")
        if "status" in body:
            rec.status = str(body["status"])
            if rec.status == "sent":
                rec.sent_at = _utcnow()
        await session.commit()
    return {"id": queue_id, "status": rec.status}


# GET /api/v1/outreach/queue — use api.routers.outreach.list_queue (single canonical route).


# ── Payments ─────────────────────────────────────────────────────

@router.post("/payments/manual-request")
async def manual_payment_request(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """Mark deal as payment_requested + create matching task."""
    deal_id = str(body.get("deal_id") or "").strip()
    if not deal_id:
        raise HTTPException(status_code=400, detail="deal_id_required")
    method = body.get("method") or "bank_transfer"

    async with async_session_factory()() as session:
        result = await session.execute(select(DealRecord).where(DealRecord.id == deal_id))
        deal = result.scalar_one_or_none()
        if not deal:
            raise HTTPException(status_code=404, detail="deal_not_found")
        deal.stage = "payment_requested"
        # Schedule check-in task in 3 days
        task = TaskRecord(
            id=_new_id("task"),
            deal_id=deal_id,
            lead_id=deal.lead_id,
            task_type="payment_check",
            due_at=_utcnow() + timedelta(days=3),
            status="pending",
            owner="auto",
            notes=f"Check payment proof for deal {deal_id} (method: {method})",
        )
        session.add(task)
        await session.commit()
    return {
        "deal_id": deal_id,
        "status": "payment_requested",
        "method": method,
        "follow_up_task_id": task.id,
        "instruction": (
            "Send invoice to customer via WhatsApp/email with bank IBAN or STC Pay number. "
            "Use template in docs/ops/MANUAL_PAYMENT_SOP.md."
        ),
    }


@router.post("/payments/mark-paid")
async def mark_paid(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """Mark deal as paid + auto-create customer onboarding."""
    deal_id = str(body.get("deal_id") or "").strip()
    amount = float(body.get("amount") or 0)
    if not deal_id:
        raise HTTPException(status_code=400, detail="deal_id_required")

    async with async_session_factory()() as session:
        result = await session.execute(select(DealRecord).where(DealRecord.id == deal_id))
        deal = result.scalar_one_or_none()
        if not deal:
            raise HTTPException(status_code=404, detail="deal_not_found")
        deal.stage = "paid"
        if amount:
            deal.amount = amount

        # Auto-create customer
        cust = CustomerRecord(
            id=_new_id("cust"),
            deal_id=deal_id,
            plan=str(body.get("plan") or "pilot"),
            onboarding_status="kickoff_pending",
            pilot_start_at=_utcnow(),
            pilot_end_at=_utcnow() + timedelta(days=7),
            success_metric=body.get("success_metric") or None,
        )
        session.add(cust)

        # Schedule onboarding kickoff task
        task = TaskRecord(
            id=_new_id("task"),
            deal_id=deal_id,
            lead_id=deal.lead_id,
            task_type="onboarding_kickoff",
            due_at=_utcnow() + timedelta(hours=4),
            status="pending",
            owner="sami",
            notes=f"Kickoff call within 4 hours for paid deal {deal_id}. Use FIRST_CUSTOMER_DELIVERY_TEMPLATE.md",
        )
        session.add(task)
        await session.commit()
    return {
        "deal_id": deal_id,
        "status": "paid",
        "customer_id": cust.id,
        "onboarding_task_id": task.id,
        "celebration": "🎉 First revenue! Open docs/sales-kit/dealix_case_study_template.md within 48h.",
    }


# ── Customer onboarding ─────────────────────────────────────────

@router.post("/customers/onboard")
async def customer_onboard(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """Mark customer onboarding milestone."""
    customer_id = str(body.get("customer_id") or "").strip()
    status = str(body.get("status") or "kickoff_done").strip()
    if not customer_id:
        raise HTTPException(status_code=400, detail="customer_id_required")

    async with async_session_factory()() as session:
        result = await session.execute(select(CustomerRecord).where(CustomerRecord.id == customer_id))
        cust = result.scalar_one_or_none()
        if not cust:
            raise HTTPException(status_code=404, detail="customer_not_found")
        cust.onboarding_status = status
        if "nps_score" in body:
            cust.nps_score = int(body["nps_score"])
        if "churn_risk" in body:
            cust.churn_risk = str(body["churn_risk"])
        await session.commit()
    return {"customer_id": customer_id, "onboarding_status": status}


# ── Partners ─────────────────────────────────────────────────────

@router.post("/partners/intake")
async def partner_intake(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """Add a partner (agency / implementation / referral / strategic)."""
    name = str(body.get("company_name") or "").strip()
    ptype = str(body.get("partner_type") or "AGENCY").upper()
    if not name:
        raise HTTPException(status_code=400, detail="company_name_required")

    pid = _new_id("partner")
    # Default commission terms by type
    commission = {
        "REFERRAL":       "10% MRR × 12 months",
        "AGENCY":         "Setup 3,000-15,000 SAR + 20-30% MRR (lifetime)",
        "IMPLEMENTATION": "Setup fee + service hours + 20% MRR",
        "STRATEGIC":      "Co-selling / bundle / white-label option (Scale tier)",
    }.get(ptype, "Custom — TBD")

    async with async_session_factory()() as session:
        rec = PartnerRecord(
            id=pid,
            company_name=name,
            partner_type=ptype,
            contact_name=body.get("contact_name") or None,
            contact_email=body.get("contact_email") or None,
            status="prospecting",
            commission_terms=commission,
            setup_fee_sar=float(body.get("setup_fee_sar") or 0),
            mrr_share_pct=float(body.get("mrr_share_pct") or 0),
            next_action="PREPARE_PARTNER_PITCH",
            next_action_at=_utcnow() + timedelta(days=1),
            notes=body.get("notes") or None,
        )
        session.add(rec)
        await session.commit()
    return {"id": pid, "partner_type": ptype, "commission_terms": commission, "next_action": "PREPARE_PARTNER_PITCH"}


# ── Lead form import (Google Ads / Meta) ────────────────────────

@router.post("/leads/import/google-ads")
async def import_google_lead(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """
    Google Ads Lead Form webhook. Google posts:
    {"google_key":"<your-key>","lead_id":"...","user_column_data":[{"column_name":"Name","string_value":"..."}],...}
    Validate google_key against env GOOGLE_ADS_LEAD_KEY.
    """
    import os
    expected_key = os.getenv("GOOGLE_ADS_LEAD_KEY", "")
    if expected_key and str(body.get("google_key") or "") != expected_key:
        raise HTTPException(status_code=401, detail="invalid_webhook_key")

    cols = body.get("user_column_data") or []
    fields = {c.get("column_id") or c.get("column_name"): c.get("string_value") for c in cols if isinstance(c, dict)}
    name = fields.get("Full Name") or fields.get("FULL_NAME") or fields.get("Name") or ""
    email = fields.get("Email") or fields.get("EMAIL") or ""
    phone = fields.get("Phone Number") or fields.get("PHONE_NUMBER") or fields.get("Phone") or ""
    company = fields.get("Company Name") or fields.get("COMPANY_NAME") or "Unknown"
    message = fields.get("Custom Question") or fields.get("MESSAGE") or "Google Ads lead"

    rec_id = _new_id("lead_gads")
    async with async_session_factory()() as session:
        lead = LeadRecord(
            id=rec_id,
            source="google_ads",
            company_name=company,
            contact_name=name,
            contact_email=email or None,
            contact_phone=phone or None,
            sector=None,
            region="Saudi Arabia",
            locale="ar",
            status="new",
            message=f"[Google Ads] {message}",
        )
        session.add(lead)
        # Auto-trigger inbound handler conversation log
        conv = ConversationRecord(
            id=_new_id("conv"),
            lead_id=rec_id,
            channel="google_ads",
            sender=email or phone,
            inbound_message=f"Lead form: {message}",
            classification="interested",
            next_action="PREPARE_DM",
            auto_sent=False,
        )
        session.add(conv)
        await session.commit()
    return {"lead_id": rec_id, "source": "google_ads", "status": "captured"}


@router.post("/leads/import/meta")
async def import_meta_lead(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """
    Meta Lead Ads webhook. Format: {entry:[{changes:[{value:{leadgen_id, form_id, field_data:[...]}}]}]}
    Or simplified: {form_id, field_data:[{name,values}], lead_id}
    """
    import os
    expected_token = os.getenv("META_VERIFY_TOKEN", "")
    if expected_token and str(body.get("verify_token") or "") != expected_token:
        # If verify_token sent, must match. If not sent, allow (Meta uses different verification)
        if body.get("verify_token") is not None:
            raise HTTPException(status_code=401, detail="invalid_verify_token")

    # Try Meta entry format
    field_data = []
    if "entry" in body:
        try:
            field_data = body["entry"][0]["changes"][0]["value"].get("field_data", [])
        except (KeyError, IndexError, TypeError):
            field_data = []
    field_data = field_data or body.get("field_data", [])

    fields = {}
    for fd in field_data:
        if isinstance(fd, dict):
            name = fd.get("name") or fd.get("field_name") or ""
            vals = fd.get("values") or [fd.get("value")]
            fields[name.lower()] = (vals[0] if vals else "")

    name = fields.get("full_name") or fields.get("name") or ""
    email = fields.get("email") or ""
    phone = fields.get("phone_number") or fields.get("phone") or ""
    company = fields.get("company_name") or "Unknown"
    msg = fields.get("message") or "Meta lead form"

    rec_id = _new_id("lead_meta")
    async with async_session_factory()() as session:
        lead = LeadRecord(
            id=rec_id,
            source="meta_lead_ads",
            company_name=company,
            contact_name=name,
            contact_email=email or None,
            contact_phone=phone or None,
            region="Saudi Arabia",
            locale="ar",
            status="new",
            message=f"[Meta] {msg}",
        )
        session.add(lead)
        conv = ConversationRecord(
            id=_new_id("conv"),
            lead_id=rec_id,
            channel="meta_lead_ads",
            sender=email or phone,
            inbound_message=f"Meta lead form: {msg}",
            classification="interested",
            next_action="PREPARE_DM",
            auto_sent=False,
        )
        session.add(conv)
        await session.commit()
    return {"lead_id": rec_id, "source": "meta_lead_ads", "status": "captured"}


@router.post("/admin/init-db")
async def admin_init_db() -> dict[str, Any]:
    """Force-create all tables. Idempotent. Public for debug — secure in prod."""
    try:
        from db.session import init_db
        await init_db()
        return {"status": "ok", "message": "All tables created or verified"}
    except Exception as e:
        log.exception("init_db_failed")
        return {"status": "error", "error": str(e)[:500], "type": type(e).__name__}


@router.post("/admin/test-insert")
async def admin_test_insert() -> dict[str, Any]:
    """Insert one test row and report exact error if it fails."""
    try:
        async with async_session_factory()() as session:
            rec = ConversationRecord(
                id=_new_id("test"),
                channel="test",
                sender="diagnostic",
                inbound_message="test",
                classification="test",
                next_action="test",
            )
            session.add(rec)
            await session.commit()
            return {"status": "ok", "inserted_id": rec.id}
    except Exception as e:
        log.exception("test_insert_failed")
        return {"status": "error", "error": str(e)[:500], "type": type(e).__name__}


@router.get("/admin/db-diag")
async def db_diag() -> dict[str, Any]:
    """Show DATABASE_URL prefix (redacted) + try a simple query."""
    import os
    url = os.getenv("DATABASE_URL", "")
    safe_url = (url[:30] + "..." + url[-20:]) if len(url) > 60 else url
    try:
        from core.config.settings import get_settings
        s = get_settings()
        cfg_url = s.database_url
        cfg_safe = (cfg_url[:35] + "..." + cfg_url[-25:]) if len(cfg_url) > 70 else cfg_url
    except Exception as e:
        cfg_safe = f"settings_error: {e}"
    return {
        "raw_env_prefix": safe_url[:50],
        "raw_env_length": len(url),
        "settings_url_prefix": cfg_safe[:80],
    }


# ── Aliases for /api/v1/integrations/* (matches external webhook config conventions) ──

@router.post("/integrations/google-lead-form")
async def alias_google_lead(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    return await import_google_lead(body)


@router.post("/integrations/meta-lead-form")
async def alias_meta_lead(body: dict[str, Any] = Body(...)) -> dict[str, Any]:
    return await import_meta_lead(body)

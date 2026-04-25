"""Dealix Full OS Orchestrator — connects all services into a unified deal lifecycle.

This is the brain that ties WhatsApp brain + sequences + autopilot + CRM + booking
into one autonomous system. Every inbound lead flows through a state machine:

  new_lead → qualify → nurture → meeting_booked → proposal → negotiation → closed_won/lost

At each stage, the orchestrator:
1. Detects what happened (inbound message, reply, booking, payment)
2. Classifies intent
3. Decides next action
4. Executes via the appropriate service (WhatsApp, email, CRM, booking)
5. Logs everything
6. Moves to next stage or holds for human approval
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, Optional
from uuid import uuid4

from pydantic import BaseModel

logger = logging.getLogger("dealix.full_os")


class DealStage(str, Enum):
    NEW_LEAD = "new_lead"
    QUALIFYING = "qualifying"
    QUALIFIED = "qualified"
    NURTURING = "nurturing"
    MEETING_BOOKED = "meeting_booked"
    MEETING_DONE = "meeting_done"
    PROPOSAL_SENT = "proposal_sent"
    NEGOTIATING = "negotiating"
    PAYMENT_REQUESTED = "payment_requested"
    PILOT_ACTIVE = "pilot_active"
    CLOSED_WON = "closed_won"
    CLOSED_LOST = "closed_lost"
    OPTED_OUT = "opted_out"


class LeadSource(str, Enum):
    WHATSAPP_INBOUND = "whatsapp_inbound"
    WEBSITE_FORM = "website_form"
    LINKEDIN_REPLY = "linkedin_reply"
    EMAIL_REPLY = "email_reply"
    OUTREACH_REPLY = "outreach_reply"
    REFERRAL = "referral"
    PARTNER = "partner"
    MANUAL = "manual"


class ActionType(str, Enum):
    SEND_WHATSAPP = "send_whatsapp"
    SEND_EMAIL = "send_email"
    SEND_SMS = "send_sms"
    BOOK_MEETING = "book_meeting"
    SEND_PROPOSAL = "send_proposal"
    REQUEST_PAYMENT = "request_payment"
    ENROLL_SEQUENCE = "enroll_sequence"
    CLASSIFY_REPLY = "classify_reply"
    ESCALATE_HUMAN = "escalate_human"
    SYNC_CRM = "sync_crm"
    LOG_ACTIVITY = "log_activity"
    ONBOARD_CUSTOMER = "onboard_customer"
    GENERATE_REPORT = "generate_report"
    DO_NOTHING = "do_nothing"


STAGE_TRANSITIONS = {
    DealStage.NEW_LEAD: {
        "interested": DealStage.QUALIFYING,
        "ask_price": DealStage.QUALIFYING,
        "ask_demo": DealStage.MEETING_BOOKED,
        "ask_details": DealStage.QUALIFYING,
        "not_now": DealStage.NURTURING,
        "unsubscribe": DealStage.OPTED_OUT,
        "default": DealStage.QUALIFYING,
    },
    DealStage.QUALIFYING: {
        "qualified": DealStage.QUALIFIED,
        "not_qualified": DealStage.NURTURING,
        "wants_demo": DealStage.MEETING_BOOKED,
        "unsubscribe": DealStage.OPTED_OUT,
        "default": DealStage.NURTURING,
    },
    DealStage.QUALIFIED: {
        "meeting_booked": DealStage.MEETING_BOOKED,
        "sequence_enrolled": DealStage.NURTURING,
        "default": DealStage.NURTURING,
    },
    DealStage.NURTURING: {
        "replied_positive": DealStage.QUALIFYING,
        "meeting_booked": DealStage.MEETING_BOOKED,
        "unsubscribe": DealStage.OPTED_OUT,
        "default": DealStage.NURTURING,
    },
    DealStage.MEETING_BOOKED: {
        "meeting_done": DealStage.MEETING_DONE,
        "no_show": DealStage.NURTURING,
        "cancelled": DealStage.NURTURING,
        "default": DealStage.MEETING_BOOKED,
    },
    DealStage.MEETING_DONE: {
        "proposal_sent": DealStage.PROPOSAL_SENT,
        "not_interested": DealStage.CLOSED_LOST,
        "needs_time": DealStage.NURTURING,
        "default": DealStage.PROPOSAL_SENT,
    },
    DealStage.PROPOSAL_SENT: {
        "accepted": DealStage.PAYMENT_REQUESTED,
        "negotiating": DealStage.NEGOTIATING,
        "rejected": DealStage.CLOSED_LOST,
        "default": DealStage.NEGOTIATING,
    },
    DealStage.NEGOTIATING: {
        "accepted": DealStage.PAYMENT_REQUESTED,
        "rejected": DealStage.CLOSED_LOST,
        "default": DealStage.NEGOTIATING,
    },
    DealStage.PAYMENT_REQUESTED: {
        "paid": DealStage.PILOT_ACTIVE,
        "declined": DealStage.NEGOTIATING,
        "default": DealStage.PAYMENT_REQUESTED,
    },
    DealStage.PILOT_ACTIVE: {
        "converted": DealStage.CLOSED_WON,
        "churned": DealStage.CLOSED_LOST,
        "default": DealStage.PILOT_ACTIVE,
    },
}

STAGE_AUTO_ACTIONS = {
    DealStage.NEW_LEAD: [
        ActionType.CLASSIFY_REPLY,
        ActionType.SEND_WHATSAPP,
        ActionType.LOG_ACTIVITY,
    ],
    DealStage.QUALIFYING: [
        ActionType.SEND_WHATSAPP,
        ActionType.LOG_ACTIVITY,
    ],
    DealStage.QUALIFIED: [
        ActionType.BOOK_MEETING,
        ActionType.ENROLL_SEQUENCE,
        ActionType.SYNC_CRM,
    ],
    DealStage.NURTURING: [
        ActionType.ENROLL_SEQUENCE,
    ],
    DealStage.MEETING_BOOKED: [
        ActionType.SEND_WHATSAPP,
        ActionType.SYNC_CRM,
    ],
    DealStage.MEETING_DONE: [
        ActionType.SEND_PROPOSAL,
        ActionType.LOG_ACTIVITY,
    ],
    DealStage.PROPOSAL_SENT: [
        ActionType.LOG_ACTIVITY,
    ],
    DealStage.NEGOTIATING: [
        ActionType.CLASSIFY_REPLY,
        ActionType.ESCALATE_HUMAN,
    ],
    DealStage.PAYMENT_REQUESTED: [
        ActionType.SEND_WHATSAPP,
        ActionType.LOG_ACTIVITY,
    ],
    DealStage.PILOT_ACTIVE: [
        ActionType.GENERATE_REPORT,
        ActionType.ONBOARD_CUSTOMER,
    ],
    DealStage.CLOSED_WON: [
        ActionType.SYNC_CRM,
        ActionType.ONBOARD_CUSTOMER,
        ActionType.GENERATE_REPORT,
    ],
    DealStage.OPTED_OUT: [
        ActionType.DO_NOTHING,
    ],
}

QUALIFICATION_QUESTIONS_AR = [
    "كم lead تقريباً تستقبلون شهرياً؟",
    "وش أكبر تحدي عندكم في متابعة الاستفسارات؟",
    "هل عندكم فريق مبيعات يتابع الـ leads حالياً؟",
    "كم ميزانيتكم الشهرية لأدوات المبيعات/التسويق؟",
    "متى تبون تبدون لو الحل مناسب؟",
]

STAGE_MESSAGES_AR = {
    DealStage.NEW_LEAD: "أهلاً وسهلاً! 👋 أنا مساعد Dealix الذكي. كيف أقدر أساعدك اليوم؟",
    DealStage.QUALIFYING: "ممتاز! عشان أفهم احتياجكم بشكل أفضل — {question}",
    DealStage.QUALIFIED: "بناءً على اللي ذكرته، Dealix يقدر يساعدكم. تبي نحجز 20 دقيقة demo؟\ncalendly.com/sami-assiri11/dealix-demo",
    DealStage.NURTURING: "مرحبا مرة ثانية! عندنا تحديثات جديدة في Dealix ممكن تفيدكم. تبي أشرح؟",
    DealStage.MEETING_BOOKED: "تم الحجز! 🎯 بنرسل لك تذكير قبل الموعد. لو تحتاج تغيّر الوقت قلّي.",
    DealStage.MEETING_DONE: "شكراً على وقتك اليوم! بناءً على اللي ناقشناه، جهّزت لك عرض pilot مخصص.",
    DealStage.PROPOSAL_SENT: "أرسلت لك تفاصيل العرض. أي سؤال أنا موجود.",
    DealStage.NEGOTIATING: "فاهم. خلّني أشوف وش أقدر أسوي عشان نوصل لاتفاق يناسب الطرفين.",
    DealStage.PAYMENT_REQUESTED: "العرض جاهز! الدفع:\n- تحويل بنكي\n- STC Pay\nبعد التأكيد نبدأ الإعداد خلال 4 ساعات.",
    DealStage.PILOT_ACTIVE: "يوم {day} من الـ pilot! هذا تقرير اليوم:\n{report}",
    DealStage.CLOSED_WON: "مبروك! 🎉 أهلاً بكم في Dealix. بنبدأ الإعداد الكامل.",
    DealStage.OPTED_OUT: "تم. لن نتواصل مرة ثانية. شكراً على وقتكم.",
}


class OrchestratorEvent(BaseModel):
    lead_id: str = ""
    phone: str = ""
    email: str = ""
    company: str = ""
    sector: str = ""
    source: str = "whatsapp_inbound"
    message: str = ""
    current_stage: str = "new_lead"
    event_type: str = "inbound_message"


class FullOSOrchestrator:
    """Central brain that processes events and drives the deal lifecycle."""

    def process_event(self, event: OrchestratorEvent) -> Dict[str, Any]:
        current = DealStage(event.current_stage) if event.current_stage else DealStage.NEW_LEAD

        intent = self._classify_intent(event.message)

        transitions = STAGE_TRANSITIONS.get(current, {})
        next_stage = transitions.get(intent, transitions.get("default", current))

        actions = STAGE_AUTO_ACTIONS.get(next_stage, [])

        response_message = self._get_stage_message(next_stage, event)

        human_required = next_stage in (
            DealStage.NEGOTIATING,
            DealStage.PAYMENT_REQUESTED,
            DealStage.PILOT_ACTIVE,
        )

        return {
            "lead_id": event.lead_id or str(uuid4())[:8],
            "previous_stage": current.value,
            "intent_detected": intent,
            "new_stage": next_stage.value,
            "actions": [a.value for a in actions],
            "response_message_ar": response_message,
            "human_approval_required": human_required,
            "auto_send_allowed": not human_required and next_stage != DealStage.OPTED_OUT,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "qualification_question": self._get_next_question(next_stage, event),
        }

    def _classify_intent(self, message: str) -> str:
        if not message:
            return "default"
        text = message.lower()

        if any(w in text for w in ["إيقاف", "stop", "unsubscribe", "لا تتواصل"]):
            return "unsubscribe"
        if any(w in text for w in ["مهتم", "interested", "أبي أجرب", "نجرب", "تمام", "نعم"]):
            return "interested"
        if any(w in text for w in ["demo", "ديمو", "أوريني", "عرض", "شرح"]):
            return "wants_demo"
        if any(w in text for w in ["كم السعر", "كم التكلفة", "pricing", "أسعار"]):
            return "ask_price"
        if any(w in text for w in ["تفاصيل", "details", "أكثر"]):
            return "ask_details"
        if any(w in text for w in ["لاحقاً", "later", "مو الحين", "بعدين"]):
            return "not_now"
        if any(w in text for w in ["دفعت", "حوّلت", "paid", "تم الدفع"]):
            return "paid"
        if any(w in text for w in ["شراكة", "partner", "وكالة"]):
            return "interested"
        return "default"

    def _get_stage_message(self, stage: DealStage, event: OrchestratorEvent) -> str:
        template = STAGE_MESSAGES_AR.get(stage, "")
        return template.replace("{company}", event.company or "").replace("{question}", "").replace("{day}", "1").replace("{report}", "")

    def _get_next_question(self, stage: DealStage, event: OrchestratorEvent) -> Optional[str]:
        if stage == DealStage.QUALIFYING:
            return QUALIFICATION_QUESTIONS_AR[0]
        return None


orchestrator = FullOSOrchestrator()

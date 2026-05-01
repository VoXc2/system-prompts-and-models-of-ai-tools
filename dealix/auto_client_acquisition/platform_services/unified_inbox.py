"""
Unified Growth Inbox — turn platform events into Arabic action cards.

8 card types: opportunity / email_lead / whatsapp_reply / social_comment /
payment / meeting_prep / review_response / partner_suggestion.

Every card: title_ar, summary_ar, why_it_matters_ar, recommended_action_ar,
risk_level, expected_impact_sar, ≤3 buttons, approval_required.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from auto_client_acquisition.platform_services.event_bus import PlatformEvent


CARD_TYPES: tuple[str, ...] = (
    "opportunity",
    "email_lead",
    "whatsapp_reply",
    "social_comment",
    "payment",
    "meeting_prep",
    "review_response",
    "partner_suggestion",
)


@dataclass
class InboxCard:
    """One card in the unified inbox."""

    card_id: str
    type: str
    channel: str
    title_ar: str
    summary_ar: str
    why_it_matters_ar: str
    recommended_action_ar: str
    risk_level: str                      # low / medium / high
    expected_impact_sar: float = 0.0
    buttons_ar: tuple[str, ...] = ()     # ≤3 per WhatsApp limit
    approval_required: bool = True

    def __post_init__(self):
        if len(self.buttons_ar) > 3:
            raise ValueError("buttons_ar must have ≤3 items (WhatsApp limit)")
        if self.type not in CARD_TYPES:
            raise ValueError(f"unknown card type: {self.type}")
        if self.risk_level not in ("low", "medium", "high"):
            raise ValueError(f"invalid risk_level: {self.risk_level}")

    def to_dict(self) -> dict[str, Any]:
        return {
            "card_id": self.card_id,
            "type": self.type,
            "channel": self.channel,
            "title_ar": self.title_ar,
            "summary_ar": self.summary_ar,
            "why_it_matters_ar": self.why_it_matters_ar,
            "recommended_action_ar": self.recommended_action_ar,
            "risk_level": self.risk_level,
            "expected_impact_sar": self.expected_impact_sar,
            "buttons_ar": list(self.buttons_ar),
            "approval_required": self.approval_required,
        }


# ── Per-event-type renderers ─────────────────────────────────────
def build_card_from_event(event: PlatformEvent) -> InboxCard | None:
    """Render an event into a card. Returns None for non-actionable events."""
    et = event.event_type
    p = event.payload

    if et == "whatsapp.message_received":
        return InboxCard(
            card_id=f"card_{event.event_id}",
            type="whatsapp_reply",
            channel="whatsapp",
            title_ar=f"رد جديد من {p.get('from_name', '—')}",
            summary_ar=str(p.get("text_preview", ""))[:160],
            why_it_matters_ar="رد سريع خلال ٣٠ دقيقة يضاعف احتمال الحجز.",
            recommended_action_ar="صنّف الرد + جهّز رد عربي مناسب",
            risk_level="low",
            expected_impact_sar=2_500,
            buttons_ar=("اعتمد", "تخطّي", "عدّل"),
        )

    if et == "email.received":
        return InboxCard(
            card_id=f"card_{event.event_id}",
            type="email_lead",
            channel="gmail",
            title_ar=f"إيميل جديد من {p.get('from', '—')}",
            summary_ar=str(p.get("subject", ""))[:200],
            why_it_matters_ar="إيميل من عميل محتمل — رد ≤4 ساعات يضاعف التحويل.",
            recommended_action_ar="جهّز رد رسمي + عرض اجتماع 15 دقيقة",
            risk_level="low",
            expected_impact_sar=8_000,
            buttons_ar=("جهّز مسودة", "احجز اجتماع", "تخطّي"),
        )

    if et == "calendar.meeting_scheduled":
        return InboxCard(
            card_id=f"card_{event.event_id}",
            type="meeting_prep",
            channel="google_calendar",
            title_ar=f"اجتماع {p.get('when', 'قريباً')} مع {p.get('contact', '—')}",
            summary_ar="جهّزت ملخص الشركة + 5 أسئلة + اعتراضات محتملة + عرض مناسب.",
            why_it_matters_ar="الاجتماع المُحضَّر يرفع احتمال الإغلاق بنسبة 40%+.",
            recommended_action_ar="افتح ملف التحضير + راجع الأجندة",
            risk_level="low",
            expected_impact_sar=p.get("expected_value_sar", 25_000),
            buttons_ar=("افتح التحضير", "اكتب أجندة", "أرسل تأكيد"),
            approval_required=False,
        )

    if et == "payment.failed":
        return InboxCard(
            card_id=f"card_{event.event_id}",
            type="payment",
            channel="moyasar",
            title_ar="فشل دفعة",
            summary_ar=f"العميل {p.get('customer_id', '—')} — مبلغ {p.get('amount_sar', 0):,.0f} ريال.",
            why_it_matters_ar="فشل الدفع غالباً سببه فني — متابعة سريعة تنقذ الصفقة.",
            recommended_action_ar="جهّز رسالة WhatsApp + رابط Moyasar جديد",
            risk_level="medium",
            expected_impact_sar=p.get("amount_sar", 2_999),
            buttons_ar=("جهّز رسالة", "رابط جديد", "اتصل"),
        )

    if et == "review.created":
        rating = float(p.get("rating", 5))
        risk = "high" if rating <= 2 else "medium" if rating <= 3 else "low"
        return InboxCard(
            card_id=f"card_{event.event_id}",
            type="review_response",
            channel="google_business_profile",
            title_ar=f"تقييم Google جديد: {rating} نجوم",
            summary_ar=str(p.get("text", ""))[:180],
            why_it_matters_ar=(
                "التقييم السلبي بدون رد خلال 24 ساعة يضرّ بالسمعة المحلية."
                if rating <= 3 else "التقييم الإيجابي فرصة للشكر + طلب إحالة."
            ),
            recommended_action_ar=(
                "اعتذار قصير + طلب تواصل + حل" if rating <= 3
                else "شكر دافئ + دعوة لطلب إحالة"
            ),
            risk_level=risk,
            expected_impact_sar=1_000,
            buttons_ar=("اعتمد الرد", "صعّد للمدير", "تخطّي")
            if rating <= 3
            else ("اعتمد الرد", "اطلب إحالة", "تخطّي"),
        )

    if et == "social.comment_received":
        return InboxCard(
            card_id=f"card_{event.event_id}",
            type="social_comment",
            channel=event.channel,
            title_ar=f"تعليق جديد على {event.channel}",
            summary_ar=str(p.get("text", ""))[:150],
            why_it_matters_ar="التعليقات الإيجابية = leads warmer من cold outreach.",
            recommended_action_ar="جهّز رد عربي + اقترح DM لو فيه إشارة شراء",
            risk_level="medium",
            expected_impact_sar=1_500,
            buttons_ar=("جهّز رد", "ابدأ DM", "تخطّي"),
        )

    if et == "lead.form_submitted":
        return InboxCard(
            card_id=f"card_{event.event_id}",
            type="opportunity",
            channel=event.channel,
            title_ar=f"Lead جديد: {p.get('company', '—')}",
            summary_ar=f"{p.get('name', '')} — {p.get('email', '')} — {p.get('city', '')}",
            why_it_matters_ar="Lead تعبأ نموذج → أعلى احتمال تحويل بين كل المصادر.",
            recommended_action_ar="رد ≤30 دقيقة + احجز مكالمة 15 دقيقة",
            risk_level="low",
            expected_impact_sar=p.get("expected_value_sar", 12_000),
            buttons_ar=("جهّز رد فوري", "احجز مكالمة", "تخطّي"),
        )

    if et == "partner.suggested":
        return InboxCard(
            card_id=f"card_{event.event_id}",
            type="partner_suggestion",
            channel="internal",
            title_ar=f"اقتراح شريك: {p.get('partner_name', '—')}",
            summary_ar=str(p.get("rationale_ar", ""))[:200],
            why_it_matters_ar="الشراكة الواحدة تفتح 3-5 leads warmer من cold.",
            recommended_action_ar="جهّز رسالة warm + احجز مكالمة 20 دقيقة",
            risk_level="low",
            expected_impact_sar=p.get("expected_revenue_sar", 50_000),
            buttons_ar=("اكتب رسالة", "احجز", "تخطّي"),
        )

    return None  # non-actionable event


# ── Demo feed builder ────────────────────────────────────────────
def build_demo_feed() -> dict[str, Any]:
    """A deterministic demo feed for the dashboard preview."""
    from auto_client_acquisition.platform_services.event_bus import make_event

    events = [
        make_event(
            event_type="lead.form_submitted", channel="website_forms",
            customer_id="demo",
            payload={"company": "شركة العقار الذهبي", "name": "خالد",
                     "email": "khalid@example.sa", "city": "الرياض",
                     "expected_value_sar": 18_000},
        ),
        make_event(
            event_type="email.received", channel="gmail",
            customer_id="demo",
            payload={"from": "ali@example.sa", "subject": "استفسار عن الباقات للشركات"},
        ),
        make_event(
            event_type="whatsapp.message_received", channel="whatsapp",
            customer_id="demo",
            payload={"from_name": "نورا — Saudi Logistics",
                     "text_preview": "ابغى أعرف وش الفرق بين Growth و Scale؟"},
        ),
        make_event(
            event_type="payment.failed", channel="moyasar",
            customer_id="demo",
            payload={"customer_id": "cust_123", "amount_sar": 2_999},
        ),
        make_event(
            event_type="review.created", channel="google_business_profile",
            customer_id="demo",
            payload={"rating": 2, "text": "تأخر الرد في عيادتنا"},
        ),
        make_event(
            event_type="partner.suggested", channel="internal",
            customer_id="demo",
            payload={"partner_name": "وكالة B2B في جدة",
                     "rationale_ar": "عملاؤها يحتاجون lead-gen — Dealix يكمل خدماتها.",
                     "expected_revenue_sar": 60_000},
        ),
    ]
    cards = [c.to_dict() for e in events if (c := build_card_from_event(e)) is not None]
    return {
        "feed_size": len(cards),
        "cards": cards,
        "policy_note_ar": "كل card عربي + ≤3 buttons + approval-aware.",
    }

"""Support ticket router — P0–P3 categorization + routing + first-response template."""

from __future__ import annotations

import re
from typing import Any

# 4 priority tiers Dealix supports.
SUPPORT_PRIORITIES: tuple[dict[str, Any], ...] = (
    {
        "id": "P0",
        "label_ar": "حرج جداً — أمان / إرسال خاطئ / تعطل كامل",
        "first_response_minutes": 30,
        "resolution_target_hours": 4,
        "escalation_owner": "founder",
    },
    {
        "id": "P1",
        "label_ar": "خدمة مهمة معطلة",
        "first_response_minutes": 120,
        "resolution_target_hours": 24,
        "escalation_owner": "operator_oncall",
    },
    {
        "id": "P2",
        "label_ar": "Connector أو Proof Pack متأخر",
        "first_response_minutes": 480,  # 8h
        "resolution_target_hours": 72,
        "escalation_owner": "operator_oncall",
    },
    {
        "id": "P3",
        "label_ar": "سؤال عام / تحسين",
        "first_response_minutes": 1440,  # 24h
        "resolution_target_hours": 168,  # 1 week
        "escalation_owner": "operator_team",
    },
)


# Keyword → priority hints.
_P0_KEYWORDS = (
    "أمان", "تسريب", "إرسال خاطئ", "إرسال بدون موافقة",
    "بدون موافقتي", "أرسل رسالة بدون", "أرسل بدون",
    "secret", "leak", "data breach", "outage", "completely down",
    "live charge", "charge بدون موافقة", "unauthorized",
)
_P1_KEYWORDS = (
    "service down", "خدمة معطلة", "service failed",
    "Pilot stopped", "Proof Pack مفقود",
)
_P2_KEYWORDS = (
    "connector", "Gmail", "Calendar", "Sheets",
    "WhatsApp setup", "Moyasar invoice",
)


def classify_ticket_priority(text: str) -> dict[str, Any]:
    """
    Classify a free-text support ticket → P0 / P1 / P2 / P3.

    Deterministic keyword matching. Returns matched priority + reasoning.
    """
    text = (text or "").strip()
    if not text:
        return {"priority": "P3", "reason_ar": "لا يوجد نص — اعتبار افتراضي."}

    text_lc = text.lower()
    for kw in _P0_KEYWORDS:
        if kw in text or kw.lower() in text_lc:
            return {
                "priority": "P0",
                "matched_keyword": kw,
                "reason_ar": f"كلمة حرجة مطابقة: {kw}",
            }
    for kw in _P1_KEYWORDS:
        if kw in text or kw.lower() in text_lc:
            return {
                "priority": "P1",
                "matched_keyword": kw,
                "reason_ar": f"خدمة مهمة معطلة: {kw}",
            }
    for kw in _P2_KEYWORDS:
        if kw in text or kw.lower() in text_lc:
            return {
                "priority": "P2",
                "matched_keyword": kw,
                "reason_ar": f"connector أو Proof Pack: {kw}",
            }
    return {"priority": "P3", "reason_ar": "افتراضي — سؤال أو تحسين."}


def route_ticket(
    *,
    text: str,
    customer_id: str = "",
    contact_email: str = "",
) -> dict[str, Any]:
    """Classify + route a ticket to the right SLA + owner."""
    classification = classify_ticket_priority(text)
    priority = classification["priority"]

    sla = next(
        (dict(p) for p in SUPPORT_PRIORITIES if p["id"] == priority),
        dict(SUPPORT_PRIORITIES[3]),
    )

    return {
        "customer_id": customer_id,
        "contact_email": contact_email,
        "priority": priority,
        "classification": classification,
        "sla": sla,
        "first_response_template": build_first_response_template(priority),
        "approval_required": True,
        "live_send_allowed": False,
    }


def build_first_response_template(priority: str) -> dict[str, Any]:
    """Build an Arabic first-response template per priority."""
    if priority == "P0":
        body = (
            "وصلني بلاغك الآن. نتعامل معه كأولوية حرجة. "
            "سأرد عليك خلال 30 دقيقة بتفاصيل ما حدث + الإجراءات المتخذة. "
            "إذا اكتشفت أي إرسال غير معتمد أو تسريب بيانات، سأتواصل معك مباشرة."
        )
    elif priority == "P1":
        body = (
            "وصلني بلاغك. نتعامل معه كأولوية عالية. "
            "سأرد بتفاصيل خلال ساعتين كحد أقصى."
        )
    elif priority == "P2":
        body = (
            "وصلني سؤالك حول الـ connector / Proof Pack. "
            "سأتابع خلال 8 ساعات عمل وأرسل لك حل أو خطوات تالية."
        )
    else:
        body = (
            "شاكر لك على ملاحظتك. سأرد عليك خلال 24 ساعة عمل. "
            "إذا الأمر عاجل، اكتب 'حرج' في رسالة جديدة وأرفعها للأولوية."
        )

    return {
        "priority": priority,
        "body_ar": body,
        "approval_required": True,
        "live_send_allowed": False,
    }

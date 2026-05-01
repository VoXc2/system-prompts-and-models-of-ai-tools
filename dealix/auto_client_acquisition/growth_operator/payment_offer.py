"""
Payment-in-Chat — Moyasar payment-link drafts (NO live charge).

In production: link goes to a Moyasar hosted checkout. The user enters
their card on Moyasar's domain (PCI-safe), not inside WhatsApp.

This module produces a STRUCTURED draft only — the actual
`POST /v1/payments` call to Moyasar happens elsewhere with the
customer's secret key.
"""

from __future__ import annotations

import uuid
from typing import Any


# ── Pricing (mirrors landing/pricing.html + business/pricing_strategy.py) ──
PLAN_CATALOG_SAR: dict[str, dict[str, Any]] = {
    "founder_operator": {"label_ar": "مشغّل المؤسس", "amount_sar": 499.0},
    "growth_os": {"label_ar": "نظام النمو (Growth OS)", "amount_sar": 2999.0},
    "scale_os": {"label_ar": "نظام التوسّع (Scale OS)", "amount_sar": 7999.0},
    "performance_pilot": {"label_ar": "Pay-per-Result pilot 30 يوم", "amount_sar": 1.0},  # placeholder
}


def sar_to_halalas(amount_sar: float) -> int:
    """Convert SAR to halalas (Moyasar's smallest unit). 1 SAR = 100 halalas."""
    if amount_sar < 0:
        raise ValueError("amount_sar must be non-negative")
    return int(round(amount_sar * 100))


def build_moyasar_payment_link_draft(
    *,
    plan_key: str,
    customer_id: str,
    contact_email: str | None = None,
    locale: str = "ar",
    callback_url: str = "https://dealix.sa/payment-success.html",
    cancel_url: str = "https://dealix.sa/payment-cancelled.html",
    custom_amount_sar: float | None = None,
) -> dict[str, Any]:
    """
    Build a Moyasar payment payload (NOT yet sent to Moyasar API).

    Returns a dict the operator can review + approve. The actual
    `POST /v1/payments` is fired elsewhere by the billing service.
    """
    plan = PLAN_CATALOG_SAR.get(plan_key)
    if plan is None and custom_amount_sar is None:
        return {
            "error": f"unknown_plan: {plan_key}",
            "approval_required": True,
            "approval_status": "pending_approval",
            "live_charged": False,
        }
    amount_sar = custom_amount_sar if custom_amount_sar is not None else plan["amount_sar"]
    label_ar = (plan["label_ar"] if plan else "خطة مخصصة")

    description_ar = (
        f"اشتراك Dealix — {label_ar}. "
        f"المبلغ {amount_sar:,.2f} ريال شامل ضريبة القيمة المضافة 15%."
    )

    return {
        "moyasar_request_draft": {
            "amount": sar_to_halalas(amount_sar),
            "currency": "SAR",
            "description": description_ar,
            "callback_url": callback_url,
            "cancel_url": cancel_url,
            "metadata": {
                "customer_id": customer_id,
                "plan_key": plan_key,
                "locale": locale,
                "draft_id": f"draft_pay_{uuid.uuid4().hex[:16]}",
            },
        },
        "amount_sar": amount_sar,
        "amount_halalas": sar_to_halalas(amount_sar),
        "label_ar": label_ar,
        "channel_recommendation": "whatsapp_with_link",
        "in_chat_message_ar": (
            f"الباقة المقترحة:\n{label_ar} — {amount_sar:,.0f} ريال\n\n"
            "[ادفع الآن]   [أرسل فاتورة]   [كلم المبيعات]\n\n"
            "ملاحظة: الدفع آمن عبر Moyasar (سعودي مرخّص). فاتورة ZATCA "
            "تصلكم تلقائياً بعد التأكيد."
        ),
        "approval_required": True,
        "approval_status": "pending_approval",
        "live_charged": False,
        "compliance_note_ar": (
            "draft فقط — لا يتم خصم أي مبلغ حتى يضغط العميل 'ادفع' "
            "على Moyasar وتصلنا webhook 'paid'."
        ),
    }

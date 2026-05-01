"""Manual Moyasar invoice/payment-link flow — never charges live from API."""

from __future__ import annotations

from typing import Any


def build_moyasar_invoice_instructions(
    *,
    amount_sar: int = 499,
    customer_name: str = "",
    invoice_description: str = "Dealix Private Beta Pilot — 7 days",
) -> dict[str, Any]:
    """
    Step-by-step instructions to create a Moyasar invoice from the dashboard.

    Never calls the API. Founder-driven only.
    """
    amount_halalas = int(amount_sar) * 100
    return {
        "amount_sar": amount_sar,
        "amount_halalas": amount_halalas,
        "currency": "SAR",
        "customer_name": customer_name,
        "description": invoice_description,
        "method": "manual_moyasar_dashboard",
        "no_live_charge": True,
        "instructions_ar": [
            "1. افتح Moyasar dashboard.",
            "2. اختر Invoices → Create Invoice.",
            f"3. ضع المبلغ {amount_sar} ريال (الـ API يستخدم halalas = {amount_halalas}).",
            f"4. اكتب الوصف: {invoice_description}.",
            f"5. أضف اسم العميل: {customer_name or '(اسم العميل)'}.",
            "6. فعّل خيار إرسال الفاتورة بالإيميل.",
            "7. اضغط Send.",
            "8. سجّل invoice ID + رابط الفاتورة في pipeline_tracker.",
        ],
        "do_not_do_ar": [
            "لا تخزّن بيانات بطاقة العميل.",
            "لا تستخدم API live charge من Dealix.",
            "لا ترسل دفعة بدون تأكيد العميل صراحة.",
        ],
    }


def build_payment_link_message(
    *,
    customer_name: str = "[الاسم]",
    invoice_url: str = "[INVOICE_URL]",
    amount_sar: int = 499,
) -> dict[str, Any]:
    """Build the Arabic message to send to the customer with the payment link."""
    body_ar = (
        f"هلا {customer_name}،\n\n"
        f"تمام، نبدأ Pilot 7 أيام بـ{amount_sar} ريال.\n\n"
        "يشمل:\n"
        "• 10 فرص مناسبة\n"
        "• رسائل عربية جاهزة\n"
        "• فحص مخاطر القنوات\n"
        "• خطة متابعة 7 أيام\n"
        "• Proof Pack مختصر\n\n"
        f"رابط الدفع/الفاتورة: {invoice_url}\n\n"
        "بعد الدفع أحتاج منك:\n"
        "1. رابط موقعكم.\n"
        "2. القطاع المستهدف.\n"
        "3. المدينة.\n"
        "4. العرض الرئيسي.\n\n"
        "خلال 24 ساعة عمل بعد الدفع، أسلّمك أول دفعة من المخرجات.\n\nشاكر لك."
    )
    return {
        "channel": "email_or_whatsapp",
        "body_ar": body_ar,
        "amount_sar": amount_sar,
        "invoice_url": invoice_url,
        "approval_required": True,
        "live_send_allowed": False,
    }


def build_payment_confirmation_checklist() -> dict[str, Any]:
    """Checklist after the customer claims to have paid."""
    return {
        "title_ar": "تأكيد دفعة Moyasar",
        "checks_ar": [
            "افتح Moyasar dashboard → Invoices.",
            "تحقق أن invoice في حالة paid (وليس initiated أو failed).",
            "تطابق amount/currency مع الفاتورة الأصلية.",
            "سجّل في pipeline_tracker: stage=paid + price_sar.",
            "ابعث للعميل: تأكيد + intake form + موعد الكيك-أوف.",
            "ابدأ build_24h_delivery_plan.",
        ],
        "do_not_do_ar": [
            "لا تبدأ التسليم قبل تأكيد paid في Moyasar.",
            "لا تشارك invoice ID في القنوات العامة.",
        ],
        "approval_required": True,
    }

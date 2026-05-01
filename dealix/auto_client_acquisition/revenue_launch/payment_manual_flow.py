"""Manual Moyasar / invoice flow — no API charge inside Dealix."""

from __future__ import annotations

from typing import Any


def build_moyasar_invoice_instructions() -> dict[str, Any]:
    return {
        "steps_ar": [
            "سجّل الدخول إلى لوحة Moyasar (بيئة sandbox أو live حسب سياسة شركتك).",
            "أنشئ فاتورة أو رابط دفع بالمبلغ المتفق عليه (مثلاً ٤٩٩ ريال = ٤٩٩٠٠ هللة).",
            "أرسل الرابط للعميل عبر قناة موثوقة (إيميل أو رسالة يدوية).",
            "احتفظ بمرجع الدفع في pipeline_tracker يدوياً.",
        ],
        "amount_halalas_note_ar": "١ ريال = ١٠٠ هللة في واجهة Moyasar عادةً — راجع وثائق Moyasar الرسمية.",
        "no_live_charge": True,
        "manual_or_dashboard_only": True,
        "demo": True,
    }


def build_payment_link_message() -> dict[str, Any]:
    return {
        "template_ar": (
            "تمام، هذا رابط الدفع/الفاتورة لـ Pilot (٧ أيام — ٤٩٩ ريال). "
            "بعد إتمام الدفع أرسل لي رابط الموقع + القطاع + المدينة + العرض الرئيسي."
        ),
        "no_live_charge": True,
        "demo": True,
    }


def build_payment_confirmation_checklist() -> dict[str, Any]:
    return {
        "checklist_ar": [
            "تأكيد استلام المبلغ في Moyasar",
            "تسجيل paid في pipeline",
            "إرسال نموذج intake للعميل",
            "جدولة kickoff ٣٠ دقيقة",
        ],
        "demo": True,
    }

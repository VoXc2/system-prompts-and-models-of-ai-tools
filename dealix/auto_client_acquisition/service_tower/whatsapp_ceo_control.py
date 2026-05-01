"""WhatsApp CEO Control — كل القرارات بكروت عربية ≤3 أزرار."""

from __future__ import annotations

from typing import Any

from .service_catalog import get_service


def build_ceo_daily_service_brief() -> dict[str, Any]:
    """The daily service brief sent to the CEO via WhatsApp/Email."""
    return {
        "type": "ceo_daily_service_brief",
        "title_ar": "موجز الخدمات اليومي",
        "summary_ar": [
            "3 خدمات نشطة اليوم.",
            "5 رسائل drafts تنتظر اعتمادك.",
            "2 Free Diagnostic مكتمل وينتظر التسليم.",
            "1 شريك وكالة جاهز للعرض.",
            "0 مخاطر سمعة (الحالة صحية).",
        ],
        "buttons_ar": ["اعرض المسودات", "موافقة جماعية", "لاحقاً"],
        "approval_required": True,
    }


def build_service_approval_card(
    service_id: str, action: str,
) -> dict[str, Any]:
    """Approval card for a single service action (draft send / publish / charge)."""
    s = get_service(service_id)
    if s is None:
        return {"error": f"unknown service: {service_id}"}
    label_ar_by_action = {
        "send_email": "إرسال إيميل",
        "send_whatsapp": "إرسال واتساب",
        "insert_calendar": "إدراج موعد",
        "create_payment_link": "إنشاء رابط دفع",
        "publish_review_reply": "نشر رد تقييم",
        "share_diagnostic": "مشاركة Free Diagnostic",
    }
    return {
        "type": "service_approval",
        "service_id": service_id,
        "service_name_ar": s.name_ar,
        "action": action,
        "title_ar": f"اعتماد: {label_ar_by_action.get(action, action)}",
        "summary_ar": f"يتم تنفيذ هذا الفعل ضمن خدمة {s.name_ar}.",
        "risk_level": s.risk_level,
        "buttons_ar": ["اعتمد", "عدّل", "ارفض"],
        "approval_required": True,
        "live_send_allowed": False,
    }


def build_risk_alert_card() -> dict[str, Any]:
    """A risk alert card surfaced to the CEO."""
    return {
        "type": "risk_alert",
        "title_ar": "تنبيه مخاطر",
        "summary_ar": (
            "ارتفاع نسبة الـ bounce على الإيميل تجاوز الحد الآمن. "
            "اقتراح: إيقاف الحملات الجديدة 14 يوماً + تنظيف القائمة."
        ),
        "risk_level": "high",
        "buttons_ar": ["أوقف القناة", "خفّض الحجم", "تجاهل"],
        "approval_required": True,
    }


def build_end_of_day_service_report() -> dict[str, Any]:
    """End-of-day report on services run today."""
    return {
        "type": "end_of_day_service_report",
        "title_ar": "تقرير نهاية اليوم — الخدمات",
        "summary_ar": [
            "خدمات منفذة اليوم: 3.",
            "Drafts معتمدة: 6.",
            "ردود إيجابية: 2.",
            "اجتماعات مجدولة: 1.",
            "Pipeline متأثر: 24,000 ريال.",
            "مخاطر تم منعها: 8.",
        ],
        "next_day_focus_ar": (
            "غداً: تابع الردود الإيجابية، اعتمد رسائل Partner Sprint، "
            "سلّم 2 Free Diagnostic للعملاء الجدد."
        ),
    }

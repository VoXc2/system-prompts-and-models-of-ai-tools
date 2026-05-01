"""24-hour pilot delivery templates per service."""

from __future__ import annotations

from typing import Any


def build_client_intake_form() -> dict[str, Any]:
    """The single intake form sent to a customer after they pay."""
    return {
        "fields": [
            {"key": "company_name", "label_ar": "اسم الشركة", "required": True},
            {"key": "website", "label_ar": "رابط الموقع", "required": True},
            {"key": "sector", "label_ar": "القطاع", "required": True},
            {"key": "city", "label_ar": "المدينة", "required": True},
            {"key": "primary_offer", "label_ar": "العرض الرئيسي", "required": True},
            {"key": "ideal_customer", "label_ar": "العميل المثالي",
             "required": True},
            {"key": "avg_deal_value_sar", "label_ar": "متوسط قيمة الصفقة",
             "required": False},
            {"key": "has_contact_list", "label_ar": "هل عندكم قائمة عملاء؟",
             "required": True, "type": "boolean"},
            {"key": "channels_available", "label_ar": "القنوات المتاحة",
             "required": True, "type": "multi"},
            {"key": "whatsapp_opt_in_status",
             "label_ar": "حالة opt-in واتساب", "required": False},
            {"key": "approval_owner",
             "label_ar": "من يوافق على الرسائل قبل الإرسال؟",
             "required": True},
            {"key": "exclusions",
             "label_ar": "شركات أو أشخاص لا نتواصل معهم",
             "required": False, "type": "list"},
        ],
        "estimated_completion_minutes": 10,
        "approval_required": True,
    }


def build_24h_delivery_plan(service_id: str) -> dict[str, Any]:
    """Generic 24-hour delivery plan for any service."""
    return {
        "service_id": service_id,
        "phases": [
            {"phase": "T+0h", "label_ar": "كيك-أوف",
             "actions_ar": ["مراجعة intake + تأكيد القناة الأساسية"]},
            {"phase": "T+1h", "label_ar": "Diagnosis",
             "actions_ar": [
                 "تشغيل targeting/contactability على القائمة أو القطاع",
                 "تحديد buying committee + why-now",
             ]},
            {"phase": "T+6h", "label_ar": "Drafting",
             "actions_ar": [
                 "صياغة 10 رسائل عربية",
                 "تشغيل safety + Saudi tone evals على كل رسالة",
             ]},
            {"phase": "T+18h", "label_ar": "Approval Pack",
             "actions_ar": [
                 "إرسال drafts للعميل في approval cards (≤3 أزرار لكل بطاقة)",
                 "تحديث Action Ledger",
             ]},
            {"phase": "T+24h", "label_ar": "Proof Pack v1",
             "actions_ar": [
                 "تسليم Proof Pack المختصر",
                 "حجز جلسة مراجعة 30 دقيقة في نهاية الأسبوع",
             ]},
        ],
        "approval_required": True,
        "live_send_allowed": False,
    }


def build_first_10_opportunities_delivery(intake: dict[str, Any]) -> dict[str, Any]:
    """Service-specific delivery for First 10 Opportunities Sprint."""
    return {
        "service_id": "first_10_opportunities_sprint",
        "intake_received": bool(intake),
        "delivery_steps_ar": [
            "تشغيل account_finder على (sector, city) + offer.",
            "buyer_role_mapper لكل شركة → 1 DM + 2 influencers.",
            "explain_why_now لكل شركة (Arabic).",
            "draft_b2b_email و/أو draft_whatsapp_message حسب القناة.",
            "safety_eval + saudi_tone_eval على كل رسالة قبل التسليم.",
            "بناء follow-up sequence لـ7 أيام.",
            "Proof Pack v1 (PDF + JSON).",
        ],
        "deliverables": [
            "10 opportunity cards",
            "10 Arabic messages",
            "follow-up plan",
            "Proof Pack v1",
        ],
        "approval_required": True,
    }


def build_list_intelligence_delivery(intake: dict[str, Any]) -> dict[str, Any]:
    """Service-specific delivery for List Intelligence."""
    return {
        "service_id": "list_intelligence",
        "intake_received": bool(intake),
        "delivery_steps_ar": [
            "تنظيف الـ CSV + dedupe.",
            "classify_source لكل صف.",
            "evaluate_contactability + allowed_channels لكل contact.",
            "تقسيم القائمة: safe / needs_review / blocked.",
            "اختيار أفضل 50 target.",
            "كتابة رسائل عربية للقطاع المهيمن.",
            "Risk report + retention recommendation.",
        ],
        "deliverables": [
            "Cleaned CSV",
            "Top 50 targets",
            "Arabic messages per segment",
            "Risk report",
            "Channel mix recommendation",
        ],
        "approval_required": True,
    }


def build_growth_diagnostic_delivery(intake: dict[str, Any]) -> dict[str, Any]:
    """Free 24-hour growth diagnostic delivery."""
    return {
        "service_id": "free_growth_diagnostic",
        "intake_received": bool(intake),
        "delivery_steps_ar": [
            "تشغيل recommend_accounts(sector, city) → 3 فرص.",
            "كتابة رسالة عربية واحدة جاهزة.",
            "تقرير risk سريع (واتساب opt-in / domain reputation / channel mix).",
            "توصية بالخدمة المدفوعة الأنسب (Pilot 499 / Growth OS Pilot).",
        ],
        "deliverables": [
            "3 opportunities",
            "1 Arabic message",
            "Risk note",
            "Paid pilot recommendation",
        ],
        "delivery_time": "خلال 24 ساعة عمل",
        "approval_required": True,
    }

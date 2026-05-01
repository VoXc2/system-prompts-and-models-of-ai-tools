"""Pilot delivery checklist — deterministic templates."""

from __future__ import annotations

from typing import Any


def build_client_intake_form() -> dict[str, Any]:
    return {
        "fields": [
            "company_name",
            "website_url",
            "sector",
            "city",
            "main_offer",
            "ideal_customer",
            "avg_deal_value_sar",
            "has_contact_list",
            "available_channels",
            "whatsapp_opt_in_status",
            "approver_name",
        ],
        "note_ar": "لا تُخزَّن أسرار في هذا النموذج التجريبي — استخدم قنوات آمنة لجمع البيانات.",
        "demo": True,
    }


def build_24h_delivery_plan() -> dict[str, Any]:
    return {
        "hours": [
            {"h": "0-4", "task_ar": "جمع المدخلات والتحقق من القنوات المسموحة."},
            {"h": "4-12", "task_ar": "توليد فرص ومسودات (عرض داخلي للمراجعة)."},
            {"h": "12-20", "task_ar": "تشغيل contactability وتقرير مخاطر."},
            {"h": "20-24", "task_ar": "تسليم حزمة أولية + موعد مراجعة مع العميل."},
        ],
        "demo": True,
    }


def build_first_10_opportunities_delivery() -> dict[str, Any]:
    return {
        "deliverables_ar": [
            "١٠ فرص مع لماذا الآن",
            "١٠ رسائل عربية (مسودات)",
            "توصية قناة لكل فرصة",
            "خطة متابعة ٧ أيام",
        ],
        "approval_required": True,
        "demo": True,
    }


def build_list_intelligence_delivery() -> dict[str, Any]:
    return {
        "deliverables_ar": [
            "تقرير تنظيف وتصنيف مصدر",
            "أفضل ٥٠ هدفاً (تجريبي)",
            "مسودات رسائل للآمن فقط",
            "تقرير مخاطر",
        ],
        "approval_required": True,
        "demo": True,
    }


def build_growth_diagnostic_delivery() -> dict[str, Any]:
    return {
        "deliverables_ar": ["٣ فرص", "١ رسالة", "١ ملاحظة مخاطر", "١ توصية خدمة مدفوعة"],
        "approval_required": False,
        "demo": True,
    }

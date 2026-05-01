"""Pre-meeting brief from company/contact context."""

from __future__ import annotations

from typing import Any


def build_pre_meeting_brief(
    company: dict[str, Any] | None = None,
    contact: dict[str, Any] | None = None,
    opportunity: dict[str, Any] | None = None,
) -> dict[str, Any]:
    c = company or {}
    p = contact or {}
    o = opportunity or {}
    return {
        "company_ar": str(c.get("name") or c.get("company_name") or "الشركة"),
        "contact_ar": str(p.get("name") or "جهة الاتصال"),
        "objective_ar": str(o.get("objective_ar") or "مناقشة ملاءمة الحل والخطوة التالية."),
        "questions_ar": [
            "ما معيار القرار والجدول الزمني؟",
            "ما أكبر مخاطرة يرونها اليوم؟",
            "ما الشكل المثالي للتجربة خلال ٧ أيام؟",
            "ما الميزانية أو نطاقها التقريبي؟",
            "من يشارك من جانبهم في التنفيذ؟",
        ],
        "likely_objections_ar": ["السعر", "التوقيت", "التكامل مع الأنظمة الحالية"],
        "demo": True,
    }

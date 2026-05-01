"""12-minute demo script structure for founders."""

from __future__ import annotations

from typing import Any


def build_demo_script() -> dict[str, Any]:
    return {
        "duration_minutes": 12,
        "sections": [
            {
                "minute_range": "0-2",
                "title_ar": "المشكلة والوعد",
                "talking_points_ar": [
                    "Dealix ليس CRM ولا بوت واتساب فقط.",
                    "نحوّل الإشارات إلى قرار يومي عربي + موافقة + Proof.",
                ],
            },
            {
                "minute_range": "2-4",
                "title_ar": "Daily Brief",
                "api_hint": "GET /api/v1/personal-operator/daily-brief",
                "talking_points_ar": ["٣ قرارات", "مخاطر", "جاهزية"],
            },
            {
                "minute_range": "4-6",
                "title_ar": "Growth Operator / ١٠ فرص",
                "api_hint": "GET /api/v1/growth-operator/missions",
                "talking_points_ar": ["لماذا الآن", "Accept/Skip", "لا cold WhatsApp"],
            },
            {
                "minute_range": "6-8",
                "title_ar": "Inbox ومنصة",
                "api_hint": "GET /api/v1/platform/inbox/feed",
                "talking_points_ar": ["كروت عربية", "موافقة قبل الإرسال"],
            },
            {
                "minute_range": "8-10",
                "title_ar": "برج الخدمات",
                "api_hint": "GET /api/v1/services/catalog",
                "talking_points_ar": ["تشخيص", "قوائم", "Growth OS", "أسعار تقديرية"],
            },
            {
                "minute_range": "10-12",
                "title_ar": "Pilot وProof",
                "talking_points_ar": ["٧ أيام أو ٣٠ يوم", "Proof Pack", "الخطوة التالية"],
            },
        ],
        "closing_line_ar": "لا نعد نتائج مضمونة — نعد مسودات وموافقات وتقارير قياس.",
        "demo": True,
    }

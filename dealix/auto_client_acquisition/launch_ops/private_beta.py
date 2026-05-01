"""Private beta commercial offer — deterministic copy."""

from __future__ import annotations

from typing import Any


def build_private_beta_offer() -> dict[str, Any]:
    return {
        "title_ar": "Dealix — البيتا الخاصة",
        "tagline_ar": "مدير نمو عربي: فرص، مسودات، موافقة، Proof — بدون إرسال حي افتراضياً.",
        "included_ar": [
            "تشخيص نمو مجاني أو مدفوع حسب الاتفاق",
            "سباق ١٠ فرص أو ذكاء قائمة (حسب الحالة)",
            "كروت موافقة عربية (أزرار ≤٣)",
            "Proof Pack أسبوعي تجريبي",
        ],
        "excluded_ar": [
            "إرسال واتساب جماعي بارد",
            "Gmail إرسال تلقائي",
            "إدراج تقويم حي بدون موافقة",
            "شحن بطاقات داخل Dealix",
        ],
        "pilot_pricing_sar": {"low": 499, "high": 3000, "note_ar": "٧ أيام أو ٣٠ يوم — حسب النطاق"},
        "monthly_after_sar": {"low": 2999, "high": 9999},
        "live_send_default": False,
        "demo": True,
    }

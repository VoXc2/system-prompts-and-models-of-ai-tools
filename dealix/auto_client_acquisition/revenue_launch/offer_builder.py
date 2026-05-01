"""Structured commercial offers — deterministic, no payment execution."""

from __future__ import annotations

from typing import Any


def build_private_beta_offer() -> dict[str, Any]:
    return {
        "offer_id": "private_beta_shell",
        "title_ar": "البيتا الخاصة — Dealix",
        "summary_ar": "Pilot محدود: فرص، مسودات، موافقة، Proof — بدون إرسال حي افتراضياً.",
        "price_sar": None,
        "includes_ar": ["تشخيص أو سباق فرص", "كروت موافقة", "Proof Pack تجريبي"],
        "no_live_send": True,
        "demo": True,
    }


def build_499_pilot_offer() -> dict[str, Any]:
    return {
        "offer_id": "pilot_7d_499",
        "title_ar": "Pilot — ٧ أيام (٤٩٩ ريال)",
        "price_sar": 499,
        "duration_days": 7,
        "deliverables_ar": [
            "تشخيص نمو مختصر أو ٣ فرص عينة",
            "١٠ فرص B2B مع لماذا الآن",
            "١٠ رسائل عربية (مسودات)",
            "فحص قابلية التواصل والمخاطر",
            "خطة متابعة ٧ أيام",
            "Proof Pack مختصر",
        ],
        "payment_ar": "فاتورة أو رابط دفع يدوي عبر Moyasar (لوحة التحكم) — لا charge من API داخل Dealix في هذه المرحلة.",
        "no_live_charge": True,
        "no_live_send": True,
        "demo": True,
    }


def build_growth_os_pilot_offer() -> dict[str, Any]:
    return {
        "offer_id": "growth_os_pilot_30d",
        "title_ar": "Growth OS Pilot — ٣٠ يوم",
        "price_range_sar": {"min": 1500, "max": 3000},
        "duration_days": 30,
        "deliverables_ar": [
            "موجز يومي تجريبي",
            "١٠ فرص + ذكاء قوائم حسب الحالة",
            "مسودات قنوات (بدون إرسال حي)",
            "Proof Pack أسبوعي",
        ],
        "no_live_charge": True,
        "no_live_send": True,
        "demo": True,
    }


def build_case_study_free_offer() -> dict[str, Any]:
    return {
        "offer_id": "pilot_free_case_study",
        "title_ar": "Pilot مجاني مقابل Case Study",
        "price_sar": 0,
        "conditions_ar": [
            "موافقة على نشر نتائج معممة بدون بيانات حساسة",
            "مقابلة قصيرة بعد الأسبوع",
        ],
        "no_live_send": True,
        "demo": True,
    }


def recommend_offer_for_segment(segment: str) -> dict[str, Any]:
    s = (segment or "").strip().lower()
    if s in ("agency", "وكالة"):
        return {"recommended": "growth_os_pilot_30d", "reason_ar": "وكالات غالباً تحتاج نطاق أوسع وتقارير لعملاء.", "demo": True}
    if s in ("founder", "مؤسس", "b2b"):
        return {"recommended": "pilot_7d_499", "reason_ar": "أسرع إثبات قيمة لشركة واحدة.", "demo": True}
    return {"recommended": "pilot_7d_499", "reason_ar": "افتراضي آمن للبيع السريع.", "demo": True}

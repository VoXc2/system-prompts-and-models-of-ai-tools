"""Today's paid offers — 499 Pilot, Growth OS Pilot, free case study."""

from __future__ import annotations

from typing import Any


def build_499_pilot_offer() -> dict[str, Any]:
    """The headline 499 SAR Pilot — Dealix's revenue funnel entry."""
    return {
        "offer_id": "pilot_499_7d",
        "name_ar": "Pilot 7 أيام — 499 ريال",
        "promise_ar": (
            "خلال 7 أيام: 10 فرص B2B + رسائل عربية + خطة متابعة + Proof Pack."
        ),
        "deliverables_ar": [
            "10 فرص مرتبة بـ fit_score",
            "10 رسائل عربية بنبرة سعودية",
            "تصنيف القنوات (safe / needs_review / blocked)",
            "خطة متابعة 7 أيام",
            "Proof Pack مختصر (PDF + JSON)",
            "جلسة مراجعة 30 دقيقة في نهاية الأسبوع",
        ],
        "price_sar": 499,
        "duration_days": 7,
        "approval_required": True,
        "live_send_allowed": False,
        "no_live_charge": True,
        "payment_method": "moyasar_invoice_or_payment_link",
        "delivery_starts": "next_sunday_after_payment",
    }


def build_growth_os_pilot_offer() -> dict[str, Any]:
    """30-day Growth OS Pilot — for serious customers."""
    return {
        "offer_id": "growth_os_pilot_30d",
        "name_ar": "Growth OS Pilot — 30 يوم",
        "promise_ar": (
            "تشغيل يومي للنمو لمدة شهر: command feed + drafts + اجتماعات + Proof Pack."
        ),
        "deliverables_ar": [
            "Daily growth brief عربي",
            "First 10 Opportunities Sprint",
            "List Intelligence على قائمة العميل",
            "Email/WhatsApp drafts (بدون live send)",
            "Meeting drafts على Calendar",
            "Weekly Proof Pack",
            "تحويل لـ Growth OS Monthly بعد الإثبات",
        ],
        "price_sar_min": 1500,
        "price_sar_max": 3000,
        "duration_days": 30,
        "approval_required": True,
        "no_live_charge": True,
        "payment_method": "moyasar_invoice_or_payment_link",
    }


def build_case_study_free_offer() -> dict[str, Any]:
    """Free Pilot in exchange for a case study + permission to publish."""
    return {
        "offer_id": "case_study_free_7d",
        "name_ar": "Pilot مجاني مقابل case study",
        "promise_ar": (
            "نسلّم Pilot 7 أيام مجاناً، وأنت تعطينا تصريحاً بنشر case study بدون "
            "بيانات حساسة."
        ),
        "eligibility_ar": [
            "شركة سعودية أو خليجية",
            "حجم متوسط (≥10 موظفين)",
            "قرار سريع (مدير مفوّض على الرد)",
            "موافقة كتابية على نشر النتائج بدون بيانات حساسة",
        ],
        "price_sar": 0,
        "case_study_required": True,
        "approval_required": True,
        "no_live_charge": True,
    }


def build_private_beta_offer() -> dict[str, Any]:
    """Re-export the Private Beta offer (single source of truth)."""
    from auto_client_acquisition.launch_ops import PRIVATE_BETA_OFFER
    return dict(PRIVATE_BETA_OFFER)


def recommend_offer_for_segment(segment_id: str) -> dict[str, Any]:
    """Map outreach segment → best-fit paid offer."""
    s = (segment_id or "").lower().strip()

    if s == "agency_b2b":
        return {
            "primary_offer": "growth_os_pilot_30d",
            "fallback_offer": "case_study_free_7d",
            "reason_ar": (
                "وكالة → Growth OS Pilot يعطيها revenue share واضح. "
                "إذا ترددت، اعرض free case study."
            ),
        }
    if s == "training_consulting":
        return {
            "primary_offer": "pilot_499_7d",
            "fallback_offer": "case_study_free_7d",
            "reason_ar": (
                "تدريب/استشارات → Pilot 499 سريع. "
                "free case study للأسماء البارزة."
            ),
        }
    if s == "saas_tech_small":
        return {
            "primary_offer": "pilot_499_7d",
            "fallback_offer": "growth_os_pilot_30d",
            "reason_ar": (
                "SaaS صغيرة → Pilot 499 يكسر الجليد + ترقية لـ Growth OS Pilot."
            ),
        }
    if s == "services_with_whatsapp":
        return {
            "primary_offer": "pilot_499_7d",
            "fallback_offer": "case_study_free_7d",
            "reason_ar": (
                "خدمات بقاعدة واتساب → Pilot 499 ثم WhatsApp Compliance Setup."
            ),
        }

    return {
        "primary_offer": "pilot_499_7d",
        "fallback_offer": "case_study_free_7d",
        "reason_ar": "افتراضي: Pilot 499.",
    }

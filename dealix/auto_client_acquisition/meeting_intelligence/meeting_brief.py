"""Pre-meeting brief builder — deterministic Arabic output."""

from __future__ import annotations

from typing import Any


def build_pre_meeting_brief(
    *,
    company: dict[str, Any] | None = None,
    contact: dict[str, Any] | None = None,
    opportunity: dict[str, Any] | None = None,
    sector: str | None = None,
) -> dict[str, Any]:
    """
    Build a 6-section Arabic pre-meeting brief.

    All inputs are optional; the brief degrades to a generic but useful template.
    """
    company = company or {}
    contact = contact or {}
    opportunity = opportunity or {}
    sector = sector or str(company.get("sector", "saas"))

    company_name = company.get("name", "?")
    contact_name = contact.get("name", "?")
    contact_role = contact.get("role", "?")
    deal_value = opportunity.get("expected_value_sar", 0)

    objective_ar = (
        f"توضيح ملاءمة الحل لشركة {company_name}، "
        f"وفهم المعيار الذي يستخدمه {contact_name} للقرار، "
        "ثم تحديد خطوة تالية واضحة."
    )

    questions_ar = [
        f"كيف تتعاملون اليوم مع [مشكلة قطاع {sector}]؟",
        "ما الذي جعلكم تنظرون لحل الآن وليس قبل 6 أشهر؟",
        "من المسؤول عن قرار الشراء غيرك؟",
        "ما المعيار الذي يجعلكم تقولون: نعم، خلونا نبدأ؟",
        "ما الميزانية التقريبية المخصصة لهذه المشكلة؟",
    ]

    likely_objections_ar = [
        "السعر مرتفع مقارنة بالأدوات المحلية.",
        "نحن مرتبطون بـ CRM/أداة حالية ولا نريد التبديل.",
        "نحتاج تجربة فريق صغير أولاً قبل القرار.",
        "هل الحل متوافق مع PDPL ولا يخزن بياناتنا خارج المملكة؟",
        "كم يستغرق الإعداد فعلياً؟",
    ]

    offer_skeleton_ar = (
        f"عرض pilot لمدة 7 أيام لشركة {company_name}: "
        "10 فرص B2B + رسائل عربية + متابعة + Proof Pack. "
        "السعر 499 ريال أو مجاني مقابل case study."
    )

    next_step_ar = (
        "في نهاية المكالمة: اقترح خطوة محددة بتاريخ — "
        "إما الموافقة على بدء Pilot، أو إعادة الاجتماع خلال 5 أيام مع صانع القرار."
    )

    return {
        "company_name": company_name,
        "contact_name": contact_name,
        "contact_role": contact_role,
        "expected_value_sar": deal_value,
        "objective_ar": objective_ar,
        "questions_ar": questions_ar,
        "likely_objections_ar": likely_objections_ar,
        "offer_skeleton_ar": offer_skeleton_ar,
        "next_step_ar": next_step_ar,
        "approval_required": True,
    }

"""Contract draft outlines — Arabic skeletons; legal review required."""

from __future__ import annotations

from typing import Any


_DISCLAIMER_AR = (
    "هذه مسودة هيكلية فقط، ليست استشارة قانونية. "
    "لا تُوقَّع قبل مراجعة محامٍ مرخّص في المملكة العربية السعودية."
)


def draft_pilot_agreement_outline() -> dict[str, Any]:
    """Pilot Agreement outline (Arabic skeleton)."""
    return {
        "title_ar": "اتفاقية تجربة Pilot لخدمة Dealix",
        "sections_ar": [
            "الأطراف والتعريفات.",
            "نطاق الـ Pilot ومدته (7 أيام).",
            "المدخلات المطلوبة من العميل.",
            "المخرجات المُتفق عليها (10 فرص + رسائل + Proof Pack).",
            "السرية وعدم استخدام بيانات العميل لأغراض أخرى.",
            "PDPL وحقوق الموضوعات (الأشخاص).",
            "السعر وطريقة الدفع (Pilot أو case study).",
            "إنهاء الاتفاقية والاستمرارية.",
            "حدود المسؤولية.",
            "القانون الواجب التطبيق والاختصاص.",
        ],
        "approval_required": True,
        "legal_review_required": True,
        "not_legal_advice": True,
        "disclaimer_ar": _DISCLAIMER_AR,
    }


def draft_dpa_outline() -> dict[str, Any]:
    """Data Processing Addendum outline (Arabic skeleton, PDPL-aware)."""
    return {
        "title_ar": "ملحق معالجة البيانات (DPA)",
        "sections_ar": [
            "التعريفات حسب نظام حماية البيانات الشخصية السعودي (PDPL).",
            "أدوار الأطراف (Controller / Processor).",
            "أنواع البيانات والـ subjects.",
            "أغراض المعالجة.",
            "الإجراءات الأمنية المطبّقة.",
            "نقل البيانات خارج المملكة (إن وُجد).",
            "الاحتفاظ والإتلاف.",
            "حقوق الموضوعات (طلبات الوصول/التصحيح/الحذف).",
            "خرق البيانات والإبلاغ.",
            "الـ subprocessors المعتمدون.",
            "التدقيق والامتثال.",
        ],
        "approval_required": True,
        "legal_review_required": True,
        "not_legal_advice": True,
        "disclaimer_ar": _DISCLAIMER_AR,
    }


def draft_referral_agreement_outline() -> dict[str, Any]:
    """Referral Agreement outline."""
    return {
        "title_ar": "اتفاقية إحالة (Referral)",
        "sections_ar": [
            "تعريف الـ Referrer والإحالة المؤهلة.",
            "نموذج الـ revenue share (نسبة + مدة).",
            "شروط الدفع وتاريخ الاستحقاق.",
            "السرية.",
            "عدم الإغراء (no-poach اختيارية).",
            "سياسات PDPL لمشاركة بيانات الـ leads.",
            "إنهاء الاتفاقية.",
        ],
        "approval_required": True,
        "legal_review_required": True,
        "not_legal_advice": True,
        "disclaimer_ar": _DISCLAIMER_AR,
    }


def draft_agency_partner_outline() -> dict[str, Any]:
    """Agency Partner Agreement outline (white-label/co-branded)."""
    return {
        "title_ar": "اتفاقية شريك وكالة لـ Dealix",
        "sections_ar": [
            "هيكل الشراكة (revenue share / setup fee / co-branding).",
            "نطاق الخدمات المقدّمة من الوكالة لعملائها.",
            "Proof Packs مشتركة العلامة.",
            "حقوق الملكية الفكرية.",
            "السرية والـ NDAs.",
            "PDPL ونقل البيانات بين Dealix والوكالة.",
            "حدود المسؤولية والـ SLA.",
            "إنهاء الاتفاقية وتسليم العملاء.",
        ],
        "approval_required": True,
        "legal_review_required": True,
        "not_legal_advice": True,
        "disclaimer_ar": _DISCLAIMER_AR,
    }


def draft_scope_of_work() -> dict[str, Any]:
    """Generic Scope-of-Work outline."""
    return {
        "title_ar": "نطاق العمل (SOW)",
        "sections_ar": [
            "ملخص الخدمة.",
            "المدخلات المطلوبة من العميل.",
            "المخرجات والـ deliverables.",
            "الجدول الزمني والـ milestones.",
            "المسؤوليات والـ approvals.",
            "السعر وطريقة الدفع.",
            "حدود نطاق العمل وما خارجه.",
            "تغييرات النطاق (Change Requests).",
            "معايير القبول (Acceptance Criteria).",
        ],
        "approval_required": True,
        "legal_review_required": True,
        "not_legal_advice": True,
        "disclaimer_ar": _DISCLAIMER_AR,
    }

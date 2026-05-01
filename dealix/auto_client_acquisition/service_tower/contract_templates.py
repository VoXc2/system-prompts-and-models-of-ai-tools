"""Service-tier contract templates — re-export from targeting_os and add SLA."""

from __future__ import annotations

from typing import Any

from auto_client_acquisition.targeting_os.contract_drafts import (
    draft_agency_partner_outline,
    draft_dpa_outline,
    draft_pilot_agreement_outline,
    draft_referral_agreement_outline,
    draft_scope_of_work,
)


def list_contract_templates() -> dict[str, Any]:
    """List all contract templates available to the Service Tower."""
    return {
        "templates": [
            {"id": "pilot_agreement", **draft_pilot_agreement_outline()},
            {"id": "dpa", **draft_dpa_outline()},
            {"id": "referral", **draft_referral_agreement_outline()},
            {"id": "agency_partner", **draft_agency_partner_outline()},
            {"id": "sow", **draft_scope_of_work()},
            {"id": "sla", **draft_sla_outline()},
        ],
        "approval_required": True,
        "legal_review_required": True,
        "not_legal_advice": True,
    }


def draft_sla_outline() -> dict[str, Any]:
    """Service Level Agreement outline for paid pilots and Growth OS Monthly."""
    return {
        "title_ar": "اتفاقية مستوى الخدمة (SLA)",
        "sections_ar": [
            "نطاق الخدمة (الـ Pilot أو Growth OS).",
            "أوقات الاستجابة (intake خلال 30 دقيقة، diagnostic خلال 24 ساعة).",
            "أوقات التسليم لكل deliverable.",
            "حدود التوفر (أيام العمل، Time Zone).",
            "المسارات في حالة التأخير (escalation).",
            "حقوق العميل عند عدم الالتزام (refund / extension).",
            "حدود المسؤولية.",
            "السرية.",
            "PDPL والاحتفاظ بالبيانات.",
            "التغييرات في النطاق.",
            "إنهاء الاتفاقية.",
        ],
        "approval_required": True,
        "legal_review_required": True,
        "not_legal_advice": True,
        "disclaimer_ar": (
            "هذه مسودة هيكلية فقط، ليست استشارة قانونية. "
            "لا تُوقَّع قبل مراجعة محامٍ مرخّص في المملكة العربية السعودية."
        ),
    }


__all__ = [
    "draft_agency_partner_outline",
    "draft_dpa_outline",
    "draft_pilot_agreement_outline",
    "draft_referral_agreement_outline",
    "draft_scope_of_work",
    "draft_sla_outline",
    "list_contract_templates",
]

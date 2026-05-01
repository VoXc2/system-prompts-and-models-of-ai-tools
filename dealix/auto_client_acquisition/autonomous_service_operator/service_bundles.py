"""Productized service bundles — SAR ranges and catalog service_ids."""

from __future__ import annotations

from typing import Any

BundleId = str

_BUNDLES: dict[BundleId, dict[str, Any]] = {
    "growth_starter": {
        "bundle_id": "growth_starter",
        "title_ar": "Growth Starter",
        "services": ["free_growth_diagnostic", "first_10_opportunities"],
        "timeline_days": 14,
        "price_range_sar": {"min": 499, "max": 499},
        "best_for_ar": "شركات تريد أول قيمة سريعة + Pilot واضح.",
        "deliverables_ar": ["تشخيص مجاني", "١٠ فرص + مسودات", "Proof Pack مختصر"],
        "proof_metrics": ["opportunities_count", "drafts_created", "approvals_logged"],
        "risk_policy_ar": "لا إرسال حي بدون موافقة؛ لا واتساب بارد.",
        "upsell_path": "data_to_revenue",
    },
    "data_to_revenue": {
        "bundle_id": "data_to_revenue",
        "title_ar": "من البيانات إلى الإيراد",
        "services": ["list_intelligence", "first_10_opportunities"],
        "timeline_days": 21,
        "price_range_sar": {"min": 1500, "max": 2500},
        "best_for_ar": "من لديه قائمة جهات ويريد أهدافاً مرتبة ومسودات.",
        "deliverables_ar": ["أفضل ٥٠ هدفاً", "تقرير قابلية تواصل", "مسودات رسائل"],
        "proof_metrics": ["safe_ratio", "drafts_created", "target_ranked"],
        "risk_policy_ar": "مسودات فقط؛ موافقة قبل أي إرسال.",
        "upsell_path": "executive_growth_os",
    },
    "executive_growth_os": {
        "bundle_id": "executive_growth_os",
        "title_ar": "Executive Growth OS",
        "services": ["executive_growth_brief", "growth_os"],
        "timeline_days": 30,
        "price_range_sar": {"min": 2999, "max": 9999},
        "best_for_ar": "CEO ومدير نمو يريدان موجزاً يومياً وتشغيل Growth OS.",
        "deliverables_ar": ["موجز يومي", "Command feed", "Proof Pack أسبوعي"],
        "proof_metrics": ["decisions_logged", "revenue_influenced_sar", "risks_blocked"],
        "risk_policy_ar": "بوابة أدوات آمنة؛ تكاملات مسودة افتراضياً.",
        "upsell_path": "full_growth_control_tower",
    },
    "partnership_growth": {
        "bundle_id": "partnership_growth",
        "title_ar": "نمو عبر الشراكات",
        "services": ["partner_sprint", "meeting_booking_sprint"],
        "timeline_days": 30,
        "price_range_sar": {"min": 3000, "max": 7500},
        "best_for_ar": "توسع عبر شركاء ووكالات.",
        "deliverables_ar": ["قائمة شركاء", "مسودات اجتماعات", "مسودة اتفاق إحالة"],
        "proof_metrics": ["partner_meetings", "referral_pipeline"],
        "risk_policy_ar": "مراجعة قانونية للاتفاقيات.",
        "upsell_path": "agency_partner_program",
    },
    "local_growth_os": {
        "bundle_id": "local_growth_os",
        "title_ar": "نمو محلي",
        "services": ["local_growth_os"],
        "timeline_days": 30,
        "price_range_sar": {"min": 999, "max": 2999},
        "best_for_ar": "عيادات ومطاعم ومتاجر محلية.",
        "deliverables_ar": ["كروت سمعة", "مسودات رد", "روابط دفع draft"],
        "proof_metrics": ["reviews_addressed", "reactivation_drafts"],
        "risk_policy_ar": "موافقة على الرسائل العامة.",
        "upsell_path": "growth_os",
    },
    "full_growth_control_tower": {
        "bundle_id": "full_growth_control_tower",
        "title_ar": "برج تحكم كامل — مخصص",
        "services": ["growth_os", "agency_partner_program"],
        "timeline_days": 90,
        "price_range_sar": {"min": 15000, "max": 80000},
        "best_for_ar": "مؤسسات تريد كل الطبقات على مراحل.",
        "deliverables_ar": ["خارطة ٣٠/٦٠/٩٠ يوماً", "حوكمة موافقات", "Proof شهري"],
        "proof_metrics": ["pipeline_influenced", "partners_created", "payments_requested"],
        "risk_policy_ar": "DPA + مراجعة امتثال قبل التوسع.",
        "upsell_path": None,
    },
}


def list_bundles() -> dict[str, Any]:
    return {"bundles": list(_BUNDLES.values()), "demo": True}


def get_bundle(bundle_id: str) -> dict[str, Any] | None:
    return _BUNDLES.get((bundle_id or "").strip())

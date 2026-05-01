"""Service bundles — 6 packaged offerings instead of 20 raw services."""

from __future__ import annotations

from typing import Any

# 6 bundles that simplify the customer's choice.
BUNDLES: tuple[dict[str, Any], ...] = (
    {
        "id": "growth_starter",
        "name_ar": "Growth Starter",
        "best_for_ar": "أي شركة تجرب Dealix لأول مرة",
        "services": [
            "free_growth_diagnostic",
            "first_10_opportunities_sprint",
        ],
        "deliverables_ar": [
            "تشخيص نمو مجاني خلال 24 ساعة",
            "10 فرص + رسائل عربية",
            "Proof Pack مختصر",
        ],
        "timeline_ar": "8 أيام (1 ديمو + 7 Pilot)",
        "price_min_sar": 499,
        "price_max_sar": 1500,
        "proof_metrics": [
            "opportunities_count", "drafts_approved",
            "positive_replies", "diagnostic_to_paid_conversion",
        ],
        "upgrade_path": ["executive_growth_os"],
    },
    {
        "id": "data_to_revenue",
        "name_ar": "Data to Revenue",
        "best_for_ar": "شركات لديها قائمة عملاء/أرقام لم تُستثمر",
        "services": [
            "list_intelligence",
            "first_10_opportunities_sprint",
        ],
        "deliverables_ar": [
            "قائمة منظفة + تصنيف مصادر",
            "أفضل 50 target بالقنوات الآمنة",
            "رسائل عربية لكل segment",
            "Risk report + retention",
        ],
        "timeline_ar": "10 أيام",
        "price_min_sar": 1500,
        "price_max_sar": 3000,
        "proof_metrics": [
            "contacts_classified", "safe_targets_found",
            "risks_blocked", "pipeline_influenced_sar",
        ],
        "upgrade_path": ["executive_growth_os"],
    },
    {
        "id": "executive_growth_os",
        "name_ar": "Executive Growth OS",
        "best_for_ar": "CEO / Growth Manager — تشغيل شهري",
        "services": [
            "growth_os_monthly",
            "executive_growth_brief",
        ],
        "deliverables_ar": [
            "Daily Command Feed عربي",
            "Approval Center عبر واتساب",
            "First 10 Opportunities أسبوعياً",
            "Proof Pack شهري",
            "Founder Shadow Board أسبوعي",
            "Revenue Leak Detector",
        ],
        "timeline_ar": "شهري متجدد (ابدأ بـPilot 30 يوم)",
        "price_min_sar": 2999,
        "price_max_sar": 2999,
        "proof_metrics": [
            "monthly_pipeline_sar", "monthly_meetings",
            "monthly_revenue_influenced", "monthly_risks_blocked",
        ],
        "upgrade_path": ["partnership_growth", "full_growth_control_tower"],
    },
    {
        "id": "partnership_growth",
        "name_ar": "Partnership Growth",
        "best_for_ar": "شركات تنمو عبر الشركاء/الوكالات/الموزعين",
        "services": [
            "partner_sprint",
            "meeting_booking_sprint",
        ],
        "deliverables_ar": [
            "20 شريك محتمل + scorecard",
            "10 رسائل + drafts اجتماعات",
            "Referral Agreement Draft",
            "Partner-Proof Pack",
        ],
        "timeline_ar": "14 يوم",
        "price_min_sar": 3000,
        "price_max_sar": 7500,
        "proof_metrics": [
            "partners_identified", "partner_meetings",
            "referral_revenue_sar",
        ],
        "upgrade_path": ["full_growth_control_tower"],
    },
    {
        "id": "local_growth_os",
        "name_ar": "Local Growth OS",
        "best_for_ar": "عيادات / متاجر / فروع / خدمات محلية",
        "services": [
            "local_growth_os",
            "whatsapp_compliance_setup",
            "list_intelligence",
        ],
        "deliverables_ar": [
            "Google Business reviews ledger + draft replies",
            "WhatsApp opt-in audit + templates",
            "Customer reactivation campaign drafts",
            "Branch-level Proof Pack",
        ],
        "timeline_ar": "3 أسابيع",
        "price_min_sar": 999,
        "price_max_sar": 2999,
        "proof_metrics": [
            "reviews_handled", "opt_ins_collected",
            "customers_reactivated", "risks_blocked",
        ],
        "upgrade_path": ["executive_growth_os"],
    },
    {
        "id": "full_growth_control_tower",
        "name_ar": "Full Growth Control Tower",
        "best_for_ar": "مؤسسات تريد تشغيل كامل على 30+ يوم",
        "services": [
            "growth_os_monthly",
            "list_intelligence",
            "first_10_opportunities_sprint",
            "partner_sprint",
            "executive_growth_brief",
            "linkedin_lead_gen_setup",
        ],
        "deliverables_ar": [
            "كل خدمات Growth OS",
            "Partnership Sprint موازٍ",
            "LinkedIn Lead Gen campaign",
            "Founder Shadow Board",
            "Service Excellence weekly review",
        ],
        "timeline_ar": "30 يوم — قابل للتجديد",
        "price_min_sar": 12000,
        "price_max_sar": 25000,
        "proof_metrics": [
            "monthly_pipeline_sar", "monthly_revenue_influenced",
            "partners_signed", "monthly_meetings",
        ],
        "upgrade_path": [],
    },
)


def list_bundles() -> dict[str, Any]:
    return {
        "total": len(BUNDLES),
        "bundles": [dict(b) for b in BUNDLES],
    }


def get_bundle(bundle_id: str) -> dict[str, Any] | None:
    return next((dict(b) for b in BUNDLES if b["id"] == bundle_id), None)


def recommend_bundle(
    *,
    intent: str | None = None,
    has_contact_list: bool = False,
    is_agency: bool = False,
    is_local_business: bool = False,
    budget_sar: int = 1000,
) -> dict[str, Any]:
    """
    Recommend the best-fit bundle deterministically.

    Order of priority:
      agency → partnership_growth
      local business → local_growth_os
      has list → data_to_revenue
      monthly budget → executive_growth_os
      partnerships intent → partnership_growth
      default → growth_starter
    """
    if is_agency:
        chosen = "partnership_growth"
        reason = "وكالة → Partnership Growth + ترقية لـ Agency Partner Program."
    elif is_local_business:
        chosen = "local_growth_os"
        reason = "نشاط محلي → Local Growth OS."
    elif has_contact_list:
        chosen = "data_to_revenue"
        reason = "العميل لديه قائمة → Data to Revenue."
    elif intent == "want_partnerships":
        chosen = "partnership_growth"
        reason = "هدف الشراكات → Partnership Growth."
    elif intent == "want_daily_growth" or budget_sar >= 2999:
        chosen = "executive_growth_os"
        reason = "تشغيل يومي/ميزانية شهرية → Executive Growth OS."
    elif budget_sar >= 12000:
        chosen = "full_growth_control_tower"
        reason = "ميزانية كبيرة → Full Growth Control Tower."
    else:
        chosen = "growth_starter"
        reason = "ابدأ بـ Growth Starter."

    bundle = get_bundle(chosen)
    return {
        "recommended_bundle_id": chosen,
        "bundle": bundle,
        "reason_ar": reason,
        "approval_required": True,
    }

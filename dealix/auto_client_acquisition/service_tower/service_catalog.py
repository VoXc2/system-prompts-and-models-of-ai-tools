"""The full Dealix service catalog — 12 productized services."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class Service:
    """A single sellable, productized service."""
    id: str
    name_ar: str
    target_customer_ar: str
    outcome_ar: str
    inputs_required: tuple[str, ...]
    workflow_steps: tuple[str, ...]
    deliverables_ar: tuple[str, ...]
    pricing_min_sar: int
    pricing_max_sar: int
    pricing_model: str             # "one_time" | "monthly" | "sprint"
    risk_level: str                # "low" | "medium" | "high"
    required_integrations: tuple[str, ...]
    approval_policy: str           # short label
    proof_metrics: tuple[str, ...]
    upgrade_path: tuple[str, ...] = field(default_factory=tuple)

    def to_dict(self) -> dict[str, object]:
        return {
            "id": self.id, "name_ar": self.name_ar,
            "target_customer_ar": self.target_customer_ar,
            "outcome_ar": self.outcome_ar,
            "inputs_required": list(self.inputs_required),
            "workflow_steps": list(self.workflow_steps),
            "deliverables_ar": list(self.deliverables_ar),
            "pricing_min_sar": self.pricing_min_sar,
            "pricing_max_sar": self.pricing_max_sar,
            "pricing_model": self.pricing_model,
            "risk_level": self.risk_level,
            "required_integrations": list(self.required_integrations),
            "approval_policy": self.approval_policy,
            "proof_metrics": list(self.proof_metrics),
            "upgrade_path": list(self.upgrade_path),
        }


_DEFAULT_WORKFLOW: tuple[str, ...] = (
    "intake", "data_check", "targeting", "contactability",
    "strategy", "drafting", "approval",
    "execution_or_export", "tracking", "proof", "upsell",
)


ALL_SERVICES: tuple[Service, ...] = (
    Service(
        id="free_growth_diagnostic",
        name_ar="تشخيص نمو مجاني",
        target_customer_ar="أي شركة B2B تريد عينة قبل Pilot",
        outcome_ar="3 فرص + رسالة + تقرير مخاطر + خطة Pilot — خلال 24 ساعة عمل",
        inputs_required=("sector", "city", "offer", "goal"),
        workflow_steps=_DEFAULT_WORKFLOW,
        deliverables_ar=(
            "3 فرص B2B مع why-now",
            "رسالة عربية مخصصة",
            "تقرير مخاطر",
            "خطة Pilot مقترحة",
        ),
        pricing_min_sar=0, pricing_max_sar=0,
        pricing_model="one_time",
        risk_level="low",
        required_integrations=(),
        approval_policy="approval_required_for_share",
        proof_metrics=("diagnostic_to_paid_conversion",),
        upgrade_path=("first_10_opportunities_sprint", "growth_os_monthly"),
    ),
    Service(
        id="list_intelligence",
        name_ar="تحليل القوائم (List Intelligence)",
        target_customer_ar="شركات لديها قوائم أرقام/إيميلات/عملاء قدامى",
        outcome_ar="تنظيف + تصنيف + أفضل 50 target + رسائل + خطة 7 أيام",
        inputs_required=("uploaded_csv", "channels_available"),
        workflow_steps=_DEFAULT_WORKFLOW,
        deliverables_ar=(
            "قائمة منظفة + dedupe",
            "تصنيف safe / needs_review / blocked",
            "أفضل 50 target",
            "رسائل عربية",
            "تقرير مخاطر",
        ),
        pricing_min_sar=499, pricing_max_sar=1500,
        pricing_model="one_time",
        risk_level="medium",
        required_integrations=("google_sheets",),
        approval_policy="draft_only",
        proof_metrics=("contacts_classified", "safe_targets_found", "risks_blocked"),
        upgrade_path=("growth_os_monthly",),
    ),
    Service(
        id="first_10_opportunities_sprint",
        name_ar="10 فرص في 10 دقائق (Sprint)",
        target_customer_ar="شركة B2B تحتاج فرصاً مؤهلة بسرعة",
        outcome_ar="10 فرص + رسائل + خطة متابعة + Proof Pack — خلال 7 أيام",
        inputs_required=("sector", "city", "offer", "goal"),
        workflow_steps=_DEFAULT_WORKFLOW,
        deliverables_ar=(
            "10 فرص B2B مع why-now",
            "10 رسائل عربية",
            "خطة متابعة 7 أيام",
            "Proof Pack تفصيلي",
        ),
        pricing_min_sar=499, pricing_max_sar=1500,
        pricing_model="sprint",
        risk_level="low",
        required_integrations=(),
        approval_policy="draft_only",
        proof_metrics=("opportunities_count", "approval_rate",
                       "positive_replies", "meetings_drafted"),
        upgrade_path=("growth_os_monthly", "self_growth_operator"),
    ),
    Service(
        id="self_growth_operator",
        name_ar="مدير نمو شخصي (Self-Growth Operator)",
        target_customer_ar="مؤسسون / مستشارون / وكالات صغيرة",
        outcome_ar="Daily brief + drafts + متابعة + تقارير أسبوعية",
        inputs_required=("company_profile", "goals"),
        workflow_steps=_DEFAULT_WORKFLOW,
        deliverables_ar=(
            "Daily brief عربي",
            "5 cards/day للقرارات",
            "Drafts + approvals",
            "Weekly learning report",
        ),
        pricing_min_sar=999, pricing_max_sar=999,
        pricing_model="monthly",
        risk_level="low",
        required_integrations=("gmail", "google_calendar"),
        approval_policy="approval_required",
        proof_metrics=("decisions_per_day", "drafts_approved",
                       "meetings_drafted", "pipeline_sar"),
        upgrade_path=("growth_os_monthly",),
    ),
    Service(
        id="growth_os_monthly",
        name_ar="Growth OS — اشتراك شهري",
        target_customer_ar="شركات B2B صغيرة-متوسطة",
        outcome_ar="منصة كاملة: قنوات، command feed، proof pack، فريق",
        inputs_required=("company_profile", "channels", "team_size"),
        workflow_steps=_DEFAULT_WORKFLOW,
        deliverables_ar=(
            "ربط القنوات",
            "Daily autopilot",
            "Approvals مركزية",
            "Proof Pack شهري",
            "Revenue leak detector",
        ),
        pricing_min_sar=2999, pricing_max_sar=2999,
        pricing_model="monthly",
        risk_level="medium",
        required_integrations=("gmail", "google_calendar", "moyasar",
                               "google_sheets"),
        approval_policy="approval_required",
        proof_metrics=("monthly_pipeline_sar", "monthly_meetings",
                       "monthly_revenue_influenced", "monthly_risks_blocked"),
        upgrade_path=("agency_partner_program",),
    ),
    Service(
        id="email_revenue_rescue",
        name_ar="استعادة الإيرادات من الإيميل",
        target_customer_ar="شركات إيميل الشركة فيه فرص ضائعة",
        outcome_ar="استخراج فرص ضائعة + drafts + meetings + missed revenue report",
        inputs_required=("gmail_label", "ICP"),
        workflow_steps=_DEFAULT_WORKFLOW,
        deliverables_ar=(
            "Scan الـ inbox/labels",
            "Drafts للردود المتأخرة",
            "Meeting drafts",
            "Missed revenue report",
        ),
        pricing_min_sar=1500, pricing_max_sar=5000,
        pricing_model="one_time",
        risk_level="high",
        required_integrations=("gmail",),
        approval_policy="approval_required",
        proof_metrics=("opportunities_found", "drafts_created",
                       "meetings_drafted", "missed_revenue_sar"),
        upgrade_path=("growth_os_monthly",),
    ),
    Service(
        id="meeting_booking_sprint",
        name_ar="سبرنت حجز الاجتماعات",
        target_customer_ar="شركات لديها prospects ولا تحوّلهم لاجتماعات",
        outcome_ar="invitations + meeting drafts + briefs + follow-ups",
        inputs_required=("prospect_list", "calendar_link"),
        workflow_steps=_DEFAULT_WORKFLOW,
        deliverables_ar=(
            "دعوات اجتماع",
            "Pre-meeting brief",
            "Calendar drafts",
            "Post-meeting follow-up",
        ),
        pricing_min_sar=1500, pricing_max_sar=5000,
        pricing_model="sprint",
        risk_level="medium",
        required_integrations=("google_calendar", "gmail"),
        approval_policy="approval_required",
        proof_metrics=("meetings_drafted", "meetings_confirmed",
                       "meetings_completed"),
        upgrade_path=("growth_os_monthly",),
    ),
    Service(
        id="partner_sprint",
        name_ar="سبرنت شراكات",
        target_customer_ar="شركات تحتاج نمو عبر الشركاء والوكالات",
        outcome_ar="20 شريك محتمل + 10 رسائل + 5 اجتماعات + scorecard",
        inputs_required=("sector", "partner_goal"),
        workflow_steps=_DEFAULT_WORKFLOW,
        deliverables_ar=(
            "قائمة شركاء محتملين",
            "Scorecard لكل شريك",
            "Outreach drafts",
            "Meeting plan",
            "Referral agreement draft",
        ),
        pricing_min_sar=3000, pricing_max_sar=7500,
        pricing_model="sprint",
        risk_level="medium",
        required_integrations=("gmail",),
        approval_policy="approval_required",
        proof_metrics=("partners_identified", "partner_meetings",
                       "referral_revenue_sar"),
        upgrade_path=("agency_partner_program",),
    ),
    Service(
        id="agency_partner_program",
        name_ar="برنامج وكالة شريكة",
        target_customer_ar="وكالات تسويق/مبيعات/CRM",
        outcome_ar="بيع Dealix لعملاء الوكالة مع co-branding + revenue share",
        inputs_required=("agency_profile", "client_count"),
        workflow_steps=("agency_onboarding", "client_diagnostic",
                        "proposal", "pilot", "proof_pack", "revenue_share"),
        deliverables_ar=(
            "Agency onboarding",
            "Client diagnostics",
            "Co-branded proof packs",
            "Revenue share dashboard",
        ),
        pricing_min_sar=10000, pricing_max_sar=50000,
        pricing_model="one_time",
        risk_level="medium",
        required_integrations=("gmail", "google_calendar", "moyasar"),
        approval_policy="approval_required",
        proof_metrics=("clients_added", "agency_revenue_sar",
                       "co_branded_proofs"),
    ),
    Service(
        id="whatsapp_compliance_setup",
        name_ar="إعداد امتثال واتساب",
        target_customer_ar="شركات تستخدم واتساب بشكل عشوائي",
        outcome_ar="audit + opt-in templates + approval workflow + ledger",
        inputs_required=("contact_list", "current_practice"),
        workflow_steps=_DEFAULT_WORKFLOW,
        deliverables_ar=(
            "تصنيف القوائم",
            "Opt-in templates",
            "Approval cards",
            "Opt-out ledger",
            "Safety report",
        ),
        pricing_min_sar=1500, pricing_max_sar=4000,
        pricing_model="one_time",
        risk_level="high",
        required_integrations=("whatsapp_cloud",),
        approval_policy="draft_only",
        proof_metrics=("contacts_classified", "opt_ins_collected",
                       "risks_blocked"),
        upgrade_path=("growth_os_monthly",),
    ),
    Service(
        id="linkedin_lead_gen_setup",
        name_ar="إعداد LinkedIn Lead Gen",
        target_customer_ar="شركات B2B تحتاج decision makers",
        outcome_ar="حملة Lead Gen Form + audiences + ربط CRM + content angle",
        inputs_required=("ICP", "offer", "ad_budget"),
        workflow_steps=_DEFAULT_WORKFLOW,
        deliverables_ar=(
            "Audience plan",
            "Lead magnet",
            "Lead Gen Form",
            "Hidden fields setup",
            "Dealix intake",
            "Follow-up drafts",
        ),
        pricing_min_sar=2000, pricing_max_sar=7500,
        pricing_model="one_time",
        risk_level="medium",
        required_integrations=("linkedin_lead_forms",),
        approval_policy="approval_required",
        proof_metrics=("leads_captured", "qualified_leads",
                       "meetings_booked"),
        upgrade_path=("growth_os_monthly",),
    ),
    Service(
        id="executive_growth_brief",
        name_ar="موجز نمو تنفيذي (Executive Brief)",
        target_customer_ar="CEO / Growth Manager / Sales Manager",
        outcome_ar="3 قرارات + 3 فرص + 3 مخاطر + Pipeline + اجتماعات اليوم",
        inputs_required=("company_profile",),
        workflow_steps=("intake", "aggregate", "prioritize", "deliver"),
        deliverables_ar=(
            "Daily brief عبر واتساب/Email",
            "Approval cards (≤3 buttons)",
            "Risk alerts",
            "Weekly Founder Shadow Board",
        ),
        pricing_min_sar=499, pricing_max_sar=999,
        pricing_model="monthly",
        risk_level="low",
        required_integrations=(),
        approval_policy="approval_required",
        proof_metrics=("decisions_made", "alerts_actioned"),
        upgrade_path=("growth_os_monthly",),
    ),
)


def get_service(service_id: str) -> Service | None:
    return next((s for s in ALL_SERVICES if s.id == service_id), None)


def list_all_services() -> dict[str, object]:
    return {
        "total": len(ALL_SERVICES),
        "services": [s.to_dict() for s in ALL_SERVICES],
    }


def catalog_summary() -> dict[str, object]:
    by_pricing: dict[str, int] = {}
    by_risk: dict[str, int] = {}
    for s in ALL_SERVICES:
        by_pricing[s.pricing_model] = by_pricing.get(s.pricing_model, 0) + 1
        by_risk[s.risk_level] = by_risk.get(s.risk_level, 0) + 1
    return {
        "total": len(ALL_SERVICES),
        "by_pricing_model": by_pricing,
        "by_risk_level": by_risk,
        "free_offers": [s.id for s in ALL_SERVICES if s.pricing_max_sar == 0],
    }

"""
Service Catalog — 12 sellable services on top of the platform.

Each service has: target_customer, outcome, deliverables, pricing_model,
required_integrations, proof_metric.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class ServiceOffering:
    """A sellable service offering."""

    key: str
    label_ar: str
    label_en: str
    target_customer_ar: str
    outcome_ar: str
    deliverables_ar: tuple[str, ...]
    pricing_model_ar: str
    required_integrations: tuple[str, ...]
    proof_metric_ar: str

    def to_dict(self) -> dict[str, Any]:
        return {
            "key": self.key,
            "label_ar": self.label_ar,
            "label_en": self.label_en,
            "target_customer_ar": self.target_customer_ar,
            "outcome_ar": self.outcome_ar,
            "deliverables_ar": list(self.deliverables_ar),
            "pricing_model_ar": self.pricing_model_ar,
            "required_integrations": list(self.required_integrations),
            "proof_metric_ar": self.proof_metric_ar,
        }


SELLABLE_SERVICES: tuple[ServiceOffering, ...] = (
    ServiceOffering(
        key="growth_operator_subscription",
        label_ar="Growth Operator — اشتراك شهري",
        label_en="Growth Operator Subscription",
        target_customer_ar="شركات B2B سعودية تبحث عن نمو منظم",
        outcome_ar="فرص يومية + رسائل عربية + موافقات + Proof Pack شهري",
        deliverables_ar=(
            "Daily brief", "Command Feed", "Top opportunities",
            "Message drafts", "Approvals", "Weekly Proof Pack",
        ),
        pricing_model_ar="شهري (299 / 2,999 / 7,999 ريال حسب الحجم)",
        required_integrations=("whatsapp",),
        proof_metric_ar="Pipeline added × monthly cost multiple",
    ),
    ServiceOffering(
        key="channel_setup_service",
        label_ar="إعداد القنوات",
        label_en="Channel Setup Service",
        target_customer_ar="عملاء جدد لم يربطوا قنواتهم بعد",
        outcome_ar="ربط آمن لكل قنوات نمو الشركة (PDPL-compliant)",
        deliverables_ar=(
            "ربط WhatsApp", "ربط Gmail", "ربط Calendar",
            "ربط Sheets / CRM", "ربط Moyasar", "ربط social accounts",
        ),
        pricing_model_ar="رسوم setup (3,000-15,000 ريال) لمرة واحدة",
        required_integrations=("whatsapp", "gmail", "google_calendar", "moyasar"),
        proof_metric_ar="عدد القنوات المربوطة + uptime أسبوعي",
    ),
    ServiceOffering(
        key="lead_intelligence_service",
        label_ar="Lead Intelligence — تنظيف وتصنيف القوائم",
        label_en="Lead Intelligence Service",
        target_customer_ar="عملاء عندهم قوائم أرقام ضخمة غير منظمة",
        outcome_ar="قائمة آمنة + مصنّفة + Top-10 مرشحة للإطلاق",
        deliverables_ar=(
            "normalize_phone", "dedupe", "classify source",
            "contactability scoring", "segmentation", "Top-10 + why_now",
        ),
        pricing_model_ar="رسوم لمرة + per-1000-contact pricing",
        required_integrations=("website_forms", "google_sheets"),
        proof_metric_ar="نسبة contacts safe + Top-10 conversion",
    ),
    ServiceOffering(
        key="outreach_approval_service",
        label_ar="Outreach بموافقة كاملة",
        label_en="Outreach Approval Service",
        target_customer_ar="شركات تخاف من الإرسال العشوائي",
        outcome_ar="حملات outreach آمنة عبر approval-first flow",
        deliverables_ar=(
            "Drafts عربية", "PDPL gates", "Approval queue",
            "Tracking", "Follow-up", "Proof",
        ),
        pricing_model_ar="مدمج مع subscription + add-on per-campaign",
        required_integrations=("whatsapp", "gmail"),
        proof_metric_ar="معدل الرد + meeting rate + opt-out rate",
    ),
    ServiceOffering(
        key="partnership_sprint",
        label_ar="Partnership Sprint — 14 يوم",
        label_en="Partnership Sprint",
        target_customer_ar="شركات تريد قناة شراكات منظمة",
        outcome_ar="20 شريك محتمل + 10 رسائل + 5 اجتماعات + 1 partner offer",
        deliverables_ar=(
            "Target list", "Outreach drafts", "Meeting drafts",
            "Partner scorecard", "Revenue share template",
        ),
        pricing_model_ar="رسوم ثابتة (10,000 ريال للـ sprint)",
        required_integrations=("gmail", "google_calendar"),
        proof_metric_ar="Partner intros replied + first deal influenced",
    ),
    ServiceOffering(
        key="email_revenue_rescue",
        label_ar="Email Revenue Rescue — استخراج فرص ضائعة",
        label_en="Email Revenue Rescue",
        target_customer_ar="شركات عندها inbox مزدحم وفرص ضائعة",
        outcome_ar="استخراج leads + فرص + drafts من إيميل الشركة",
        deliverables_ar=(
            "Inbox audit", "Lost leads list", "Drafts",
            "Meeting prep", "Pipeline update",
        ),
        pricing_model_ar="رسوم لمرة + ongoing add-on",
        required_integrations=("gmail", "google_calendar"),
        proof_metric_ar="عدد الفرص المُستخرجة + pipeline rescued",
    ),
    ServiceOffering(
        key="social_growth_os",
        label_ar="Social Growth OS — تعليقات + DMs + leads",
        label_en="Social Growth OS",
        target_customer_ar="شركات نشطة على LinkedIn / X / Instagram",
        outcome_ar="تحويل التعليقات والـ mentions إلى فرص",
        deliverables_ar=(
            "Listening", "Reply drafts", "Lead extraction",
            "DM drafts (with permission)", "Reputation tasks",
        ),
        pricing_model_ar="add-on شهري على Growth/Scale",
        required_integrations=("x_api", "instagram_graph", "linkedin_lead_forms"),
        proof_metric_ar="Social-sourced leads + replied mentions",
    ),
    ServiceOffering(
        key="local_business_growth",
        label_ar="Local Business Growth — للمتاجر والعيادات",
        label_en="Local Business Growth",
        target_customer_ar="عيادات + مطاعم + متاجر + فروع",
        outcome_ar="إدارة Google Business + reviews + WhatsApp inbound + booking",
        deliverables_ar=(
            "Reviews response", "GBP posts", "Branch info sync",
            "WhatsApp booking flow", "Payment links",
        ),
        pricing_model_ar="شهري (999-2,999 ريال) + per-location",
        required_integrations=("google_business_profile", "whatsapp", "moyasar"),
        proof_metric_ar="Booking rate + average review rating + revenue per location",
    ),
    ServiceOffering(
        key="ai_visibility_aeo_sprint",
        label_ar="AI Visibility / AEO Sprint",
        label_en="AI Visibility / AEO Sprint",
        target_customer_ar="شركات تريد تظهر في إجابات ChatGPT / Gemini / Perplexity",
        outcome_ar="زيادة ظهور الشركة في answer engines + خطة محتوى 30 يوم",
        deliverables_ar=(
            "AEO audit", "Question-gap analysis", "Content plan",
            "FAQ pages", "Comparison pages", "Local posts",
        ),
        pricing_model_ar="رسوم لمرة (15,000 ريال) أو monthly retainer",
        required_integrations=("google_business_profile",),
        proof_metric_ar="عدد الأسئلة التي تظهر فيها الشركة + competitor delta",
    ),
    ServiceOffering(
        key="revenue_proof_pack_service",
        label_ar="Revenue Proof Pack — شهري للإدارة",
        label_en="Revenue Proof Pack Service",
        target_customer_ar="مدراء يحتاجون إثبات قيمة Dealix شهرياً",
        outcome_ar="تقرير شهري بـ ROI + grading + خطة الشهر القادم",
        deliverables_ar=(
            "Activity report", "Money report", "Quality + Risk report",
            "Best-of insights", "Next-month plan",
        ),
        pricing_model_ar="مدمج مع subscription Growth/Scale",
        required_integrations=(),
        proof_metric_ar="Customer NPS + renewal rate",
    ),
    ServiceOffering(
        key="customer_success_operator",
        label_ar="Customer Success Operator — منع churn",
        label_en="Customer Success Operator",
        target_customer_ar="شركات SaaS / subscription business",
        outcome_ar="health score + churn prediction + upsell signals",
        deliverables_ar=(
            "Health score 4-dim", "Churn prediction",
            "Expansion signals", "QBR auto-drafts",
        ),
        pricing_model_ar="add-on على Scale tier (1,500 ريال/شهر)",
        required_integrations=("crm",),
        proof_metric_ar="Customer churn rate + NRR (Net Revenue Retention)",
    ),
    ServiceOffering(
        key="payments_collections_operator",
        label_ar="Payments & Collections Operator",
        label_en="Payments & Collections Operator",
        target_customer_ar="شركات عندها فواتير متأخرة أو payments ضائعة",
        outcome_ar="quote + invoice drafts + reminders + recovery",
        deliverables_ar=(
            "Payment links (Moyasar)", "Invoice drafts",
            "Failed-payment recovery", "Renewal reminders",
        ),
        pricing_model_ar="شهري + 1-3% success fee على recovered revenue",
        required_integrations=("moyasar", "whatsapp", "gmail"),
        proof_metric_ar="Recovered SAR + on-time payment rate",
    ),
)


def list_services() -> dict[str, Any]:
    """Catalog the platform's sellable services."""
    return {
        "total": len(SELLABLE_SERVICES),
        "services": [s.to_dict() for s in SELLABLE_SERVICES],
    }

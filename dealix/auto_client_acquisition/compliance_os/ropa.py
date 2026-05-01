"""
RoPA — Records of Processing Activities.

PDPL requires controllers + processors to maintain a RoPA. This module
generates one programmatically per customer based on what Dealix actually
does with their data.

Output is exportable as JSON + CSV for SDAIA inspection.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any


@dataclass
class ProcessingActivity:
    """One processing activity per PDPL Art. 14 / equivalent."""

    activity_id: str
    name_ar: str
    name_en: str
    purpose_ar: str
    data_categories: list[str]               # business_contact / behavioral / sensitive
    data_subject_categories: list[str]       # decision_makers / leads / customers
    recipients: list[str]                    # who else sees this data
    international_transfers: list[str]       # GCC only / no transfers / specific
    retention_period_days: int
    security_measures: list[str]
    lawful_basis: str


# The canonical list of activities Dealix performs
DEFAULT_ACTIVITIES: tuple[ProcessingActivity, ...] = (
    ProcessingActivity(
        activity_id="discovery",
        name_ar="اكتشاف الشركات والـ leads",
        name_en="Lead discovery",
        purpose_ar="إيجاد شركات سعودية تطابق ICP العميل من المصادر العامة",
        data_categories=["business_contact", "company_metadata"],
        data_subject_categories=["business_decision_makers"],
        recipients=["customer_internal_use_only"],
        international_transfers=[],
        retention_period_days=730,
        security_measures=["TLS_1.3", "AES_256_at_rest", "RBAC", "audit_log"],
        lawful_basis="legitimate_interest",
    ),
    ProcessingActivity(
        activity_id="enrichment",
        name_ar="تكميل بيانات الشركات",
        name_en="Lead enrichment",
        purpose_ar="إكمال بيانات الشركة + DM من Apollo / ZoomInfo / LinkedIn",
        data_categories=["business_contact"],
        data_subject_categories=["business_decision_makers"],
        recipients=["customer_internal_use_only", "enrichment_subprocessors"],
        international_transfers=["enrichment_provider_us_eu"],
        retention_period_days=730,
        security_measures=["TLS_1.3", "AES_256_at_rest", "RBAC", "audit_log"],
        lawful_basis="legitimate_interest",
    ),
    ProcessingActivity(
        activity_id="outreach",
        name_ar="التواصل عبر القنوات (إيميل/واتساب/LinkedIn)",
        name_en="B2B outreach",
        purpose_ar="إرسال رسائل تجارية مخصصة بناءً على lawful basis مسجل",
        data_categories=["business_contact", "behavioral"],
        data_subject_categories=["business_decision_makers"],
        recipients=["whatsapp_provider", "email_provider"],
        international_transfers=["whatsapp_global", "gmail"],
        retention_period_days=1095,
        security_measures=["consent_check_pre_send", "opt_out_honored", "list_unsubscribe", "audit_log"],
        lawful_basis="consent_or_legitimate_interest",
    ),
    ProcessingActivity(
        activity_id="reply_classification",
        name_ar="تصنيف ردود العملاء",
        name_en="Reply classification",
        purpose_ar="فهم نية الرد وتحديد next action",
        data_categories=["behavioral", "communication_content"],
        data_subject_categories=["business_decision_makers"],
        recipients=["customer_internal_use_only", "llm_provider_for_classification"],
        international_transfers=["anthropic_groq_us"],
        retention_period_days=1095,
        security_measures=["TLS", "PII_redaction_for_LLM", "no_training_use"],
        lawful_basis="legitimate_interest",
    ),
    ProcessingActivity(
        activity_id="customer_success",
        name_ar="مراقبة صحة العميل + توليد QBR",
        name_en="Customer health + QBR",
        purpose_ar="قياس النجاح + تنبيه القادة + توصيات upsell",
        data_categories=["behavioral", "business_contact"],
        data_subject_categories=["customer_internal_users"],
        recipients=["customer_internal_only"],
        international_transfers=[],
        retention_period_days=2555,  # 7 years
        security_measures=["TLS", "audit_log", "encrypted_at_rest"],
        lawful_basis="contract",
    ),
    ProcessingActivity(
        activity_id="anonymized_benchmarks",
        name_ar="benchmarks مجهولة بين العملاء",
        name_en="Anonymized cross-customer benchmarks",
        purpose_ar="نشر Pulse الشهري + benchmarks للقطاعات بمعايير privacy (≥5 شركات)",
        data_categories=["aggregated_only"],
        data_subject_categories=["aggregated_no_individual"],
        recipients=["public_pulse_subscribers"],
        international_transfers=[],
        retention_period_days=3650,  # 10 years for anonymized aggregates
        security_measures=["min_cohort_5", "no_re_identification_possible", "linear_interpolation_only"],
        lawful_basis="legitimate_interest",
    ),
)


@dataclass
class RoPAExporter:
    """Generates and exports the RoPA bundle."""

    customer_id: str
    customer_name: str
    activities: tuple[ProcessingActivity, ...] = DEFAULT_ACTIVITIES
    dpo_name: str | None = None
    dpo_email: str | None = None
    generated_at: datetime = field(
        default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None)
    )

    def to_json(self) -> dict[str, Any]:
        return {
            "customer_id": self.customer_id,
            "customer_name": self.customer_name,
            "dpo": {"name": self.dpo_name, "email": self.dpo_email},
            "generated_at": self.generated_at.isoformat(),
            "n_activities": len(self.activities),
            "activities": [
                {
                    "activity_id": a.activity_id,
                    "name_ar": a.name_ar,
                    "name_en": a.name_en,
                    "purpose_ar": a.purpose_ar,
                    "data_categories": a.data_categories,
                    "data_subject_categories": a.data_subject_categories,
                    "recipients": a.recipients,
                    "international_transfers": a.international_transfers,
                    "retention_period_days": a.retention_period_days,
                    "security_measures": a.security_measures,
                    "lawful_basis": a.lawful_basis,
                }
                for a in self.activities
            ],
        }

    def to_csv_rows(self) -> list[dict[str, Any]]:
        """For Excel-style export to compliance teams."""
        rows: list[dict[str, Any]] = []
        for a in self.activities:
            rows.append({
                "activity_id": a.activity_id,
                "name_ar": a.name_ar,
                "purpose_ar": a.purpose_ar,
                "data_categories": "; ".join(a.data_categories),
                "data_subject_categories": "; ".join(a.data_subject_categories),
                "recipients": "; ".join(a.recipients),
                "international_transfers": "; ".join(a.international_transfers),
                "retention_period_days": a.retention_period_days,
                "lawful_basis": a.lawful_basis,
                "security_measures": "; ".join(a.security_measures),
            })
        return rows


def build_ropa(
    *,
    customer_id: str,
    customer_name: str,
    dpo_name: str | None = None,
    dpo_email: str | None = None,
    additional_activities: tuple[ProcessingActivity, ...] = (),
) -> RoPAExporter:
    """Build a RoPA exporter customized for one customer."""
    return RoPAExporter(
        customer_id=customer_id,
        customer_name=customer_name,
        dpo_name=dpo_name,
        dpo_email=dpo_email,
        activities=DEFAULT_ACTIVITIES + additional_activities,
    )

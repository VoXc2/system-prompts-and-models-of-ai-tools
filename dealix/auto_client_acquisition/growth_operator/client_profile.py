"""
Client Growth Profile — the per-customer config that turns Dealix from a
generic operator into a specialized one.

Without this profile every agent works on a generic prompt; with it,
every draft, every Why-Now, and every recommendation is grounded in:
the customer's offer, ICP, sales cycle, channels, objection history,
approval rules, and compliance constraints.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass
class ClientGrowthProfile:
    """Per-customer growth context fed to every agent decision."""

    customer_id: str
    company_name: str
    sector: str
    city: str
    offer_one_liner: str
    ideal_customer: str
    average_deal_size_sar: float = 0.0
    current_channels: tuple[str, ...] = ()       # e.g. ("whatsapp", "email")
    sales_cycle_days: int = 30
    common_objections: tuple[str, ...] = ()
    approval_rules: dict[str, Any] = field(default_factory=dict)
    compliance_rules: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "customer_id": self.customer_id,
            "company_name": self.company_name,
            "sector": self.sector,
            "city": self.city,
            "offer_one_liner": self.offer_one_liner,
            "ideal_customer": self.ideal_customer,
            "average_deal_size_sar": self.average_deal_size_sar,
            "current_channels": list(self.current_channels),
            "sales_cycle_days": self.sales_cycle_days,
            "common_objections": list(self.common_objections),
            "approval_rules": self.approval_rules,
            "compliance_rules": self.compliance_rules,
        }

    def is_specialized(self) -> bool:
        """A profile becomes 'specialized' once the minimum context is set."""
        return all([
            self.sector,
            self.city,
            self.offer_one_liner,
            self.ideal_customer,
        ])


# Sane defaults reflecting Saudi B2B norms — used until customer overrides.
_DEFAULT_APPROVAL_RULES: dict[str, Any] = {
    "require_human_for_first_send": True,
    "require_human_for_high_value_deals_above_sar": 100_000,
    "max_consecutive_followups": 3,
    "quiet_hours_riyadh": [21, 8],   # no outbound 9pm-8am Riyadh
    "blocked_dates": [],
}
_DEFAULT_COMPLIANCE_RULES: dict[str, Any] = {
    "no_cold_whatsapp_without_lawful_basis": True,
    "require_unsubscribe_in_email": True,
    "blocked_keywords": ["ضمان 100", "نتائج مضمونة", "رقم الهوية", "iban"],
    "weekly_message_cap_per_contact": 2,
    "min_cohort_for_benchmarks": 5,
}


def profile_from_dict(data: dict[str, Any]) -> ClientGrowthProfile:
    """Build a profile from a dict; missing optional fields fall back to defaults."""
    return ClientGrowthProfile(
        customer_id=str(data.get("customer_id") or ""),
        company_name=str(data.get("company_name") or ""),
        sector=str(data.get("sector") or "").lower().strip(),
        city=str(data.get("city") or "").strip(),
        offer_one_liner=str(data.get("offer_one_liner") or "").strip(),
        ideal_customer=str(data.get("ideal_customer") or "").strip(),
        average_deal_size_sar=float(data.get("average_deal_size_sar") or 0),
        current_channels=tuple(data.get("current_channels") or ()),
        sales_cycle_days=int(data.get("sales_cycle_days") or 30),
        common_objections=tuple(data.get("common_objections") or ()),
        approval_rules=data.get("approval_rules") or dict(_DEFAULT_APPROVAL_RULES),
        compliance_rules=data.get("compliance_rules") or dict(_DEFAULT_COMPLIANCE_RULES),
    )


def build_demo_profile(*, customer_id: str = "demo") -> ClientGrowthProfile:
    """Deterministic demo profile — used in /docs and test fixtures."""
    return ClientGrowthProfile(
        customer_id=customer_id,
        company_name="Demo Saudi B2B Co.",
        sector="real_estate",
        city="الرياض",
        offer_one_liner="منصة سعودية لتشغيل الإيرادات + اكتشاف فرص B2B",
        ideal_customer="شركات تطوير عقاري متوسطة، 50-200 موظف، مهتمة بـ pre-sales pipeline",
        average_deal_size_sar=85_000,
        current_channels=("whatsapp", "email"),
        sales_cycle_days=45,
        common_objections=(
            "السعر عالي",
            "كلم الشريك",
            "بعد العيد",
            "وش يضمن النتائج؟",
            "أرسل العرض واتساب",
        ),
        approval_rules=dict(_DEFAULT_APPROVAL_RULES),
        compliance_rules=dict(_DEFAULT_COMPLIANCE_RULES),
    )

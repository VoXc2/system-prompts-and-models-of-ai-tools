"""
ICP Matcher Agent — scores how well a lead fits our Ideal Customer Profile.
وكيل مطابقة العميل المثالي — يُقيّم مدى ملاءمة العميل.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from auto_client_acquisition.agents.intake import Lead
from core.agents.base import BaseAgent


class Industry(StrEnum):
    TECHNOLOGY = "technology"
    REAL_ESTATE = "real_estate"
    HEALTHCARE = "healthcare"
    EDUCATION = "education"
    LOGISTICS = "logistics"
    RETAIL = "retail"
    FINANCE = "finance"
    MANUFACTURING = "manufacturing"
    CONSULTING = "consulting"
    CONSTRUCTION = "construction"
    OIL_GAS = "oil_gas"
    TOURISM = "tourism"
    OTHER = "other"


class CompanySize(StrEnum):
    MICRO = "micro"  # 1-9
    SMALL = "small"  # 10-49
    MEDIUM = "medium"  # 50-199
    LARGE = "large"  # 200-999
    ENTERPRISE = "enterprise"  # 1000+


@dataclass
class ICP:
    """Ideal Customer Profile definition | تعريف العميل المثالي."""

    industries: list[Industry] = field(default_factory=list)
    company_sizes: list[CompanySize] = field(default_factory=list)
    regions: list[str] = field(default_factory=list)
    budget_range: tuple[float, float] = (10_000, 200_000)  # SAR
    pain_points: list[str] = field(default_factory=list)


@dataclass
class FitScore:
    """Result of ICP matching | نتيجة المطابقة."""

    overall_score: float
    industry_match: float
    size_match: float
    region_match: float
    budget_match: float
    pain_match: float
    reasons: list[str] = field(default_factory=list)
    recommendations: list[str] = field(default_factory=list)

    @property
    def tier(self) -> str:
        """Tier label | تصنيف."""
        if self.overall_score >= 0.8:
            return "A"  # hot
        if self.overall_score >= 0.6:
            return "B"  # warm
        if self.overall_score >= 0.4:
            return "C"  # cold
        return "D"  # disqualified

    def to_dict(self) -> dict[str, Any]:
        return {
            "overall_score": round(self.overall_score, 3),
            "industry_match": round(self.industry_match, 3),
            "size_match": round(self.size_match, 3),
            "region_match": round(self.region_match, 3),
            "budget_match": round(self.budget_match, 3),
            "pain_match": round(self.pain_match, 3),
            "tier": self.tier,
            "reasons": self.reasons,
            "recommendations": self.recommendations,
        }


DEFAULT_ICP = ICP(
    industries=[
        Industry.TECHNOLOGY,
        Industry.REAL_ESTATE,
        Industry.HEALTHCARE,
        Industry.EDUCATION,
        Industry.LOGISTICS,
    ],
    company_sizes=[CompanySize.SMALL, CompanySize.MEDIUM, CompanySize.LARGE],
    regions=[
        "saudi arabia",
        "sa",
        "ksa",
        "uae",
        "ae",
        "kuwait",
        "kw",
        "bahrain",
        "bh",
        "qatar",
        "qa",
        "oman",
        "om",
        "السعودية",
        "الإمارات",
        "الكويت",
        "البحرين",
        "قطر",
        "عمان",
    ],
    budget_range=(10_000, 200_000),
    pain_points=[
        "lead management",
        "sales automation",
        "customer service",
        "data analysis",
        "digital marketing",
        "crm",
        "إدارة العملاء",
        "أتمتة المبيعات",
        "خدمة العملاء",
        "تحليل البيانات",
        "التسويق الرقمي",
    ],
)


class ICPMatcherAgent(BaseAgent):
    """Scores leads against an ICP across 5 dimensions with weights."""

    name = "icp_matcher"

    # Dimension weights (must sum to 1.0)
    WEIGHTS = {
        "industry": 0.25,
        "size": 0.15,
        "region": 0.20,
        "budget": 0.20,
        "pain": 0.20,
    }

    def __init__(self, icp: ICP | None = None) -> None:
        super().__init__()
        self.icp = icp or DEFAULT_ICP

    async def run(self, *, lead: Lead, **_: Any) -> FitScore:
        """Score a lead against the ICP."""
        industry_match, industry_reason = self._match_industry(lead.sector)
        size_match, size_reason = self._match_size(lead.company_size)
        region_match, region_reason = self._match_region(lead.region)
        budget_match, budget_reason = self._match_budget(lead.budget)
        pain_match, pain_reason = self._match_pains(lead.pain_points, lead.message)

        overall = (
            self.WEIGHTS["industry"] * industry_match
            + self.WEIGHTS["size"] * size_match
            + self.WEIGHTS["region"] * region_match
            + self.WEIGHTS["budget"] * budget_match
            + self.WEIGHTS["pain"] * pain_match
        )

        reasons = [industry_reason, size_reason, region_reason, budget_reason, pain_reason]
        reasons = [r for r in reasons if r]

        recommendations = self._build_recommendations(
            overall, industry_match, size_match, region_match, budget_match, pain_match
        )

        score = FitScore(
            overall_score=overall,
            industry_match=industry_match,
            size_match=size_match,
            region_match=region_match,
            budget_match=budget_match,
            pain_match=pain_match,
            reasons=reasons,
            recommendations=recommendations,
        )

        self.log.info(
            "icp_scored",
            lead_id=lead.id,
            overall_score=round(overall, 3),
            tier=score.tier,
        )
        return score

    # ── Dimension matchers ──────────────────────────────────────
    def _match_industry(self, sector: str | None) -> tuple[float, str]:
        if not sector:
            return 0.3, "Unknown industry — neutral default"
        sector_lower = sector.lower().strip()
        target_values = {i.value for i in self.icp.industries}
        if sector_lower in target_values:
            return 1.0, f"Industry '{sector}' is in target ICP"
        for target in target_values:
            if target in sector_lower or sector_lower in target:
                return 0.8, f"Industry '{sector}' partially matches '{target}'"
        return 0.2, f"Industry '{sector}' not in target ICP"

    def _match_size(self, size: str | None) -> tuple[float, str]:
        if not size:
            return 0.4, "Company size unknown"
        size_lower = size.lower().strip()
        target_values = {s.value for s in self.icp.company_sizes}
        if size_lower in target_values:
            return 1.0, f"Size '{size}' matches ICP"
        if size_lower in {"enterprise", "micro"}:
            return 0.4, f"Size '{size}' outside sweet spot"
        return 0.5, f"Size '{size}' unrecognized — neutral"

    def _match_region(self, region: str | None) -> tuple[float, str]:
        if not region:
            return 0.4, "Region unknown"
        region_lower = region.lower().strip()
        for target in self.icp.regions:
            if target in region_lower or region_lower in target:
                return 1.0, f"Region '{region}' is in target GCC"
        return 0.2, f"Region '{region}' outside GCC"

    def _match_budget(self, budget: float | None) -> tuple[float, str]:
        if budget is None:
            return 0.5, "Budget unknown"
        min_b, max_b = self.icp.budget_range
        if min_b <= budget <= max_b:
            return 1.0, f"Budget {budget:,.0f} SAR in target range"
        if budget < min_b:
            ratio = budget / min_b if min_b else 0
            return max(0.2, ratio), f"Budget {budget:,.0f} SAR below minimum"
        # above max
        return 0.9, f"Budget {budget:,.0f} SAR above target (still good)"

    def _match_pains(self, lead_pains: list[str], message: str | None) -> tuple[float, str]:
        haystack = " ".join([*lead_pains, message or ""]).lower()
        if not haystack.strip():
            return 0.3, "No pain points provided"
        matches = [p for p in self.icp.pain_points if p.lower() in haystack]
        if matches:
            score = min(1.0, 0.3 + 0.2 * len(matches))
            return score, f"Pain matches: {', '.join(matches[:3])}"
        return 0.3, "No explicit pain matches — will probe in qualification"

    def _build_recommendations(
        self,
        overall: float,
        industry: float,
        size: float,
        region: float,
        budget: float,
        pain: float,
    ) -> list[str]:
        recs: list[str] = []
        if overall >= 0.8:
            recs.append("Tier A — prioritize; book discovery call within 24h")
        elif overall >= 0.6:
            recs.append("Tier B — qualify via short email/WhatsApp exchange")
        elif overall >= 0.4:
            recs.append("Tier C — nurture sequence; revisit in 30 days")
        else:
            recs.append("Tier D — politely decline or route to partner")

        if industry < 0.5:
            recs.append("Confirm industry/use case before committing")
        if budget < 0.5:
            recs.append("Clarify budget expectations early")
        if region < 0.5:
            recs.append("Check if we serve this region / need local partner")
        if pain < 0.5:
            recs.append("Run discovery to surface concrete pain points")
        return recs

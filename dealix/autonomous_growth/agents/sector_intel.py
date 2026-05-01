"""
Sector Intelligence Agent — Saudi sector deep knowledge.
وكيل ذكاء القطاعات — معرفة عميقة بالقطاعات السعودية.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any

from core.agents.base import BaseAgent
from core.config.models import Task
from core.llm.base import Message
from core.prompts import get_prompt


class SaudiSector(StrEnum):
    REAL_ESTATE = "real_estate"
    HEALTHCARE = "healthcare"
    EDUCATION = "education"
    LOGISTICS = "logistics"
    RETAIL = "retail"
    FINANCE = "finance"
    MANUFACTURING = "manufacturing"
    CONSULTING = "consulting"
    TECHNOLOGY = "technology"
    CONSTRUCTION = "construction"
    OIL_GAS = "oil_gas"
    TOURISM = "tourism"


@dataclass
class SectorIntel:
    sector: SaudiSector
    market_size_sar: float = 0.0
    growth_rate: float = 0.0
    key_players: list[str] = field(default_factory=list)
    pain_points: list[str] = field(default_factory=list)
    opportunities: list[str] = field(default_factory=list)
    ai_readiness: float = 0.0  # 0-1
    regulations: list[str] = field(default_factory=list)
    trends: list[str] = field(default_factory=list)
    vision_2030_alignment: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "sector": self.sector.value,
            "market_size_sar": self.market_size_sar,
            "market_size_sar_formatted": self._fmt_money(self.market_size_sar),
            "growth_rate": self.growth_rate,
            "key_players": self.key_players,
            "pain_points": self.pain_points,
            "opportunities": self.opportunities,
            "ai_readiness": self.ai_readiness,
            "regulations": self.regulations,
            "trends": self.trends,
            "vision_2030_alignment": self.vision_2030_alignment,
        }

    @staticmethod
    def _fmt_money(amount: float) -> str:
        if amount >= 1_000_000_000:
            return f"{amount / 1_000_000_000:.1f}B SAR"
        if amount >= 1_000_000:
            return f"{amount / 1_000_000:.1f}M SAR"
        return f"{amount:.0f} SAR"


# Curated baseline knowledge — enrichable via LLM when needed
SAUDI_SECTOR_DATA: dict[SaudiSector, SectorIntel] = {
    SaudiSector.REAL_ESTATE: SectorIntel(
        sector=SaudiSector.REAL_ESTATE,
        market_size_sar=150_000_000_000,
        growth_rate=0.08,
        key_players=["Dar Al Arkan", "ROSHN", "Emaar Economic City", "NHC"],
        pain_points=[
            "إدارة العقود والمستأجرين",
            "التسويق العقاري",
            "تحليل السوق",
            "الصيانة والإصلاحات",
            "Lead qualification",
        ],
        opportunities=[
            "أتمتة إدارة العقارات",
            "تحليل البيانات العقارية بالذكاء الاصطناعي",
            "AI-powered property matching",
            "Virtual tours at scale",
            "Predictive maintenance",
        ],
        ai_readiness=0.7,
        regulations=["REGA", "White Land Tax", "Sakani program"],
        trends=["Giga-projects (NEOM, Red Sea)", "Build-to-rent", "PropTech funding"],
        vision_2030_alignment="Housing program — 70% ownership target",
    ),
    SaudiSector.HEALTHCARE: SectorIntel(
        sector=SaudiSector.HEALTHCARE,
        market_size_sar=180_000_000_000,
        growth_rate=0.10,
        key_players=["MOH", "Dr. Sulaiman Al Habib", "Mouwasat", "Dallah"],
        pain_points=[
            "جدولة المواعيد",
            "إدارة السجلات الطبية",
            "التواصل مع المرضى",
            "الفواتير والتأمين",
            "Operational inefficiency",
        ],
        opportunities=[
            "مساعد طبي ذكي (Arabic clinical NLP)",
            "تحليل الصور الطبية",
            "التنبؤ بالأمراض",
            "Telemedicine platforms",
            "Claims automation",
        ],
        ai_readiness=0.6,
        regulations=["MOH Licensing", "SCFHS", "CCHI", "CDSI data rules"],
        trends=["Privatization wave", "Seha Virtual Hospital", "Medical tourism"],
        vision_2030_alignment="Privatization 25% of services, Health Sector Transformation",
    ),
    SaudiSector.EDUCATION: SectorIntel(
        sector=SaudiSector.EDUCATION,
        market_size_sar=50_000_000_000,
        growth_rate=0.12,
        key_players=["Ministry of Education", "Noor", "Madrasati", "Tatweer", "Classera"],
        pain_points=[
            "إدارة الطلاب",
            "التقييم والمتابعة",
            "التواصل مع أولياء الأمور",
            "إعداد المحتوى",
            "Personalization at scale",
        ],
        opportunities=[
            "منصات تعليم ذكية",
            "مساعد تدريس AI بالعربية",
            "تحليل أداء الطلاب",
            "AI tutoring",
            "Arabic content generation for curricula",
        ],
        ai_readiness=0.8,  # highest readiness
        regulations=["Tatweer", "National Curriculum Framework"],
        trends=["EdTech investment", "Gamified learning", "Bilingual K-12"],
        vision_2030_alignment="Human Capability Development Program",
    ),
    SaudiSector.LOGISTICS: SectorIntel(
        sector=SaudiSector.LOGISTICS,
        market_size_sar=30_000_000_000,
        growth_rate=0.15,
        key_players=["SALIC", "Aramex", "SMSA", "Naqel", "DHL KSA"],
        pain_points=[
            "تتبع الشحنات",
            "تحسين المسارات",
            "إدارة المخزون",
            "التوصيل الميل الأخير",
            "Customs bottlenecks",
        ],
        opportunities=[
            "تحسين المسارات بالذكاء الاصطناعي",
            "التنبؤ بالطلب",
            "أتمتة المستودعات",
            "Last-mile optimization",
            "Customs document automation",
        ],
        ai_readiness=0.75,
        regulations=["Zakat & Customs", "Saudi Post", "TGA"],
        trends=["E-commerce growth (30%+)", "Cold chain", "NEOM logistics"],
        vision_2030_alignment="Logistics hub — top 25 globally",
    ),
    SaudiSector.FINANCE: SectorIntel(
        sector=SaudiSector.FINANCE,
        market_size_sar=400_000_000_000,
        growth_rate=0.06,
        key_players=["SNB", "Al Rajhi", "Riyad Bank", "STC Pay", "SABB"],
        pain_points=[
            "AML/KYC compliance cost",
            "Fraud detection",
            "Customer service at scale",
            "Manual underwriting",
        ],
        opportunities=[
            "AML/KYC automation with Arabic OCR",
            "Conversational banking (Arabic)",
            "Fraud ML",
            "Credit scoring",
            "RegTech",
        ],
        ai_readiness=0.75,
        regulations=["SAMA", "CMA", "AML Law", "SAMA Open Banking framework"],
        trends=["Open banking", "BNPL surge", "FinTech sandbox"],
        vision_2030_alignment="Financial Sector Development Program",
    ),
    SaudiSector.RETAIL: SectorIntel(
        sector=SaudiSector.RETAIL,
        market_size_sar=250_000_000_000,
        growth_rate=0.09,
        key_players=["Panda", "Othaim", "Noon", "Amazon.sa", "Jarir", "Extra"],
        pain_points=[
            "Inventory forecasting",
            "Customer service in Arabic",
            "Marketing attribution",
            "Shrinkage",
        ],
        opportunities=[
            "Demand forecasting",
            "Arabic chatbots / voice",
            "Dynamic pricing",
            "Personalization",
        ],
        ai_readiness=0.7,
        regulations=["MoCI", "SASO", "VAT"],
        trends=["Quick commerce", "Q-Pay", "Omnichannel"],
        vision_2030_alignment="Quality of life program — retail experience",
    ),
    SaudiSector.TECHNOLOGY: SectorIntel(
        sector=SaudiSector.TECHNOLOGY,
        market_size_sar=130_000_000_000,
        growth_rate=0.14,
        key_players=["STC", "Mobily", "Zain", "Elm", "Thiqah", "SDAIA"],
        pain_points=["Talent gap", "Scaling support", "Localization"],
        opportunities=[
            "Arabic LLM applications",
            "DevOps automation",
            "Sector-specific SaaS",
            "AI-enabled products",
        ],
        ai_readiness=0.85,
        regulations=["NCA (cybersecurity)", "SDAIA", "Data privacy law PDPL"],
        trends=["LEAP conference", "Unicorns emerging", "Gov digital transformation"],
        vision_2030_alignment="Digital Transformation Program",
    ),
    SaudiSector.CONSTRUCTION: SectorIntel(
        sector=SaudiSector.CONSTRUCTION,
        market_size_sar=180_000_000_000,
        growth_rate=0.11,
        key_players=["SBG", "El Seif", "Al Rashid", "Nesma"],
        pain_points=["Cost overruns", "Delays", "Safety", "Document handling"],
        opportunities=[
            "Computer vision for safety",
            "Procurement optimization",
            "Document extraction",
            "Scheduling AI",
        ],
        ai_readiness=0.55,
        regulations=["MoMRA", "Saudi Building Code"],
        trends=["Giga-projects boom", "Modular construction"],
        vision_2030_alignment="NEOM, Red Sea, Diriyah, Qiddiya",
    ),
    SaudiSector.OIL_GAS: SectorIntel(
        sector=SaudiSector.OIL_GAS,
        market_size_sar=800_000_000_000,
        growth_rate=0.03,
        key_players=["Saudi Aramco", "SABIC", "Maaden"],
        pain_points=["Predictive maintenance", "Safety incidents", "Document review"],
        opportunities=[
            "Predictive maintenance",
            "Seismic analysis AI",
            "Process optimization",
            "Arabic HSE compliance",
        ],
        ai_readiness=0.8,
        regulations=["MoEnergy", "Saudi Aramco standards"],
        trends=["Energy transition", "Hydrogen", "Downstream growth"],
        vision_2030_alignment="Sustainability + downstream localization",
    ),
    SaudiSector.TOURISM: SectorIntel(
        sector=SaudiSector.TOURISM,
        market_size_sar=90_000_000_000,
        growth_rate=0.20,
        key_players=["STA", "Red Sea Global", "Neom", "Diriyah Gate"],
        pain_points=["Multilingual support", "Demand forecasting", "Experience personalization"],
        opportunities=[
            "Multilingual AI concierge",
            "Dynamic pricing",
            "Itinerary AI",
            "Review analysis",
        ],
        ai_readiness=0.65,
        regulations=["STA", "SAGIA"],
        trends=["100M visitors target", "Giga-projects", "Religious tourism tech"],
        vision_2030_alignment="Tourism — 10% GDP target",
    ),
    SaudiSector.MANUFACTURING: SectorIntel(
        sector=SaudiSector.MANUFACTURING,
        market_size_sar=220_000_000_000,
        growth_rate=0.07,
        key_players=["SABIC", "Maaden", "Al-Yamamah Steel", "Zamil"],
        pain_points=["Predictive maintenance", "Quality control", "Supply chain"],
        opportunities=["Computer vision QC", "Predictive maintenance", "Demand sensing"],
        ai_readiness=0.6,
        regulations=["SASO", "MODON", "Made in Saudi program"],
        trends=["Localization drive", "Industry 4.0 push"],
        vision_2030_alignment="NIDLP — National Industrial Development",
    ),
    SaudiSector.CONSULTING: SectorIntel(
        sector=SaudiSector.CONSULTING,
        market_size_sar=15_000_000_000,
        growth_rate=0.10,
        key_players=["Big4 KSA offices", "Strategy&", "Oliver Wyman", "Elixir"],
        pain_points=["Report turnaround", "Research efficiency", "Proposal writing"],
        opportunities=[
            "Research co-pilots",
            "Proposal generation",
            "Deck automation",
            "Knowledge management",
        ],
        ai_readiness=0.8,
        regulations=["SAGIA licensing"],
        trends=["Gov consulting boom", "Vision 2030 PMO work"],
        vision_2030_alignment="Serves all VRPs (Vision Realization Programs)",
    ),
}


class SectorIntelAgent(BaseAgent):
    """Deep knowledge + LLM-enriched analysis for Saudi sectors."""

    name = "sector_intel"

    async def run(
        self,
        *,
        sector: SaudiSector | str,
        enrich_with_llm: bool = False,
        locale: str = "ar",
        **_: Any,
    ) -> SectorIntel:
        """Return baseline sector intel, optionally enriched by LLM."""
        if isinstance(sector, str):
            sector = SaudiSector(sector)

        base = SAUDI_SECTOR_DATA.get(sector)
        if base is None:
            base = SectorIntel(sector=sector)

        if not enrich_with_llm:
            return base

        try:
            prompt = get_prompt("sector_analysis", sector=sector.value)
            response = await self.router.run(
                task=Task.RESEARCH,
                messages=[Message(role="user", content=prompt)],
                max_tokens=1500,
                temperature=0.3,
            )
            extra = self.parse_json_response(response.content)
            # Merge — LLM adds fresh items without losing baseline
            base.pain_points = list(set(base.pain_points + list(extra.get("pain_points", []))))
            base.opportunities = list(
                set(base.opportunities + list(extra.get("opportunities", [])))
            )
            if extra.get("market_size_sar"):
                base.market_size_sar = float(extra["market_size_sar"])
            if extra.get("growth_rate"):
                base.growth_rate = float(extra["growth_rate"])
            if extra.get("ai_readiness"):
                base.ai_readiness = float(extra["ai_readiness"])
        except Exception as e:
            self.log.warning("sector_enrich_failed", error=str(e))

        return base

    async def best_opportunity(self) -> SectorIntel:
        """Return the sector with the highest (growth × AI readiness) product."""
        scored = [(s.growth_rate * s.ai_readiness, s) for s in SAUDI_SECTOR_DATA.values()]
        scored.sort(key=lambda x: x[0], reverse=True)
        return scored[0][1]

    def target_sectors(self) -> list[SectorIntel]:
        """Return our priority target sectors (top 5 by opportunity)."""
        scored = sorted(
            SAUDI_SECTOR_DATA.values(),
            key=lambda s: s.growth_rate * s.ai_readiness,
            reverse=True,
        )
        return scored[:5]

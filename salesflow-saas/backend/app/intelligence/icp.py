"""
ICP Builder — Ideal Customer Profile Engine
Defines and stores ICP configs per org. Drives all discovery logic.
"""
from dataclasses import dataclass, field, asdict
from typing import List, Optional, Dict, Any
import json


@dataclass
class ICPConfig:
    """Ideal Customer Profile — full definition per org"""
    org_id: str

    # Company attributes
    industries: List[str] = field(default_factory=list)        # e.g. ["tech", "healthcare", "banking"]
    company_sizes: List[str] = field(default_factory=list)     # e.g. ["50-200", "200-1000"]
    regions: List[str] = field(default_factory=list)           # e.g. ["Riyadh", "Jeddah", "KSA"]
    revenue_range_sar: Dict[str, float] = field(default_factory=dict)  # {"min": 1000000, "max": 50000000}
    tech_signals: List[str] = field(default_factory=list)      # e.g. ["Salesforce", "SAP", "HubSpot"]
    growth_signals: List[str] = field(default_factory=list)    # e.g. ["hiring", "funding", "expansion"]
    languages: List[str] = field(default_factory=list)         # e.g. ["ar", "en"]

    # Person attributes (buying committee)
    target_titles_ar: List[str] = field(default_factory=list)  # Arabic titles
    target_titles_en: List[str] = field(default_factory=list)  # English titles
    seniority_levels: List[str] = field(default_factory=list)  # e.g. ["C-level", "VP", "Director"]

    # Opportunity type
    motion: str = "sales"                                       # sales | partnership | channel | tender
    segment: str = "B2B"                                        # B2B | B2C | B2T

    # Scoring weights (must sum to 1.0)
    fit_weight: float = 0.30
    intent_weight: float = 0.25
    access_weight: float = 0.15
    value_weight: float = 0.20
    urgency_weight: float = 0.10

    # Discovery sources
    discovery_sources: List[str] = field(default_factory=lambda: [
        "web_search", "linkedin_public", "news", "job_boards", "directories"
    ])

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def build_search_queries(self) -> List[str]:
        """Auto-generate search queries from ICP attributes — Arabic + English"""
        queries = []
        for industry in self.industries[:3]:
            for region in self.regions[:2]:
                queries.append(f"شركات {industry} في {region}")
                queries.append(f"{industry} companies in {region} Saudi Arabia")
        for signal in self.growth_signals[:2]:
            for industry in self.industries[:2]:
                queries.append(f"{industry} {signal} Saudi Arabia 2025 2026")
        for title in self.target_titles_ar[:2]:
            for industry in self.industries[:2]:
                queries.append(f"{title} {industry} السعودية")
        for title in self.target_titles_en[:2]:
            for industry in self.industries[:2]:
                queries.append(f"{title} {industry} Saudi Arabia LinkedIn")
        return queries[:20]  # cap at 20 queries


# Default Dealix ICP — B2B SaaS / Enterprise, Saudi-first
DEALIX_DEFAULT_ICP = ICPConfig(
    org_id="dealix",
    industries=["تقنية", "رعاية صحية", "مالية وبنوك", "عقارات", "تصنيع", "تجزئة", "لوجستيات",
                "technology", "healthcare", "banking", "real estate", "manufacturing", "retail"],
    company_sizes=["10-50", "50-200", "200-1000", "1000+"],
    regions=["الرياض", "جدة", "الدمام", "المنطقة الشرقية", "Riyadh", "Jeddah", "Dammam", "KSA"],
    revenue_range_sar={"min": 500_000, "max": 500_000_000},
    tech_signals=["Salesforce", "SAP", "Oracle", "HubSpot", "Zoho", "Microsoft Dynamics", "Excel", "WhatsApp Business"],
    growth_signals=["hiring", "expansion", "funding", "partnership", "IPO", "digital transformation",
                    "توظيف", "توسع", "تمويل", "شراكة", "تحول رقمي"],
    languages=["ar", "en"],
    target_titles_ar=["مدير تطوير الأعمال", "مدير المبيعات", "الرئيس التنفيذي", "المدير التجاري",
                       "مدير الشراكات", "مدير التسويق", "مدير المشتريات", "نائب الرئيس"],
    target_titles_en=["CEO", "CCO", "VP Sales", "Head of Business Development", "Commercial Director",
                       "Chief Revenue Officer", "Sales Director", "Partnerships Manager"],
    seniority_levels=["C-level", "VP", "Director", "Head of", "Manager"],
    motion="sales",
    segment="B2B",
    discovery_sources=["web_search", "news", "job_boards", "directories", "linkedin_public"],
)

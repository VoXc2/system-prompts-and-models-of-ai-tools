"""
Saudi Arabia market context — constants + helpers.
سياق السوق السعودي.
"""

from __future__ import annotations

from dataclasses import dataclass

GCC_COUNTRIES: list[str] = [
    "Saudi Arabia",
    "UAE",
    "Kuwait",
    "Bahrain",
    "Qatar",
    "Oman",
]

VISION_2030_PROGRAMS: list[str] = [
    "National Transformation Program",
    "Housing Program",
    "Quality of Life Program",
    "Public Investment Fund Program",
    "Financial Sector Development Program",
    "Human Capability Development Program",
    "Digital Transformation Program",
    "Health Sector Transformation Program",
    "National Industrial Development and Logistics Program (NIDLP)",
    "Privatization Program",
]

SAUDI_REGULATORS: dict[str, str] = {
    "SAMA": "Central Bank — banking & fintech",
    "CMA": "Capital Market Authority",
    "MOH": "Ministry of Health",
    "SCFHS": "Saudi Commission for Health Specialties",
    "CCHI": "Council of Cooperative Health Insurance",
    "MoCI": "Ministry of Commerce",
    "MoE": "Ministry of Education",
    "SDAIA": "Saudi Data and AI Authority",
    "NCA": "National Cybersecurity Authority",
    "REGA": "Real Estate General Authority",
    "STA": "Saudi Tourism Authority",
    "MoMRA": "Ministry of Municipal and Rural Affairs",
    "MODON": "Saudi Industrial Property Authority",
    "SASO": "Saudi Standards Authority",
    "ZATCA": "Zakat, Tax and Customs Authority",
}


@dataclass(frozen=True)
class SaudiHoliday:
    """Major Saudi public holidays (approximate, Gregorian)."""

    name_ar: str
    name_en: str
    month: int
    day: int


STATIC_HOLIDAYS: list[SaudiHoliday] = [
    SaudiHoliday("اليوم الوطني", "Saudi National Day", 9, 23),
    SaudiHoliday("يوم التأسيس", "Founding Day", 2, 22),
]


def is_gcc_country(country: str) -> bool:
    """Return True if country is in the GCC | هل الدولة من دول الخليج؟"""
    if not country:
        return False
    normalized = country.strip().lower()
    gcc_variants = {
        "saudi arabia",
        "sa",
        "ksa",
        "السعودية",
        "المملكة العربية السعودية",
        "uae",
        "ae",
        "الإمارات",
        "الامارات",
        "kuwait",
        "kw",
        "الكويت",
        "bahrain",
        "bh",
        "البحرين",
        "qatar",
        "qa",
        "قطر",
        "oman",
        "om",
        "عمان",
    }
    return normalized in gcc_variants


def region_tier(region: str | None) -> str:
    """Classify a region into our pricing tiers | صنّف المنطقة إلى طبقة سعرية."""
    if not region:
        return "global"
    lower = region.lower().strip()
    if any(t in lower for t in ("saudi", "ksa", "sa", "riyadh", "jeddah", "dammam", "السعودية")):
        return "saudi"
    if is_gcc_country(region):
        return "gcc"
    return "global"

"""Saudi-first ICP templates — seed into DB or use in-memory fallback."""

from __future__ import annotations

from typing import Any, Dict, List

DEFAULT_ICP_TEMPLATES: List[Dict[str, Any]] = [
    {
        "slug": "healthcare_clinics",
        "name_ar": "عيادات ورعاية صحية",
        "name_en": "Healthcare & clinics",
        "config_json": {
            "sectors": ["healthcare", "medical", "عيادات"],
            "geo_priority": ["Riyadh", "Jeddah", "Dammam", "Eastern Province"],
            "company_size": "smb",
            "buyer_roles": ["owner", "operations", "practice_manager"],
            "commercial_triggers": ["expansion", "patient_volume", "digital_front"],
            "technographic": ["basic_website", "whatsapp"],
            "acv_band_sar": "20k-200k",
            "urgency_signals": ["new_branch", "hiring_reception"],
            "exclusions": ["individual_patients"],
        },
    },
    {
        "slug": "real_estate",
        "name_ar": "عقارات ومكاتب وساطة",
        "name_en": "Real estate",
        "config_json": {
            "sectors": ["real_estate", "عقارات", "property"],
            "geo_priority": ["Riyadh", "Jeddah", "NEOM_adjacent"],
            "company_size": "smb_enterprise",
            "buyer_roles": ["broker_owner", "sales_director", "marketing"],
            "acv_band_sar": "15k-500k",
            "exclusions": [],
        },
    },
    {
        "slug": "industrial_contracting",
        "name_ar": "مقاولات وصناعة",
        "name_en": "Industrial & contracting",
        "config_json": {
            "sectors": ["construction", "industrial", "مقاولات"],
            "geo_priority": ["Eastern Province", "Riyadh"],
            "buyer_roles": ["gm", "projects", "procurement"],
            "acv_band_sar": "50k-2M",
        },
    },
    {
        "slug": "enterprise_services",
        "name_ar": "خدمات مؤسسية وبرمجيات",
        "name_en": "Enterprise B2B services",
        "config_json": {
            "sectors": ["saas", "it_services", "consulting"],
            "company_size": "enterprise",
            "buyer_roles": ["cio", "cfo", "head_of_sales"],
            "acv_band_sar": "100k+",
        },
    },
]


def match_icp_slug(lead_sector: str, meta: Dict[str, Any]) -> str:
    """Pick best slug from keywords in sector + metadata."""
    blob = f"{lead_sector} {meta}".lower()
    if any(x in blob for x in ("عياد", "clinic", "medical", "صح")):
        return "healthcare_clinics"
    if any(x in blob for x in ("عقار", "real", "property")):
        return "real_estate"
    if any(x in blob for x in ("مقاول", "industrial", "factory")):
        return "industrial_contracting"
    return "enterprise_services"

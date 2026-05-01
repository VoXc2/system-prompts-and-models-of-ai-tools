"""Map buying committees — من غالباً يقرر داخل الشركة."""

from __future__ import annotations

from typing import Any

# All buyer roles Dealix knows about, with Arabic labels.
ALL_BUYER_ROLES: dict[str, str] = {
    "founder_ceo": "المؤسس / الرئيس التنفيذي",
    "coo": "مدير العمليات",
    "head_of_sales": "مدير المبيعات",
    "marketing_manager": "مدير التسويق",
    "business_development": "تطوير الأعمال",
    "operations_manager": "مدير العمليات التشغيلية",
    "clinic_manager": "مدير العيادة",
    "branch_manager": "مدير الفرع",
    "hr_manager": "مدير الموارد البشرية",
    "procurement_manager": "مدير المشتريات",
    "agency_owner": "صاحب الوكالة",
    "store_manager": "مدير المتجر",
    "growth_manager": "مدير النمو",
    "cto": "المدير التقني",
}

# Sector-specific decision-maker priors (descending priority).
_DM_BY_SECTOR: dict[str, list[str]] = {
    "training":     ["founder_ceo", "head_of_sales", "hr_manager"],
    "saas":         ["founder_ceo", "head_of_sales", "growth_manager"],
    "real_estate":  ["founder_ceo", "head_of_sales", "branch_manager"],
    "retail":       ["founder_ceo", "store_manager", "marketing_manager"],
    "healthcare":   ["clinic_manager", "founder_ceo", "operations_manager"],
    "logistics":    ["coo", "operations_manager", "founder_ceo"],
    "fintech":      ["founder_ceo", "growth_manager", "cto"],
    "agency":       ["agency_owner", "head_of_sales", "growth_manager"],
    "education":    ["founder_ceo", "operations_manager", "marketing_manager"],
    "consulting":   ["founder_ceo", "business_development", "head_of_sales"],
}

_INFLUENCERS_BY_SECTOR: dict[str, list[str]] = {
    "training":     ["marketing_manager", "operations_manager"],
    "saas":         ["marketing_manager", "cto"],
    "real_estate":  ["marketing_manager"],
    "retail":       ["operations_manager"],
    "healthcare":   ["marketing_manager", "operations_manager"],
    "logistics":    ["procurement_manager"],
    "fintech":      ["marketing_manager", "head_of_sales"],
    "agency":       ["marketing_manager", "business_development"],
    "education":    ["hr_manager"],
    "consulting":   ["marketing_manager"],
}

# Goal-based message angles per role.
_ROLE_ANGLES_AR: dict[str, str] = {
    "founder_ceo": "نمو إيرادات ملموس بدون توظيف فريق كبير.",
    "coo": "تنظيم العمليات وقياس الأثر يومياً.",
    "head_of_sales": "ملء الـ pipeline بفرص مؤهلة + متابعة منظمة.",
    "marketing_manager": "تحويل الـ traffic والإعلانات إلى اجتماعات.",
    "business_development": "فتح قنوات شراكة وتوزيع جديدة.",
    "operations_manager": "أتمتة المتابعات + تقليل الوقت الضائع.",
    "clinic_manager": "تذكير المرضى + ردود التقييمات + قنوات حجز.",
    "branch_manager": "إدارة عملاء الفرع + reactivation.",
    "hr_manager": "برامج تدريب وتوظيف بدون فوضى inbox.",
    "procurement_manager": "تقييم مزودين + التزامات SLA واضحة.",
    "agency_owner": "خدمة عملاء الوكالة + Proof Pack + revenue share.",
    "store_manager": "استرجاع العملاء + payment links + reviews.",
    "growth_manager": "تجارب نمو منظمة + قياس Proof.",
    "cto": "أمان البيانات + PDPL + تكاملات مصرّحة.",
}


def _norm_sector(sector: str) -> str:
    s = (sector or "").lower().strip()
    return s if s in _DM_BY_SECTOR else "saas"


def map_buying_committee(
    sector: str,
    *,
    company_size: str = "small",
    goal: str = "fill_pipeline",
) -> dict[str, Any]:
    """Build a buying-committee map for a sector + company-size."""
    s = _norm_sector(sector)
    dm_keys = _DM_BY_SECTOR[s]
    inf_keys = _INFLUENCERS_BY_SECTOR[s]

    # For small companies, the founder is almost always the primary DM.
    if company_size in ("micro", "small") and "founder_ceo" not in dm_keys[:2]:
        dm_keys = ["founder_ceo"] + [k for k in dm_keys if k != "founder_ceo"]

    return {
        "sector": s,
        "company_size": company_size,
        "goal": goal,
        "primary_decision_maker": {
            "role_key": dm_keys[0],
            "label_ar": ALL_BUYER_ROLES[dm_keys[0]],
            "angle_ar": _ROLE_ANGLES_AR[dm_keys[0]],
        },
        "secondary_decision_makers": [
            {"role_key": k, "label_ar": ALL_BUYER_ROLES[k],
             "angle_ar": _ROLE_ANGLES_AR[k]}
            for k in dm_keys[1:]
        ],
        "influencers": [
            {"role_key": k, "label_ar": ALL_BUYER_ROLES[k],
             "angle_ar": _ROLE_ANGLES_AR[k]}
            for k in inf_keys
        ],
        "approach_notes_ar": (
            "ابدأ بمحاور أعلى — المؤسس أو مدير المبيعات. "
            "اشمل الـ influencers في الرسالة الثانية لبناء التوافق الداخلي."
        ),
    }


def recommend_decision_maker_roles(
    sector: str, *, goal: str = "fill_pipeline",
) -> list[dict[str, str]]:
    s = _norm_sector(sector)
    return [
        {"role_key": k, "label_ar": ALL_BUYER_ROLES[k],
         "angle_ar": _ROLE_ANGLES_AR[k]}
        for k in _DM_BY_SECTOR[s]
    ]


def recommend_influencer_roles(
    sector: str, *, goal: str = "fill_pipeline",
) -> list[dict[str, str]]:
    s = _norm_sector(sector)
    return [
        {"role_key": k, "label_ar": ALL_BUYER_ROLES[k],
         "angle_ar": _ROLE_ANGLES_AR[k]}
        for k in _INFLUENCERS_BY_SECTOR[s]
    ]


def draft_role_based_angle(
    role_key: str, *, sector: str = "saas", offer: str = "",
) -> dict[str, str]:
    """Build a one-sentence Arabic angle suited to a role."""
    role_key = role_key if role_key in ALL_BUYER_ROLES else "founder_ceo"
    role_ar = ALL_BUYER_ROLES[role_key]
    base_angle = _ROLE_ANGLES_AR[role_key]
    offer_part = f" — {offer}" if offer else ""
    return {
        "role_key": role_key,
        "role_ar": role_ar,
        "angle_ar": f"رسالة لـ{role_ar}: {base_angle}{offer_part}",
    }

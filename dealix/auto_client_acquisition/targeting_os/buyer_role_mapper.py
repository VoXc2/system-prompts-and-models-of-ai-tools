"""Map sector/goal to buying committee roles — deterministic."""

from __future__ import annotations

from typing import Any

_SECTOR_ROLES: dict[str, dict[str, list[str]]] = {
    "training": {
        "primary": ["Founder/CEO", "Head of Sales"],
        "influencers": ["HR Manager", "Operations Manager"],
    },
    "saas": {
        "primary": ["Founder/CEO", "Procurement Manager"],
        "influencers": ["IT Manager", "Head of Sales"],
    },
    "clinics": {
        "primary": ["Clinic Manager", "Founder/CEO"],
        "influencers": ["Operations Manager", "HR Manager"],
    },
    "default": {
        "primary": ["Founder/CEO", "Head of Sales"],
        "influencers": ["Marketing Manager", "Business Development Manager"],
    },
}


def map_buying_committee(sector: str, company_size: str | None, goal: str | None) -> dict[str, Any]:
    key = (sector or "").strip().lower() or "default"
    if key not in _SECTOR_ROLES:
        key = "default"
    roles = _SECTOR_ROLES[key]
    size = (company_size or "smb").lower()
    g = (goal or "book_more_b2b_meetings").lower()
    note = "شركة أكبر: أضف Procurement" if size in ("enterprise", "large") else "تركيز على Founder/Head of Sales في SMB."
    if "partner" in g:
        note += " هدف شراكة: أضف Agency Owner كمؤثر."
    return {
        "sector": sector or "unknown",
        "company_size": size,
        "goal": g,
        "primary_decision_makers": roles["primary"],
        "influencers": roles["influencers"],
        "note_ar": note,
        "demo": True,
    }


def recommend_decision_maker_roles(sector: str, goal: str | None) -> list[str]:
    return list(map_buying_committee(sector, None, goal)["primary_decision_makers"])


def recommend_influencer_roles(sector: str, goal: str | None) -> list[str]:
    return list(map_buying_committee(sector, None, goal)["influencers"])


def draft_role_based_angle(role: str, sector: str, offer: str) -> dict[str, Any]:
    return {
        "role": role,
        "sector": sector,
        "angle_ar": f"نربط «{offer}» بأثر مباشر على {role}: وقت أقل، صفقات أوضح، متابعة موثّقة.",
        "demo": True,
    }

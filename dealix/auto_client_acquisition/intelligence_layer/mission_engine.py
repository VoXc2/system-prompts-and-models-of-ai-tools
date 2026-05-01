"""Mission catalog — references innovation missions without duplicating HTTP."""

from __future__ import annotations

from typing import Any

from auto_client_acquisition.innovation.growth_missions import list_growth_missions


_MISSIONS_META: list[dict[str, Any]] = [
    {
        "id": "first_10_opportunities",
        "title_ar": "10 فرص في 10 دقائق",
        "canonical_http": "POST /api/v1/intelligence/missions/first-10-opportunities",
        "safety_rules_ar": ["لا واتساب بارد", "موافقة على المسودات"],
        "required_integrations": [],
    },
    {
        "id": "revenue_leak_rescue",
        "title_ar": "إنقاذ تسريب إيراد",
        "canonical_http": "GET /api/v1/intelligence/command-feed/demo",
        "safety_rules_ar": ["مراجعة المصدر", "حد أسبوعي للمسودات"],
        "required_integrations": ["gmail_draft"],
    },
    {
        "id": "partnership_sprint",
        "title_ar": "سباق شراكات",
        "canonical_http": "POST /api/v1/targeting/linkedin/strategy",
        "safety_rules_ar": ["LinkedIn Lead Gen فقط", "لا auto-DM"],
        "required_integrations": [],
    },
    {
        "id": "customer_reactivation",
        "title_ar": "إعادة تفعيل عملاء",
        "canonical_http": "POST /api/v1/platform/contacts/import-preview",
        "safety_rules_ar": ["تصنيف القائمة", "opt-out فوري"],
        "required_integrations": [],
    },
]


def list_mission_catalog() -> dict[str, Any]:
    gm = list_growth_missions()
    return {"missions": _MISSIONS_META, "innovation_growth_missions": gm, "demo": True}


def get_mission(mission_id: str) -> dict[str, Any]:
    for m in _MISSIONS_META:
        if m["id"] == mission_id:
            return {**m, "found": True}
    return {"found": False, "error": "unknown_mission", "demo": True}

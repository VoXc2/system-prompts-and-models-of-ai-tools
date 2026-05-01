"""Upsell / upgrade paths between services."""

from __future__ import annotations

from typing import Any

from auto_client_acquisition.service_tower.service_catalog import get_service_by_id, list_tower_services


def build_all_upgrade_paths() -> dict[str, Any]:
    paths = []
    for s in list_tower_services().get("services") or []:
        paths.append(
            {
                "service_id": s["service_id"],
                "name_ar": s.get("name_ar"),
                "upgrade_path": s.get("upgrade_path"),
            }
        )
    return {"paths": paths, "demo": True}


def recommend_upgrade(service_id: str, results: dict[str, Any]) -> dict[str, Any]:
    svc = get_service_by_id(service_id)
    default_next = (svc or {}).get("upgrade_path") or "growth_os"
    r = results or {}
    if int(r.get("paid_conversion", 0)) > 0:
        default_next = "growth_os"
    return {
        "from_service": service_id,
        "recommended_upgrade": default_next,
        "reason_ar": "بعد إثبات القيمة: Growth OS للتشغيل الشهري.",
        "demo": True,
    }


def build_upsell_message_ar(service_id: str, next_offer: str) -> str:
    return (
        f"أكملنا {service_id} بنجاح. الخطوة المنطقية: {next_offer} "
        "للتشغيل الشهري مع Proof Pack — بدون إرسال حي بدون موافقتك."
    )


def map_service_to_subscription(service_id: str) -> dict[str, Any]:
    if service_id in ("growth_os", "self_growth_operator", "local_growth_os"):
        return {"subscription_id": "growth_os_monthly", "eligible": True, "demo": True}
    return {"subscription_id": "growth_os_monthly", "eligible": False, "note_ar": "خدمة مشروع — اشتراك اختياري بعد Pilot.", "demo": True}

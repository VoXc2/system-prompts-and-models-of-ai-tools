"""Suggest next service / bundle from catalog upgrade_path."""

from __future__ import annotations

from typing import Any

from auto_client_acquisition.autonomous_service_operator import service_bundles as sb
from auto_client_acquisition.service_tower.service_catalog import get_service_by_id


def suggest_upsell(service_id: str) -> dict[str, Any]:
    svc = get_service_by_id(service_id) or {}
    nxt = svc.get("upgrade_path")
    next_svc = get_service_by_id(str(nxt)) if nxt else None
    bundle_hint = None
    if nxt == "growth_os":
        bundle_hint = "executive_growth_os"
    return {
        "from_service_id": service_id,
        "next_service_id": nxt,
        "next_name_ar": (next_svc or {}).get("name_ar"),
        "suggested_bundle_id": bundle_hint,
        "bundles": sb.get_bundle(bundle_hint) if bundle_hint else None,
        "demo": True,
    }

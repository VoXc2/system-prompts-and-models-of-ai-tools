"""Map each sellable service to default mission / workflow steps."""

from __future__ import annotations

from typing import Any

from auto_client_acquisition.service_tower.service_catalog import get_service_by_id


_DEFAULT_STEPS = [
    "intake",
    "analyze",
    "target",
    "draft",
    "approve",
    "track",
    "proof",
    "upsell",
]


def build_service_workflow(service_id: str) -> dict[str, Any]:
    svc = get_service_by_id(service_id)
    if not svc:
        return {"service_id": service_id, "steps": [], "error": "unknown_service", "demo": True}
    steps = list(svc.get("workflow_steps") or _DEFAULT_STEPS)
    return {
        "service_id": service_id,
        "steps": steps,
        "approval_gates": [s for s in steps if s in ("approve", "approval")],
        "live_send": False,
        "demo": True,
    }


def get_default_mission_steps(service_id: str) -> list[str]:
    return list(build_service_workflow(service_id).get("steps") or [])


def map_service_to_growth_mission(service_id: str) -> dict[str, Any]:
    """Bridge to growth_operator mission naming where applicable."""
    mapping = {
        "first_10_opportunities": "first_10_opportunities",
        "list_intelligence": "contact_import_preview",
        "growth_os": "daily_growth_loop",
        "partner_sprint": "partnership_sprint",
        "email_revenue_rescue": "email_revenue_rescue",
    }
    mid = mapping.get(service_id, "generic_service_run")
    return {
        "service_id": service_id,
        "growth_mission_id": mid,
        "note_ar": "ربط منطقي للعرض — لا يشغّل مهمة حية.",
        "demo": True,
    }

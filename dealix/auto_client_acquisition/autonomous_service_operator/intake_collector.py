"""Required intake fields per service_id — from Service Tower catalog."""

from __future__ import annotations

from typing import Any

from auto_client_acquisition.service_tower.service_catalog import get_service_by_id


def intake_questions(service_id: str) -> dict[str, Any]:
    svc = get_service_by_id(service_id) or {}
    fields = svc.get("inputs_required") or []
    return {
        "service_id": service_id,
        "fields": [{"name": f, "prompt_ar": f"يرجى تزويدنا بـ: {f}"} for f in fields],
        "demo": True,
    }

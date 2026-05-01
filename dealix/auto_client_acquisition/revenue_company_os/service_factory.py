"""Bridge to Service Tower for Company OS."""

from __future__ import annotations

from typing import Any

from auto_client_acquisition.service_tower.service_catalog import list_tower_services


def demo_service_snapshot() -> dict[str, Any]:
    cat = list_tower_services()
    return {"catalog": cat, "demo": True}

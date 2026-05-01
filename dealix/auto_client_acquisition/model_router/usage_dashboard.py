"""Demo usage dashboard for the model router (deterministic)."""

from __future__ import annotations

from .provider_registry import ALL_PROVIDERS, ALL_TASK_TYPES
from .task_router import route_task


def build_usage_demo() -> dict[str, object]:
    """
    Demo: route every task type once and surface aggregate stats.

    Used by /api/v1/model-router/usage/demo to show the router behavior.
    """
    routes: list[dict[str, object]] = []
    for tt in ALL_TASK_TYPES:
        d = route_task(tt, requires_arabic=(tt == "arabic_copywriting"))
        routes.append(d.to_dict())

    cost_counts: dict[str, int] = {}
    primary_counts: dict[str, int] = {}
    for r in routes:
        cost_counts[str(r.get("cost_class"))] = cost_counts.get(str(r.get("cost_class")), 0) + 1
        primary_counts[str(r.get("primary_provider"))] = primary_counts.get(str(r.get("primary_provider")), 0) + 1

    return {
        "providers_total": len(ALL_PROVIDERS),
        "task_types_total": len(ALL_TASK_TYPES),
        "routes": routes,
        "cost_counts": cost_counts,
        "primary_counts": primary_counts,
    }

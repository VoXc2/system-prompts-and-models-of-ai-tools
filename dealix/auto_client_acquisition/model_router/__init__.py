"""Model Router — pick the right model/provider for each task type, with fallback."""

from __future__ import annotations

from .cost_policy import CostClass, classify_cost
from .fallback_policy import build_fallback_chain
from .provider_registry import (
    ALL_PROVIDERS,
    ALL_TASK_TYPES,
    Provider,
    TaskType,
    get_provider,
)
from .task_router import RouteDecision, route_task
from .usage_dashboard import build_usage_demo

__all__ = [
    "ALL_PROVIDERS",
    "ALL_TASK_TYPES",
    "CostClass",
    "Provider",
    "RouteDecision",
    "TaskType",
    "build_fallback_chain",
    "build_usage_demo",
    "classify_cost",
    "get_provider",
    "route_task",
]

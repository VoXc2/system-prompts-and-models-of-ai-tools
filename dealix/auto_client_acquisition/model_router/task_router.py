"""Map task types to suggested provider + cost class — deterministic."""

from __future__ import annotations

from typing import Any

_ROUTES: dict[str, dict[str, Any]] = {
    "strategic_reasoning": {"provider": "anthropic", "cost_class": "high", "needs_guardrail": True},
    "arabic_copywriting": {"provider": "anthropic", "cost_class": "medium", "needs_guardrail": True},
    "classification": {"provider": "openai", "cost_class": "low", "needs_guardrail": True},
    "compliance_guardrail": {"provider": "openai", "cost_class": "low", "needs_guardrail": False},
    "meeting_analysis": {"provider": "google", "cost_class": "medium", "needs_guardrail": True},
    "vision_analysis": {"provider": "google", "cost_class": "medium", "needs_guardrail": True},
    "extraction": {"provider": "groq", "cost_class": "low", "needs_guardrail": True},
    "summarization": {"provider": "openai", "cost_class": "low", "needs_guardrail": True},
    "low_cost_bulk": {"provider": "groq", "cost_class": "minimal", "needs_guardrail": True},
    "coding_project_understanding": {"provider": "anthropic", "cost_class": "high", "needs_guardrail": True},
}


def list_tasks() -> dict[str, Any]:
    return {"task_types": sorted(_ROUTES.keys()), "demo": True}


def route_task(task_type: str) -> dict[str, Any]:
    t = (task_type or "").strip().lower().replace("-", "_")
    if t not in _ROUTES:
        return {"ok": False, "error": "unknown_task_type", "known": sorted(_ROUTES.keys()), "demo": True}
    r = _ROUTES[t]
    return {"ok": True, "task_type": t, **r, "fallback_provider": "groq", "demo": True}

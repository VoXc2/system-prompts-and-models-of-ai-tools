"""
Model Routing Fabric — routes tasks to optimal model based on benchmark pool.

Routing tiers:
- codex:   implementation, refactors, test fixes, fast repo work
- gpt:     architecture, system design, typed outputs, executive memos, complex tool workflows
- opus:    heavy strategic decisions, board-level synthesis, cross-domain comparison
- sonnet:  high-throughput drafting, structured operational content
- composer: lightweight fallback, auxiliary support tasks
"""

from __future__ import annotations

from typing import Optional
from .schemas import ModelRoutingDecision


ROUTING_TABLE: dict[str, dict[str, str]] = {
    "code_implementation": {
        "primary": "codex-5.3-extra-high-fast",
        "fallback": "codex-5.3-high-fast",
    },
    "architecture_design": {
        "primary": "gpt-5.4-extra-high-fast",
        "fallback": "gpt-5.4-high",
    },
    "executive_memo": {
        "primary": "gpt-5.4-high",
        "fallback": "opus-4.6-high",
    },
    "board_synthesis": {
        "primary": "opus-4.6-high-fast",
        "fallback": "gpt-5.4-extra-high-fast",
    },
    "strategic_comparison": {
        "primary": "opus-4.6-high",
        "fallback": "gpt-5.4-high-fast",
    },
    "operational_drafting": {
        "primary": "sonnet-4.6-high",
        "fallback": "gpt-5.4-high-fast",
    },
    "arabic_memo": {
        "primary": "gpt-5.4-high",
        "fallback": "sonnet-4.6-high",
    },
    "scoring": {
        "primary": "sonnet-4.6-high",
        "fallback": "gpt-5.4-high-fast",
    },
    "enrichment": {
        "primary": "sonnet-4.6-high",
        "fallback": "composer-2",
    },
    "lightweight": {
        "primary": "composer-2",
        "fallback": "sonnet-4.6-high",
    },
}


def route_model(task_class: str, override: Optional[str] = None) -> ModelRoutingDecision:
    """Select the optimal model for a task class from the internal benchmark pool."""
    if override:
        return ModelRoutingDecision(
            task_class=task_class,
            selected_model=override,
            fallback_model=None,
            reason=f"Manual override to {override}",
        )

    entry = ROUTING_TABLE.get(task_class, ROUTING_TABLE["lightweight"])
    return ModelRoutingDecision(
        task_class=task_class,
        selected_model=entry["primary"],
        fallback_model=entry.get("fallback"),
        reason=f"Benchmark-pool routing for {task_class}",
    )

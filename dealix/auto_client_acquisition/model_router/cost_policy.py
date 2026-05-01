"""Cost policy — classify a task's cost class without locking to specific tokens prices."""

from __future__ import annotations

from typing import Literal

CostClass = Literal["low", "mid", "high"]


def classify_cost(
    *,
    task_type: str,
    expected_input_tokens: int = 0,
    expected_output_tokens: int = 0,
    bulk: bool = False,
) -> CostClass:
    """
    Heuristic cost class.

    - bulk volume → low
    - large output (>1500 tokens) → high
    - strategic / vision / arabic_copywriting → mid
    - everything else → low
    """
    if bulk:
        return "low"
    if expected_output_tokens > 1500 or expected_input_tokens > 8000:
        return "high"
    if task_type in {
        "strategic_reasoning", "vision_analysis",
        "compliance_guardrail", "meeting_analysis",
    }:
        return "mid"
    if task_type in {"arabic_copywriting"}:
        return "mid"
    return "low"

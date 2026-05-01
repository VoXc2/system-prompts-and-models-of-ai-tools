"""Lightweight in-memory cost tracker (per process; persistence is the ledger's job)."""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field


@dataclass
class CostTracker:
    """Track agent run costs in memory for the current process."""
    by_workflow: dict[str, float] = field(default_factory=lambda: defaultdict(float))
    by_provider: dict[str, float] = field(default_factory=lambda: defaultdict(float))
    by_task_type: dict[str, float] = field(default_factory=lambda: defaultdict(float))
    total: float = 0.0
    runs: int = 0

    def record(
        self,
        *,
        workflow_name: str,
        provider_key: str,
        task_type: str,
        cost_estimate: float,
    ) -> None:
        self.by_workflow[workflow_name] += cost_estimate
        self.by_provider[provider_key] += cost_estimate
        self.by_task_type[task_type] += cost_estimate
        self.total += cost_estimate
        self.runs += 1

    def summary(self) -> dict[str, object]:
        return {
            "runs": self.runs,
            "total": round(self.total, 4),
            "by_workflow": {k: round(v, 4) for k, v in self.by_workflow.items()},
            "by_provider": {k: round(v, 4) for k, v in self.by_provider.items()},
            "by_task_type": {k: round(v, 4) for k, v in self.by_task_type.items()},
        }

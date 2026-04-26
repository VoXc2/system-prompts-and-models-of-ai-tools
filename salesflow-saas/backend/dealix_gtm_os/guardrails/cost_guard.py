"""Cost guard — prevents runaway AI spending."""
import yaml
from pathlib import Path

_config_path = Path(__file__).parent.parent / "config" / "ai_budget.yaml"
_config = {}
if _config_path.exists():
    with open(_config_path) as f:
        _config = yaml.safe_load(f) or {}

class CostGuard:
    def __init__(self):
        budget = _config.get("daily_budget", {})
        self.max_cost = budget.get("max_cost_sar", 10.0)
        self.max_requests = budget.get("max_requests", 500)
        self.alert_pct = budget.get("alert_at_percent", 80)
        self.total_cost = 0.0
        self.total_requests = 0

    def check(self) -> dict:
        cost_pct = (self.total_cost / self.max_cost * 100) if self.max_cost > 0 else 0
        req_pct = (self.total_requests / self.max_requests * 100) if self.max_requests > 0 else 0
        return {
            "allowed": cost_pct < 100 and req_pct < 100,
            "cost_sar": round(self.total_cost, 4),
            "cost_pct": round(cost_pct, 1),
            "requests": self.total_requests,
            "requests_pct": round(req_pct, 1),
            "alert": cost_pct >= self.alert_pct or req_pct >= self.alert_pct,
        }

    def record(self, cost_sar: float):
        self.total_cost += cost_sar
        self.total_requests += 1

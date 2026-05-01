"""Simple numeric opportunity scenarios."""

from __future__ import annotations

from typing import Any


def simulate_opportunities(inputs: dict[str, Any] | None) -> dict[str, Any]:
    ins = inputs or {}
    pipeline = float(ins.get("pipeline_sar") or 250_000)
    win_rate = float(ins.get("win_rate") or 0.18)
    forecast = round(pipeline * win_rate, 2)
    return {
        "pipeline_sar": pipeline,
        "win_rate_assumption": win_rate,
        "weighted_forecast_sar": forecast,
        "scenarios": [
            {"label_ar": "أساسي", "forecast_sar": forecast},
            {"label_ar": "تفاؤل محدود", "forecast_sar": round(forecast * 1.12, 2)},
            {"label_ar": "تحفظ", "forecast_sar": round(forecast * 0.85, 2)},
        ],
        "demo": True,
    }

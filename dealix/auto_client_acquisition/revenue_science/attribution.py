"""
Channel Attribution — credits revenue across the touchpoints that produced it.

Four standard models supported:
  - first_touch: 100% to the first channel that engaged the lead
  - last_touch:  100% to the last channel before close
  - linear:      equal split across all touchpoints
  - time_decay:  more credit to recent touchpoints (half-life 14 days)
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class AttributionResult:
    """Per-channel credited revenue."""

    model: str
    by_channel: dict[str, float] = field(default_factory=dict)
    total_revenue_sar: float = 0.0


def _normalize(touchpoints: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Sort by occurred_at ascending; require channel + at."""
    return sorted(
        [t for t in touchpoints if t.get("channel") and t.get("at")],
        key=lambda x: x["at"],
    )


def compute_first_touch(*, deals: list[dict[str, Any]]) -> AttributionResult:
    """100% credit to the first touchpoint per won deal."""
    by_channel: dict[str, float] = defaultdict(float)
    total = 0.0
    for d in deals:
        if d.get("status") != "won":
            continue
        tps = _normalize(d.get("touchpoints", []))
        if not tps:
            continue
        revenue = float(d.get("value_sar", 0))
        by_channel[tps[0]["channel"]] += revenue
        total += revenue
    return AttributionResult(model="first_touch", by_channel=dict(by_channel), total_revenue_sar=total)


def compute_last_touch(*, deals: list[dict[str, Any]]) -> AttributionResult:
    """100% credit to the last touchpoint before close."""
    by_channel: dict[str, float] = defaultdict(float)
    total = 0.0
    for d in deals:
        if d.get("status") != "won":
            continue
        tps = _normalize(d.get("touchpoints", []))
        if not tps:
            continue
        revenue = float(d.get("value_sar", 0))
        by_channel[tps[-1]["channel"]] += revenue
        total += revenue
    return AttributionResult(model="last_touch", by_channel=dict(by_channel), total_revenue_sar=total)


def compute_linear(*, deals: list[dict[str, Any]]) -> AttributionResult:
    """Equal credit across all touchpoints."""
    by_channel: dict[str, float] = defaultdict(float)
    total = 0.0
    for d in deals:
        if d.get("status") != "won":
            continue
        tps = _normalize(d.get("touchpoints", []))
        if not tps:
            continue
        revenue = float(d.get("value_sar", 0))
        share = revenue / len(tps)
        for tp in tps:
            by_channel[tp["channel"]] += share
        total += revenue
    return AttributionResult(model="linear", by_channel=dict(by_channel), total_revenue_sar=total)


def compute_time_decay(*, deals: list[dict[str, Any]], half_life_days: float = 14) -> AttributionResult:
    """
    Time-decay: each touchpoint's weight decays exponentially with distance
    from close. Most credit goes to recent touches.
    """
    by_channel: dict[str, float] = defaultdict(float)
    total = 0.0
    for d in deals:
        if d.get("status") != "won":
            continue
        tps = _normalize(d.get("touchpoints", []))
        if not tps:
            continue
        revenue = float(d.get("value_sar", 0))
        close_at = d.get("closed_at") or tps[-1]["at"]
        weights = []
        for tp in tps:
            days_before_close = (close_at - tp["at"]).total_seconds() / 86400
            weights.append(0.5 ** (days_before_close / half_life_days))
        total_weight = sum(weights) or 1.0
        for tp, w in zip(tps, weights, strict=False):
            by_channel[tp["channel"]] += revenue * (w / total_weight)
        total += revenue
    return AttributionResult(
        model=f"time_decay(hl={half_life_days}d)",
        by_channel=dict(by_channel),
        total_revenue_sar=total,
    )

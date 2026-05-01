"""Trust score 0–100 from simple signals."""

from __future__ import annotations

from typing import Any


def compute_trust_score(signals: dict[str, Any] | None) -> dict[str, Any]:
    s = signals or {}
    base = 55
    if s.get("has_signed_dpa"):
        base += 15
    if s.get("reply_rate_30d", 0) and float(s["reply_rate_30d"]) > 0.2:
        base += 10
    if s.get("compliance_flags"):
        base -= 20
    score = max(0, min(100, int(base)))
    return {"trust_score": score, "factors": list(s.keys()) or ["default"], "demo": True}

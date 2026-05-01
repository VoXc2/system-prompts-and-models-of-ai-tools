"""Lightweight Saudi-Arabic tone score — heuristic."""

from __future__ import annotations

import re
from typing import Any


def evaluate_saudi_tone(text_ar: str) -> dict[str, Any]:
    t = (text_ar or "").strip()
    score = 65
    if re.search(r"(هل|ممكن|نقدّم|نرحب|شاكرين)", t):
        score += 10
    if len(t) > 600:
        score -= 10
    if "!!!" in t or "؟؟؟" in t:
        score -= 8
    score = max(0, min(100, score))
    return {"tone_score": score, "demo": True}

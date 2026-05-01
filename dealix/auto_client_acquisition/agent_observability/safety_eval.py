"""Tripwire checks on Arabic marketing copy — deterministic."""

from __future__ import annotations

import re
from typing import Any

_BAD = ("ضمان كامل", "مضمون 100%", "ارسل لي رقم البطاقة", "كلمة المرور", "حسابك معلق")


def evaluate_safety(text_ar: str) -> dict[str, Any]:
    t = text_ar or ""
    trips: list[str] = []
    for phrase in _BAD:
        if phrase in t:
            trips.append(phrase)
    if re.search(r"\b\d{16}\b", t):
        trips.append("possible_pan")
    return {"passed": len(trips) == 0, "tripwires": trips, "demo": True}

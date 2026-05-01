"""Deal risk hint from simple signals."""

from __future__ import annotations

from typing import Any


def assess_deal_risk(signals: dict[str, Any] | None = None) -> dict[str, Any]:
    s = signals or {}
    risk = "low"
    reasons: list[str] = []
    if s.get("no_followup_scheduled"):
        risk = "medium"
        reasons.append("لا يوجد موعد متابعة بعد الاجتماع.")
    if s.get("ghosted_after_proposal"):
        risk = "high"
        reasons.append("توقف التواصل بعد العرض.")
    return {"risk_level": risk, "reasons_ar": reasons, "demo": True}

"""Trust Score — composite per-action verdict before execution."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class TrustVerdict:
    """Output of compute_trust_score."""

    verdict: str           # safe / needs_review / blocked
    score: int             # 0-100 (higher = safer)
    reasons_ar: list[str]
    fixes_ar: list[str]


def compute_trust_score(
    *,
    source_quality: str = "unknown",   # public / partner / customer / cold / unknown
    opt_in: bool = False,
    channel: str = "whatsapp",
    message_text: str = "",
    frequency_count_this_week: int = 0,
    weekly_cap: int = 2,
    approval_status: str = "pending",
) -> dict[str, Any]:
    """
    Composite trust verdict on a proposed action.

    Pure deterministic — same inputs → same verdict.
    """
    score = 100
    reasons: list[str] = []
    fixes: list[str] = []

    # 1. Source quality
    src_penalty = {
        "customer": 0,
        "partner": -5,
        "public": -10,
        "unknown": -25,
        "cold": -40,
    }.get(source_quality, -20)
    score += src_penalty
    if src_penalty <= -25:
        reasons.append(f"جودة المصدر منخفضة ({source_quality}).")
        fixes.append("وثّق lawful basis قبل أي تواصل.")

    # 2. Opt-in
    if not opt_in and channel == "whatsapp":
        score -= 30
        reasons.append("لا opt-in على قناة WhatsApp.")
        fixes.append("احصل على opt-in صريح أو حوّل القناة للإيميل.")

    # 3. Channel risk
    if channel in ("whatsapp", "instagram_graph"):
        score -= 5  # consumer-facing channels need extra care
    elif channel == "x_api":
        score -= 10  # public broadcast risk

    # 4. Message risk — banned phrases
    risky_phrases = ("ضمان 100", "نتائج مضمونة", "آخر فرصة", "اضغط هنا فوراً")
    found = [p for p in risky_phrases if p in (message_text or "")]
    if found:
        score -= 15 * len(found)
        reasons.append(f"عبارات محظورة: {found}")
        fixes.append("احذف العبارات المبالغة قبل الإرسال.")

    # 5. Frequency cap
    if frequency_count_this_week >= weekly_cap:
        score -= 20
        reasons.append(f"تجاوز السقف الأسبوعي ({frequency_count_this_week}/{weekly_cap}).")
        fixes.append("انتظر بداية الأسبوع التالي.")

    # 6. Approval gate
    if approval_status == "pending":
        score -= 10
        reasons.append("لم يصل approval المشغّل بعد.")
        fixes.append("اطلب موافقة المشغّل.")

    score = max(0, min(100, score))

    if score >= 70:
        verdict = "safe"
    elif score >= 40:
        verdict = "needs_review"
    else:
        verdict = "blocked"

    if not reasons:
        reasons = ["كل القواعد مستوفاة."]
    if not fixes and verdict == "safe":
        fixes = ["جاهز للتنفيذ بعد approval إذا لزم."]

    return {
        "verdict": verdict,
        "score": score,
        "reasons_ar": reasons,
        "fixes_ar": fixes,
    }

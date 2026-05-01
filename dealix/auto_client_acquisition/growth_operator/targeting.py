"""
Targeting — turn a list of safe contacts into a ranked Top-N with Why-Now.

Pure functions; no LLM calls. Heuristic ranking:
  - existing customer / inbound lead: highest base score
  - event lead: strong recency boost
  - old lead with last_contacted_at: medium
  - referral: high trust
  - unknown / cold: filtered out unless explicitly allowed
"""

from __future__ import annotations

import hashlib
from typing import Any

from auto_client_acquisition.growth_operator.contact_importer import (
    classify_contact_source,
    detect_opt_out,
    normalize_phone,
)
from auto_client_acquisition.growth_operator.contactability import (
    score_contactability,
)


# ── Segments ─────────────────────────────────────────────────────
_SEGMENT_BASE_SCORE: dict[str, float] = {
    "existing_customer": 90.0,
    "inbound_lead": 85.0,
    "referral": 80.0,
    "event_lead": 75.0,
    "old_lead": 60.0,
    "unknown": 35.0,
    "cold_list": 20.0,
}


def segment_contacts(contacts: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    """Group contacts into segments using classify_contact_source."""
    segs: dict[str, list[dict[str, Any]]] = {
        "existing_customer": [],
        "inbound_lead": [],
        "referral": [],
        "event_lead": [],
        "old_lead": [],
        "unknown": [],
        "cold_list": [],
        "blocked_or_invalid": [],
    }
    for c in contacts:
        if detect_opt_out(c) or not normalize_phone(c.get("phone")):
            segs["blocked_or_invalid"].append(c)
            continue
        src = classify_contact_source(c)
        segs.setdefault(src, []).append(c)
    return segs


# ── Why-Now stub (deterministic; placeholder until live signals) ──
_WHY_NOW_TEMPLATES_AR: dict[str, str] = {
    "existing_customer": "علاقة قائمة — توقيت ممتاز لعرض expansion / upsell.",
    "inbound_lead": "أبدى اهتماماً مؤخراً — السرعة (≤24 ساعة) ترفع التحويل.",
    "referral": "قادم بإحالة موثوقة — احترام السياق المهني.",
    "event_lead": "تواصل من فعالية مؤخراً — نافذة 30 يوم ذهبية.",
    "old_lead": "lead سابق — انتهز موسم/حدث جديد للعودة.",
    "unknown": "مصدر غير محدد — يحتاج warm-up + توثيق lawful basis.",
    "cold_list": "قائمة باردة — لا تواصل قبل توثيق العلاقة.",
}


def why_now_stub(contact: dict[str, Any], *, sector_hint: str = "") -> dict[str, Any]:
    """
    Deterministic Why-Now stub.

    In production, this is replaced by a live signal-driven explainer
    that reads market_intelligence + company website diff + jobs.
    """
    src = classify_contact_source(contact)
    company = contact.get("company") or contact.get("name") or "—"
    rationale = _WHY_NOW_TEMPLATES_AR.get(src, "تواصل قياسي — راجع المصدر قبل الإرسال.")
    if sector_hint and src in ("event_lead", "inbound_lead", "old_lead"):
        rationale += f" · مرتبط بقطاع {sector_hint}."
    # Synthetic stable score (testable, no entropy)
    seed = hashlib.md5(f"{company}|{src}|{sector_hint}".encode()).digest()
    bonus = (seed[0] % 21) - 10  # -10..+10
    return {
        "rationale_ar": rationale,
        "score_modifier": bonus,
        "source": src,
    }


# ── Ranking ──────────────────────────────────────────────────────
def rank_targets(
    contacts: list[dict[str, Any]],
    *,
    sector_hint: str = "",
    channel: str = "whatsapp",
    require_safe: bool = True,
) -> list[dict[str, Any]]:
    """
    Score every contact, optionally filter to safe-only, return sorted desc.

    Each item in the result is the original contact + score + why_now + decision.
    """
    out: list[dict[str, Any]] = []
    for c in contacts:
        decision = score_contactability(c, channel=channel)
        if require_safe and decision["label"] != "safe":
            continue
        why = why_now_stub(c, sector_hint=sector_hint)
        base = _SEGMENT_BASE_SCORE.get(why["source"], 30.0)
        score = max(0.0, min(100.0, base + why["score_modifier"]))
        out.append({
            **c,
            "fit_score": round(score, 1),
            "why_now": why,
            "contactability": decision,
        })
    out.sort(key=lambda x: x["fit_score"], reverse=True)
    return out


def recommend_top_10(
    contacts: list[dict[str, Any]],
    *,
    sector_hint: str = "",
    channel: str = "whatsapp",
) -> dict[str, Any]:
    """The Top-10 view consumed by the dashboard's Growth Radar tile."""
    ranked = rank_targets(
        contacts, sector_hint=sector_hint, channel=channel, require_safe=True,
    )
    top = ranked[:10]
    return {
        "channel": channel,
        "sector_hint": sector_hint,
        "candidates_evaluated": len(contacts),
        "candidates_safe": len(ranked),
        "top": top,
        "recommendation_ar": (
            f"اخترنا أعلى {len(top)} فرصة آمنة من قائمة {len(contacts)} "
            f"بعد فلترة المخاطرة. كل واحدة بحالة pending_approval."
        ),
    }

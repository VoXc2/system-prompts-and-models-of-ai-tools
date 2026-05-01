"""
Lead scoring + Data Quality scoring.

Both deterministic — no LLM required. Used by /leads/enrich/* + the data
ingestion pipeline. LLM scoring (qualitative) lives in agents/qualification.py.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass
class ScoreBreakdown:
    fit: float = 0.0
    intent: float = 0.0
    urgency: float = 0.0
    risk: float = 0.0
    total: float = 0.0
    priority: str = "P3"
    recommended_channel: str | None = None
    reason: str = ""


# ── Data Quality (0..100) ──────────────────────────────────────────
DQ_WEIGHTS = {
    "has_domain": 12,
    "has_website": 6,
    "has_city": 8,
    "has_sector": 8,
    "has_source_url": 8,
    "has_email_or_phone": 12,
    "has_signal": 12,
    "has_place_id": 8,
    "low_dup_risk": 6,
    # Negatives (subtracted)
    "missing_source": -10,
    "personal_only_contact": -8,
    "no_allowed_use": -15,
    "opt_out": -100,
    "high_risk": -20,
}


def compute_data_quality(account: dict[str, Any]) -> tuple[float, list[str]]:
    """
    Compute DQ score from a normalized account dict.
    Returns (score, reasons).
    """
    reasons: list[str] = []
    score = 0.0
    if account.get("domain"):
        score += DQ_WEIGHTS["has_domain"]; reasons.append("+domain")
    if account.get("website"):
        score += DQ_WEIGHTS["has_website"]; reasons.append("+website")
    if account.get("city"):
        score += DQ_WEIGHTS["has_city"]; reasons.append("+city")
    if account.get("sector"):
        score += DQ_WEIGHTS["has_sector"]; reasons.append("+sector")
    if account.get("source_url") or account.get("best_source"):
        score += DQ_WEIGHTS["has_source_url"]; reasons.append("+source_url")
    has_business_contact = bool(account.get("email")) or bool(account.get("phone"))
    if has_business_contact:
        score += DQ_WEIGHTS["has_email_or_phone"]; reasons.append("+contact")
    if account.get("google_place_id"):
        score += DQ_WEIGHTS["has_place_id"]; reasons.append("+place_id")
    if account.get("signals"):
        score += DQ_WEIGHTS["has_signal"]; reasons.append("+signals")
    if int(account.get("source_count") or 1) >= 2:
        score += DQ_WEIGHTS["low_dup_risk"]; reasons.append("+multi_source")

    if not account.get("source_type") and not account.get("best_source"):
        score += DQ_WEIGHTS["missing_source"]; reasons.append("-no_source")
    if account.get("allowed_use") in (None, "", "unknown"):
        score += DQ_WEIGHTS["no_allowed_use"]; reasons.append("-no_allowed_use")
    if account.get("opt_out"):
        score += DQ_WEIGHTS["opt_out"]; reasons.append("-opt_out")
    if (account.get("risk_level") or "").lower() == "high":
        score += DQ_WEIGHTS["high_risk"]; reasons.append("-high_risk")

    return max(0.0, min(100.0, score)), reasons


# ── Lead Score (0..100, P0..P3) ────────────────────────────────────
def compute_lead_score(
    account: dict[str, Any],
    *,
    signals: list[dict[str, Any]] | None = None,
    technologies: list[dict[str, Any]] | None = None,
) -> ScoreBreakdown:
    """
    Deterministic ICP score. Mirrors the Saudi B2B 100-point spec:
        Fit 40 + Intent 30 + Access 15 + Revenue 15 → priority bucket.
    """
    sig_list = signals or []
    tech_list = technologies or []

    # ── FIT (40) ─────────────────────────────────────────────────
    fit = 0.0
    sector = (account.get("sector") or "").lower()
    high_value_sectors = {
        "saas", "fintech", "ecommerce", "real_estate", "real_estate_developer",
        "marketing_agency", "training_center", "consulting_firm", "accounting_firm",
        "law_firm", "logistics", "education",
        # Lead-driven hospitality + events: every inquiry = booking-value
        "events", "hospitality", "hotel", "wedding_hall", "event_venue",
        "tourism_agency",
    }
    medium_value_sectors = {
        "dental_clinic", "medical_clinic", "cosmetic_clinic",
        "restaurant", "retail_store", "fitness_gym", "salon_spa", "auto_dealer",
        "construction", "food_manufacturing", "retail",
    }
    if sector in high_value_sectors:
        fit += 25
    elif sector in medium_value_sectors:
        fit += 18
    elif sector:
        fit += 10
    if (account.get("country") or "SA").upper() == "SA":
        fit += 10
    if account.get("city") in {"الرياض", "Riyadh", "riyadh", "جدة", "Jeddah", "jeddah",
                                "الدمام", "Dammam", "dammam"}:
        fit += 5
    fit = min(40.0, fit)

    # ── INTENT (30) ───────────────────────────────────────────────
    intent = 0.0
    intent_signal_types = {"intent", "hire", "funding", "news"}
    intent += min(15, sum(s.get("confidence", 0.5) * 5 for s in sig_list
                          if s.get("signal_type") in intent_signal_types))
    # Tech signals (CRM/booking/payments) imply they're already commerce-active
    tech_categories = {t.get("category") for t in tech_list}
    if tech_categories & {"booking", "crm", "ecom_mena", "payment_mena", "chat_mena"}:
        intent += 10
    if any(t.get("name", "").lower() in {"calendly", "hubspot", "salla", "zid"} for t in tech_list):
        intent += 5
    intent = min(30.0, intent)

    # ── ACCESSIBILITY (15) ────────────────────────────────────────
    access = 0.0
    if account.get("phone"):
        access += 5
    if account.get("email"):
        access += 5
    if account.get("website") or account.get("domain"):
        access += 3
    if account.get("google_place_id"):
        access += 2
    access = min(15.0, access)

    # ── REVENUE POTENTIAL (15) ────────────────────────────────────
    revenue = 0.0
    rev_hints = (account.get("revenue_hint") or "").lower()
    if "enterprise" in rev_hints or "large" in rev_hints:
        revenue = 15
    elif "mid" in rev_hints or "growth" in rev_hints:
        revenue = 10
    elif "smb" in rev_hints or "small" in rev_hints:
        revenue = 6
    else:
        revenue = 8  # default neutral
    revenue = min(15.0, revenue)

    total = fit + intent + access + revenue

    # ── RISK (subtractive, 0..30) ─────────────────────────────────
    risk = 0.0
    if (account.get("risk_level") or "").lower() == "high":
        risk += 20
    if account.get("opt_out"):
        risk += 30
    if not account.get("allowed_use") or account["allowed_use"] == "unknown":
        risk += 8

    if total >= 80:
        priority = "P0"
    elif total >= 65:
        priority = "P1"
    elif total >= 45:
        priority = "P2"
    else:
        priority = "P3"

    # ── Channel recommendation ───────────────────────────────────
    if account.get("opt_out") or risk >= 30:
        channel = None
    elif account.get("email") and intent >= 15:
        channel = "email_warm"
    elif account.get("website"):
        channel = "website_form_or_phone_task"
    elif account.get("phone"):
        channel = "phone_task"
    elif account.get("google_place_id"):
        channel = "in_person_or_phone"
    else:
        channel = "needs_enrichment"

    reason = (
        f"fit={fit:.0f} intent={intent:.0f} access={access:.0f} rev={revenue:.0f} "
        f"risk={risk:.0f} → {priority} via {channel or 'BLOCKED'}"
    )

    return ScoreBreakdown(
        fit=fit, intent=intent, urgency=intent,  # urgency mirrors intent for now
        risk=risk, total=total, priority=priority,
        recommended_channel=channel, reason=reason,
    )

"""
Saudi B2B Revenue Graph — pure data structures + similarity + propagation.

The Revenue Graph is the company's defensive moat. Every interaction
(signal detected, message sent, reply received, deal won/lost) updates
the graph. New leads borrow probability estimates from similar past
outcomes, so the system's accuracy compounds with usage.

This module is pure-Python — persistence is layered on top via a Repository
adapter (SQLAlchemy in production, dict in tests).
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

# ── Node types ─────────────────────────────────────────────────────
NODE_TYPES: tuple[str, ...] = (
    "company",
    "contact",
    "signal",
    "channel",
    "message",
    "objection",
    "outcome",
    "sector",
    "city",
    "campaign",
    "playbook",
)


@dataclass
class GraphNode:
    """A node in the Saudi Revenue Graph."""

    node_id: str
    node_type: str
    label: str
    properties: dict[str, Any] = field(default_factory=dict)
    last_updated: datetime | None = None


# ── Edge types — directional, typed relationships ─────────────────
EDGE_TYPES: tuple[str, ...] = (
    "operates_in",       # company -> sector / city
    "decides_at",        # contact -> company
    "shows_signal",      # company -> signal
    "received",          # company -> message
    "responded_with",    # company -> objection / outcome
    "engaged_via",       # company -> channel
    "matches_playbook",  # company -> playbook
    "similar_to",        # company -> company
    "originated",        # campaign -> message
    "led_to",            # message -> outcome
)


@dataclass
class GraphEdge:
    """A typed edge between two nodes with a confidence weight."""

    src_id: str
    dst_id: str
    edge_type: str
    weight: float = 1.0
    properties: dict[str, Any] = field(default_factory=dict)
    last_updated: datetime | None = None


# ── Outcome types — what we learn from each interaction ──────────
OUTCOME_TYPES: tuple[str, ...] = (
    "no_response",
    "negative_reply",
    "neutral_reply",
    "positive_reply",
    "meeting_booked",
    "demo_held",
    "proposal_sent",
    "deal_won",
    "deal_lost",
    "expansion",
    "churn",
)


# ── Similarity scoring ────────────────────────────────────────────
@dataclass
class CompanyVector:
    """Numeric representation of a company for similarity search."""

    company_id: str
    sector: str | None = None
    city: str | None = None
    size_bucket: str | None = None  # micro / small / mid / large
    has_website: bool = False
    has_booking_page: bool = False
    has_whatsapp_business: bool = False
    is_hiring: bool = False
    runs_ads: bool = False
    has_government_clients: bool = False
    arabic_first: bool = True
    multi_branch: bool = False
    revenue_estimate_sar: float = 0.0


def _categorical_match(a: str | None, b: str | None) -> float:
    if a is None or b is None:
        return 0.0
    return 1.0 if a == b else 0.0


def _bool_match(a: bool, b: bool) -> float:
    return 1.0 if a == b else 0.0


def cosine_similarity(a: CompanyVector, b: CompanyVector) -> float:
    """
    Hybrid similarity:
      - Sector + city + size match  → 0.5 weight
      - Capability flags match      → 0.4 weight
      - Revenue tier proximity      → 0.1 weight
    Returns [0, 1] score.
    """
    cat_score = (
        _categorical_match(a.sector, b.sector) * 0.25
        + _categorical_match(a.city, b.city) * 0.15
        + _categorical_match(a.size_bucket, b.size_bucket) * 0.10
    )
    flag_pairs = [
        (a.has_website, b.has_website),
        (a.has_booking_page, b.has_booking_page),
        (a.has_whatsapp_business, b.has_whatsapp_business),
        (a.is_hiring, b.is_hiring),
        (a.runs_ads, b.runs_ads),
        (a.has_government_clients, b.has_government_clients),
        (a.arabic_first, b.arabic_first),
        (a.multi_branch, b.multi_branch),
    ]
    flag_match = sum(_bool_match(x, y) for x, y in flag_pairs) / len(flag_pairs)
    flag_score = flag_match * 0.4

    # Revenue proximity: closer => higher
    rev_score = 0.0
    if a.revenue_estimate_sar > 0 and b.revenue_estimate_sar > 0:
        ratio = min(a.revenue_estimate_sar, b.revenue_estimate_sar) / max(
            a.revenue_estimate_sar, b.revenue_estimate_sar
        )
        rev_score = ratio * 0.10

    return round(cat_score + flag_score + rev_score, 4)


def find_similar_companies(
    *, target: CompanyVector, candidates: list[CompanyVector], top_k: int = 5
) -> list[tuple[CompanyVector, float]]:
    """Top-k similar companies by hybrid similarity."""
    scored = [(c, cosine_similarity(target, c)) for c in candidates if c.company_id != target.company_id]
    scored.sort(key=lambda x: x[1], reverse=True)
    return scored[:top_k]


# ── Outcome propagation — borrow stats from similar past wins ────
@dataclass
class OutcomeStats:
    """Aggregated outcome distribution for a cohort."""

    cohort_size: int
    reply_rate: float
    booking_rate: float
    win_rate: float
    avg_deal_size_sar: float
    median_cycle_days: float
    confidence: float  # 0..1, scales with cohort size


def aggregate_outcomes(
    outcomes: list[dict[str, Any]], min_cohort: int = 5
) -> OutcomeStats | None:
    """
    Aggregate outcome dicts into stats. Returns None if cohort too small —
    enforces statistical & privacy minimum.

    Each outcome dict expected:
      {responded: bool, booked: bool, won: bool, deal_size_sar: float, cycle_days: int}
    """
    n = len(outcomes)
    if n < min_cohort:
        return None
    replied = sum(1 for o in outcomes if o.get("responded"))
    booked = sum(1 for o in outcomes if o.get("booked"))
    won = sum(1 for o in outcomes if o.get("won"))
    deal_sizes = [o.get("deal_size_sar", 0) for o in outcomes if o.get("won")]
    cycles = sorted(o.get("cycle_days", 0) for o in outcomes if o.get("cycle_days"))
    median = cycles[len(cycles) // 2] if cycles else 0.0
    avg_deal = sum(deal_sizes) / len(deal_sizes) if deal_sizes else 0.0

    # Confidence climbs with cohort size; logarithmic, plateaus around 100
    confidence = min(1.0, math.log10(n + 1) / 2.0)

    return OutcomeStats(
        cohort_size=n,
        reply_rate=round(replied / n, 4),
        booking_rate=round(booked / n, 4),
        win_rate=round(won / n, 4),
        avg_deal_size_sar=round(avg_deal, 2),
        median_cycle_days=round(median, 1),
        confidence=round(confidence, 4),
    )


# ── Probability borrowing — predict for new lead from similar past ────
def predict_outcome_probabilities(
    *,
    target: CompanyVector,
    historical: list[tuple[CompanyVector, dict[str, Any]]],
    top_k: int = 10,
    min_cohort: int = 5,
) -> dict[str, float] | None:
    """
    Predict reply/booking/win probabilities for a new lead by borrowing
    from the top-k most similar historical outcomes.

    historical: list of (vector, outcome_dict) tuples.
    """
    similar = find_similar_companies(
        target=target, candidates=[v for v, _ in historical], top_k=top_k
    )
    if not similar:
        return None
    # Build cohort of outcomes from the top-k similar companies
    sim_ids = {v.company_id for v, _ in similar}
    cohort_outcomes = [o for v, o in historical if v.company_id in sim_ids]
    stats = aggregate_outcomes(cohort_outcomes, min_cohort=min_cohort)
    if stats is None:
        return None
    return {
        "reply_probability": stats.reply_rate,
        "booking_probability": stats.booking_rate,
        "win_probability": stats.win_rate,
        "expected_deal_size_sar": stats.avg_deal_size_sar,
        "expected_cycle_days": stats.median_cycle_days,
        "cohort_size": float(stats.cohort_size),
        "confidence": stats.confidence,
    }


# ── Next-best-action — graph-based recommendation ────────────────
@dataclass
class NextBestAction:
    """A single recommended action with rationale."""

    action: str            # e.g. "send_whatsapp_template_v3"
    channel: str           # whatsapp / email / linkedin / call
    rationale: str         # human-readable explanation in Arabic
    expected_reply_lift: float  # delta vs baseline
    confidence: float      # 0..1
    playbook_id: str | None = None


def recommend_next_action(
    *,
    target: CompanyVector,
    last_outcome: str | None,
    days_since_last_touch: int,
    win_history: dict[str, OutcomeStats] | None = None,
) -> NextBestAction:
    """
    Recommend next best action using simple decision tree on graph state.

    Production version would consult the full graph; this is the
    initial heuristic encoding of Saudi B2B best practice.
    """
    # No prior touch yet
    if last_outcome is None:
        if target.has_whatsapp_business:
            return NextBestAction(
                action="open_whatsapp_with_arabic_personalization",
                channel="whatsapp",
                rationale=(
                    "الشركة تستخدم WhatsApp Business — فتح المحادثة برسالة "
                    "عربية مخصصة يرفع معدل الرد بنسبة 3× مقارنة بالإيميل البارد."
                ),
                expected_reply_lift=2.4,
                confidence=0.7,
            )
        return NextBestAction(
            action="send_email_with_value_first_intro",
            channel="email",
            rationale="نبدأ بإيميل قصير يقدم قيمة محددة قبل أي طلب اجتماع.",
            expected_reply_lift=1.0,
            confidence=0.55,
        )

    # Stalled — no response in >5 days
    if last_outcome == "no_response" and days_since_last_touch > 5:
        return NextBestAction(
            action="multi_channel_followup",
            channel="whatsapp",
            rationale=(
                "5+ أيام بدون رد — التحول لـ WhatsApp برسالة قصيرة + إعادة "
                "صياغة العرض بزاوية مختلفة (مثلاً ROI بدلاً من ميزات)."
            ),
            expected_reply_lift=1.6,
            confidence=0.62,
        )

    # Negative reply — extract objection, route to library
    if last_outcome == "negative_reply":
        return NextBestAction(
            action="objection_handling_response",
            channel="whatsapp",
            rationale="رد سلبي — استخراج الاعتراض من المحتوى وتطبيق المسار المناسب من Objection Library.",
            expected_reply_lift=0.8,
            confidence=0.7,
        )

    # Positive reply — accelerate to demo
    if last_outcome == "positive_reply":
        return NextBestAction(
            action="propose_demo_within_24h",
            channel="whatsapp",
            rationale="رد إيجابي — السرعة (≤24 ساعة) ترفع نسبة الحجز إلى 3.2× في B2B السعودي.",
            expected_reply_lift=3.2,
            confidence=0.85,
        )

    # Fallback
    return NextBestAction(
        action="hold_and_review",
        channel="manual",
        rationale="حالة غير اعتيادية — يحتاج مراجعة بشرية قبل الإجراء التالي.",
        expected_reply_lift=0.0,
        confidence=0.4,
    )


# ── Public summary — what powers the in-product Insights panel ────
def graph_health_summary(
    *,
    n_companies: int,
    n_signals: int,
    n_messages: int,
    n_outcomes: int,
    n_won_deals: int,
) -> dict[str, Any]:
    """High-level health metrics for the Revenue Graph dashboard tile."""
    learning_density = round(n_outcomes / n_companies, 2) if n_companies else 0
    moat_score = min(100, int((n_outcomes * 0.4 + n_signals * 0.3 + n_won_deals * 5) / max(1, n_companies / 100)))
    return {
        "nodes": {
            "companies": n_companies,
            "signals": n_signals,
            "messages": n_messages,
            "outcomes": n_outcomes,
            "won_deals": n_won_deals,
        },
        "learning_density": learning_density,
        "moat_score": moat_score,  # higher = stronger competitive moat
        "ready_for_predictions": n_outcomes >= 50,
    }

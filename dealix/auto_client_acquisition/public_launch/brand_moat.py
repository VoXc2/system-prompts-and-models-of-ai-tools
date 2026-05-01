"""Brand Moat Score — measure competitive defensibility.

Five moat dimensions per MASTER_STRATEGIC_PLAN §6:
  1. Data Moat (Saudi Revenue Graph)
  2. Brand Moat (Saudi-First presence)
  3. Compliance Moat (PDPL Native)
  4. Network Moat (Agency Channel)
  5. Distribution Moat (Operator Network)

Each dimension is scored 0–100. A weighted total is the overall
moat strength. This is a forward-looking metric — it does not gate
Public Launch (PDPL + GateVerdict do that), but it's used in
weekly Founder briefs and investor decks.
"""

from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Mapping


@dataclass(frozen=True)
class BrandMoatDimension:
    key: str
    name_ar: str
    weight: float       # 0.0–1.0
    description_ar: str


BRAND_MOAT_DIMENSIONS: tuple[BrandMoatDimension, ...] = (
    BrandMoatDimension(
        key="data_moat",
        name_ar="Data Moat (Saudi Revenue Graph)",
        weight=0.30,
        description_ar="عمق بيانات العلاقات والإشارات السعودية",
    ),
    BrandMoatDimension(
        key="brand_moat",
        name_ar="Brand Moat (Saudi-First)",
        weight=0.20,
        description_ar="حضور الـ founder + المحتوى العربي + الـ brand awareness",
    ),
    BrandMoatDimension(
        key="compliance_moat",
        name_ar="Compliance Moat (PDPL Native)",
        weight=0.20,
        description_ar="audit trail + DPA + opt-in + ISO 27001",
    ),
    BrandMoatDimension(
        key="network_moat",
        name_ar="Network Moat (Agency Channel)",
        weight=0.20,
        description_ar="عدد + جودة الوكالات الشريكة + revenue share",
    ),
    BrandMoatDimension(
        key="distribution_moat",
        name_ar="Distribution Moat (Operator Network)",
        weight=0.10,
        description_ar="Dealix Operators المعتمدون يبيعون كـ خدمة",
    ),
)


# Sub-criteria scoring (each 0–100 → averaged within a dimension)
DATA_MOAT_SUBSCORES = {
    "events_logged_count": (1_000, 100),       # ≥1000 events = 100
    "messages_per_sector_count": (50, 100),    # ≥50 messages per sector = 100
    "sectors_covered_count": (10, 100),        # ≥10 sectors = 100
}

BRAND_MOAT_SUBSCORES = {
    "linkedin_followers": (5_000, 100),
    "newsletter_subscribers": (1_000, 100),
    "monthly_branded_searches": (500, 100),
    "case_studies_published": (10, 100),
}

COMPLIANCE_MOAT_SUBSCORES = {
    "pdpl_compliance_pct": (100, 100),  # already 0–100
    "iso_27001_progress_pct": (100, 100),
    "audit_count_last_year": (4, 100),
    "dpa_signed_with_customers_pct": (100, 100),
}

NETWORK_MOAT_SUBSCORES = {
    "agency_partners_count": (30, 100),
    "active_referring_agencies_count": (15, 100),
    "agency_revenue_share_paid_sar": (100_000, 100),
}

DISTRIBUTION_MOAT_SUBSCORES = {
    "certified_operators_count": (100, 100),
    "operators_active_last_30d": (50, 100),
    "operator_revenue_share_paid_sar": (50_000, 100),
}

ALL_SUBSCORES = {
    "data_moat": DATA_MOAT_SUBSCORES,
    "brand_moat": BRAND_MOAT_SUBSCORES,
    "compliance_moat": COMPLIANCE_MOAT_SUBSCORES,
    "network_moat": NETWORK_MOAT_SUBSCORES,
    "distribution_moat": DISTRIBUTION_MOAT_SUBSCORES,
}


@dataclass
class BrandMoatScore:
    overall_score: float      # 0–100
    tier: str                 # "fragile" | "emerging" | "defensible" | "dominant"
    dimensions: list[Mapping[str, Any]]
    weakest_dimension: str
    strongest_dimension: str
    next_actions_ar: list[str]
    summary_ar: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def _score_dimension(dim_key: str, state: Mapping[str, Any]) -> float:
    subs = ALL_SUBSCORES.get(dim_key, {})
    if not subs:
        return 0.0
    scores: list[float] = []
    for metric, (target, max_score) in subs.items():
        raw = state.get(metric, 0) or 0
        try:
            v = float(raw)
        except (TypeError, ValueError):
            v = 0.0
        pct = min(v / target, 1.0) * max_score
        scores.append(pct)
    return round(sum(scores) / len(scores), 1)


def _tier_for(score: float) -> str:
    if score >= 80:
        return "dominant"
    if score >= 60:
        return "defensible"
    if score >= 35:
        return "emerging"
    return "fragile"


def _tier_summary(tier: str) -> str:
    return {
        "dominant": "🏆 موقع مهيمن — Dealix لا يُستبدل بسهولة من المنافسين العالميين",
        "defensible": "🛡️ موقع دفاعي — moat واضح لكن يحتاج تعميق",
        "emerging": "🌱 موقع ناشئ — البناء قائم؛ الـ moat لم يكتمل",
        "fragile": "⚠️ موقع هش — المنافسون يقدرون يدخلون السوق بسهولة",
    }[tier]


def compute_brand_moat_score(state: Mapping[str, Any]) -> BrandMoatScore:
    """Compute weighted brand moat score across 5 dimensions.

    Args:
        state: dict with sub-metric keys (see *_SUBSCORES dicts above).

    Returns:
        BrandMoatScore with overall, per-dimension, and recommendations.
    """
    dimensions: list[dict[str, Any]] = []
    weighted_total = 0.0

    for dim in BRAND_MOAT_DIMENSIONS:
        score = _score_dimension(dim.key, state)
        weighted_total += score * dim.weight
        dimensions.append({
            "key": dim.key,
            "name_ar": dim.name_ar,
            "score": score,
            "weight": dim.weight,
            "tier": _tier_for(score),
        })

    overall = round(weighted_total, 1)
    tier = _tier_for(overall)

    weakest = min(dimensions, key=lambda d: d["score"])
    strongest = max(dimensions, key=lambda d: d["score"])

    actions: list[str] = []
    if weakest["score"] < 50:
        actions.append(
            f"ضاعف الجهد على {weakest['name_ar']} — هذه أضعف نقطة دفاعية الآن."
        )
    if overall < 60:
        actions.append("لا تنتقل لـ GCC expansion قبل أن يصبح overall ≥ 60.")
    if overall >= 80:
        actions.append("ابدأ Series-A pitch — عندك moat قابل للعرض.")

    summary = (
        f"Brand Moat Score: {overall}/100 ({tier}). "
        f"الأقوى: {strongest['name_ar']}. "
        f"الأضعف: {weakest['name_ar']}. "
        f"{_tier_summary(tier)}."
    )

    return BrandMoatScore(
        overall_score=overall,
        tier=tier,
        dimensions=dimensions,
        weakest_dimension=weakest["key"],
        strongest_dimension=strongest["key"],
        next_actions_ar=actions,
        summary_ar=summary,
    )

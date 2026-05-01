"""
Dealix Benchmark Score — sales maturity diagnostic per customer.

Each customer gets a composite score (0..100) across 7 dimensions:
  1. Sales maturity
  2. Follow-up discipline
  3. Message quality
  4. Market fit
  5. Offer clarity
  6. Conversion efficiency
  7. Customer success readiness

The score comes with a roadmap: "you're at 42 → here are the 5 steps to 75."
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

DIMENSIONS: tuple[str, ...] = (
    "sales_maturity",
    "follow_up_discipline",
    "message_quality",
    "market_fit",
    "offer_clarity",
    "conversion_efficiency",
    "customer_success_readiness",
)

# Weights summing to 1.0
DIMENSION_WEIGHTS: dict[str, float] = {
    "sales_maturity": 0.15,
    "follow_up_discipline": 0.18,
    "message_quality": 0.15,
    "market_fit": 0.12,
    "offer_clarity": 0.15,
    "conversion_efficiency": 0.15,
    "customer_success_readiness": 0.10,
}


@dataclass
class DimensionScore:
    name: str
    score: float                    # 0..100
    bucket: str                     # weak / developing / strong / exceptional
    summary_ar: str
    next_step_ar: str


@dataclass
class BenchmarkReport:
    customer_id: str
    overall: float                  # 0..100
    bucket: str
    dimensions: list[DimensionScore]
    roadmap: list[str]              # ordered next steps to lift score by 25+
    peer_percentile: float | None = None  # vs sector cohort

    def to_markdown(self) -> str:
        lines = [
            f"# Dealix Benchmark Score — {self.customer_id}",
            f"**Overall: {self.overall}/100** ({self.bucket})",
            "",
            "## التفاصيل",
        ]
        for d in self.dimensions:
            lines.append(f"### {d.name} — {d.score}/100 ({d.bucket})")
            lines.append(d.summary_ar)
            lines.append(f"_الخطوة التالية: {d.next_step_ar}_")
            lines.append("")
        lines.append("## خريطة الطريق")
        for i, step in enumerate(self.roadmap, 1):
            lines.append(f"{i}. {step}")
        return "\n".join(lines)


# ── Bucket helper ─────────────────────────────────────────────────
def _bucket(score: float) -> str:
    if score >= 85:
        return "exceptional"
    if score >= 70:
        return "strong"
    if score >= 50:
        return "developing"
    return "weak"


# ── Per-dimension scorers (pure) ─────────────────────────────────
def _score_sales_maturity(*, has_playbook: bool, has_quota: bool, weekly_pipeline_review: bool) -> DimensionScore:
    s = 0.0
    if has_playbook:
        s += 40
    if has_quota:
        s += 30
    if weekly_pipeline_review:
        s += 30
    s = min(100, s)
    return DimensionScore(
        name="sales_maturity",
        score=s,
        bucket=_bucket(s),
        summary_ar=(
            f"playbook: {'✅' if has_playbook else '❌'}، "
            f"quota: {'✅' if has_quota else '❌'}، "
            f"pipeline review أسبوعي: {'✅' if weekly_pipeline_review else '❌'}."
        ),
        next_step_ar=(
            "ضع playbook قطاعي مكتوب." if not has_playbook
            else "ابدأ pipeline review أسبوعي 30 دقيقة." if not weekly_pipeline_review
            else "جدّد الـ playbook كل ربع سنة بناءً على Pulse."
        ),
    )


def _score_follow_up_discipline(*, median_response_minutes: int, followups_per_lead: float) -> DimensionScore:
    # Inverse of response time (capped) + reward for multi-touch
    response_score = max(0, 100 - (median_response_minutes / 6))  # 600 min = 0
    followup_score = min(100, followups_per_lead * 20)  # 5 follow-ups = 100
    s = round(response_score * 0.6 + followup_score * 0.4, 1)
    return DimensionScore(
        name="follow_up_discipline",
        score=s,
        bucket=_bucket(s),
        summary_ar=(
            f"وقت الرد الوسطي: {median_response_minutes} دقيقة، "
            f"متوسط متابعات لكل lead: {followups_per_lead:.1f}."
        ),
        next_step_ar=(
            "اهدف للرد خلال 30 دقيقة عبر WhatsApp auto-reply."
            if median_response_minutes > 60
            else "أضف 2-3 follow-ups مبرمجة (يوم 3، يوم 7، يوم 14)."
            if followups_per_lead < 3
            else "حافظ على الإيقاع — راقب الـ tracker الأسبوعي."
        ),
    )


def _score_message_quality(*, reply_rate: float, positive_reply_rate: float) -> DimensionScore:
    s = round(min(100, reply_rate * 800) * 0.5 + min(100, positive_reply_rate * 1500) * 0.5, 1)
    return DimensionScore(
        name="message_quality",
        score=s,
        bucket=_bucket(s),
        summary_ar=(
            f"reply rate {reply_rate*100:.1f}%، "
            f"positive replies {positive_reply_rate*100:.1f}%."
        ),
        next_step_ar=(
            "اختبر 3 صيغ subject line مختلفة + قياس open rates."
            if reply_rate < 0.05
            else "حسّن الـ CTA — الأسئلة المغلقة تنتج ردود أكثر."
            if positive_reply_rate < 0.02
            else "ابني library من الرسائل الناجحة + شاركها."
        ),
    )


def _score_market_fit(*, sectors_targeted: int, win_rate_top_sector: float) -> DimensionScore:
    focus_score = 100 - min(100, max(0, sectors_targeted - 3) * 15)  # 1-3 sectors = 100
    win_score = min(100, win_rate_top_sector * 400)  # 25% = 100
    s = round(focus_score * 0.5 + win_score * 0.5, 1)
    return DimensionScore(
        name="market_fit",
        score=s,
        bucket=_bucket(s),
        summary_ar=(
            f"يستهدف {sectors_targeted} قطاع، "
            f"win-rate في القطاع الأفضل {win_rate_top_sector*100:.1f}%."
        ),
        next_step_ar=(
            "ركز على 1-3 قطاعات بدلاً من التشتت." if sectors_targeted > 5
            else "وثّق الـ ICP بدقة — أي حجم/مدينة/قطاع." if win_rate_top_sector < 0.1
            else "وسّع للقطاعات المجاورة بنفس الـ playbook."
        ),
    )


def _score_offer_clarity(*, has_pricing_page: bool, has_case_studies: bool, avg_proposal_pages: float) -> DimensionScore:
    s = 0.0
    if has_pricing_page:
        s += 40
    if has_case_studies:
        s += 30
    if 1 <= avg_proposal_pages <= 5:
        s += 30
    elif avg_proposal_pages > 5:
        s += 10  # too long
    s = min(100, s)
    return DimensionScore(
        name="offer_clarity",
        score=s,
        bucket=_bucket(s),
        summary_ar=(
            f"pricing page: {'✅' if has_pricing_page else '❌'}، "
            f"case studies: {'✅' if has_case_studies else '❌'}، "
            f"متوسط صفحات العرض: {avg_proposal_pages:.0f}."
        ),
        next_step_ar=(
            "أنشئ pricing page شفافة." if not has_pricing_page
            else "اطلب 3 case studies مكتوبة من العملاء الحاليين." if not has_case_studies
            else "اختصر العروض إلى 3-5 صفحات + 1 page summary."
        ),
    )


def _score_conversion_efficiency(*, lead_to_meeting: float, meeting_to_deal: float, deal_to_close: float) -> DimensionScore:
    # Geometric mean — penalizes uneven funnel
    funnel = max(0.001, lead_to_meeting * meeting_to_deal * deal_to_close)
    s = min(100, funnel ** (1/3) * 200)
    s = round(s, 1)
    return DimensionScore(
        name="conversion_efficiency",
        score=s,
        bucket=_bucket(s),
        summary_ar=(
            f"lead→meeting {lead_to_meeting*100:.1f}%، "
            f"meeting→deal {meeting_to_deal*100:.1f}%، "
            f"deal→close {deal_to_close*100:.1f}%."
        ),
        next_step_ar=(
            "حسّن الـ qualification قبل الاجتماع." if lead_to_meeting < 0.10
            else "افحص جودة الـ demo + الـ discovery." if meeting_to_deal < 0.30
            else "راجع التفاوض + الـ closing — المشكلة في النهاية."
        ),
    )


def _score_customer_success_readiness(*, has_onboarding_flow: bool, nps_collected: bool, runs_qbr: bool) -> DimensionScore:
    s = 0.0
    if has_onboarding_flow:
        s += 40
    if nps_collected:
        s += 25
    if runs_qbr:
        s += 35
    return DimensionScore(
        name="customer_success_readiness",
        score=min(100, s),
        bucket=_bucket(s),
        summary_ar=(
            f"onboarding flow: {'✅' if has_onboarding_flow else '❌'}، "
            f"NPS: {'✅' if nps_collected else '❌'}، "
            f"QBR: {'✅' if runs_qbr else '❌'}."
        ),
        next_step_ar=(
            "ابني onboarding flow مكتوب لأول 30 يوم." if not has_onboarding_flow
            else "ابدأ NPS ربع سنوي." if not nps_collected
            else "أضف QBR شهري للحسابات الكبرى."
        ),
    )


# ── Public API: compose all dimensions ────────────────────────────
def compute_benchmark_score(
    *,
    customer_id: str,
    has_playbook: bool = False,
    has_quota: bool = False,
    weekly_pipeline_review: bool = False,
    median_response_minutes: int = 240,
    followups_per_lead: float = 1.0,
    reply_rate: float = 0.0,
    positive_reply_rate: float = 0.0,
    sectors_targeted: int = 1,
    win_rate_top_sector: float = 0.0,
    has_pricing_page: bool = False,
    has_case_studies: bool = False,
    avg_proposal_pages: float = 10,
    lead_to_meeting: float = 0.0,
    meeting_to_deal: float = 0.0,
    deal_to_close: float = 0.0,
    has_onboarding_flow: bool = False,
    nps_collected: bool = False,
    runs_qbr: bool = False,
    peer_percentile: float | None = None,
) -> BenchmarkReport:
    """Compose the full benchmark report for one customer."""
    dims = [
        _score_sales_maturity(
            has_playbook=has_playbook,
            has_quota=has_quota,
            weekly_pipeline_review=weekly_pipeline_review,
        ),
        _score_follow_up_discipline(
            median_response_minutes=median_response_minutes,
            followups_per_lead=followups_per_lead,
        ),
        _score_message_quality(
            reply_rate=reply_rate,
            positive_reply_rate=positive_reply_rate,
        ),
        _score_market_fit(
            sectors_targeted=sectors_targeted,
            win_rate_top_sector=win_rate_top_sector,
        ),
        _score_offer_clarity(
            has_pricing_page=has_pricing_page,
            has_case_studies=has_case_studies,
            avg_proposal_pages=avg_proposal_pages,
        ),
        _score_conversion_efficiency(
            lead_to_meeting=lead_to_meeting,
            meeting_to_deal=meeting_to_deal,
            deal_to_close=deal_to_close,
        ),
        _score_customer_success_readiness(
            has_onboarding_flow=has_onboarding_flow,
            nps_collected=nps_collected,
            runs_qbr=runs_qbr,
        ),
    ]
    overall = round(
        sum(d.score * DIMENSION_WEIGHTS[d.name] for d in dims), 1
    )
    # Roadmap: take the 3 weakest dimensions, in priority order
    weakest = sorted(dims, key=lambda d: d.score)[:5]
    roadmap = [d.next_step_ar for d in weakest]

    return BenchmarkReport(
        customer_id=customer_id,
        overall=overall,
        bucket=_bucket(overall),
        dimensions=dims,
        roadmap=roadmap,
        peer_percentile=peer_percentile,
    )

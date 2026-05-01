"""
Why-Now? Engine — explains why each lead is a priority TODAY.

Every lead surfaced by Dealix gets a Why-Now? rationale combining detected
signals + market timing + cohort context. This kills random outreach and
makes every message feel handcrafted.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any

# ── Signal taxonomy — every signal has weight + freshness decay ────
SIGNAL_WEIGHTS: dict[str, float] = {
    "hiring_sales_rep": 9.0,
    "hiring_marketing": 7.0,
    "hiring_engineering": 5.0,
    "new_branch_opened": 8.5,
    "new_service_launched": 7.5,
    "booking_page_added": 7.0,
    "whatsapp_business_added": 6.5,
    "ads_volume_increased": 6.5,
    "website_redesigned": 5.5,
    "exhibition_participation": 7.5,
    "negative_review_spike": 5.0,
    "sector_pulse_rising": 4.5,
    "tender_published": 9.5,
    "leadership_change": 6.0,
    "funding_round": 8.0,
    "vision2030_alignment": 5.5,
}


@dataclass
class WhyNowSignal:
    """A single timed signal with its detection metadata."""

    signal_type: str
    detected_at: datetime
    source: str              # google_search / google_maps / linkedin / pulse
    evidence_url: str | None = None
    payload: dict[str, Any] = field(default_factory=dict)


def freshness_factor(detected_at: datetime, *, now: datetime | None = None, half_life_days: float = 14) -> float:
    """
    Exponential decay: freshness halves every 14 days.
    A signal detected today = 1.0; 14 days old = 0.5; 28 days = 0.25; 60+ ≈ 0.05.
    """
    n = now or datetime.now(timezone.utc).replace(tzinfo=None)
    detected = detected_at.replace(tzinfo=None) if detected_at.tzinfo else detected_at
    delta_days = max(0.0, (n - detected).total_seconds() / 86400)
    return 0.5 ** (delta_days / half_life_days)


@dataclass
class WhyNowExplanation:
    """A scored rationale shown next to the lead card."""

    company_id: str
    score: float                            # 0..100
    headline_ar: str                        # the one-line "why now"
    detail_ar: str                          # 2-3 sentence justification
    suggested_angle_ar: str                 # the actual sales angle to use
    primary_signals: list[str] = field(default_factory=list)
    decay_warning: str | None = None        # if signals are getting old


# ── Saudi-B2B-specific narrative templates ─────────────────────────
_HEADLINE_TEMPLATES: dict[str, str] = {
    "hiring_sales_rep": "يوظفون SDR الآن — جاهزون لسماع حلول مبيعات",
    "hiring_marketing": "يبنون فريق تسويق — يبحثون عن أدوات",
    "new_branch_opened": "افتتحوا فرعاً جديداً — يحتاجون عملاء سريعاً",
    "new_service_launched": "أطلقوا خدمة جديدة — قمة وقت الـ go-to-market",
    "booking_page_added": "أضافوا صفحة حجز — جاهزون لاستقبال leads",
    "whatsapp_business_added": "فعّلوا WhatsApp Business — قناة مفتوحة",
    "ads_volume_increased": "زادوا إعلاناتهم 40%+ — يستثمرون في النمو",
    "exhibition_participation": "في معرض هذا الشهر — pipeline موسمي عالي",
    "tender_published": "نشروا مناقصة — buying intent مؤكد",
    "leadership_change": "تغيير في القيادة — نافذة لإعادة التقييم",
    "funding_round": "أغلقوا جولة تمويل — لديهم ميزانية للأنفاق",
    "sector_pulse_rising": "قطاعهم صاعد في Pulse هذا الشهر",
    "vision2030_alignment": "متوائمون مع رؤية 2030 — توسع متوقع",
}

_DETAIL_TEMPLATES: dict[str, str] = {
    "hiring_sales_rep": (
        "إعلان توظيف SDR/AE نشر منذ {days} يوم. الشركات في هذه المرحلة "
        "تكون مفتوحة على أدوات تساعد فريقها الجديد على الإنتاج بسرعة. "
        "الزاوية: قلّل وقت ramp-up من 90 يوم إلى 21 يوم."
    ),
    "new_branch_opened": (
        "افتتاح الفرع الجديد منذ {days} يوم يعني ضغط على الإيراد لتغطية "
        "تكاليف الإطلاق. هذه نافذة 60-90 يوم من الـ urgency العالي. "
        "الزاوية: سرعة الـ pipeline لتعويض الإطلاق."
    ),
    "tender_published": (
        "مناقصة منشورة قبل {days} يوم — buying intent مؤكد ومحدد "
        "بالـ scope. الزاوية: قدّم نفسك كمورّد قادر على تنفيذ "
        "متطلبات المناقصة بدقة."
    ),
    "booking_page_added": (
        "إضافة صفحة الحجز قبل {days} يوم تعني انتقالهم إلى نموذج "
        "الـ inbound — يحتاجون مزيد من الزيارات للصفحة. الزاوية: "
        "نملأ صفحتك بـ leads مؤهلة."
    ),
    "ads_volume_increased": (
        "ارتفاع الإنفاق الإعلاني 40%+ خلال {days} يوم — الشركة في "
        "مرحلة توسع. الزاوية: نحسّن CAC الذي يدفعونه حالياً."
    ),
    "funding_round": (
        "جولة تمويل مؤخراً ({days} يوم) — لديهم ميزانية تجريب "
        "أدوات جديدة. الزاوية: ROI سريع قابل للقياس قبل board next."
    ),
    "leadership_change": (
        "تغيير قيادي قبل {days} يوم — القائد الجديد يبحث عن quick wins "
        "في أول 90 يوم. الزاوية: ساعدنا في إثبات نتائج Q1 لمجلس الإدارة."
    ),
}

_ANGLE_TEMPLATES: dict[str, str] = {
    "hiring_sales_rep": "في 21 يوماً نخلي SDR الجديد يحقق quota كاملة بـ playbook + AI drafts.",
    "new_branch_opened": "60 يوم. 50 lead مؤهل. اجتماع واحد على الأقل أسبوعياً. مضمون.",
    "tender_published": "نسلم لكم ملف pre-qualification + 5 موردين بدائل قبل deadline المناقصة.",
    "booking_page_added": "نوصل صفحة الحجز بـ Dealix → كل زائر يصبح lead مؤهل + رد آلي بالعربي.",
    "ads_volume_increased": "Dealix يخفّض CAC 35% بتحويل الـ traffic الموجود إلى محادثات.",
    "funding_round": "30 يوم لإثبات pipeline 5×. تقرير ROI جاهز لمجلس الإدارة.",
    "leadership_change": "في 90 يوم نسلم لك أرقام واضحة قابلة للعرض في أول board.",
    "default": "نتقدم بـ pilot 30 يوم — تدفع فقط على الـ qualified leads.",
}


def explain_why_now(
    *,
    company_id: str,
    signals: list[WhyNowSignal],
    sector: str | None = None,
    sector_pulse_trend: str | None = None,
    now: datetime | None = None,
) -> WhyNowExplanation | None:
    """
    Score and narrate the priority case for contacting this lead today.

    Returns None if no actionable signals (avoid spam — better silence
    than weak rationale).
    """
    if not signals:
        return None

    n = now or datetime.now(timezone.utc).replace(tzinfo=None)
    scored: list[tuple[WhyNowSignal, float]] = []
    for s in signals:
        weight = SIGNAL_WEIGHTS.get(s.signal_type, 2.0)
        fresh = freshness_factor(s.detected_at, now=n)
        scored.append((s, round(weight * fresh, 3)))

    scored.sort(key=lambda x: x[1], reverse=True)
    raw_total = sum(s for _, s in scored)
    score = min(100.0, round(raw_total * 7, 1))  # scale into 0-100

    if score < 8:
        return None  # signals too weak/stale to bother

    # Take the strongest signal as the headline
    primary, _ = scored[0]
    days_old = max(1, int((n - primary.detected_at).total_seconds() / 86400))

    headline = _HEADLINE_TEMPLATES.get(
        primary.signal_type,
        f"إشارة جديدة في قطاعهم: {primary.signal_type}",
    )
    detail = _DETAIL_TEMPLATES.get(
        primary.signal_type,
        "إشارة من السوق تستحق التواصل خلال أسبوع.",
    ).format(days=days_old)
    angle = _ANGLE_TEMPLATES.get(primary.signal_type, _ANGLE_TEMPLATES["default"])

    if sector_pulse_trend == "rising":
        detail += f" والقطاع ({sector}) صاعد في Pulse هذا الشهر."

    decay_warning = None
    if days_old > 21 and primary.signal_type != "tender_published":
        decay_warning = "الإشارة بدأت تتقادم — تواصل خلال 7 أيام أو فقدت قيمتها."

    return WhyNowExplanation(
        company_id=company_id,
        score=score,
        headline_ar=headline,
        detail_ar=detail,
        suggested_angle_ar=angle,
        primary_signals=[s.signal_type for s, _ in scored[:3]],
        decay_warning=decay_warning,
    )


# ── Bulk processing for daily Growth Radar ────────────────────────
def rank_todays_priorities(
    *,
    explanations: list[WhyNowExplanation],
    top_n: int = 20,
) -> list[WhyNowExplanation]:
    """Top-N highest-priority leads to surface in the Growth Radar."""
    return sorted(explanations, key=lambda x: x.score, reverse=True)[:top_n]

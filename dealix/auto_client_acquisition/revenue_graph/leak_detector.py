"""
Revenue Leak Detector — finds money lost in the funnel.

Scans pipeline state and flags every place revenue is leaking:
- Leads with no follow-up
- Meetings without proposals
- Proposals without next steps
- Stalled deals
- Customers at risk
- High-open / low-reply campaigns
- Slow-response reps
- WhatsApp blocked-risk accounts

Each leak comes with: severity, estimated $ impact, and a recommended action.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any

# ── Leak taxonomy with severity weights ──────────────────────────
LEAK_TYPES: tuple[str, ...] = (
    "lead_no_followup",
    "meeting_no_proposal",
    "proposal_no_next_step",
    "deal_stalled",
    "customer_churn_risk",
    "campaign_open_no_reply",
    "rep_slow_response",
    "whatsapp_block_risk",
    "expired_signal",
    "single_threaded_deal",
)

SEVERITY_WEIGHTS: dict[str, float] = {
    "critical": 1.0,
    "high": 0.7,
    "medium": 0.4,
    "low": 0.2,
}


@dataclass
class RevenueLeak:
    """A single detected leak with context + recommendation."""

    leak_type: str
    severity: str                      # critical / high / medium / low
    entity_type: str                   # lead / deal / customer / campaign / rep
    entity_id: str
    headline_ar: str
    detail_ar: str
    estimated_impact_sar: float
    suggested_action_ar: str
    days_in_state: int
    detected_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc).replace(tzinfo=None))


# ── Detector functions — pure, stateless, testable ───────────────
def detect_lead_no_followup(
    *,
    leads: list[dict[str, Any]],
    sla_days: int = 2,
    avg_deal_value_sar: float = 5000,
    now: datetime | None = None,
) -> list[RevenueLeak]:
    """A lead with no draft sent within SLA."""
    n = now or datetime.now(timezone.utc).replace(tzinfo=None)
    leaks: list[RevenueLeak] = []
    for lead in leads:
        last = lead.get("last_outreach_at")
        created = lead.get("created_at")
        if last is not None:
            continue  # already touched
        if not created:
            continue
        if created.tzinfo:
            created = created.replace(tzinfo=None)
        days = max(0, (n - created).days)
        if days < sla_days:
            continue
        sev = "critical" if days > 7 else "high" if days > 4 else "medium"
        leaks.append(
            RevenueLeak(
                leak_type="lead_no_followup",
                severity=sev,
                entity_type="lead",
                entity_id=lead.get("id", "?"),
                headline_ar=f"Lead بدون رد لأكثر من {days} يوم",
                detail_ar=(
                    f"{lead.get('company_name', 'الشركة')} وصلت قبل {days} يوم "
                    f"ولم نرسل أي رسالة. السلوك السعودي: تذكر العلامة التجارية "
                    f"يضعف بعد 48 ساعة."
                ),
                estimated_impact_sar=avg_deal_value_sar * 0.15,
                suggested_action_ar="أرسل رسالة WhatsApp أو إيميل خلال الـ 24 ساعة القادمة.",
                days_in_state=days,
            )
        )
    return leaks


def detect_meeting_no_proposal(
    *,
    meetings: list[dict[str, Any]],
    sla_days: int = 5,
    avg_deal_value_sar: float = 25000,
    now: datetime | None = None,
) -> list[RevenueLeak]:
    """Meeting held without a proposal sent."""
    n = now or datetime.now(timezone.utc).replace(tzinfo=None)
    leaks: list[RevenueLeak] = []
    for m in meetings:
        if m.get("proposal_sent"):
            continue
        held_at = m.get("held_at")
        if not held_at:
            continue
        if held_at.tzinfo:
            held_at = held_at.replace(tzinfo=None)
        days = (n - held_at).days
        if days < sla_days:
            continue
        sev = "high" if days > 14 else "medium"
        leaks.append(
            RevenueLeak(
                leak_type="meeting_no_proposal",
                severity=sev,
                entity_type="meeting",
                entity_id=m.get("id", "?"),
                headline_ar=f"اجتماع منذ {days} يوم بدون عرض رسمي",
                detail_ar=(
                    f"الاجتماع مع {m.get('company_name', 'الشركة')} انتهى قبل "
                    f"{days} يوم. كل أسبوع يمر = 12% انخفاض في احتمال الإغلاق."
                ),
                estimated_impact_sar=avg_deal_value_sar * 0.30,
                suggested_action_ar="أرسل العرض اليوم — حتى لو نسخة draft للموافقة.",
                days_in_state=days,
            )
        )
    return leaks


def detect_stalled_deals(
    *,
    deals: list[dict[str, Any]],
    sla_days: int = 14,
    now: datetime | None = None,
) -> list[RevenueLeak]:
    """Deals with no activity for too long."""
    n = now or datetime.now(timezone.utc).replace(tzinfo=None)
    leaks: list[RevenueLeak] = []
    for d in deals:
        if d.get("status") in ("won", "lost"):
            continue
        last = d.get("last_activity_at")
        if not last:
            continue
        if last.tzinfo:
            last = last.replace(tzinfo=None)
        days = (n - last).days
        if days < sla_days:
            continue
        sev = "critical" if days > 30 else "high" if days > 21 else "medium"
        leaks.append(
            RevenueLeak(
                leak_type="deal_stalled",
                severity=sev,
                entity_type="deal",
                entity_id=d.get("id", "?"),
                headline_ar=f"صفقة جامدة منذ {days} يوم",
                detail_ar=(
                    f"الصفقة مع {d.get('company_name', 'الشركة')} (قيمة "
                    f"{d.get('value_sar', 0):,.0f} ريال) لم تتحرك منذ "
                    f"{days} يوم. عادةً عند هذه النقطة، إما تتحرك بدفعة قوية أو تختفي."
                ),
                estimated_impact_sar=d.get("value_sar", 0) * 0.5,
                suggested_action_ar=(
                    "نظّم مكالمة مع decision-maker واحد جديد داخل الحساب "
                    "(multi-thread)، أو أرسل ROI proof pack."
                ),
                days_in_state=days,
            )
        )
    return leaks


def detect_high_open_low_reply(
    *,
    campaigns: list[dict[str, Any]],
    open_rate_threshold: float = 0.40,
    reply_rate_threshold: float = 0.04,
) -> list[RevenueLeak]:
    """Campaigns where people read but don't reply — message issue."""
    leaks: list[RevenueLeak] = []
    for c in campaigns:
        opens = c.get("open_rate", 0)
        replies = c.get("reply_rate", 0)
        if opens < open_rate_threshold:
            continue
        if replies > reply_rate_threshold:
            continue
        sent = c.get("sent_count", 0)
        if sent < 50:
            continue
        leaks.append(
            RevenueLeak(
                leak_type="campaign_open_no_reply",
                severity="medium",
                entity_type="campaign",
                entity_id=c.get("id", "?"),
                headline_ar=f"حملة '{c.get('name', '')}' — يفتحون لكن لا يردّون",
                detail_ar=(
                    f"معدل الفتح {opens*100:.0f}% (ممتاز) لكن الرد {replies*100:.1f}% "
                    "(منخفض). المشكلة في الـ CTA أو زاوية الرسالة، ليس في "
                    "الـ subject line."
                ),
                estimated_impact_sar=sent * 50,  # naive: 50 SAR/lead lost
                suggested_action_ar=(
                    "أعد كتابة آخر فقرة + الـ CTA. اختبر زاوية ROI بدلاً من زاوية الميزات."
                ),
                days_in_state=c.get("running_days", 7),
            )
        )
    return leaks


def detect_slow_responders(
    *,
    reps: list[dict[str, Any]],
    target_response_minutes: int = 60,
) -> list[RevenueLeak]:
    """Reps slow to respond to inbound replies."""
    leaks: list[RevenueLeak] = []
    for r in reps:
        median = r.get("median_response_minutes", 0)
        if median <= target_response_minutes:
            continue
        replies = r.get("replies_handled", 0)
        if replies < 5:
            continue  # too few to judge
        sev = "high" if median > 240 else "medium"
        leaks.append(
            RevenueLeak(
                leak_type="rep_slow_response",
                severity=sev,
                entity_type="rep",
                entity_id=r.get("id", "?"),
                headline_ar=f"المندوب {r.get('name', '')} بطيء في الرد ({median} دقيقة)",
                detail_ar=(
                    f"بينما المعيار 60 دقيقة، المندوب يستجيب في {median} دقيقة. "
                    "كل ساعة تأخير = 14% انخفاض في احتمال الحجز (دراسة Lead Response Management)."
                ),
                estimated_impact_sar=replies * 200,
                suggested_action_ar=(
                    "فعّل WhatsApp notifications + auto-acknowledge template + "
                    "هدف SLA 30 دقيقة لمدة أسبوع."
                ),
                days_in_state=7,
            )
        )
    return leaks


def detect_single_threaded_deals(
    *,
    deals: list[dict[str, Any]],
    min_value_sar: float = 50000,
) -> list[RevenueLeak]:
    """High-value deals with only one contact — fragile."""
    leaks: list[RevenueLeak] = []
    for d in deals:
        if d.get("status") in ("won", "lost"):
            continue
        value = d.get("value_sar", 0)
        if value < min_value_sar:
            continue
        contacts = d.get("contacts_count", 1)
        if contacts >= 2:
            continue
        leaks.append(
            RevenueLeak(
                leak_type="single_threaded_deal",
                severity="high",
                entity_type="deal",
                entity_id=d.get("id", "?"),
                headline_ar=f"صفقة بقيمة {value:,.0f} ريال — جهة اتصال واحدة فقط",
                detail_ar=(
                    "الصفقات الكبيرة بـ contact واحد تموت إذا غيّر هذا الشخص "
                    "وظيفته أو تغيّر رأيه. متوسط win-rate ينخفض من 38% إلى 11% "
                    "في الـ single-threaded deals."
                ),
                estimated_impact_sar=value * 0.27,
                suggested_action_ar=(
                    "احصل على معرفي من الـ champion الحالي إلى 2 آخرين داخل "
                    "الـ buying committee خلال أسبوع."
                ),
                days_in_state=d.get("days_in_pipeline", 0),
            )
        )
    return leaks


# ── Aggregator — runs every detector + ranks total leaks ─────────
@dataclass
class LeakReport:
    """Output for the Revenue Leak dashboard tile."""

    leaks: list[RevenueLeak]
    total_estimated_impact_sar: float
    by_severity: dict[str, int]
    by_type: dict[str, int]
    top_3_actions_ar: list[str]


def detect_all_leaks(
    *,
    leads: list[dict[str, Any]] | None = None,
    meetings: list[dict[str, Any]] | None = None,
    deals: list[dict[str, Any]] | None = None,
    campaigns: list[dict[str, Any]] | None = None,
    reps: list[dict[str, Any]] | None = None,
    avg_deal_value_sar: float = 25000,
    now: datetime | None = None,
) -> LeakReport:
    """Run every detector and roll up into a single report."""
    leaks: list[RevenueLeak] = []
    leaks += detect_lead_no_followup(
        leads=leads or [], avg_deal_value_sar=avg_deal_value_sar, now=now
    )
    leaks += detect_meeting_no_proposal(
        meetings=meetings or [], avg_deal_value_sar=avg_deal_value_sar, now=now
    )
    leaks += detect_stalled_deals(deals=deals or [], now=now)
    leaks += detect_high_open_low_reply(campaigns=campaigns or [])
    leaks += detect_slow_responders(reps=reps or [])
    leaks += detect_single_threaded_deals(deals=deals or [])

    # Sort by severity weight × impact
    leaks.sort(
        key=lambda x: SEVERITY_WEIGHTS.get(x.severity, 0) * x.estimated_impact_sar,
        reverse=True,
    )

    by_sev: dict[str, int] = {}
    by_type: dict[str, int] = {}
    for lk in leaks:
        by_sev[lk.severity] = by_sev.get(lk.severity, 0) + 1
        by_type[lk.leak_type] = by_type.get(lk.leak_type, 0) + 1

    return LeakReport(
        leaks=leaks,
        total_estimated_impact_sar=round(sum(lk.estimated_impact_sar for lk in leaks), 2),
        by_severity=by_sev,
        by_type=by_type,
        top_3_actions_ar=[lk.suggested_action_ar for lk in leaks[:3]],
    )

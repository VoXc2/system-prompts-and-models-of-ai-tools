"""
Projections — read models computed by replaying the event stream.

Each projection is a deterministic function of (event_stream, filter).
This means: nuke the projection storage, replay events, get identical state.
That property is the foundation of the audit trail and disaster recovery.

Six projections cover the dashboard's needs:
  - AccountTimeline       — chronological story of one account/company
  - DealHealthProjection  — current state + risk signals for one deal
  - CampaignPerformanceProjection  — sent/replied/won per campaign
  - AgentActionLedger     — every AI agent action + approvals
  - ComplianceAuditProjection      — for SDAIA / DPO inspection
  - CustomerROIProjection — what Dealix delivered this period
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Iterable
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any

from auto_client_acquisition.revenue_memory.events import RevenueEvent


# ── 1. Account Timeline ──────────────────────────────────────────
@dataclass
class TimelineEntry:
    occurred_at: datetime
    event_type: str
    headline: str
    payload: dict[str, Any]


@dataclass
class AccountTimeline:
    customer_id: str
    account_id: str
    entries: list[TimelineEntry] = field(default_factory=list)
    first_seen: datetime | None = None
    last_activity: datetime | None = None
    n_messages_sent: int = 0
    n_replies: int = 0
    n_meetings: int = 0
    n_signals: int = 0

    def to_dict(self) -> dict[str, Any]:
        return {
            "customer_id": self.customer_id,
            "account_id": self.account_id,
            "first_seen": self.first_seen.isoformat() if self.first_seen else None,
            "last_activity": self.last_activity.isoformat() if self.last_activity else None,
            "metrics": {
                "messages_sent": self.n_messages_sent,
                "replies": self.n_replies,
                "meetings": self.n_meetings,
                "signals": self.n_signals,
            },
            "entries": [
                {
                    "at": e.occurred_at.isoformat(),
                    "type": e.event_type,
                    "headline": e.headline,
                    "payload": e.payload,
                }
                for e in self.entries
            ],
        }


_TYPE_HEADLINES_AR: dict[str, str] = {
    "lead.created": "أُنشئ lead جديد",
    "lead.qualified": "تمت تأهيل الـ lead",
    "company.enriched": "اكتمل enrichment الشركة",
    "signal.detected": "اكتُشفت إشارة شراء",
    "message.drafted": "تم إعداد رسالة",
    "message.approved": "وافق المستخدم على الرسالة",
    "message.sent": "أُرسلت الرسالة",
    "reply.received": "وصل رد",
    "reply.classified": "تم تصنيف الرد",
    "meeting.booked": "تم حجز اجتماع",
    "meeting.held": "انعقد الاجتماع",
    "deal.created": "أُنشئت صفقة",
    "deal.stage_changed": "تغيرت مرحلة الصفقة",
    "deal.won": "🏆 صفقة مكسوبة",
    "deal.lost": "صفقة ضائعة",
    "deal.stalled": "صفقة جامدة",
    "compliance.opt_out_received": "وصل طلب opt-out",
    "compliance.blocked": "حُظرت رسالة لأسباب امتثال",
}


def build_account_timeline(
    *,
    customer_id: str,
    account_id: str,
    events: Iterable[RevenueEvent],
) -> AccountTimeline:
    """Replay events for one account into a chronological timeline."""
    timeline = AccountTimeline(customer_id=customer_id, account_id=account_id)
    sorted_events = sorted(events, key=lambda e: e.occurred_at)
    for e in sorted_events:
        if e.subject_type not in ("account", "company") or e.subject_id != account_id:
            continue
        if timeline.first_seen is None:
            timeline.first_seen = e.occurred_at
        timeline.last_activity = e.occurred_at
        if e.event_type == "message.sent":
            timeline.n_messages_sent += 1
        elif e.event_type in ("reply.received", "reply.classified"):
            if e.event_type == "reply.received":
                timeline.n_replies += 1
        elif e.event_type in ("meeting.booked", "meeting.held"):
            if e.event_type == "meeting.booked":
                timeline.n_meetings += 1
        elif e.event_type == "signal.detected":
            timeline.n_signals += 1

        timeline.entries.append(
            TimelineEntry(
                occurred_at=e.occurred_at,
                event_type=e.event_type,
                headline=_TYPE_HEADLINES_AR.get(e.event_type, e.event_type),
                payload=e.payload,
            )
        )
    return timeline


# ── 2. Deal Health Projection ────────────────────────────────────
@dataclass
class DealHealthProjection:
    customer_id: str
    deal_id: str
    current_stage: str = "unknown"
    value_sar: float = 0.0
    days_in_current_stage: int = 0
    last_activity_at: datetime | None = None
    risk_flags: list[str] = field(default_factory=list)
    health_score: float = 50.0
    expected_close: datetime | None = None
    stage_history: list[tuple[datetime, str]] = field(default_factory=list)


def build_deal_health(
    *, customer_id: str, deal_id: str, events: Iterable[RevenueEvent], now: datetime
) -> DealHealthProjection:
    """Compute current deal health from its event stream."""
    proj = DealHealthProjection(customer_id=customer_id, deal_id=deal_id)
    last_stage_at = None
    for e in sorted(events, key=lambda x: x.occurred_at):
        if e.subject_type != "deal" or e.subject_id != deal_id:
            continue
        proj.last_activity_at = e.occurred_at
        if e.event_type == "deal.created":
            proj.value_sar = float(e.payload.get("value_sar", 0))
            proj.current_stage = e.payload.get("stage", "open")
            last_stage_at = e.occurred_at
            proj.stage_history.append((e.occurred_at, proj.current_stage))
        elif e.event_type == "deal.stage_changed":
            new_stage = e.payload.get("to_stage", proj.current_stage)
            proj.current_stage = new_stage
            last_stage_at = e.occurred_at
            proj.stage_history.append((e.occurred_at, new_stage))
        elif e.event_type == "deal.won":
            proj.current_stage = "won"
            proj.health_score = 100
            proj.risk_flags = []
        elif e.event_type == "deal.lost":
            proj.current_stage = "lost"
            proj.health_score = 0
        elif e.event_type == "deal.stalled":
            proj.risk_flags.append("stalled")
            proj.health_score = max(0, proj.health_score - 30)

    if last_stage_at and proj.current_stage not in ("won", "lost"):
        proj.days_in_current_stage = max(0, (now - last_stage_at).days)
        if proj.days_in_current_stage > 21:
            proj.risk_flags.append(f"in_stage_{proj.days_in_current_stage}d")
            proj.health_score = max(0, proj.health_score - 20)
    return proj


# ── 3. Campaign Performance Projection ──────────────────────────
@dataclass
class CampaignPerformanceProjection:
    customer_id: str
    campaign_id: str
    sent: int = 0
    replied: int = 0
    meetings_booked: int = 0
    deals_won: int = 0
    revenue_won_sar: float = 0.0
    blocked_compliance: int = 0
    open_rate: float = 0.0
    reply_rate: float = 0.0
    win_rate: float = 0.0


def build_campaign_performance(
    *, customer_id: str, campaign_id: str, events: Iterable[RevenueEvent]
) -> CampaignPerformanceProjection:
    proj = CampaignPerformanceProjection(customer_id=customer_id, campaign_id=campaign_id)
    n_opened = 0
    for e in events:
        if e.payload.get("campaign_id") != campaign_id:
            continue
        if e.event_type == "message.sent":
            proj.sent += 1
        elif e.event_type == "message.opened":
            n_opened += 1
        elif e.event_type == "reply.received":
            proj.replied += 1
        elif e.event_type == "meeting.booked":
            proj.meetings_booked += 1
        elif e.event_type == "deal.won":
            proj.deals_won += 1
            proj.revenue_won_sar += float(e.payload.get("value_sar", 0))
        elif e.event_type == "compliance.blocked":
            proj.blocked_compliance += 1
    if proj.sent:
        proj.open_rate = round(n_opened / proj.sent, 4)
        proj.reply_rate = round(proj.replied / proj.sent, 4)
    if proj.meetings_booked:
        proj.win_rate = round(proj.deals_won / proj.meetings_booked, 4)
    return proj


# ── 4. Agent Action Ledger ──────────────────────────────────────
@dataclass
class AgentAction:
    occurred_at: datetime
    event_type: str  # requested / approved / rejected / executed / failed
    agent_id: str
    task_id: str
    actor: str
    payload: dict[str, Any]


@dataclass
class AgentActionLedger:
    customer_id: str
    actions: list[AgentAction] = field(default_factory=list)
    by_agent: dict[str, int] = field(default_factory=dict)
    by_status: dict[str, int] = field(default_factory=dict)
    requires_review: int = 0


def build_agent_ledger(
    *, customer_id: str, events: Iterable[RevenueEvent]
) -> AgentActionLedger:
    ledger = AgentActionLedger(customer_id=customer_id)
    for e in events:
        if not e.event_type.startswith("agent."):
            continue
        agent_id = e.payload.get("agent_id", "unknown")
        action = AgentAction(
            occurred_at=e.occurred_at,
            event_type=e.event_type,
            agent_id=agent_id,
            task_id=e.payload.get("task_id", ""),
            actor=e.actor,
            payload=e.payload,
        )
        ledger.actions.append(action)
        ledger.by_agent[agent_id] = ledger.by_agent.get(agent_id, 0) + 1
        status = e.event_type.split(".", 1)[1]
        ledger.by_status[status] = ledger.by_status.get(status, 0) + 1
        if e.event_type == "agent.action_requested" and e.payload.get("requires_approval"):
            ledger.requires_review += 1
    return ledger


# ── 5. Compliance Audit Projection ──────────────────────────────
@dataclass
class ComplianceAuditProjection:
    customer_id: str
    consent_recorded: int = 0
    opt_outs: int = 0
    blocked_messages: int = 0
    dsr_received: int = 0
    dsr_completed: int = 0
    last_block_reason: str | None = None


def build_compliance_audit(
    *, customer_id: str, events: Iterable[RevenueEvent]
) -> ComplianceAuditProjection:
    proj = ComplianceAuditProjection(customer_id=customer_id)
    for e in events:
        if e.event_type == "compliance.consent_recorded":
            proj.consent_recorded += 1
        elif e.event_type == "compliance.opt_out_received":
            proj.opt_outs += 1
        elif e.event_type == "compliance.blocked":
            proj.blocked_messages += 1
            proj.last_block_reason = e.payload.get("reason")
        elif e.event_type == "compliance.dsr_received":
            proj.dsr_received += 1
        elif e.event_type == "compliance.dsr_completed":
            proj.dsr_completed += 1
    return proj


# ── 6. Customer ROI Projection ──────────────────────────────────
@dataclass
class CustomerROIProjection:
    customer_id: str
    period_start: datetime | None
    period_end: datetime | None
    n_leads: int = 0
    n_meetings: int = 0
    n_proposals: int = 0
    n_deals_won: int = 0
    revenue_won_sar: float = 0.0
    pipeline_added_sar: float = 0.0


def build_customer_roi(
    *,
    customer_id: str,
    events: Iterable[RevenueEvent],
    period_start: datetime | None = None,
    period_end: datetime | None = None,
) -> CustomerROIProjection:
    proj = CustomerROIProjection(
        customer_id=customer_id,
        period_start=period_start,
        period_end=period_end,
    )
    for e in events:
        if period_start and e.occurred_at < period_start:
            continue
        if period_end and e.occurred_at > period_end:
            continue
        if e.event_type == "lead.created":
            proj.n_leads += 1
        elif e.event_type == "meeting.booked":
            proj.n_meetings += 1
        elif e.event_type == "deal.proposal_sent":
            proj.n_proposals += 1
        elif e.event_type == "deal.created":
            proj.pipeline_added_sar += float(e.payload.get("value_sar", 0))
        elif e.event_type == "deal.won":
            proj.n_deals_won += 1
            proj.revenue_won_sar += float(e.payload.get("value_sar", 0))
    return proj

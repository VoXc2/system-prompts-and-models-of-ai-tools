"""
Replay — entry-point helpers that read the event store and build projections.

These are the functions the API and Copilot call to answer "what's the
state of X?". They never write, never mutate — pure functions of the
event stream.
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from auto_client_acquisition.revenue_memory.event_store import (
    EventStore,
    get_default_store,
)
from auto_client_acquisition.revenue_memory.projections import (
    AccountTimeline,
    AgentActionLedger,
    CampaignPerformanceProjection,
    ComplianceAuditProjection,
    CustomerROIProjection,
    DealHealthProjection,
    build_account_timeline,
    build_agent_ledger,
    build_campaign_performance,
    build_compliance_audit,
    build_customer_roi,
    build_deal_health,
)


def _now() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def replay_for_account(
    *,
    customer_id: str,
    account_id: str,
    store: EventStore | None = None,
) -> AccountTimeline:
    s = store or get_default_store()
    events = list(s.read_for_subject("account", account_id, customer_id=customer_id))
    events += list(s.read_for_subject("company", account_id, customer_id=customer_id))
    return build_account_timeline(
        customer_id=customer_id, account_id=account_id, events=events
    )


def replay_deal_health(
    *,
    customer_id: str,
    deal_id: str,
    store: EventStore | None = None,
) -> DealHealthProjection:
    s = store or get_default_store()
    events = list(s.read_for_subject("deal", deal_id, customer_id=customer_id))
    return build_deal_health(
        customer_id=customer_id, deal_id=deal_id, events=events, now=_now()
    )


def replay_campaign(
    *,
    customer_id: str,
    campaign_id: str,
    store: EventStore | None = None,
) -> CampaignPerformanceProjection:
    s = store or get_default_store()
    events = list(s.read_for_customer(customer_id))
    return build_campaign_performance(
        customer_id=customer_id, campaign_id=campaign_id, events=events
    )


def replay_agent_ledger(
    *,
    customer_id: str,
    store: EventStore | None = None,
) -> AgentActionLedger:
    s = store or get_default_store()
    events = list(s.read_for_customer(customer_id))
    return build_agent_ledger(customer_id=customer_id, events=events)


def replay_compliance_audit(
    *,
    customer_id: str,
    store: EventStore | None = None,
) -> ComplianceAuditProjection:
    s = store or get_default_store()
    events = list(s.read_for_customer(customer_id))
    return build_compliance_audit(customer_id=customer_id, events=events)


def replay_for_customer(
    *,
    customer_id: str,
    period_start: datetime | None = None,
    period_end: datetime | None = None,
    store: EventStore | None = None,
) -> CustomerROIProjection:
    s = store or get_default_store()
    events = list(s.read_for_customer(customer_id, since=period_start, until=period_end))
    return build_customer_roi(
        customer_id=customer_id,
        events=events,
        period_start=period_start,
        period_end=period_end,
    )

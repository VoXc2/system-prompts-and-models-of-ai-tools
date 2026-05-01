"""Smoke tests for the event-sourced Revenue Memory layer."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from auto_client_acquisition.revenue_memory.audit import dsr_export, full_audit_export
from auto_client_acquisition.revenue_memory.event_store import InMemoryEventStore
from auto_client_acquisition.revenue_memory.events import (
    EVENT_TYPES,
    event_from_dict,
    event_to_dict,
    make_event,
)
from auto_client_acquisition.revenue_memory.projections import (
    build_account_timeline,
    build_agent_ledger,
    build_campaign_performance,
    build_compliance_audit,
    build_customer_roi,
    build_deal_health,
)
from auto_client_acquisition.revenue_memory.replay import (
    replay_agent_ledger,
    replay_campaign,
    replay_compliance_audit,
    replay_deal_health,
    replay_for_account,
    replay_for_customer,
)
from auto_client_acquisition.revenue_memory.retention import (
    LEGAL_HOLD_TYPES,
    apply_retention,
    classify_retention_tier,
    is_expired,
    retention_summary,
)
from auto_client_acquisition.revenue_memory.timeline import (
    render_timeline_markdown,
    timeline_to_dashboard_dict,
)


def _now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


# ── events.py ─────────────────────────────────────────────────────
def test_make_event_assigns_unique_id():
    e1 = make_event(event_type="lead.created", customer_id="c1", subject_type="account", subject_id="a1")
    e2 = make_event(event_type="lead.created", customer_id="c1", subject_type="account", subject_id="a1")
    assert e1.event_id != e2.event_id
    assert e1.event_id.startswith("evt_")


def test_make_event_unknown_type_raises():
    with pytest.raises(ValueError):
        make_event(event_type="totally.fake", customer_id="c", subject_type="x", subject_id="y")


def test_event_serialization_round_trip():
    e = make_event(
        event_type="deal.won",
        customer_id="c1",
        subject_type="deal",
        subject_id="d1",
        payload={"value_sar": 50000},
    )
    e2 = event_from_dict(event_to_dict(e))
    assert e2.event_id == e.event_id
    assert e2.payload == e.payload
    assert e2.event_type == "deal.won"


def test_event_taxonomy_no_duplicates():
    assert len(EVENT_TYPES) == len(set(EVENT_TYPES))


# ── event_store.py ────────────────────────────────────────────────
def test_event_store_append_and_count():
    store = InMemoryEventStore()
    e = make_event(event_type="lead.created", customer_id="c1", subject_type="account", subject_id="a1")
    store.append(e)
    assert store.count() == 1
    assert store.count(customer_id="c1") == 1
    assert store.count(customer_id="c2") == 0


def test_event_store_filters_by_subject():
    store = InMemoryEventStore()
    store.append(make_event(event_type="lead.created", customer_id="c1", subject_type="account", subject_id="a1"))
    store.append(make_event(event_type="lead.created", customer_id="c1", subject_type="account", subject_id="a2"))
    a1_events = list(store.read_for_subject("account", "a1", customer_id="c1"))
    assert len(a1_events) == 1
    assert a1_events[0].subject_id == "a1"


def test_event_store_export_import():
    store = InMemoryEventStore()
    store.append(make_event(event_type="lead.created", customer_id="c1", subject_type="account", subject_id="a1"))
    store.append(make_event(event_type="message.sent", customer_id="c1", subject_type="account", subject_id="a1"))
    dump = store.export_all()
    new_store = InMemoryEventStore()
    new_store.import_all(dump)
    assert new_store.count() == 2


# ── projections.py — account timeline ────────────────────────────
def test_account_timeline_replays_metrics():
    n = _now()
    events = [
        make_event(event_type="lead.created", customer_id="c1", subject_type="account", subject_id="a1", occurred_at=n - timedelta(days=10)),
        make_event(event_type="message.sent", customer_id="c1", subject_type="account", subject_id="a1", occurred_at=n - timedelta(days=8)),
        make_event(event_type="reply.received", customer_id="c1", subject_type="account", subject_id="a1", occurred_at=n - timedelta(days=7)),
        make_event(event_type="meeting.booked", customer_id="c1", subject_type="account", subject_id="a1", occurred_at=n - timedelta(days=5)),
        make_event(event_type="signal.detected", customer_id="c1", subject_type="account", subject_id="a1", occurred_at=n - timedelta(days=4)),
    ]
    timeline = build_account_timeline(customer_id="c1", account_id="a1", events=events)
    assert timeline.n_messages_sent == 1
    assert timeline.n_replies == 1
    assert timeline.n_meetings == 1
    assert timeline.n_signals == 1
    assert timeline.first_seen is not None
    assert timeline.last_activity > timeline.first_seen


def test_account_timeline_empty_returns_empty():
    timeline = build_account_timeline(customer_id="c1", account_id="a1", events=[])
    assert timeline.n_messages_sent == 0
    assert timeline.first_seen is None


def test_timeline_markdown_render():
    n = _now()
    events = [
        make_event(event_type="lead.created", customer_id="c1", subject_type="account", subject_id="a1", occurred_at=n),
    ]
    timeline = build_account_timeline(customer_id="c1", account_id="a1", events=events)
    md = render_timeline_markdown(timeline)
    assert "Timeline" in md
    assert "a1" in md


def test_timeline_dashboard_dict():
    n = _now()
    events = [make_event(event_type="lead.created", customer_id="c1", subject_type="account", subject_id="a1", occurred_at=n)]
    timeline = build_account_timeline(customer_id="c1", account_id="a1", events=events)
    d = timeline_to_dashboard_dict(timeline)
    assert "metrics" in d
    assert d["account_id"] == "a1"


# ── projections.py — deal health ──────────────────────────────────
def test_deal_health_basic():
    n = _now()
    events = [
        make_event(event_type="deal.created", customer_id="c1", subject_type="deal", subject_id="d1",
                   occurred_at=n - timedelta(days=5), payload={"value_sar": 100000, "stage": "discovery"}),
        make_event(event_type="deal.stage_changed", customer_id="c1", subject_type="deal", subject_id="d1",
                   occurred_at=n - timedelta(days=2), payload={"to_stage": "proposal"}),
    ]
    proj = build_deal_health(customer_id="c1", deal_id="d1", events=events, now=n)
    assert proj.value_sar == 100000
    assert proj.current_stage == "proposal"
    assert proj.days_in_current_stage == 2
    assert len(proj.stage_history) == 2


def test_deal_health_stalled_flag():
    n = _now()
    events = [
        make_event(event_type="deal.created", customer_id="c1", subject_type="deal", subject_id="d1",
                   occurred_at=n - timedelta(days=30), payload={"value_sar": 50000, "stage": "open"}),
    ]
    proj = build_deal_health(customer_id="c1", deal_id="d1", events=events, now=n)
    assert any(f.startswith("in_stage_") for f in proj.risk_flags)


def test_deal_health_won_zeroes_risk():
    n = _now()
    events = [
        make_event(event_type="deal.created", customer_id="c1", subject_type="deal", subject_id="d1",
                   occurred_at=n - timedelta(days=10), payload={"value_sar": 100000}),
        make_event(event_type="deal.won", customer_id="c1", subject_type="deal", subject_id="d1",
                   occurred_at=n, payload={}),
    ]
    proj = build_deal_health(customer_id="c1", deal_id="d1", events=events, now=n)
    assert proj.health_score == 100
    assert proj.current_stage == "won"


# ── projections.py — campaign ────────────────────────────────────
def test_campaign_performance():
    events = []
    for _ in range(10):
        events.append(make_event(event_type="message.sent", customer_id="c1", subject_type="campaign", subject_id="camp1",
                                payload={"campaign_id": "camp1"}))
    for _ in range(2):
        events.append(make_event(event_type="reply.received", customer_id="c1", subject_type="campaign", subject_id="camp1",
                                payload={"campaign_id": "camp1"}))
    proj = build_campaign_performance(customer_id="c1", campaign_id="camp1", events=events)
    assert proj.sent == 10
    assert proj.replied == 2
    assert proj.reply_rate == 0.2


# ── projections.py — agent ledger ────────────────────────────────
def test_agent_ledger_counts():
    events = [
        make_event(event_type="agent.action_requested", customer_id="c1", subject_type="agent_task", subject_id="t1",
                   payload={"agent_id": "outreach", "task_id": "t1", "requires_approval": True}),
        make_event(event_type="agent.action_approved", customer_id="c1", subject_type="agent_task", subject_id="t1",
                   payload={"agent_id": "outreach", "task_id": "t1"}),
        make_event(event_type="agent.action_executed", customer_id="c1", subject_type="agent_task", subject_id="t1",
                   payload={"agent_id": "outreach", "task_id": "t1"}),
    ]
    ledger = build_agent_ledger(customer_id="c1", events=events)
    assert ledger.by_agent.get("outreach") == 3
    assert ledger.by_status.get("action_executed") == 1
    assert ledger.requires_review == 1


# ── projections.py — compliance audit ────────────────────────────
def test_compliance_audit_counts_opt_outs():
    events = [
        make_event(event_type="compliance.consent_recorded", customer_id="c1", subject_type="contact", subject_id="x"),
        make_event(event_type="compliance.opt_out_received", customer_id="c1", subject_type="contact", subject_id="y"),
        make_event(event_type="compliance.blocked", customer_id="c1", subject_type="message", subject_id="m1",
                   payload={"reason": "no_consent"}),
    ]
    audit = build_compliance_audit(customer_id="c1", events=events)
    assert audit.consent_recorded == 1
    assert audit.opt_outs == 1
    assert audit.blocked_messages == 1
    assert audit.last_block_reason == "no_consent"


# ── projections.py — customer ROI ────────────────────────────────
def test_customer_roi_aggregates():
    events = [
        make_event(event_type="lead.created", customer_id="c1", subject_type="account", subject_id="a1"),
        make_event(event_type="meeting.booked", customer_id="c1", subject_type="meeting", subject_id="m1"),
        make_event(event_type="deal.created", customer_id="c1", subject_type="deal", subject_id="d1",
                   payload={"value_sar": 50000}),
        make_event(event_type="deal.won", customer_id="c1", subject_type="deal", subject_id="d1",
                   payload={"value_sar": 50000}),
    ]
    roi = build_customer_roi(customer_id="c1", events=events)
    assert roi.n_leads == 1
    assert roi.n_meetings == 1
    assert roi.n_deals_won == 1
    assert roi.revenue_won_sar == 50000


# ── replay.py end-to-end ─────────────────────────────────────────
def test_replay_for_account_via_store():
    store = InMemoryEventStore()
    n = _now()
    store.append(make_event(event_type="lead.created", customer_id="c1", subject_type="account", subject_id="a1", occurred_at=n))
    store.append(make_event(event_type="message.sent", customer_id="c1", subject_type="account", subject_id="a1", occurred_at=n))
    timeline = replay_for_account(customer_id="c1", account_id="a1", store=store)
    assert timeline.n_messages_sent == 1


def test_replay_for_customer_via_store():
    store = InMemoryEventStore()
    store.append(make_event(event_type="deal.won", customer_id="c1", subject_type="deal", subject_id="d1",
                             payload={"value_sar": 25000}))
    roi = replay_for_customer(customer_id="c1", store=store)
    assert roi.revenue_won_sar == 25000


# ── retention.py ─────────────────────────────────────────────────
def test_retention_classifies_legal_hold():
    assert classify_retention_tier("compliance.consent_recorded") == "legal_hold"
    assert classify_retention_tier("compliance.opt_out_received") == "legal_hold"


def test_retention_classifies_operational():
    assert classify_retention_tier("message.opened") == "operational"
    assert classify_retention_tier("signal.detected") == "operational"


def test_retention_default_is_business_record():
    assert classify_retention_tier("lead.created") == "business_record"
    assert classify_retention_tier("deal.won") == "business_record"


def test_retention_legal_hold_never_expires():
    n = _now()
    e = make_event(
        event_type="compliance.consent_recorded",
        customer_id="c1", subject_type="contact", subject_id="x",
        occurred_at=n - timedelta(days=365 * 100),  # 100 years
    )
    assert is_expired(e, now=n) is False


def test_apply_retention_keeps_legal_hold_drops_old_business():
    n = _now()
    legal = make_event(
        event_type="compliance.opt_out_received",
        customer_id="c1", subject_type="contact", subject_id="x",
        occurred_at=n - timedelta(days=365 * 5),
    )
    old_lead = make_event(
        event_type="lead.created", customer_id="c1", subject_type="account", subject_id="a",
        occurred_at=n - timedelta(days=365 * 5),
    )
    fresh = make_event(
        event_type="lead.created", customer_id="c1", subject_type="account", subject_id="b",
    )
    kept, removed = apply_retention([legal, old_lead, fresh], now=n)
    kept_ids = {e.event_id for e in kept}
    assert legal.event_id in kept_ids
    assert fresh.event_id in kept_ids
    assert old_lead.event_id in removed


def test_apply_retention_tombstones_old_operational():
    n = _now()
    old_op = make_event(
        event_type="message.opened",
        customer_id="c1", subject_type="message", subject_id="m1",
        occurred_at=n - timedelta(days=200),
        payload={"ip": "192.0.2.1"},
    )
    kept, removed = apply_retention([old_op], now=n)
    assert len(kept) == 1
    assert kept[0].event_type.endswith(".tombstoned")
    assert kept[0].payload.get("_tombstoned") is True
    # Original PII (ip) is gone
    assert "ip" not in kept[0].payload


def test_retention_summary_counts():
    n = _now()
    events = [
        make_event(event_type="message.opened", customer_id="c1", subject_type="message", subject_id="m"),
        make_event(event_type="lead.created", customer_id="c1", subject_type="account", subject_id="a"),
        make_event(event_type="compliance.consent_recorded", customer_id="c1", subject_type="contact", subject_id="x"),
    ]
    s = retention_summary(events)
    assert s["operational"] == 1
    assert s["business_record"] == 1
    assert s["legal_hold"] == 1


# ── audit.py ─────────────────────────────────────────────────────
def test_full_audit_export_filters_customer():
    events = [
        make_event(event_type="lead.created", customer_id="c1", subject_type="account", subject_id="a"),
        make_event(event_type="lead.created", customer_id="c2", subject_type="account", subject_id="b"),
    ]
    out = full_audit_export(customer_id="c1", events=events)
    assert len(out) == 1
    assert out[0]["customer_id"] == "c1"


def test_dsr_export_finds_subject_by_id_or_payload():
    events = [
        make_event(event_type="lead.created", customer_id="c1", subject_type="contact", subject_id="ali@example.sa"),
        make_event(event_type="message.sent", customer_id="c1", subject_type="message", subject_id="m1",
                   payload={"contact_id": "ali@example.sa"}),
    ]
    out = dsr_export(customer_id="c1", data_subject_id="ali@example.sa", events=events)
    assert out["n_events"] == 2
    assert out["right_invoked"].startswith("Right of access")

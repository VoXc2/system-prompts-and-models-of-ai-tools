"""Unit tests for the Revenue Company OS layer."""

from __future__ import annotations

import pytest

from auto_client_acquisition.revenue_company_os import (
    REVENUE_EDGE_TYPES,
    REVENUE_WORK_UNIT_TYPES,
    RevenueActionGraph,
    RevenueProofLedger,
    aggregate_work_units,
    build_card_from_event,
    build_channel_health_snapshot,
    build_command_feed_for_customer,
    build_growth_memory_demo,
    build_opportunity_factory_demo,
    build_revenue_action_graph_demo,
    build_revenue_proof_ledger_demo,
    build_revenue_work_unit,
    build_service_factory_demo,
    build_weekly_self_improvement_report,
    instantiate_service,
    revenue_os_command_feed_demo,
)


# ── Event → card ────────────────────────────────────────────
def test_email_event_returns_arabic_card():
    card = build_card_from_event({
        "event_type": "email.received",
        "customer_id": "c1",
        "payload": {"from": "ali@example.sa", "subject": "نطلب عرض"},
    })
    assert card["type"] == "email_lead"
    assert any("؀" <= ch <= "ۿ" for ch in card["title_ar"])
    assert card["live_send_allowed"] is False


def test_low_review_returns_high_risk():
    card = build_card_from_event({
        "event_type": "review.created",
        "payload": {"rating": 1, "text": "تأخير في الرد"},
    })
    assert card["risk_level"] == "high"


def test_risk_blocked_event_high_risk():
    card = build_card_from_event({
        "event_type": "risk.blocked",
        "payload": {"reason_ar": "محاولة cold WhatsApp"},
    })
    assert card["risk_level"] == "high"
    assert "فهم" in card["buttons_ar"]


def test_unknown_event_returns_action_required():
    card = build_card_from_event({"event_type": "totally.unknown"})
    assert card["type"] == "action_required"
    assert card["live_send_allowed"] is False


# ── Command feed ────────────────────────────────────────────
def test_command_feed_demo_has_8_events():
    feed = revenue_os_command_feed_demo()
    assert feed["feed_size"] == 8


def test_command_feed_sorts_high_risk_first():
    feed = revenue_os_command_feed_demo()
    cards = feed["cards"]
    assert cards[0]["risk_level"] == "high"


def test_command_feed_for_customer_empty():
    feed = build_command_feed_for_customer(customer_id="c1", events=[])
    assert feed["feed_size"] == 0
    assert feed["cards"] == []


# ── Revenue Work Units ──────────────────────────────────────
def test_rwu_types_count():
    assert len(REVENUE_WORK_UNIT_TYPES) >= 18


def test_build_rwu_validates_type():
    with pytest.raises(ValueError):
        build_revenue_work_unit(unit_type="bogus")


def test_build_rwu_returns_valid_unit():
    u = build_revenue_work_unit(
        unit_type="opportunity_created",
        customer_id="c1",
        revenue_influenced_sar=18000,
    )
    assert u["unit_type"] == "opportunity_created"
    assert u["revenue_influenced_sar"] == 18000.0


def test_aggregate_work_units_sums_revenue():
    units = [
        build_revenue_work_unit(unit_type="opportunity_created",
                                customer_id="c1", revenue_influenced_sar=10000),
        build_revenue_work_unit(unit_type="opportunity_created",
                                customer_id="c1", revenue_influenced_sar=20000),
        build_revenue_work_unit(unit_type="risk_blocked",
                                customer_id="c1", risk_level="high"),
    ]
    agg = aggregate_work_units(units)
    assert agg["total_units"] == 3
    assert agg["total_revenue_influenced_sar"] == 30000.0
    assert agg["risks_blocked"] == 1


# ── Revenue Action Graph ────────────────────────────────────
def test_action_graph_edge_types_count():
    assert len(REVENUE_EDGE_TYPES) >= 12


def test_action_graph_add_edge_validates():
    g = RevenueActionGraph()
    with pytest.raises(ValueError):
        g.add_edge(edge_type="bogus", src_id="a", dst_id="b")


def test_action_graph_demo_has_two_customers():
    out = build_revenue_action_graph_demo()
    assert "summary_a" in out
    assert "summary_b" in out
    assert out["summary_a"]["outcome_score"] > 0


def test_action_graph_what_works():
    g = RevenueActionGraph()
    g.add_edge(edge_type="proposal_led_to_payment", src_id="p1", dst_id="pay1",
               customer_id="c1")
    g.add_edge(edge_type="reply_led_to_meeting", src_id="r1", dst_id="m1",
               customer_id="c1")
    summary = g.what_works_for_customer("c1")
    assert summary["total_edges"] == 2
    assert summary["outcome_score"] > 0


# ── Channel Health ──────────────────────────────────────────
def test_channel_health_snapshot_returns_score():
    out = build_channel_health_snapshot()
    assert "channels" in out
    assert "overall_score" in out


def test_channel_health_flags_risky_channel():
    out = build_channel_health_snapshot(metrics_per_channel={
        "email": {"bounce_rate": 0.20, "complaint_rate": 0.01,
                  "opt_out_rate": 0.30, "reply_rate": 0.001},
    })
    assert "email" in out["channels_at_risk"]


# ── Opportunity factory ─────────────────────────────────────
def test_opportunity_factory_returns_5_opps():
    out = build_opportunity_factory_demo(limit=5)
    assert out["count"] == 5
    for opp in out["opportunities"]:
        assert opp["live_send_allowed"] is False


def test_opportunity_factory_blocks_unsafe_actions():
    out = build_opportunity_factory_demo()
    notes = " ".join(out["do_not_do_ar"])
    assert "scraping" in notes.lower() or "scraping" in notes


# ── Service factory ────────────────────────────────────────
def test_instantiate_service_known():
    out = instantiate_service(
        service_id="first_10_opportunities_sprint",
        customer_id="c1",
    )
    assert "intake" in out
    assert "workflow" in out
    assert "quote" in out
    assert out["live_send_allowed"] is False


def test_instantiate_service_unknown():
    out = instantiate_service(service_id="totally_unknown")
    assert "error" in out


def test_service_factory_demo_returns_4_services():
    out = build_service_factory_demo()
    assert len(out["instantiations"]) == 4


# ── Proof Ledger ────────────────────────────────────────────
def test_proof_ledger_appends_units():
    led = RevenueProofLedger()
    led.append_work_unit(build_revenue_work_unit(
        unit_type="opportunity_created", customer_id="c1",
        revenue_influenced_sar=10000,
    ))
    summary = led.summary_for_customer("c1")
    assert summary["totals"]["opportunities_created"] == 1


def test_proof_ledger_rejects_unknown_type():
    led = RevenueProofLedger()
    with pytest.raises(ValueError):
        led.append_work_unit({"unit_type": "totally_bogus"})


def test_proof_ledger_demo_has_revenue():
    out = build_revenue_proof_ledger_demo()
    assert out["totals"]["revenue_influenced_sar"] > 0
    assert out["totals"]["risks_blocked"] >= 2


# ── Growth Memory ───────────────────────────────────────────
def test_growth_memory_demo_has_top_objections():
    out = build_growth_memory_demo()
    assert out["summary"]["top_objections"]


def test_growth_memory_best_message():
    out = build_growth_memory_demo()
    assert out["best_message_training"]["sector"] == "training"


# ── Self-improvement loop ───────────────────────────────────
def test_self_improvement_low_approval_recommends_fix():
    out = build_weekly_self_improvement_report(weekly_metrics={
        "approval_rate": 0.10,
    })
    assert out["recommendations_ar"]
    assert any("approval_rate" in r for r in out["recommendations_ar"])


def test_self_improvement_blocked_actions_high_recommends_review():
    out = build_weekly_self_improvement_report(weekly_metrics={
        "approval_rate": 0.5, "blocked_actions": 25,
    })
    assert any("منع" in r for r in out["recommendations_ar"])


def test_self_improvement_returns_best_service():
    out = build_weekly_self_improvement_report(weekly_metrics={
        "service_revenue_sar": {
            "first_10_opportunities_sprint": 1500,
            "growth_os_monthly": 5000,
        },
    })
    assert out["best_service_id"] == "growth_os_monthly"

"""Unit tests for Launch Ops."""

from __future__ import annotations

import pytest

from auto_client_acquisition.launch_ops import (
    PRIVATE_BETA_OFFER,
    build_12_min_demo_flow,
    build_close_script,
    build_daily_launch_scorecard,
    build_discovery_questions,
    build_first_20_segments,
    build_followup_message,
    build_launch_readiness,
    build_objection_responses,
    build_outreach_message,
    build_private_beta_offer,
    build_private_beta_safety_notes,
    build_reply_handlers,
    build_weekly_launch_scorecard,
    decide_go_no_go,
    private_beta_faq,
    record_launch_event,
)


# ── Private Beta ─────────────────────────────────────────────
def test_private_beta_offer_has_essentials():
    o = build_private_beta_offer()
    assert o["price_sar"] == 499
    assert o["duration_days"] == 7
    assert o["live_send_allowed"] is False
    assert o["approval_required"] is True
    assert len(o["deliverables_ar"]) >= 4


def test_private_beta_offer_seats_override():
    o = build_private_beta_offer(seats_remaining=2)
    assert o["seats_available"] == 2


def test_private_beta_safety_notes_blocks_live():
    s = build_private_beta_safety_notes()
    text = " ".join(s["do_not_do_ar"])
    assert "live" in text.lower() or "عشوائي" in text or "تلقائي" in text
    assert any("PDPL" in line for line in s["do_not_do_ar"])


def test_private_beta_faq_arabic():
    faq = private_beta_faq()
    assert len(faq) >= 4
    for item in faq:
        assert any("؀" <= ch <= "ۿ" for ch in item["q_ar"])
        assert any("؀" <= ch <= "ۿ" for ch in item["a_ar"])


# ── Demo Flow ────────────────────────────────────────────────
def test_demo_flow_is_12_minutes():
    f = build_12_min_demo_flow()
    assert f["duration_minutes"] == 12
    assert len(f["minute_by_minute_ar"]) == 6


def test_demo_discovery_has_5_questions():
    out = build_discovery_questions()
    assert len(out) == 5


def test_objection_responses_cover_essentials():
    out = build_objection_responses()
    for k in ("price", "timing", "trust", "complexity", "data_privacy"):
        assert k in out


def test_close_script_arabic():
    out = build_close_script()
    assert len(out["close_sequence_ar"]) >= 3
    assert any("؀" <= ch <= "ۿ" for ch in out["close_template_ar"])


# ── Outreach ─────────────────────────────────────────────────
def test_first_20_has_4_segments_total_20():
    out = build_first_20_segments()
    assert out["total_targets"] == 20
    assert len(out["segments"]) == 4
    assert sum(s["count"] for s in out["segments"]) == 20


def test_outreach_message_is_arabic_and_drafts_only():
    out = build_outreach_message("agency_b2b", name="أحمد")
    assert any("؀" <= ch <= "ۿ" for ch in out["body_ar"])
    assert out["live_send_allowed"] is False


def test_outreach_unknown_segment_falls_back():
    out = build_outreach_message("totally_unknown", name="X")
    assert out["body_ar"]


def test_followup_step_2_different_from_1():
    s1 = build_followup_message("training_consulting", step=1, name="X")
    s2 = build_followup_message("training_consulting", step=2, name="X")
    assert s1["body_ar"] != s2["body_ar"]


def test_followup_step_3_archives():
    s3 = build_followup_message("agency_b2b", step=3, name="X")
    assert s3["kind"] == "followup_3_final"


def test_reply_handlers_include_critical():
    h = build_reply_handlers()
    for k in ("interested", "needs_more_info", "price_objection",
              "not_now", "no_thanks", "unsubscribe"):
        assert k in h


# ── Go / No-Go ───────────────────────────────────────────────
def test_readiness_all_false_returns_zero_pct():
    r = build_launch_readiness(statuses={})
    assert r["passed_pct"] == 0.0
    assert r["passed_gates"] == 0
    assert len(r["blockers_ar"]) == r["total_gates"]


def test_readiness_all_true_returns_full_pct():
    statuses = {gate["id"]: True for gate in
                __import__("auto_client_acquisition.launch_ops",
                           fromlist=["LAUNCH_GATES"]).go_no_go.LAUNCH_GATES}
    r = build_launch_readiness(statuses=statuses)
    assert r["passed_pct"] == 100.0
    assert r["passed_gates"] == r["total_gates"]


def test_go_no_go_blocks_when_no_secrets_fails():
    decision = decide_go_no_go(statuses={"tests_passed": True,
                                         "routes_check": True,
                                         "no_secrets": False,
                                         "staging_health": True,
                                         "live_sends_disabled": True})
    assert decision["verdict"] == "no_go"


def test_go_no_go_blocks_when_live_sends_enabled():
    decision = decide_go_no_go(statuses={"tests_passed": True,
                                         "routes_check": True,
                                         "no_secrets": True,
                                         "staging_health": True,
                                         "live_sends_disabled": False})
    assert decision["verdict"] == "no_go"


def test_go_no_go_passes_with_critical_and_70pct():
    statuses = {
        "tests_passed": True, "routes_check": True, "no_secrets": True,
        "staging_health": True, "supabase_staging": True,
        "service_catalog": True, "private_beta_page": True,
        "first_20_ready": True, "live_sends_disabled": True,
        "payment_manual_ready": False,  # 9/10 = 90%
    }
    decision = decide_go_no_go(statuses=statuses)
    assert decision["verdict"] == "go"


# ── Scorecard ────────────────────────────────────────────────
def test_record_event_unknown_raises():
    with pytest.raises(ValueError):
        record_launch_event(event_type="totally_invalid")


def test_record_event_appends_to_log():
    log: list = []
    record_launch_event(event_type="outreach_sent", event_log=log)
    assert len(log) == 1
    assert log[0]["event_type"] == "outreach_sent"


def test_daily_scorecard_aggregates():
    events = [{"event_type": "outreach_sent"}] * 12 + \
             [{"event_type": "demo_booked"}] * 2
    s = build_daily_launch_scorecard(events=events)
    assert s["metrics"]["outreach_sent"] == 12
    assert s["metrics"]["demo_booked"] == 2
    assert s["progress"]["outreach_sent"]["pct"] == 60.0  # 12/20 = 60%


def test_weekly_scorecard_returns_verdict():
    events = [{"event_type": "outreach_sent"}] * 50 + \
             [{"event_type": "pilot_paid"}] * 2
    s = build_weekly_launch_scorecard(events=events)
    assert s["verdict"] == "on_track"


def test_weekly_scorecard_needs_focus_for_low_demos():
    events = [{"event_type": "outreach_sent"}] * 5
    s = build_weekly_launch_scorecard(events=events)
    assert s["verdict"] == "needs_focus"


# ── Constants exposed ────────────────────────────────────────
def test_private_beta_offer_constant_exposed():
    assert PRIVATE_BETA_OFFER["price_sar"] == 499
    assert PRIVATE_BETA_OFFER["live_send_allowed"] is False

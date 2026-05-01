"""Unit tests for the Intelligence Layer."""

from __future__ import annotations

import pytest

from auto_client_acquisition.intelligence_layer import (
    DecisionMemory,
    EDGE_TYPES,
    INTEL_MISSIONS,
    ActionGraph,
    analyze_competitive_move,
    build_board_brief,
    build_command_feed_demo,
    build_growth_brain,
    build_revenue_dna_demo,
    compute_trust_score,
    extract_revenue_dna,
    learn_from_decision,
    list_intel_missions,
    recommend_missions,
    simulate_opportunity,
)


# ── Growth Brain ─────────────────────────────────────────────
def test_growth_brain_builds_with_defaults():
    brain = build_growth_brain()
    assert brain.customer_id == "demo"
    assert "whatsapp" in brain.channels_connected
    assert brain.preferred_tone == "warm"


def test_growth_brain_autopilot_readiness():
    new_brain = build_growth_brain({
        "learning_signal_count": 5, "accept_rate_30d": 0.2,
        "channels_connected": ("whatsapp",),
    })
    assert new_brain.is_ready_for_autopilot() is False

    mature_brain = build_growth_brain({
        "learning_signal_count": 50, "accept_rate_30d": 0.55,
        "channels_connected": ("whatsapp", "gmail"),
    })
    assert mature_brain.is_ready_for_autopilot() is True


# ── Command Feed ─────────────────────────────────────────────
def test_command_feed_returns_arabic_cards():
    out = build_command_feed_demo()
    assert out["feed_size"] >= 5
    for card in out["cards"]:
        assert len(card["buttons_ar"]) <= 3
        assert any("؀" <= ch <= "ۿ" for ch in card["title_ar"])


def test_command_feed_includes_critical_card_types():
    out = build_command_feed_demo()
    types = {c["type"] for c in out["cards"]}
    for required in ("opportunity", "revenue_leak", "partner_suggestion",
                     "meeting_prep", "review_response"):
        assert required in types


# ── Action Graph ─────────────────────────────────────────────
def test_action_graph_add_and_summarize():
    g = ActionGraph()
    g.add_edge(
        edge_type="signal_created_opportunity",
        src_id="signal_1", dst_id="opp_1", customer_id="c1",
    )
    g.add_edge(
        edge_type="message_triggered_reply",
        src_id="msg_1", dst_id="reply_1", customer_id="c1",
    )
    summary = g.what_works_summary("c1")
    assert summary["total_edges"] == 2
    assert "signal_created_opportunity" in summary["by_edge_type"]


def test_action_graph_unknown_edge_type_raises():
    g = ActionGraph()
    with pytest.raises(ValueError):
        g.add_edge(edge_type="bogus", src_id="a", dst_id="b", customer_id="c")


def test_edge_types_cover_essentials():
    for required in ("signal_created_opportunity", "message_triggered_reply",
                     "approval_allowed_send", "blocked_action_prevented_risk"):
        assert required in EDGE_TYPES


# ── Mission Engine ───────────────────────────────────────────
def test_missions_include_first_10():
    out = list_intel_missions()
    ids = {m["id"] for m in out["missions"]}
    assert "first_10_opportunities" in ids
    assert out["kill_feature_id"] == "first_10_opportunities"


def test_missions_include_aeo_and_competitive():
    ids = {m["id"] for m in INTEL_MISSIONS}
    assert "ai_visibility_sprint" in ids
    assert "competitive_response" in ids


def test_recommend_missions_prioritizes_kill_feature():
    """Kill feature should always be near the top."""
    brain = build_growth_brain({
        "channels_connected": ("whatsapp",),
        "growth_priorities": ("fill_pipeline",),
    })
    rec = recommend_missions(brain, limit=3)
    ids = [m["id"] for m in rec["recommended"]]
    assert "first_10_opportunities" in ids


def test_recommend_missions_without_brain():
    rec = recommend_missions(None, limit=2)
    assert len(rec["recommended"]) == 2


# ── Decision Memory ──────────────────────────────────────────
def test_decision_memory_records_and_aggregates():
    mem = DecisionMemory(customer_id="c1")
    learn_from_decision(memory=mem, decision="accept",
                        action_type="send_whatsapp", channel="whatsapp",
                        sector="real_estate", tone="warm")
    learn_from_decision(memory=mem, decision="accept",
                        action_type="send_whatsapp", channel="whatsapp",
                        tone="warm")
    learn_from_decision(memory=mem, decision="skip",
                        action_type="send_email", channel="gmail")
    prefs = mem.preferences()
    assert prefs["accept_rate"] == 0.6667 or 0.6 < prefs["accept_rate"] < 0.7
    assert "whatsapp" in prefs["preferred_channels"]
    assert "warm" in prefs["preferred_tones"]
    assert "send_email" in prefs["rejected_action_types"]


def test_decision_memory_unknown_decision_raises():
    mem = DecisionMemory(customer_id="c1")
    with pytest.raises(ValueError):
        mem.append(decision="bogus", action_type="x", channel="y")


def test_decision_memory_empty():
    mem = DecisionMemory(customer_id="c1")
    prefs = mem.preferences()
    assert prefs["samples"] == 0
    assert prefs["accept_rate"] == 0.0


# ── Trust Score ──────────────────────────────────────────────
def test_trust_blocks_cold_whatsapp_no_optin():
    out = compute_trust_score(
        source_quality="cold", opt_in=False, channel="whatsapp",
        message_text="hello", approval_status="pending",
    )
    assert out["verdict"] == "blocked"


def test_trust_safe_for_existing_customer_with_consent():
    out = compute_trust_score(
        source_quality="customer", opt_in=True, channel="whatsapp",
        message_text="مرحباً، تحديث للعميل العزيز.",
        approval_status="approved",
    )
    assert out["verdict"] == "safe"
    assert out["score"] >= 70


def test_trust_blocks_risky_phrases():
    out = compute_trust_score(
        source_quality="customer", opt_in=True, channel="whatsapp",
        message_text="ضمان 100% نتائج مضمونة آخر فرصة",
        approval_status="approved",
    )
    assert out["verdict"] in ("blocked", "needs_review")


def test_trust_freq_cap_lowers_score():
    """Hitting the weekly cap should lower the trust score vs not hitting it."""
    base = compute_trust_score(
        source_quality="customer", opt_in=True, channel="whatsapp",
        message_text="hello", frequency_count_this_week=0, weekly_cap=2,
        approval_status="approved",
    )
    capped = compute_trust_score(
        source_quality="customer", opt_in=True, channel="whatsapp",
        message_text="hello", frequency_count_this_week=2, weekly_cap=2,
        approval_status="approved",
    )
    assert capped["score"] < base["score"]
    assert any("سقف" in r or "weekly" in r.lower() or "تجاوز" in r
               for r in capped["reasons_ar"])


# ── Revenue DNA ──────────────────────────────────────────────
def test_revenue_dna_extracts_best_channel():
    out = extract_revenue_dna(
        customer_id="c1",
        won_deals=[
            {"channel": "whatsapp", "segment": "inbound_lead", "message_angle": "value", "cycle_days": 18},
            {"channel": "whatsapp", "segment": "inbound_lead", "message_angle": "value", "cycle_days": 20},
            {"channel": "email", "segment": "referral", "message_angle": "warm", "cycle_days": 30},
        ],
    )
    assert out["best_channel"] == "whatsapp"
    assert out["deals_observed"] == 3


def test_revenue_dna_demo_has_next_experiment():
    out = build_revenue_dna_demo()
    assert "next_experiment_ar" in out
    assert any("؀" <= ch <= "ۿ" for ch in out["next_experiment_ar"])


def test_revenue_dna_empty_input_returns_defaults():
    out = extract_revenue_dna(customer_id="c1")
    assert out["best_channel"] == "whatsapp"  # safe default
    assert out["deals_observed"] == 0


# ── Opportunity Simulator ────────────────────────────────────
def test_simulator_returns_pipeline_estimate():
    out = simulate_opportunity(
        target_count=100, sector="real_estate",
        avg_deal_value_sar=50_000, channel="whatsapp", cold_pct=0,
    )
    assert out["expected_replies"] >= 0
    assert out["expected_pipeline_sar"] >= 0
    assert "rates_used" in out
    assert out["approval_required"] is True


def test_simulator_warns_high_cold_pct():
    out = simulate_opportunity(
        target_count=100, sector="saas", channel="whatsapp", cold_pct=0.6,
    )
    assert out["risk_score"] >= 70
    assert any("PDPL" in r or "cold" in r for r in out["risks_ar"])


def test_simulator_unknown_sector_uses_default():
    out = simulate_opportunity(
        target_count=50, sector="totally_unknown_xyz", channel="whatsapp", cold_pct=0,
    )
    assert "rates_used" in out
    assert out["expected_pipeline_sar"] >= 0


# ── Competitive Moves ────────────────────────────────────────
def test_competitive_move_price_change_drop_high_urgency():
    out = analyze_competitive_move(
        competitor_name="X", move_type="price_change",
        payload={"price_delta_pct": -25},
    )
    assert out["urgency"] == "high"
    assert out["approval_required"] is True


def test_competitive_move_unknown_type():
    out = analyze_competitive_move(competitor_name="X", move_type="bogus_type")
    assert "error" in out


def test_competitive_move_funding_returns_action():
    out = analyze_competitive_move(competitor_name="X", move_type="funding")
    assert "recommended_action_ar" in out


# ── Board Brief ──────────────────────────────────────────────
def test_board_brief_returns_decisions_opportunities_risks():
    out = build_board_brief()
    assert len(out["decisions_required_ar"]) >= 3
    assert len(out["top_opportunities_ar"]) >= 3
    assert len(out["top_risks_ar"]) >= 3
    assert "key_relationship_ar" in out
    assert "experiment_to_run_ar" in out
    assert "metric_to_watch_ar" in out

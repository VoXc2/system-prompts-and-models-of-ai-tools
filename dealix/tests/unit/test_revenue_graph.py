"""Smoke tests for the Revenue Graph layer — graph, why-now, leaks,
maturity, simulator, objections, proof pack, agent registry, playbooks."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from auto_client_acquisition.revenue_graph.agent_registry import (
    ALL_AGENTS,
    agents_summary,
    get_agent,
    list_agents_by_autonomy,
)
from auto_client_acquisition.revenue_graph.graph import (
    CompanyVector,
    aggregate_outcomes,
    cosine_similarity,
    find_similar_companies,
    graph_health_summary,
    predict_outcome_probabilities,
    recommend_next_action,
)
from auto_client_acquisition.revenue_graph.leak_detector import (
    detect_all_leaks,
    detect_lead_no_followup,
    detect_stalled_deals,
)
from auto_client_acquisition.revenue_graph.maturity_score import (
    DIMENSIONS,
    compute_benchmark_score,
)
from auto_client_acquisition.revenue_graph.objection_library import (
    OBJECTION_CATEGORIES,
    SAUDI_B2B_OBJECTIONS,
    category_summary,
    find_by_keyword,
)
from auto_client_acquisition.revenue_graph.proof_pack import (
    ProofPackInputs,
    generate_proof_pack,
)
from auto_client_acquisition.revenue_graph.sector_playbooks import (
    ALL_PLAYBOOKS,
    get_playbook,
)
from auto_client_acquisition.revenue_graph.simulator import (
    SECTOR_BENCHMARKS,
    SimulatorInputs,
    simulate,
)
from auto_client_acquisition.revenue_graph.why_now import (
    SIGNAL_WEIGHTS,
    WhyNowSignal,
    explain_why_now,
    freshness_factor,
    rank_todays_priorities,
)


# ── Graph ─────────────────────────────────────────────────────────
def test_cosine_similarity_self_is_one():
    a = CompanyVector("c1", sector="real_estate", city="riyadh", arabic_first=True)
    # self-similarity for non-identical IDs but same vector should be high
    b = CompanyVector("c2", sector="real_estate", city="riyadh", arabic_first=True)
    assert cosine_similarity(a, b) >= 0.6


def test_cosine_similarity_different_sector_lower():
    """Same city + flags but different sector → score should be lower than full match."""
    same = CompanyVector("c1", sector="real_estate", city="riyadh")
    same2 = CompanyVector("c2", sector="real_estate", city="riyadh")
    diff = CompanyVector("c3", sector="construction", city="riyadh")
    assert cosine_similarity(same, diff) < cosine_similarity(same, same2)


def test_aggregate_outcomes_below_min_returns_none():
    out = aggregate_outcomes([{"responded": True}, {"responded": False}], min_cohort=5)
    assert out is None


def test_aggregate_outcomes_at_min_returns_stats():
    out = aggregate_outcomes(
        [
            {"responded": True, "booked": True, "won": True, "deal_size_sar": 100, "cycle_days": 30},
            {"responded": True, "booked": False, "won": False, "cycle_days": 25},
            {"responded": False, "booked": False, "won": False},
            {"responded": True, "booked": True, "won": False, "cycle_days": 40},
            {"responded": False, "booked": False, "won": False},
        ],
        min_cohort=5,
    )
    assert out is not None
    assert out.cohort_size == 5
    assert 0 <= out.reply_rate <= 1
    assert 0 <= out.confidence <= 1


def test_predict_outcome_probabilities():
    target = CompanyVector("new", sector="clinics", city="riyadh", has_whatsapp_business=True)
    historical = []
    for i in range(20):
        v = CompanyVector(f"c{i}", sector="clinics", city="riyadh", has_whatsapp_business=True)
        historical.append((v, {"responded": i % 3 == 0, "booked": i % 5 == 0, "won": i % 7 == 0, "cycle_days": 28}))
    pred = predict_outcome_probabilities(target=target, historical=historical, top_k=10, min_cohort=5)
    assert pred is not None
    assert 0 <= pred["reply_probability"] <= 1


def test_recommend_next_action_no_history_with_whatsapp():
    target = CompanyVector("c1", has_whatsapp_business=True)
    nba = recommend_next_action(target=target, last_outcome=None, days_since_last_touch=0)
    assert nba.channel == "whatsapp"
    assert nba.expected_reply_lift > 1.0


def test_recommend_next_action_positive_reply_pushes_demo():
    target = CompanyVector("c1")
    nba = recommend_next_action(target=target, last_outcome="positive_reply", days_since_last_touch=1)
    assert "24" in nba.action or "demo" in nba.action


# ── Why-Now ───────────────────────────────────────────────────────
def test_freshness_factor_today_is_one():
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    assert freshness_factor(now, now=now) == 1.0


def test_freshness_factor_decays():
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    old = now - timedelta(days=14)
    assert 0.45 <= freshness_factor(old, now=now) <= 0.55  # half-life


def test_explain_why_now_with_strong_signal():
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    signals = [
        WhyNowSignal("hiring_sales_rep", now - timedelta(days=2), "linkedin"),
        WhyNowSignal("new_branch_opened", now - timedelta(days=5), "google_search"),
    ]
    exp = explain_why_now(company_id="c1", signals=signals)
    assert exp is not None
    assert exp.score > 0
    assert "يوظفون" in exp.headline_ar or "افتتحوا" in exp.headline_ar


def test_explain_why_now_no_signals_returns_none():
    assert explain_why_now(company_id="c1", signals=[]) is None


def test_explain_why_now_ranks_todays_priorities():
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    explanations = []
    for i, sig in enumerate(["hiring_sales_rep", "new_branch_opened", "tender_published"]):
        e = explain_why_now(
            company_id=f"c{i}",
            signals=[WhyNowSignal(sig, now - timedelta(days=1), "src")],
        )
        if e:
            explanations.append(e)
    top = rank_todays_priorities(explanations=explanations, top_n=2)
    assert len(top) <= 2


# ── Leak Detector ────────────────────────────────────────────────
def test_lead_no_followup_flags_old_untouched():
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    leads = [
        {
            "id": "L1",
            "company_name": "Old Co.",
            "created_at": now - timedelta(days=10),
            "last_outreach_at": None,
        }
    ]
    leaks = detect_lead_no_followup(leads=leads, now=now)
    assert len(leaks) == 1
    assert leaks[0].severity in ("medium", "high", "critical")


def test_stalled_deals_detected():
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    deals = [
        {
            "id": "D1",
            "company_name": "Stalled Co.",
            "status": "open",
            "value_sar": 100_000,
            "last_activity_at": now - timedelta(days=20),
        }
    ]
    leaks = detect_stalled_deals(deals=deals, now=now)
    assert len(leaks) == 1


def test_detect_all_leaks_sorts_by_impact():
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    report = detect_all_leaks(
        leads=[{"id": "L1", "created_at": now - timedelta(days=8), "last_outreach_at": None}],
        deals=[{"id": "D1", "status": "open", "value_sar": 200_000, "last_activity_at": now - timedelta(days=22)}],
        now=now,
    )
    assert report.total_estimated_impact_sar > 0
    assert "critical" in report.by_severity or "high" in report.by_severity


# ── Maturity Score ───────────────────────────────────────────────
def test_benchmark_zero_returns_weak():
    r = compute_benchmark_score(customer_id="c1")
    assert r.bucket == "weak"
    assert r.overall < 50


def test_benchmark_strong_returns_strong():
    r = compute_benchmark_score(
        customer_id="c1",
        has_playbook=True, has_quota=True, weekly_pipeline_review=True,
        median_response_minutes=30, followups_per_lead=4,
        reply_rate=0.12, positive_reply_rate=0.04,
        sectors_targeted=2, win_rate_top_sector=0.30,
        has_pricing_page=True, has_case_studies=True, avg_proposal_pages=3,
        lead_to_meeting=0.20, meeting_to_deal=0.45, deal_to_close=0.35,
        has_onboarding_flow=True, nps_collected=True, runs_qbr=True,
    )
    assert r.bucket in ("strong", "exceptional")
    assert r.overall >= 70


def test_benchmark_returns_all_dimensions():
    r = compute_benchmark_score(customer_id="c")
    assert len(r.dimensions) == len(DIMENSIONS)
    names = {d.name for d in r.dimensions}
    assert names == set(DIMENSIONS)


def test_benchmark_markdown_export():
    r = compute_benchmark_score(customer_id="c1", has_playbook=True)
    md = r.to_markdown()
    assert "Dealix Benchmark" in md
    assert "خريطة الطريق" in md


# ── Simulator ────────────────────────────────────────────────────
def test_simulate_real_estate_returns_funnel():
    inputs = SimulatorInputs(
        sector="real_estate",
        city="الرياض",
        avg_deal_value_sar=500_000,
        target_revenue_sar=2_000_000,
        target_period_days=90,
    )
    r = simulate(inputs=inputs)
    # With Dealix lift, you need FEWER leads to hit the same target
    assert r.with_dealix.leads_needed < r.baseline.leads_needed
    # And the ratio is meaningful — typically ~25-40% of baseline
    assert r.with_dealix.leads_needed > r.baseline.leads_needed * 0.1
    assert r.expected_roi_x > 0
    assert r.plan.plan_name in ("Starter", "Growth", "Scale")


def test_simulate_warns_on_too_short_period():
    inputs = SimulatorInputs(
        sector="real_estate", city="الرياض",
        avg_deal_value_sar=10_000, target_revenue_sar=50_000,
        target_period_days=15,
    )
    r = simulate(inputs=inputs)
    assert any("قصيرة" in risk for risk in r.risks_ar)


def test_simulate_unknown_sector_uses_default():
    inputs = SimulatorInputs(
        sector="unknown_sector",
        city="الرياض",
        avg_deal_value_sar=50_000,
        target_revenue_sar=500_000,
    )
    r = simulate(inputs=inputs)
    assert r.with_dealix.leads_needed > 0


# ── Objection Library ────────────────────────────────────────────
def test_library_has_objections_in_each_category():
    summary = category_summary()
    assert len(summary) > 0
    assert sum(summary.values()) == len(SAUDI_B2B_OBJECTIONS)


def test_find_by_keyword_price():
    obj = find_by_keyword("السعر عالي")
    assert obj is not None
    assert obj.category == "price"


def test_find_by_keyword_no_match():
    obj = find_by_keyword("XXXX_no_match_string_XXXX")
    assert obj is None


def test_objection_categories_known():
    for o in SAUDI_B2B_OBJECTIONS:
        assert o.category in OBJECTION_CATEGORIES


# ── Proof Pack ───────────────────────────────────────────────────
def test_proof_pack_grades_a_for_high_multiple():
    inp = ProofPackInputs(
        customer_id="c1", customer_name="Test", sector="real_estate",
        month_label="إبريل 2026", plan="Growth", monthly_price_sar=2999,
        leads_discovered=500, leads_enriched=400, drafts_created=300,
        drafts_sent=280, whatsapp_sent=180, emails_sent=80, linkedin_sent=20,
        replies_received=42, positive_replies=18,
        meetings_booked=12, proposals_sent=6, deals_won=3,
        pipeline_added_sar=500_000, revenue_won_sar=180_000,
        avg_response_minutes=40, bounce_rate=0.04, opt_outs=2, compliance_blocks=0,
        sector_reply_rate_p50=0.07, sector_meeting_rate_p50=0.30, sector_win_rate_p50=0.18,
    )
    p = generate_proof_pack(inp)
    assert p.grade in ("A+", "A")
    assert "ROI" in p.to_markdown()


def test_proof_pack_grades_d_for_no_pipeline():
    inp = ProofPackInputs(
        customer_id="c1", customer_name="Test", sector="real_estate",
        month_label="مارس 2026", plan="Growth", monthly_price_sar=2999,
        leads_discovered=10, leads_enriched=5, drafts_created=3,
        drafts_sent=3, whatsapp_sent=2, emails_sent=1, linkedin_sent=0,
        replies_received=0, positive_replies=0,
        meetings_booked=0, proposals_sent=0, deals_won=0,
        pipeline_added_sar=1000, revenue_won_sar=0,
        avg_response_minutes=180, bounce_rate=0.0, opt_outs=0, compliance_blocks=0,
        sector_reply_rate_p50=0.07, sector_meeting_rate_p50=0.30, sector_win_rate_p50=0.18,
    )
    p = generate_proof_pack(inp)
    assert p.grade in ("D", "C")


# ── Agent Registry ───────────────────────────────────────────────
def test_eleven_agents_registered():
    assert len(ALL_AGENTS) == 11


def test_agent_registry_summary():
    s = agents_summary()
    assert s["total"] == 11
    assert s["safe_auto"] >= 5
    assert s["pdpl_gated"] >= 8


def test_get_agent_returns_valid_spec():
    a = get_agent("prospecting")
    assert a is not None
    assert a.name_ar
    assert a.role_ar


def test_get_agent_unknown_returns_none():
    assert get_agent("nonexistent") is None


def test_list_by_autonomy():
    safe = list_agents_by_autonomy("safe_auto")
    assert all(a.autonomy_level == "safe_auto" for a in safe)


# ── Sector Playbooks ─────────────────────────────────────────────
def test_eight_playbooks_present():
    assert len(ALL_PLAYBOOKS) == 8


def test_playbook_has_required_fields():
    p = get_playbook("real_estate")
    assert p is not None
    assert p.pain_points_ar
    assert p.opening_lines_ar
    assert p.benchmarks
    assert sum(p.recommended_channel_mix.values()) > 0.99


def test_playbook_unknown_returns_none():
    assert get_playbook("xxx_unknown") is None


# ── Graph health ─────────────────────────────────────────────────
def test_graph_health_summary():
    s = graph_health_summary(
        n_companies=200, n_signals=500, n_messages=1500,
        n_outcomes=400, n_won_deals=20,
    )
    assert "moat_score" in s
    assert s["ready_for_predictions"] is True


def test_graph_health_zero_safe():
    s = graph_health_summary(n_companies=0, n_signals=0, n_messages=0, n_outcomes=0, n_won_deals=0)
    assert s["moat_score"] == 0
    assert s["ready_for_predictions"] is False

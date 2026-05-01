"""Unit tests for Service Excellence OS."""

from __future__ import annotations

from auto_client_acquisition.service_excellence import (
    build_backlog,
    build_demo_script,
    build_feature_matrix,
    build_landing_page_outline,
    build_monthly_service_review,
    build_onboarding_checklist,
    build_proof_pack_template_excellence,
    build_sales_script,
    build_service_launch_package,
    build_service_research_brief,
    calculate_service_excellence_score,
    calculate_service_roi_estimate,
    classify_features,
    compare_against_categories,
    convert_feedback_to_backlog,
    generate_feature_hypotheses,
    prioritize_backlog_items,
    recommend_missing_features,
    recommend_next_experiments,
    recommend_weekly_improvements,
    required_proof_metrics,
    review_service_before_launch,
    score_clarity,
    score_compliance,
    score_proof,
    summarize_proof_ar,
)
from auto_client_acquisition.service_excellence.quality_review import (
    block_if_missing_proof,
    block_if_unclear_pricing,
    block_if_unsafe_channel,
)
from auto_client_acquisition.service_tower import ALL_SERVICES, get_service


# ── Feature matrix ───────────────────────────────────────────
def test_feature_matrix_has_must_have_features():
    out = build_feature_matrix("growth_os_monthly")
    assert len(out["must_have"]) >= 10


def test_classify_features_returns_three_tiers():
    out = classify_features("growth_os_monthly")
    assert "must_have" in out
    assert "advanced" in out
    assert "premium" in out


def test_recommend_missing_features_returns_list():
    out = recommend_missing_features("first_10_opportunities_sprint")
    assert isinstance(out, list)


def test_unknown_service_feature_matrix_errors():
    out = build_feature_matrix("totally_unknown")
    assert "error" in out


# ── Scoring ──────────────────────────────────────────────────
def test_score_returns_status():
    out = calculate_service_excellence_score("growth_os_monthly")
    assert out["status"] in ("launch_ready", "beta_only", "needs_work")


def test_score_clarity_for_complete_service():
    s = get_service("first_10_opportunities_sprint")
    score = score_clarity(s)
    assert score >= 7


def test_score_compliance_high_for_approval_first():
    s = get_service("growth_os_monthly")
    score = score_compliance(s)
    assert score >= 8


def test_score_proof_high_when_metrics_present():
    s = get_service("growth_os_monthly")
    score = score_proof(s)
    assert score >= 6


# ── Quality review ───────────────────────────────────────────
def test_quality_review_returns_verdict():
    out = review_service_before_launch("growth_os_monthly")
    assert out["verdict"] in ("launch_ready", "beta_only", "needs_work",
                              "blocked_at_gate")


def test_quality_review_all_services_no_blocks():
    """Every catalogued service should pass the gates (it's our catalog)."""
    for s in ALL_SERVICES:
        out = review_service_before_launch(s.id)
        assert out["verdict"] != "blocked_at_gate", f"{s.id} blocked at gate"


def test_block_if_missing_proof():
    out = block_if_missing_proof("growth_os_monthly")
    assert out["blocked"] is False  # all our services have proof metrics


def test_block_if_unclear_pricing():
    out = block_if_unclear_pricing("growth_os_monthly")
    assert out["blocked"] is False


def test_block_if_unsafe_channel():
    out = block_if_unsafe_channel("growth_os_monthly")
    assert out["blocked"] is False


# ── Proof metrics ────────────────────────────────────────────
def test_required_proof_metrics_present():
    metrics = required_proof_metrics("growth_os_monthly")
    assert len(metrics) >= 1


def test_proof_pack_template_excellence():
    out = build_proof_pack_template_excellence("growth_os_monthly")
    assert out["signature_required"] is True


def test_roi_estimate_returns_x_multiples():
    out = calculate_service_roi_estimate(
        "first_10_opportunities_sprint",
        {"price_paid_sar": 1000, "pipeline_sar": 25000, "closed_won_sar": 5000},
    )
    assert out["roi_pipeline_x"] == 25.0
    assert out["roi_closed_x"] == 5.0


def test_summarize_proof_ar_arabic():
    msg = summarize_proof_ar(
        "first_10_opportunities_sprint",
        {"price_paid_sar": 1000, "pipeline_sar": 18000, "closed_won_sar": 3000},
    )
    assert any("؀" <= ch <= "ۿ" for ch in msg)


# ── Competitor gap ───────────────────────────────────────────
def test_competitor_gap_lists_advantages():
    out = compare_against_categories("growth_os_monthly")
    assert out["dealix_advantages_ar"]
    assert out["do_not_copy_ar"]


def test_competitor_gap_unknown_service():
    out = compare_against_categories("bogus")
    assert "error" in out


# ── Research lab ─────────────────────────────────────────────
def test_research_brief_has_questions():
    out = build_service_research_brief("growth_os_monthly")
    assert len(out["questions_to_answer_ar"]) >= 5


def test_feature_hypotheses_returned():
    out = generate_feature_hypotheses("growth_os_monthly")
    assert len(out) >= 3


def test_recommend_next_experiments_max_three():
    out = recommend_next_experiments("growth_os_monthly")
    assert len(out["experiments"]) <= 3


def test_monthly_review_includes_score():
    out = build_monthly_service_review("growth_os_monthly")
    assert "current_excellence_score" in out


# ── Backlog ──────────────────────────────────────────────────
def test_backlog_returns_skeleton():
    out = build_backlog("growth_os_monthly")
    assert out["service_id"] == "growth_os_monthly"
    assert "items" in out


def test_prioritize_backlog_items():
    items = [
        {"impact": "low", "effort": "high"},
        {"impact": "high", "effort": "low"},
        {"impact": "medium", "effort": "medium"},
    ]
    out = prioritize_backlog_items(items)
    # high+low effort should be first
    assert out[0]["impact"] == "high"


def test_convert_feedback_to_backlog():
    feedback = [
        {"text": "العميل بطيء في الرد على الـ drafts", "sentiment": "negative"},
        {"text": "الـ pricing واضح", "sentiment": "positive"},
    ]
    out = convert_feedback_to_backlog(feedback)
    assert len(out) == 2


def test_weekly_improvements_returned():
    out = recommend_weekly_improvements("growth_os_monthly")
    assert len(out["weekly_plan_ar"]) >= 1


# ── Launch package ───────────────────────────────────────────
def test_launch_package_complete():
    out = build_service_launch_package("first_10_opportunities_sprint")
    assert "landing" in out
    assert "sales_script" in out
    assert "demo_script" in out
    assert "onboarding" in out


def test_landing_outline_includes_safety():
    out = build_landing_page_outline("growth_os_monthly")
    assert any("Approval-first" in s or "approval" in s.lower()
               for s in out["must_include_ar"])


def test_sales_script_has_objection_handling():
    out = build_sales_script("growth_os_monthly")
    assert "price" in out["objection_handling_ar"]
    assert "timing" in out["objection_handling_ar"]


def test_demo_script_is_12_minutes():
    out = build_demo_script("first_10_opportunities_sprint")
    assert out["duration_minutes"] == 12


def test_onboarding_blocks_live_send():
    out = build_onboarding_checklist("growth_os_monthly")
    assert out["live_send_allowed"] is False

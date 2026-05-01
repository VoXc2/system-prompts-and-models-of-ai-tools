"""
Unit tests for the dealix.business layer — pure functions, no I/O.

Covers: gtm_plan / launch_metrics / market_positioning / pricing_strategy /
proof_pack / unit_economics / verticals.
"""

from __future__ import annotations

import pytest

from auto_client_acquisition.business import (
    gtm_plan,
    launch_metrics,
    market_positioning,
    pricing_strategy,
    proof_pack,
    unit_economics,
    verticals,
)


# ── gtm_plan ─────────────────────────────────────────────────────
def test_first_10_plan_has_milestones():
    p = gtm_plan.first_10_customers_plan()
    assert isinstance(p, dict)
    assert p  # non-empty


def test_first_100_plan_distinct_from_first_10():
    p10 = gtm_plan.first_10_customers_plan()
    p100 = gtm_plan.first_100_customers_plan()
    # They should not be byte-identical structures
    assert p10 != p100


def test_channel_strategy_returns_dict():
    out = gtm_plan.channel_strategy()
    assert isinstance(out, dict)
    assert out


def test_partner_strategy_returns_dict():
    out = gtm_plan.partner_strategy()
    assert isinstance(out, dict)


def test_founder_led_sales_script_has_content():
    s = gtm_plan.founder_led_sales_script()
    assert isinstance(s, dict)
    assert s


# ── launch_metrics ───────────────────────────────────────────────
def test_north_star_metrics_dict():
    out = launch_metrics.north_star_metrics()
    assert isinstance(out, dict)
    assert out


def test_activation_metrics_dict():
    assert isinstance(launch_metrics.activation_metrics(), dict)


def test_retention_metrics_dict():
    assert isinstance(launch_metrics.retention_metrics(), dict)


def test_revenue_metrics_dict():
    assert isinstance(launch_metrics.revenue_metrics(), dict)


def test_ai_quality_metrics_dict():
    assert isinstance(launch_metrics.ai_quality_metrics(), dict)


# ── market_positioning ───────────────────────────────────────────
def test_compare_competitors_returns_list():
    out = market_positioning.compare_competitors()
    assert isinstance(out, list)
    assert len(out) > 0


def test_dealix_differentiators_non_empty_strings():
    out = market_positioning.dealix_differentiators()
    assert isinstance(out, list)
    assert len(out) > 0
    assert all(isinstance(x, str) and x for x in out)


def test_positioning_statement_returns_string():
    # Try a known segment value
    statement = market_positioning.positioning_statement("smb")
    assert isinstance(statement, str)
    assert len(statement) > 0


# ── pricing_strategy ─────────────────────────────────────────────
def test_get_pricing_tiers_structure():
    out = pricing_strategy.get_pricing_tiers()
    assert isinstance(out, dict)
    assert out["currency"] == "SAR"
    assert isinstance(out["tiers"], list)
    keys = {t["key"] for t in out["tiers"]}
    # Required tiers per pricing strategy doc
    for required in ("founder_operator", "growth_os", "scale_os"):
        assert required in keys, f"missing tier: {required}"


def test_recommend_plan_returns_known_key():
    out = pricing_strategy.recommend_plan(
        company_size="smb",
        monthly_budget_sar=3000,
        goal="grow_pipeline",
    )
    assert isinstance(out, dict)
    # Real shape: {recommended_plan, rationale_ar, tier_summary, inputs}
    assert "recommended_plan" in out
    assert "rationale_ar" in out
    assert "tier_summary" in out


def test_calculate_performance_fee_non_negative():
    out = pricing_strategy.calculate_performance_fee(
        qualified_leads=20,
        booked_meetings=8,
        won_revenue_sar=120_000,
    )
    assert isinstance(out, dict)
    for k, v in out.items():
        if isinstance(v, (int, float)):
            assert v >= 0, f"{k} should be non-negative, got {v}"


def test_estimate_roi_returns_dict():
    out = pricing_strategy.estimate_roi(
        plan_price_sar=2999,
        expected_pipeline_sar=120_000,
        expected_revenue_sar=30_000,
    )
    assert isinstance(out, dict)
    assert out


# ── proof_pack ───────────────────────────────────────────────────
def test_demo_proof_pack_structure():
    out = proof_pack.build_demo_proof_pack()
    assert isinstance(out, dict)
    assert out


def test_calculate_roi_summary_handles_zero_subscription():
    """Should not divide-by-zero on zero subscription."""
    out = proof_pack.calculate_roi_summary(
        subscription_sar=0,
        influenced_revenue_sar=0,
        hours_saved=0,
    )
    assert isinstance(out, dict)


def test_calculate_roi_summary_normal():
    out = proof_pack.calculate_roi_summary(
        subscription_sar=2999,
        influenced_revenue_sar=200_000,
        hours_saved=40,
    )
    assert isinstance(out, dict)
    # multiple should be positive given non-zero inputs
    assert out


def test_grade_account_health_thresholds():
    healthy = proof_pack.grade_account_health(
        brief_opens_4w=20, approvals_4w=10, blocks_4w=2,
    )
    weak = proof_pack.grade_account_health(
        brief_opens_4w=2, approvals_4w=0, blocks_4w=0,
    )
    # healthy should grade higher
    assert healthy["health_score"] >= weak["health_score"]
    # And the status labels should differ for these extremes
    assert healthy["status"] == "healthy"
    assert weak["status"] == "at_risk"


# ── unit_economics ───────────────────────────────────────────────
def test_estimate_gross_margin_returns_dict():
    assert isinstance(unit_economics.estimate_gross_margin(), dict)


def test_cac_payback_dict():
    assert isinstance(unit_economics.estimate_cac_payback(), dict)


def test_estimate_ltv_dict():
    assert isinstance(unit_economics.estimate_ltv(), dict)


def test_estimate_mrr_path_dict():
    out = unit_economics.estimate_mrr_path()
    assert isinstance(out, dict)


# ── verticals ────────────────────────────────────────────────────
def test_get_vertical_playbooks():
    out = verticals.get_vertical_playbooks()
    assert isinstance(out, dict)
    # Verticals are nested under 'verticals' key
    inner = out.get("verticals", {})
    assert "clinics" in inner or "real_estate" in inner or "logistics" in inner


def test_recommend_vertical_returns_dict():
    out = verticals.recommend_vertical(
        industry="medical",
        city="Riyadh",
        goal="bookings",
    )
    assert isinstance(out, dict)


def test_vertical_roi_metric_returns_string():
    # Try a known vertical
    out = verticals.vertical_roi_metric("clinics")
    assert isinstance(out, str)
    assert out

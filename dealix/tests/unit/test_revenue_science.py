"""Smoke tests for Revenue Science (forecast/attribution/impact/churn/expansion)."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest

from auto_client_acquisition.revenue_science.attribution import (
    compute_first_touch,
    compute_last_touch,
    compute_linear,
    compute_time_decay,
)
from auto_client_acquisition.revenue_science.causal_impact import simulate_impact
from auto_client_acquisition.revenue_science.churn_model import predict_churn
from auto_client_acquisition.revenue_science.expansion_model import predict_expansion
from auto_client_acquisition.revenue_science.forecast import (
    STAGE_BASE_PROBABILITY,
    compute_forecast,
)


def _now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


# ── Forecast ─────────────────────────────────────────────────────
def test_forecast_empty_pipeline_returns_zero_decision():
    f = compute_forecast(customer_id="c1", open_deals=[])
    assert f.likely.revenue_sar == 0
    assert any("ابدأ" in d for d in f.decisions_required_ar)


def test_forecast_likely_ge_worst():
    deals = [
        {"id": "d1", "stage": "demo", "value_sar": 100_000, "days_in_stage": 5},
        {"id": "d2", "stage": "proposal", "value_sar": 200_000, "days_in_stage": 3},
        {"id": "d3", "stage": "negotiation", "value_sar": 50_000, "days_in_stage": 2},
    ]
    f = compute_forecast(customer_id="c1", open_deals=deals)
    assert f.best.revenue_sar >= f.likely.revenue_sar
    assert f.likely.revenue_sar >= f.worst.revenue_sar


def test_forecast_stalled_deal_gets_penalized():
    fresh = [{"id": "d1", "stage": "discovery", "value_sar": 100_000, "days_in_stage": 2}]
    stale = [{"id": "d1", "stage": "discovery", "value_sar": 100_000, "days_in_stage": 60}]
    fresh_f = compute_forecast(customer_id="c1", open_deals=fresh)
    stale_f = compute_forecast(customer_id="c1", open_deals=stale)
    assert stale_f.likely.revenue_sar < fresh_f.likely.revenue_sar


def test_forecast_skips_won_lost():
    deals = [
        {"id": "d1", "stage": "won", "value_sar": 100_000, "days_in_stage": 0},
        {"id": "d2", "stage": "lost", "value_sar": 50_000, "days_in_stage": 0},
        {"id": "d3", "stage": "demo", "value_sar": 30_000, "days_in_stage": 5},
    ]
    f = compute_forecast(customer_id="c1", open_deals=deals)
    assert len(f.deals_breakdown) == 1


def test_stage_base_probability_monotonic():
    """Later stages should have higher probability."""
    stages = ["new", "qualified", "discovery", "demo", "proposal", "negotiation", "verbal_yes"]
    probs = [STAGE_BASE_PROBABILITY[s] for s in stages]
    assert all(probs[i] <= probs[i + 1] for i in range(len(probs) - 1))


# ── Attribution ──────────────────────────────────────────────────
def test_first_touch_credits_first_channel():
    deals = [{
        "status": "won", "value_sar": 100_000,
        "touchpoints": [
            {"channel": "linkedin", "at": _now() - timedelta(days=20)},
            {"channel": "whatsapp", "at": _now() - timedelta(days=10)},
            {"channel": "email", "at": _now() - timedelta(days=2)},
        ],
    }]
    res = compute_first_touch(deals=deals)
    assert res.by_channel == {"linkedin": 100_000}


def test_last_touch_credits_last_channel():
    deals = [{
        "status": "won", "value_sar": 100_000,
        "touchpoints": [
            {"channel": "linkedin", "at": _now() - timedelta(days=20)},
            {"channel": "whatsapp", "at": _now() - timedelta(days=2)},
        ],
    }]
    res = compute_last_touch(deals=deals)
    assert res.by_channel == {"whatsapp": 100_000}


def test_linear_splits_equally():
    deals = [{
        "status": "won", "value_sar": 100_000,
        "touchpoints": [
            {"channel": "linkedin", "at": _now() - timedelta(days=20)},
            {"channel": "whatsapp", "at": _now() - timedelta(days=10)},
            {"channel": "email", "at": _now() - timedelta(days=2)},
        ],
    }]
    res = compute_linear(deals=deals)
    for ch in ("linkedin", "whatsapp", "email"):
        assert abs(res.by_channel[ch] - 100_000 / 3) < 0.01


def test_time_decay_favors_recent():
    deals = [{
        "status": "won", "value_sar": 100_000, "closed_at": _now(),
        "touchpoints": [
            {"channel": "old", "at": _now() - timedelta(days=60)},
            {"channel": "recent", "at": _now() - timedelta(days=2)},
        ],
    }]
    res = compute_time_decay(deals=deals, half_life_days=14)
    assert res.by_channel["recent"] > res.by_channel["old"]


def test_attribution_skips_lost_deals():
    deals = [{
        "status": "lost", "value_sar": 100_000,
        "touchpoints": [{"channel": "x", "at": _now()}],
    }]
    res = compute_linear(deals=deals)
    assert res.total_revenue_sar == 0


# ── Causal Impact Simulator ──────────────────────────────────────
def test_simulate_impact_response_time_lift():
    out = simulate_impact(
        current_baseline_revenue_sar=100_000,
        response_time_reduction_hours=4,
    )
    assert out.delta_sar > 0
    assert "تقليل" in out.explanation_ar


def test_simulate_impact_no_changes_no_delta():
    out = simulate_impact(current_baseline_revenue_sar=100_000)
    assert out.delta_sar == 0
    assert out.delta_pct == 0


def test_simulate_impact_warns_on_extreme_uplift():
    out = simulate_impact(
        current_baseline_revenue_sar=100_000,
        response_time_reduction_hours=200,  # absurd
        extra_followup_touches=10,
        shift_to_whatsapp_pct=1.0,
        drop_n_sectors=10,
    )
    assert out.risk_warnings_ar  # should have warnings


def test_simulate_impact_whatsapp_shift_high_risk_warning():
    out = simulate_impact(
        current_baseline_revenue_sar=100_000,
        shift_to_whatsapp_pct=0.85,
    )
    assert any("opt-out" in w.lower() or "WhatsApp" in w for w in out.risk_warnings_ar)


# ── Churn ────────────────────────────────────────────────────────
def test_churn_high_for_disengaged():
    p = predict_churn(
        customer_id="c1",
        days_since_last_login=45,
        monthly_engagement_drop_pct=0.7,
        support_tickets_open=3,
        billing_failures_last_90d=2,
        nps=5,
        pipeline_added_drop_pct=0.6,
    )
    assert p.band == "critical"
    assert p.score >= 0.65
    assert p.drivers


def test_churn_low_for_healthy():
    p = predict_churn(
        customer_id="c1",
        days_since_last_login=2,
        monthly_engagement_drop_pct=0,
        support_tickets_open=0,
        billing_failures_last_90d=0,
        nps=9,
        pipeline_added_drop_pct=0,
    )
    assert p.band == "safe"


def test_churn_new_customer_cushion():
    """New customers get -0.1 score because of honeymoon period."""
    new = predict_churn(customer_id="c1", days_since_last_login=20, months_as_customer=1)
    old = predict_churn(customer_id="c1", days_since_last_login=20, months_as_customer=12)
    assert new.score <= old.score


# ── Expansion ────────────────────────────────────────────────────
def test_expansion_high_for_growing_customer():
    sig = predict_expansion(
        customer_id="c1",
        current_plan="Growth",
        health_score=85,
        monthly_engagement_growth_pct=0.4,
        sectors_targeted=3,
        pct_of_quota_used=0.9,
        nps=9,
        pipeline_added_growth_pct=0.4,
    )
    assert sig.likelihood >= 0.65
    assert sig.recommended_plan in ("Scale", "Enterprise")
    assert sig.estimated_upsell_sar > 0


def test_expansion_low_for_struggling():
    sig = predict_expansion(
        customer_id="c1",
        current_plan="Growth",
        health_score=40,
        monthly_engagement_growth_pct=-0.2,
        sectors_targeted=1,
        pct_of_quota_used=0.3,
        pipeline_added_growth_pct=-0.1,
    )
    assert sig.likelihood < 0.4
    assert sig.estimated_upsell_sar == 0


def test_expansion_recommends_next_tier():
    sig = predict_expansion(
        customer_id="c1", current_plan="Starter", health_score=85,
        pct_of_quota_used=0.95, nps=9, pipeline_added_growth_pct=0.5,
    )
    assert sig.recommended_plan == "Growth"

"""Smoke tests for the Customer Success layer — health, QBR, benchmarks."""

from __future__ import annotations

import pytest

from auto_client_acquisition.customer_success.benchmarks import (
    MIN_COHORT_SIZE,
    compare_customer,
    compute_sector_benchmark,
    percentile,
    saudi_b2b_pulse,
)
from auto_client_acquisition.customer_success.health_score import compute_health
from auto_client_acquisition.customer_success.qbr_generator import generate_qbr


# ── Health score ──────────────────────────────────────────────────
def test_health_zero_signals_is_critical():
    h = compute_health(customer_id="c1")
    assert h.bucket == "critical"
    assert h.overall <= 40


def test_health_strong_signals_is_healthy():
    h = compute_health(
        customer_id="c2",
        logins_last_30d=22,
        drafts_approved_last_30d=40,
        replies_acted_on_last_30d=12,
        demos_booked_last_30d=8,
        deals_stage_progressed_last_30d=10,
        paid_customers_last_30d=3,
        pipeline_value_sar=500_000,
        channels_enabled=4,
        integrations_connected=4,
        sectors_targeted=3,
        total_drafts_lifetime=400,
        nps=9,
    )
    assert h.bucket == "healthy"
    assert h.overall >= 75
    assert isinstance(h.upsell_candidate, bool)


def test_health_buckets_in_order():
    """Higher composite signals must produce higher overall scores."""
    weak = compute_health(customer_id="w", logins_last_30d=2, drafts_approved_last_30d=1)
    strong = compute_health(
        customer_id="s",
        logins_last_30d=20,
        drafts_approved_last_30d=30,
        replies_acted_on_last_30d=8,
        demos_booked_last_30d=4,
        deals_stage_progressed_last_30d=6,
        paid_customers_last_30d=2,
    )
    assert strong.overall > weak.overall


def test_health_returns_drivers():
    h = compute_health(customer_id="c3", logins_last_30d=15, drafts_approved_last_30d=20)
    # drivers is a list[str] of human-readable driver tags
    assert isinstance(h.drivers, list)
    # And the 4 dimension scores are exposed as named attributes
    for dim in ("engagement", "outcomes", "adoption", "sentiment"):
        assert hasattr(h, dim)


# ── QBR generator ─────────────────────────────────────────────────
def test_qbr_returns_markdown():
    qbr = generate_qbr(
        customer_id="c1",
        customer_name="Test Co.",
        emails_sent=120,
        emails_replied=14,
        demos_booked=4,
    )
    md = qbr.to_markdown()
    assert "Test Co." in md
    assert qbr.customer_id == "c1"
    assert isinstance(qbr.sections, list)
    assert qbr.sections, "QBR must have at least one section"


def test_qbr_sections_have_titles():
    qbr = generate_qbr(customer_id="c", customer_name="X")
    # QBRSection is a dataclass with a title attribute
    for s in qbr.sections:
        assert isinstance(s.title, str)


# ── Benchmarks — privacy guard ────────────────────────────────────
def test_benchmarks_min_cohort_is_5():
    """Privacy: must refuse to publish stats for fewer than 5 companies."""
    assert MIN_COHORT_SIZE >= 5


def test_benchmark_returns_none_below_min_cohort():
    out = compute_sector_benchmark(
        sector="clinics",
        metric="reply_rate",
        customer_values=[0.10, 0.12, 0.08],  # only 3 — below min
    )
    assert out is None


def test_benchmark_returns_value_at_min_cohort():
    out = compute_sector_benchmark(
        sector="clinics",
        metric="reply_rate",
        customer_values=[0.05, 0.10, 0.12, 0.15, 0.20],
    )
    assert out is not None
    assert out.cohort_size == 5
    assert out.metric == "reply_rate"
    assert out.p50 >= out.p25
    assert out.p90 >= out.p50


# ── Percentile correctness ────────────────────────────────────────
def test_percentile_p50_matches_median():
    vals = [1.0, 2.0, 3.0, 4.0, 5.0]
    assert percentile(vals, 50) == 3.0


def test_percentile_p90_above_p50():
    vals = [1.0, 2.0, 3.0, 4.0, 5.0]
    assert percentile(vals, 90) >= percentile(vals, 50)


def test_percentile_handles_single_value():
    assert percentile([3.0], 50) == 3.0


# ── compare_customer ──────────────────────────────────────────────
def test_compare_returns_position():
    out = compare_customer(
        customer_id="c1",
        sector="clinics",
        metric="reply_rate",
        customer_value=0.18,
        sector_values=[0.05, 0.08, 0.10, 0.12, 0.15, 0.18, 0.20],
    )
    assert out is not None
    assert out.customer_id == "c1"
    # Field is named `customer_percentile` (int 0-100)
    assert 0 <= out.customer_percentile <= 100


def test_compare_below_min_cohort_returns_none():
    out = compare_customer(
        customer_id="c1",
        sector="clinics",
        metric="reply_rate",
        customer_value=0.10,
        sector_values=[0.05, 0.10],  # only 2
    )
    assert out is None


# ── Saudi B2B Pulse — full report ─────────────────────────────────
def test_pulse_skips_undersized_sectors():
    """Sectors with <5 samples must NOT appear in published pulse."""
    pulse = saudi_b2b_pulse(
        sector_data={
            "clinics": {"reply_rate": [0.10, 0.12, 0.14, 0.15, 0.18, 0.20]},
            "tiny_sector": {"reply_rate": [0.10, 0.12]},  # below min — must be excluded
        }
    )
    sector_names = {b["sector"] for b in pulse.get("benchmarks", [])}
    assert "clinics" in sector_names
    assert "tiny_sector" not in sector_names


def test_pulse_returns_publishable_dict():
    pulse = saudi_b2b_pulse(
        sector_data={
            "clinics": {"reply_rate": [0.10, 0.12, 0.14, 0.15, 0.18, 0.20]},
            "real_estate": {"reply_rate": [0.04, 0.06, 0.07, 0.09, 0.11]},
        }
    )
    assert isinstance(pulse, dict)
    assert "benchmarks" in pulse
    assert pulse["report_name"] == "Saudi B2B Pulse"
    assert pulse["min_cohort_for_publication"] >= 5

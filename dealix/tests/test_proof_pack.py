"""Proof pack demo."""

from __future__ import annotations

from auto_client_acquisition.business.proof_pack import build_demo_proof_pack, calculate_roi_summary


def test_proof_pack_sections():
    pack = build_demo_proof_pack()
    for key in (
        "executive_summary_ar",
        "qualified_leads",
        "meetings_booked",
        "roi_calculation",
        "next_month_plan_ar",
    ):
        assert key in pack


def test_roi_summary_calculates():
    s = calculate_roi_summary(subscription_sar=2999, influenced_revenue_sar=50000, hours_saved=10)
    assert s["value_to_price_multiple"] > 0

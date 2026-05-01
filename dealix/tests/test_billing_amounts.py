"""Billing amounts — halalas consistency (no payment network calls)."""

from __future__ import annotations

from api.routers.pricing import PLANS


def test_all_plan_amounts_positive_halalas():
    for key, info in PLANS.items():
        amt = int(info["amount_halalas"])
        assert amt > 0, key


def test_halalas_to_sar_conversion():
    """Display amounts use halalas / 100 as SAR (see Moyasar docs)."""
    starter = PLANS["starter"]
    sar = starter["amount_halalas"] / 100
    assert sar == 999.0


def test_pilot_plan_small_amount_for_sandbox_smoke():
    pilot = PLANS.get("pilot_1sar")
    assert pilot is not None
    assert pilot["amount_halalas"] == 100

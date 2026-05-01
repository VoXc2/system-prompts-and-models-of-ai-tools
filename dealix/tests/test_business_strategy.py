"""Business strategy API and modules."""

from __future__ import annotations

import pytest

from auto_client_acquisition.business.gtm_plan import first_10_customers_plan
from auto_client_acquisition.business.market_positioning import compare_competitors
from auto_client_acquisition.business.pricing_strategy import estimate_roi, get_pricing_tiers, recommend_plan
from auto_client_acquisition.business.launch_metrics import north_star_metrics


def test_pricing_tiers_exist():
    data = get_pricing_tiers()
    keys = {t["key"] for t in data["tiers"]}
    assert "founder_operator" in keys
    assert "growth_os" in keys
    assert "scale_os" in keys


def test_recommend_plan_works():
    r = recommend_plan(company_size="sme", monthly_budget_sar=3500, goal="pipeline")
    assert r["recommended_plan"] in ("growth_os", "scale_os", "founder_operator")


def test_roi_calculation():
    r = estimate_roi(plan_price_sar=2999, expected_pipeline_sar=90000, expected_revenue_sar=20000)
    assert r["revenue_to_subscription_multiple"] > 0


def test_competitor_list_includes_major_players():
    names = {c["name"].lower() for c in compare_competitors()}
    assert "hubspot" in names
    assert "gong" in names
    assert "salesforce" in names
    assert any("whatsapp" in n for n in names)


def test_gtm_first_10_returns_actions():
    plan = first_10_customers_plan()
    assert "actions" in plan
    assert plan["actions"]


def test_launch_metrics_exist():
    assert "primary" in north_star_metrics()


@pytest.mark.asyncio
async def test_business_pricing_endpoint(async_client):
    r = await async_client.get("/api/v1/business/pricing")
    assert r.status_code == 200
    assert "tiers" in r.json()

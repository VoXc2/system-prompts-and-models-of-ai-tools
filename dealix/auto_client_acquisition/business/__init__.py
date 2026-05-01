"""Dealix business strategy, pricing, GTM, and unit economics (deterministic, import-safe)."""

from auto_client_acquisition.business.gtm_plan import (
    channel_strategy,
    first_100_customers_plan,
    first_10_customers_plan,
    founder_led_sales_script,
    partner_strategy,
)
from auto_client_acquisition.business.launch_metrics import (
    activation_metrics,
    ai_quality_metrics,
    north_star_metrics,
    retention_metrics,
    revenue_metrics,
)
from auto_client_acquisition.business.market_positioning import (
    compare_competitors,
    dealix_differentiators,
    positioning_statement,
)
from auto_client_acquisition.business.pricing_strategy import (
    calculate_performance_fee,
    estimate_roi,
    get_pricing_tiers,
    recommend_plan,
)
from auto_client_acquisition.business.unit_economics import (
    estimate_cac_payback,
    estimate_gross_margin,
    estimate_ltv,
    estimate_mrr_path,
)

__all__ = [
    "activation_metrics",
    "ai_quality_metrics",
    "calculate_performance_fee",
    "channel_strategy",
    "compare_competitors",
    "dealix_differentiators",
    "estimate_cac_payback",
    "estimate_gross_margin",
    "estimate_ltv",
    "estimate_mrr_path",
    "estimate_roi",
    "first_100_customers_plan",
    "first_10_customers_plan",
    "founder_led_sales_script",
    "get_pricing_tiers",
    "north_star_metrics",
    "partner_strategy",
    "positioning_statement",
    "recommend_plan",
    "retention_metrics",
    "revenue_metrics",
]

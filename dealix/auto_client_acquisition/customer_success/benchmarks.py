"""
Saudi B2B Benchmarks Engine — anonymized cross-customer percentiles.

Used by:
1. Subscriber dashboard — "your reply rate is at the 67th percentile in your sector"
2. Public Saudi B2B Pulse (lead magnet, monthly free report)
3. Sector Intelligence API — sells data insights to consultancies

Privacy: NEVER returns individual customer rows. Minimum 5 customers per sector
before publishing a benchmark to prevent re-identification.

Pure-function — takes pre-aggregated input, computes percentiles + insights.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any


MIN_COHORT_SIZE = 5  # Privacy guarantee: never publish below this


@dataclass
class SectorBenchmark:
    sector: str
    cohort_size: int  # n customers
    metric: str  # reply_rate / response_time / conversion_rate / etc.
    p25: float
    p50: float
    p75: float
    p90: float
    sample_period_days: int

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass
class CustomerComparison:
    customer_id: str
    sector: str
    metric: str
    customer_value: float
    sector_p50: float
    sector_p90: float
    customer_percentile: int  # 0-100
    insight: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


def percentile(values: list[float], p: float) -> float:
    """Linear-interpolated percentile. p in [0, 100]."""
    if not values:
        return 0.0
    sorted_v = sorted(values)
    if len(sorted_v) == 1:
        return sorted_v[0]
    rank = (p / 100) * (len(sorted_v) - 1)
    lower = int(rank)
    upper = min(lower + 1, len(sorted_v) - 1)
    frac = rank - lower
    return sorted_v[lower] + (sorted_v[upper] - sorted_v[lower]) * frac


def compute_sector_benchmark(
    sector: str, metric: str, customer_values: list[float],
    sample_period_days: int = 30,
) -> SectorBenchmark | None:
    """
    Returns a sector benchmark for `metric` if cohort >= MIN_COHORT_SIZE.
    Returns None if too few customers (privacy).
    """
    if len(customer_values) < MIN_COHORT_SIZE:
        return None
    return SectorBenchmark(
        sector=sector,
        cohort_size=len(customer_values),
        metric=metric,
        p25=round(percentile(customer_values, 25), 2),
        p50=round(percentile(customer_values, 50), 2),
        p75=round(percentile(customer_values, 75), 2),
        p90=round(percentile(customer_values, 90), 2),
        sample_period_days=sample_period_days,
    )


def compare_customer(
    *, customer_id: str, sector: str, metric: str,
    customer_value: float, sector_values: list[float],
) -> CustomerComparison | None:
    """
    Where does this customer rank in their sector cohort?
    Returns None if cohort too small.
    """
    if len(sector_values) < MIN_COHORT_SIZE:
        return None
    sorted_v = sorted(sector_values)
    # rank = how many values are <= customer_value
    below = sum(1 for v in sorted_v if v <= customer_value)
    pct = round((below / len(sorted_v)) * 100)
    p50 = percentile(sector_values, 50)
    p90 = percentile(sector_values, 90)

    if pct >= 90:
        insight = f"Top 10% in {sector} — you're outperforming peers significantly"
    elif pct >= 75:
        insight = f"Top quartile in {sector} — strong performance"
    elif pct >= 50:
        insight = f"Above median in {sector} — solid ground"
    elif pct >= 25:
        insight = f"Bottom half in {sector} — opportunity to improve {metric}"
    else:
        insight = f"Bottom quartile in {sector} — review {metric} strategy with CSM"

    return CustomerComparison(
        customer_id=customer_id, sector=sector, metric=metric,
        customer_value=round(customer_value, 2),
        sector_p50=round(p50, 2), sector_p90=round(p90, 2),
        customer_percentile=pct, insight=insight,
    )


def saudi_b2b_pulse(
    *, sector_data: dict[str, dict[str, list[float]]],
) -> dict[str, Any]:
    """
    Build the monthly free 'Saudi B2B Pulse' report.

    sector_data shape:
      { "real_estate": { "reply_rate": [4.5, 6.2, ...], "response_time_min": [12, 8, ...] }, ... }

    Returns publishable report (no individual customers, only percentiles).
    """
    benchmarks: list[dict[str, Any]] = []
    insights: list[str] = []

    for sector, metrics in sector_data.items():
        for metric, values in metrics.items():
            bench = compute_sector_benchmark(sector, metric, values)
            if bench:
                benchmarks.append(bench.to_dict())

    # Trend insights (high-level, non-identifying)
    sector_count = len(sector_data)
    insights.append(f"{sector_count} Saudi B2B sectors covered this month")

    # Find sector with best reply rate
    best_sector = None
    best_p50 = 0
    for b in benchmarks:
        if b["metric"] == "reply_rate" and b["p50"] > best_p50:
            best_p50 = b["p50"]
            best_sector = b["sector"]
    if best_sector:
        insights.append(
            f"Best-performing sector by reply rate: {best_sector} (median {best_p50:.1f}%)"
        )

    return {
        "report_name": "Saudi B2B Pulse",
        "month_summary": insights,
        "min_cohort_for_publication": MIN_COHORT_SIZE,
        "sectors_covered": sector_count,
        "benchmarks": benchmarks,
        "methodology": (
            "Aggregated anonymized data from Dealix subscribers. Sectors with "
            f"fewer than {MIN_COHORT_SIZE} customers are excluded for privacy. "
            "Percentiles use linear interpolation. No individual customer data "
            "is exposed."
        ),
    }

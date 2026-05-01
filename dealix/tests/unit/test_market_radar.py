"""Smoke tests for Saudi Market Radar."""

from __future__ import annotations

from datetime import datetime, timedelta, timezone

from auto_client_acquisition.market_intelligence.city_heatmap import (
    SAUDI_CITIES,
    build_city_heatmap,
    top_hot_cities,
)
from auto_client_acquisition.market_intelligence.opportunity_feed import (
    Opportunity,
    build_opportunity_feed,
)
from auto_client_acquisition.market_intelligence.sector_pulse import (
    build_sector_pulse,
    rank_hot_sectors,
)
from auto_client_acquisition.market_intelligence.signal_detectors import (
    SIGNAL_TYPES,
    SignalDetection,
    detect_ads_signal,
    detect_funding_signal,
    detect_hiring_signal,
    detect_tender_signal,
    detect_website_change,
)


def _now():
    return datetime.now(timezone.utc).replace(tzinfo=None)


# ── Signal detectors ─────────────────────────────────────────────
def test_hiring_detects_sales_role():
    n = _now()
    out = detect_hiring_signal(
        company_id="c1",
        job_postings=[{"title": "Senior SDR", "posted_at": n - timedelta(days=2), "url": "http://x"}],
        now=n,
    )
    assert len(out) == 1
    assert out[0].signal_type == "hiring_sales_rep"


def test_hiring_skips_old_postings():
    n = _now()
    out = detect_hiring_signal(
        company_id="c1",
        job_postings=[{"title": "Sales", "posted_at": n - timedelta(days=90), "url": "x"}],
        now=n,
    )
    assert out == []


def test_website_change_booking_page():
    n = _now()
    out = detect_website_change(
        company_id="c1",
        diff={"added_paths": ["/booking", "/about"], "homepage_url": "https://x.sa"},
        now=n,
    )
    assert any(s.signal_type == "booking_page_added" for s in out)


def test_website_change_whatsapp_widget():
    n = _now()
    out = detect_website_change(
        company_id="c1",
        diff={"added_widgets": ["whatsapp_business"], "homepage_url": "https://x.sa"},
        now=n,
    )
    assert any(s.signal_type == "whatsapp_business_added" for s in out)


def test_ads_signal_requires_meaningful_jump():
    n = _now()
    # Stable: no signal
    out = detect_ads_signal(company_id="c1", weekly_ad_spend_history=[1000, 1100, 1050, 1000], now=n)
    assert out == []
    # 50% jump: should fire
    out2 = detect_ads_signal(
        company_id="c1",
        weekly_ad_spend_history=[1000, 1100, 1500, 1600],
        now=n,
    )
    assert len(out2) == 1
    assert out2[0].signal_type == "ads_volume_increased"


def test_funding_signal_within_90d():
    n = _now()
    out = detect_funding_signal(
        company_id="c1",
        announcements=[{"announced_at": n - timedelta(days=20), "round_type": "seed", "amount_sar": 5_000_000, "url": "x"}],
        now=n,
    )
    assert len(out) == 1
    assert out[0].confidence >= 0.9


def test_tender_signal_matches_keywords():
    n = _now()
    out = detect_tender_signal(
        company_id="c1",
        tenders=[{
            "title": "أنظمة CRM",
            "body": "نظام CRM",
            "published_at": n - timedelta(days=3),
            "deadline": n + timedelta(days=20),
            "url": "x",
            "value_sar": 1_000_000,
        }],
        icp_keywords=("crm",),
        now=n,
    )
    assert len(out) == 1


def test_tender_skips_closed_deadline():
    n = _now()
    out = detect_tender_signal(
        company_id="c1",
        tenders=[{
            "title": "X", "body": "y",
            "published_at": n - timedelta(days=10),
            "deadline": n - timedelta(days=1),
            "url": "z",
        }],
        now=n,
    )
    assert out == []


def test_signal_taxonomy_no_duplicates():
    assert len(SIGNAL_TYPES) == len(set(SIGNAL_TYPES))


# ── Sector pulse ─────────────────────────────────────────────────
def test_sector_pulse_rising():
    n = _now()
    this_week = [
        SignalDetection("c1", "hiring_sales_rep", n, "linkedin", 0.9),
        SignalDetection("c2", "hiring_sales_rep", n, "linkedin", 0.9),
        SignalDetection("c3", "booking_page_added", n, "diff", 0.8),
        SignalDetection("c4", "tender_published", n, "feed", 0.95),
    ]
    prior = [SignalDetection("c1", "hiring_sales_rep", n, "linkedin", 0.9)]
    pulse = build_sector_pulse(sector="real_estate", signals_this_week=this_week,
                                signals_prior_week=prior)
    assert pulse.trend == "rising"
    assert pulse.active_signals == 4
    assert pulse.n_companies_with_signals == 4


def test_sector_pulse_cooling():
    n = _now()
    pulse = build_sector_pulse(
        sector="construction",
        signals_this_week=[],
        signals_prior_week=[SignalDetection("c1", "tender_published", n, "feed", 1.0)] * 5,
    )
    assert pulse.trend == "cooling"


def test_rank_hot_sectors_orders_by_score():
    pulses = [
        build_sector_pulse(sector="A", signals_this_week=[], signals_prior_week=[]),
        build_sector_pulse(
            sector="B",
            signals_this_week=[SignalDetection(f"c{i}", "hiring_sales_rep", _now(), "src", 0.9) for i in range(20)],
            signals_prior_week=[SignalDetection(f"c{i}", "hiring_sales_rep", _now(), "src", 0.9) for i in range(2)],
        ),
    ]
    ranked = rank_hot_sectors(pulses=pulses, top_n=2)
    assert ranked[0].sector == "B"


# ── City heatmap ─────────────────────────────────────────────────
def test_city_heatmap_groups_signals():
    signals_by_company = {
        "c1": [SignalDetection("c1", "hiring_sales_rep", _now(), "src", 0.9)] * 5,
        "c2": [SignalDetection("c2", "booking_page_added", _now(), "src", 0.8)] * 3,
        "c3": [SignalDetection("c3", "tender_published", _now(), "src", 0.95)] * 2,
    }
    metadata = {
        "c1": {"city": "الرياض", "sector": "real_estate"},
        "c2": {"city": "الرياض", "sector": "clinics"},
        "c3": {"city": "جدة", "sector": "logistics"},
    }
    heatmaps = build_city_heatmap(
        signals_by_company=signals_by_company, company_metadata=metadata
    )
    cities = {h.city: h for h in heatmaps}
    assert cities["الرياض"].n_companies == 2
    assert cities["الرياض"].n_signals == 8
    assert cities["جدة"].n_companies == 1


def test_top_hot_cities_filter():
    heatmaps = [
        type("H", (), {"city": "الرياض", "bucket": "hot", "heat_score": 70})(),
        type("H", (), {"city": "حائل", "bucket": "cool", "heat_score": 10})(),
    ]
    out = top_hot_cities(heatmaps=heatmaps)
    assert len(out) == 1
    assert out[0].city == "الرياض"


# ── Opportunity feed ─────────────────────────────────────────────
def test_opportunity_feed_uses_explainer():
    n = _now()
    signals = [
        SignalDetection("c1", "hiring_sales_rep", n, "src", 0.9),
        SignalDetection("c2", "tender_published", n, "src", 0.95),
    ]
    metadata = {
        "c1": {"name": "Alpha Co.", "sector": "real_estate", "city": "الرياض",
               "estimated_deal_value_sar": 100_000},
        "c2": {"name": "Beta Logistics", "sector": "logistics", "city": "جدة"},
    }

    # Inject the real Why-Now explainer
    from auto_client_acquisition.revenue_graph.why_now import explain_why_now, WhyNowSignal

    def explainer(*, company_id, signals, sector, sector_pulse_trend):
        wn_signals = [
            WhyNowSignal(
                signal_type=s.signal_type,
                detected_at=s.detected_at,
                source=s.source,
                evidence_url=s.evidence_url,
                payload=s.payload,
            )
            for s in signals
        ]
        return explain_why_now(
            company_id=company_id, signals=wn_signals,
            sector=sector, sector_pulse_trend=sector_pulse_trend,
        )

    feed = build_opportunity_feed(
        signals=signals, company_metadata=metadata,
        why_now_explainer=explainer, top_n=10,
    )
    assert 1 <= len(feed) <= 2
    assert all(o.priority_score > 0 for o in feed)
    # Verify opportunity has all required fields
    assert all(o.suggested_channel for o in feed)
    assert all(o.suggested_angle_ar for o in feed)

"""Smoke tests for dominance router OFFER_ROUTES + helpers."""

from __future__ import annotations

from auto_client_acquisition.intelligence.offers import (
    DEFAULT_OFFER, OFFER_ROUTES, build_tomorrow_recommendation, route_offer,
)
_build_tomorrow_recommendation = build_tomorrow_recommendation


def test_offer_routes_has_high_fit_sectors():
    """All 4 priority sectors must have a route."""
    for sec in ["real_estate_developer", "construction", "hospitality",
                "logistics", "marketing_agency"]:
        assert sec in OFFER_ROUTES, f"missing route for {sec}"


def test_offer_route_has_required_keys():
    required = {"primary_offer", "value_prop", "headline_pain",
                "kpi", "best_channel", "pricing_tier"}
    for sec, cfg in OFFER_ROUTES.items():
        missing = required - set(cfg.keys())
        assert not missing, f"{sec} missing: {missing}"


def test_default_offer_pilot_499():
    assert "499" in DEFAULT_OFFER["primary_offer"]


def test_marketing_agency_partnership_route():
    cfg = OFFER_ROUTES["marketing_agency"]
    assert "partner" in cfg["primary_offer"].lower() or "MRR" in cfg["primary_offer"]
    assert "Partnership" in cfg["pricing_tier"]


def test_tomorrow_recommendation_handles_empty_data():
    rec = _build_tomorrow_recommendation([], 0, 0)
    assert "actions" in rec
    assert len(rec["actions"]) >= 1


def test_tomorrow_recommendation_flags_low_drafts():
    rec = _build_tomorrow_recommendation([], 5, 10)  # only 5 drafts
    assert any("نقص" in a or "drafts" in a for a in rec["actions"])


def test_tomorrow_recommendation_flags_low_replies():
    rec = _build_tomorrow_recommendation([], 50, 0)
    assert any("الردود منخفض" in a or "subject" in a for a in rec["actions"])


def test_tomorrow_recommendation_promotes_winning_sector():
    leaderboard = [
        {"sector": "real_estate", "sent": 50, "replied": 5,
         "reply_rate": 0.10, "positive": 3, "positive_rate": 0.06},
        {"sector": "manufacturing", "sent": 30, "replied": 0,
         "reply_rate": 0.0, "positive": 0, "positive_rate": 0.0},
    ]
    rec = _build_tomorrow_recommendation(leaderboard, 50, 5)
    actions = rec["actions"]
    assert any("real_estate" in a and "ضاعف" in a for a in actions)

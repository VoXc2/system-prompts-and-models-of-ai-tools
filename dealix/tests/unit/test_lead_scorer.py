"""Unit tests for LeadScorer heuristic."""

from __future__ import annotations

from dealix.intelligence.lead_scorer import LeadFeatures, LeadScorer


def test_hot_lead_scores_high():
    scorer = LeadScorer()
    features = LeadFeatures(
        company_size=100,
        budget_usd=50000,
        urgency_score=0.9,
        has_company_email=True,
        has_phone=True,
        pain_points_count=3,
        sector_fit=0.9,
    )
    result = scorer.score(features)
    assert result.tier == "hot"
    assert result.score >= 0.7


def test_cold_lead_scores_low():
    scorer = LeadScorer()
    features = LeadFeatures()  # all zero
    result = scorer.score(features)
    assert result.tier == "cold"
    assert result.score < 0.45


def test_reasons_are_populated_for_strong_signals():
    scorer = LeadScorer()
    features = LeadFeatures(budget_usd=20000, urgency_score=0.8)
    result = scorer.score(features)
    assert any("ميزانية" in r for r in result.reasons)

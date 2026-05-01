"""Unit tests for the ICP matcher."""

from __future__ import annotations

import pytest

from auto_client_acquisition.agents.icp_matcher import (
    DEFAULT_ICP,
    ICPMatcherAgent,
)
from auto_client_acquisition.agents.intake import IntakeAgent, LeadSource


@pytest.mark.asyncio
async def test_ideal_lead_scores_high(sample_lead_payload):
    intake = IntakeAgent()
    lead = await intake.run(payload=sample_lead_payload, source=LeadSource.WEBSITE)
    matcher = ICPMatcherAgent(icp=DEFAULT_ICP)
    result = await matcher.run(lead=lead)

    assert 0 <= result.overall_score <= 1
    assert result.industry_match == 1.0  # technology is in target
    assert result.region_match == 1.0  # Saudi Arabia
    assert result.budget_match == 1.0  # 50k SAR in range
    assert result.tier in {"A", "B"}
    assert result.recommendations


@pytest.mark.asyncio
async def test_bad_fit_scores_low():
    intake = IntakeAgent()
    bad_lead = await intake.run(
        payload={
            "company": "Irrelevant Co",
            "name": "Jane",
            "sector": "unknown_sector",
            "region": "Antarctica",
            "budget": 100,
        },
        source=LeadSource.WEBSITE,
    )
    matcher = ICPMatcherAgent(icp=DEFAULT_ICP)
    result = await matcher.run(lead=bad_lead)

    assert result.overall_score < 0.5
    assert result.tier in {"C", "D"}


@pytest.mark.asyncio
async def test_weights_sum_to_one():
    total = sum(ICPMatcherAgent.WEIGHTS.values())
    assert abs(total - 1.0) < 1e-9

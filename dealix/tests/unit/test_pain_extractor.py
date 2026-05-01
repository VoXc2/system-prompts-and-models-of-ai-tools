"""Unit tests for the Pain Extractor."""

from __future__ import annotations

import pytest

from auto_client_acquisition.agents.pain_extractor import PainExtractorAgent


@pytest.mark.asyncio
async def test_keyword_only_arabic():
    agent = PainExtractorAgent()
    result = await agent.run(
        message="عندنا مشكلة عاجلة في إدارة العملاء، العملية بطيئة جداً ونحتاج حل فوراً",
        use_llm=False,
    )
    assert result.method == "keyword"
    assert result.urgency_score >= 0.8
    assert any(p.category in ("general", "performance") for p in result.pain_points)


@pytest.mark.asyncio
async def test_keyword_only_english():
    agent = PainExtractorAgent()
    result = await agent.run(
        message="We have a slow and expensive manual process, urgent need to fix",
        use_llm=False,
    )
    assert result.method == "keyword"
    assert result.urgency_score >= 0.8
    assert len(result.pain_points) >= 2
    assert result.likely_offer


@pytest.mark.asyncio
async def test_empty_message():
    agent = PainExtractorAgent()
    result = await agent.run(message="", use_llm=False)
    assert result.method == "empty"
    assert result.urgency_score == 0.0


@pytest.mark.asyncio
async def test_llm_path_with_mock(mock_router):
    mock_router.run.return_value.content = (
        '{"pain_points": [{"text": "slow response", "category": "performance", "severity": 0.8}], '
        '"urgency_score": 0.9, "likely_offer": "AI Automation Retainer", '
        '"recommended_next_step": "Call today", "key_phrases": ["slow"]}'
    )
    agent = PainExtractorAgent()
    result = await agent.run(message="slow response times", use_llm=True)
    assert result.method == "hybrid"
    assert result.urgency_score == pytest.approx(0.9)

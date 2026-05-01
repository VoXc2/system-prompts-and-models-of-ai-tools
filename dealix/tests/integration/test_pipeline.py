"""Integration tests for the full Phase 8 pipeline."""

from __future__ import annotations

import pytest

from auto_client_acquisition.pipeline import AcquisitionPipeline


@pytest.mark.asyncio
async def test_pipeline_runs_without_llm(sample_lead_payload, mock_router):
    """Pipeline should complete even if LLM calls fail (graceful degradation)."""
    mock_router.run.return_value.content = (
        '{"pain_points":[], "urgency_score":0.5, "likely_offer":"Demo", '
        '"recommended_next_step":"Call", "key_phrases":[]}'
    )
    pipeline = AcquisitionPipeline()
    result = await pipeline.run(
        payload=sample_lead_payload,
        auto_book=False,
        auto_proposal=False,
    )

    assert result.lead.id
    assert result.lead.company_name == sample_lead_payload["company"]
    assert result.fit_score is not None
    assert result.fit_score.overall_score > 0.5  # Good fit for our sample


@pytest.mark.asyncio
async def test_pipeline_handles_missing_optional_fields(mock_router):
    mock_router.run.return_value.content = '{"ok": true}'
    pipeline = AcquisitionPipeline()
    result = await pipeline.run(
        payload={"company": "Mini Co", "name": "X"},
        auto_book=False,
    )
    assert result.lead.id
    # Should not crash even with sparse data
    assert result.fit_score is not None

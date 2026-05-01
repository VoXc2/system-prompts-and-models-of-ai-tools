"""FastAPI dependencies — dependency injection for services."""

from __future__ import annotations

from functools import lru_cache

from auto_client_acquisition.agents.proposal import ProposalAgent
from auto_client_acquisition.pipeline import AcquisitionPipeline
from autonomous_growth.agents.content import ContentCreatorAgent
from autonomous_growth.agents.sector_intel import SectorIntelAgent
from autonomous_growth.orchestrator import GrowthOrchestrator


@lru_cache(maxsize=1)
def get_acquisition_pipeline() -> AcquisitionPipeline:
    return AcquisitionPipeline()


@lru_cache(maxsize=1)
def get_growth_orchestrator() -> GrowthOrchestrator:
    return GrowthOrchestrator()


@lru_cache(maxsize=1)
def get_sector_intel_agent() -> SectorIntelAgent:
    return SectorIntelAgent()


@lru_cache(maxsize=1)
def get_content_agent() -> ContentCreatorAgent:
    return ContentCreatorAgent()


@lru_cache(maxsize=1)
def get_proposal_agent() -> ProposalAgent:
    return ProposalAgent()

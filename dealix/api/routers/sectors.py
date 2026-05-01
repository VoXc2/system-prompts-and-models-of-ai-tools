"""Sectors (Phase 9) endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query

from api.dependencies import get_content_agent, get_sector_intel_agent
from api.schemas import ContentRequest, ContentResponse, SectorIntelResponse
from autonomous_growth.agents.content import ContentCreatorAgent
from autonomous_growth.agents.sector_intel import SaudiSector, SectorIntelAgent

router = APIRouter(prefix="/api/v1/sectors", tags=["sectors"])


@router.get("/{sector}", response_model=SectorIntelResponse)
async def sector_intel(
    sector: str,
    enrich_with_llm: bool = Query(False, description="Enrich baseline with LLM research"),
    agent: SectorIntelAgent = Depends(get_sector_intel_agent),
) -> SectorIntelResponse:
    """Deep intel for one Saudi sector."""
    try:
        sector_enum = SaudiSector(sector)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=f"Unknown sector: {sector}") from e
    intel = await agent.run(sector=sector_enum, enrich_with_llm=enrich_with_llm)
    return SectorIntelResponse(**intel.to_dict())


@router.get("/best/opportunity", response_model=SectorIntelResponse)
async def best_opportunity(
    agent: SectorIntelAgent = Depends(get_sector_intel_agent),
) -> SectorIntelResponse:
    """Return the highest-leverage sector."""
    intel = await agent.best_opportunity()
    return SectorIntelResponse(**intel.to_dict())


@router.get("/target/list", response_model=list[SectorIntelResponse])
async def target_sectors(
    agent: SectorIntelAgent = Depends(get_sector_intel_agent),
) -> list[SectorIntelResponse]:
    """Our top-5 target sectors."""
    intels = agent.target_sectors()
    return [SectorIntelResponse(**i.to_dict()) for i in intels]


@router.post("/content", response_model=ContentResponse)
async def generate_content(
    request: ContentRequest,
    agent: ContentCreatorAgent = Depends(get_content_agent),
) -> ContentResponse:
    """Generate a content piece for a sector topic."""
    piece = await agent.run(
        topic=request.topic,
        content_type=request.content_type,  # type: ignore[arg-type]
        channel=request.channel,  # type: ignore[arg-type]
        locale=request.locale,
        length=request.length,
    )
    return ContentResponse(**piece.to_dict())

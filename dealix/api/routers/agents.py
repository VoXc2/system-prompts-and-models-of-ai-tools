"""Direct agent execution endpoints — useful for testing individual agents."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body

from auto_client_acquisition.agents.icp_matcher import ICPMatcherAgent
from auto_client_acquisition.agents.intake import IntakeAgent, LeadSource
from auto_client_acquisition.agents.pain_extractor import PainExtractorAgent
from autonomous_growth.agents.market_research import MarketResearchAgent

router = APIRouter(prefix="/api/v1/agents", tags=["agents"])


@router.post("/intake")
async def run_intake(
    payload: dict[str, Any] = Body(...),
    source: str = "website",
) -> dict[str, Any]:
    agent = IntakeAgent()
    lead = await agent.run(payload=payload, source=LeadSource(source))
    return lead.to_dict()


@router.post("/pain-extractor")
async def run_pain_extractor(
    body: dict[str, Any] = Body(...),
) -> dict[str, Any]:
    agent = PainExtractorAgent()
    result = await agent.run(
        message=str(body.get("message", "")),
        locale=body.get("locale"),
        use_llm=bool(body.get("use_llm", True)),
    )
    return result.to_dict()


@router.post("/icp-match")
async def run_icp_match(
    body: dict[str, Any] = Body(...),
) -> dict[str, Any]:
    intake = IntakeAgent()
    lead = await intake.run(payload=body, source=LeadSource.API)
    matcher = ICPMatcherAgent()
    fit = await matcher.run(lead=lead)
    return {"lead": lead.to_dict(), "fit_score": fit.to_dict()}


@router.post("/research")
async def run_research(
    body: dict[str, Any] = Body(...),
) -> dict[str, Any]:
    agent = MarketResearchAgent()
    finding = await agent.run(
        question=str(body.get("question", "")),
        locale=str(body.get("locale", "en")),
        depth=str(body.get("depth", "standard")),
    )
    return finding.to_dict()

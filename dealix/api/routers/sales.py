"""Sales endpoints — scripts, proposals."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException

from api.dependencies import get_proposal_agent
from api.schemas import (
    ProposalRequest,
    ProposalResponse,
    SalesScriptRequest,
    SalesScriptResponse,
)
from auto_client_acquisition.agents.intake import Lead, LeadSource
from auto_client_acquisition.agents.proposal import ProposalAgent
from core.prompts.sales_scripts import get_sales_script
from core.utils import generate_id

router = APIRouter(prefix="/api/v1/sales", tags=["sales"])


@router.post("/script", response_model=SalesScriptResponse)
async def build_script(request: SalesScriptRequest) -> SalesScriptResponse:
    """Return a bilingual sales script for a given sector + type."""
    try:
        script = get_sales_script(
            request.script_type,
            locale=request.locale,
            name=request.name or "",
            sector=request.sector,
            company=request.company or "",
            date="",
            time="",
            link="",
        )
    except KeyError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
    return SalesScriptResponse(
        script=script,
        locale=request.locale,
        script_type=request.script_type,
    )


@router.post("/proposal", response_model=ProposalResponse)
async def generate_proposal(
    request: ProposalRequest,
    agent: ProposalAgent = Depends(get_proposal_agent),
) -> ProposalResponse:
    """Generate a proposal on demand (outside the pipeline)."""
    lead = Lead(
        id=request.lead_id or generate_id("lead"),
        source=LeadSource.MANUAL,
        company_name=request.company_name,
        contact_name="",
        sector=request.sector,
        region=request.region,
        budget=request.budget_hint,
        pain_points=request.pain_points,
        locale=request.locale,
    )
    proposal = await agent.run(lead=lead, outcomes=request.outcomes or None)
    return ProposalResponse(
        id=proposal.id,
        lead_id=proposal.lead_id,
        company_name=proposal.company_name,
        body_markdown=proposal.body_markdown,
        budget_min=proposal.budget_min,
        budget_max=proposal.budget_max,
        currency=proposal.currency,
        valid_until=proposal.valid_until,
        created_at=proposal.created_at,
    )

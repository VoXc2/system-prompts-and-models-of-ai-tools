"""Structured Outputs API — produce validated schema-bound artifacts from real data."""

from fastapi import APIRouter, Depends
from pydantic import BaseModel as PydanticBase
from typing import Any, Dict, Optional

router = APIRouter(prefix="/structured-outputs", tags=["Structured Outputs"])


async def _get_db():
    from app.database import get_db
    async for session in get_db():
        yield session


class LeadScoreRequest(PydanticBase):
    lead_id: str

class QualificationRequest(PydanticBase):
    deal_id: str
    lead_id: str

class ProposalRequest(PydanticBase):
    deal_id: str

class PricingRequest(PydanticBase):
    deal_id: str
    discount_percent: float = 0

class HandoffRequest(PydanticBase):
    deal_id: str

class TargetRequest(PydanticBase):
    company_name: str
    sector: str
    revenue_sar: float
    employees: int

class ValuationRequest(PydanticBase):
    target_id: str
    revenue_sar: float

class SynergyRequest(PydanticBase):
    target_id: str
    revenue_synergy: float
    cost_synergy: float
    integration_cost: float

class ExpansionRequest(PydanticBase):
    market: str
    market_ar: str
    dialect: str = "gulf"


@router.post("/lead-score-card")
async def lead_score_card(body: LeadScoreRequest, tenant_id: str = "00000000-0000-0000-0000-000000000000", db=Depends(_get_db)) -> Dict[str, Any]:
    from app.services.structured_output_producers import produce_lead_score_card
    return await produce_lead_score_card(db, tenant_id=tenant_id, lead_id=body.lead_id)


@router.post("/qualification-memo")
async def qualification_memo(body: QualificationRequest, tenant_id: str = "00000000-0000-0000-0000-000000000000", db=Depends(_get_db)) -> Dict[str, Any]:
    from app.services.structured_output_producers import produce_qualification_memo
    return await produce_qualification_memo(db, tenant_id=tenant_id, deal_id=body.deal_id, lead_id=body.lead_id)


@router.post("/proposal-pack")
async def proposal_pack(body: ProposalRequest, tenant_id: str = "00000000-0000-0000-0000-000000000000", db=Depends(_get_db)) -> Dict[str, Any]:
    from app.services.structured_output_producers import produce_proposal_pack
    return await produce_proposal_pack(db, tenant_id=tenant_id, deal_id=body.deal_id)


@router.post("/pricing-decision")
async def pricing_decision(body: PricingRequest, tenant_id: str = "00000000-0000-0000-0000-000000000000", db=Depends(_get_db)) -> Dict[str, Any]:
    from app.services.structured_output_producers import produce_pricing_decision
    return await produce_pricing_decision(db, tenant_id=tenant_id, deal_id=body.deal_id, discount_percent=body.discount_percent)


@router.post("/handoff-checklist")
async def handoff_checklist(body: HandoffRequest, tenant_id: str = "00000000-0000-0000-0000-000000000000", db=Depends(_get_db)) -> Dict[str, Any]:
    from app.services.structured_output_producers import produce_handoff_checklist
    return await produce_handoff_checklist(db, tenant_id=tenant_id, deal_id=body.deal_id)


@router.post("/target-profile")
async def target_profile(body: TargetRequest) -> Dict[str, Any]:
    from app.services.structured_output_producers import produce_target_profile
    return await produce_target_profile(company_name=body.company_name, sector=body.sector, revenue_sar=body.revenue_sar, employees=body.employees)


@router.post("/valuation-memo")
async def valuation_memo(body: ValuationRequest) -> Dict[str, Any]:
    from app.services.structured_output_producers import produce_valuation_memo
    return await produce_valuation_memo(target_id=body.target_id, revenue_sar=body.revenue_sar)


@router.post("/synergy-model")
async def synergy_model(body: SynergyRequest) -> Dict[str, Any]:
    from app.services.structured_output_producers import produce_synergy_model
    return await produce_synergy_model(target_id=body.target_id, revenue_synergy=body.revenue_synergy, cost_synergy=body.cost_synergy, integration_cost=body.integration_cost)


@router.post("/expansion-plan")
async def expansion_plan(body: ExpansionRequest) -> Dict[str, Any]:
    from app.services.structured_output_producers import produce_expansion_plan
    return await produce_expansion_plan(market=body.market, market_ar=body.market_ar, dialect=body.dialect)


@router.post("/stop-loss-policy")
async def stop_loss_policy(market: str = "UAE") -> Dict[str, Any]:
    from app.services.structured_output_producers import produce_stop_loss_policy
    return await produce_stop_loss_policy(market=market)

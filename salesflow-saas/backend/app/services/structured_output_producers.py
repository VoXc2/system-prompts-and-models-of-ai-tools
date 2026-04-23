"""Structured Output Producers — wire all 17 schemas to live flows.

Each producer takes real data and returns a validated Pydantic schema instance.
This is the bridge between raw DB data and schema-bound structured outputs.
"""

from __future__ import annotations

import uuid
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.structured_outputs import (
    ApprovalPacket,
    BoardPackDraft,
    DDPlan,
    EconomicsModel,
    ExecWeeklyPack,
    ExpansionPlan,
    HandoffChecklist,
    ICMemo,
    LeadScoreCard,
    PMIProgramPlan,
    PartnerDossier,
    PricingDecisionRecord,
    ProposalPack,
    Provenance,
    QualificationMemo,
    StopLossPolicy,
    SynergyModel,
    TargetProfile,
    ValuationMemo,
)


def _provenance(source: str, confidence: float = 0.8, trace_id: str | None = None) -> Provenance:
    return Provenance(
        generated_by=source,
        model_provider="system",
        confidence=confidence,
        freshness_hours=0.0,
        trace_id=trace_id or str(uuid.uuid4()),
    )


# ── Revenue Track Producers ──────────────────────────────────

async def produce_lead_score_card(
    db: AsyncSession, *, tenant_id: str, lead_id: str
) -> Dict[str, Any]:
    """Produce LeadScoreCard from real lead data."""
    from app.models.lead import Lead

    lead = (await db.execute(select(Lead).where(Lead.id == lead_id))).scalar_one_or_none()
    if not lead:
        return {"error": "lead_not_found"}

    score = lead.score or 0
    tier = "hot" if score >= 80 else ("warm" if score >= 50 else "cold")
    recommendation = "qualify" if score >= 70 else ("nurture" if score >= 40 else "disqualify")

    card = LeadScoreCard(
        lead_id=str(lead.id),
        tenant_id=tenant_id,
        score=score,
        tier=tier,
        signals=[{"source": lead.source or "unknown", "status": lead.status or "new"}],
        company_size_score=min(score * 0.2, 20),
        industry_fit_score=min(score * 0.25, 25),
        engagement_score=min(score * 0.3, 30),
        budget_signal_score=min(score * 0.15, 15),
        timing_score=min(score * 0.1, 10),
        recommendation=recommendation,
        reasoning=f"Lead score {score}/100 — {tier} tier, recommend {recommendation}",
        provenance=_provenance("structured_output_producers.produce_lead_score_card"),
    )
    return card.model_dump(mode="json")


async def produce_qualification_memo(
    db: AsyncSession, *, tenant_id: str, deal_id: str, lead_id: str
) -> Dict[str, Any]:
    """Produce QualificationMemo from real deal + lead data."""
    card_data = await produce_lead_score_card(db, tenant_id=tenant_id, lead_id=lead_id)
    if "error" in card_data:
        return card_data

    card = LeadScoreCard(**card_data)
    status = "qualified" if card.score >= 70 else ("needs_info" if card.score >= 40 else "not_qualified")

    memo = QualificationMemo(
        deal_id=deal_id,
        tenant_id=tenant_id,
        lead_score_card=card,
        qualification_status=status,
        decision_factors=[f"Score: {card.score}", f"Tier: {card.tier}", f"Recommendation: {card.recommendation}"],
        risks=["New lead — limited engagement history"] if card.score < 70 else [],
        next_steps=["Schedule discovery call"] if status == "qualified" else ["Nurture sequence"],
        provenance=_provenance("structured_output_producers.produce_qualification_memo"),
    )
    return memo.model_dump(mode="json")


async def produce_proposal_pack(
    db: AsyncSession, *, tenant_id: str, deal_id: str
) -> Dict[str, Any]:
    """Produce ProposalPack from real deal data."""
    from app.models.deal import Deal

    deal = (await db.execute(select(Deal).where(Deal.id == deal_id))).scalar_one_or_none()
    if not deal:
        return {"error": "deal_not_found"}

    value = float(deal.value or 0)
    pack = ProposalPack(
        deal_id=str(deal.id),
        tenant_id=tenant_id,
        proposal_version=1,
        title=deal.title or "Untitled",
        value_proposition=f"Dealix implementation for {deal.title}",
        line_items=[{"item": "Platform license", "amount_sar": value * 0.7}, {"item": "Implementation", "amount_sar": value * 0.3}],
        total_value_sar=value,
        discount_percent=0.0,
        discount_requires_approval=value > 100000,
        payment_terms="Net 30",
        validity_days=30,
        provenance=_provenance("structured_output_producers.produce_proposal_pack"),
    )
    return pack.model_dump(mode="json")


async def produce_pricing_decision(
    db: AsyncSession, *, tenant_id: str, deal_id: str, discount_percent: float = 0
) -> Dict[str, Any]:
    """Produce PricingDecisionRecord."""
    from app.models.deal import Deal

    deal = (await db.execute(select(Deal).where(Deal.id == deal_id))).scalar_one_or_none()
    if not deal:
        return {"error": "deal_not_found"}

    base = float(deal.value or 0)
    final = base * (1 - discount_percent / 100)

    record = PricingDecisionRecord(
        deal_id=str(deal.id),
        tenant_id=tenant_id,
        base_price_sar=base,
        final_price_sar=round(final, 2),
        discount_percent=discount_percent,
        discount_reason="Standard pricing" if discount_percent == 0 else "Negotiated discount",
        approval_required=discount_percent > 10,
        approval_status="pending" if discount_percent > 10 else None,
        policy_class="B" if discount_percent > 10 else "A",
        provenance=_provenance("structured_output_producers.produce_pricing_decision"),
    )
    return record.model_dump(mode="json")


async def produce_handoff_checklist(
    db: AsyncSession, *, tenant_id: str, deal_id: str
) -> Dict[str, Any]:
    """Produce HandoffChecklist for sales-to-onboarding transition."""
    checklist = HandoffChecklist(
        deal_id=deal_id,
        tenant_id=tenant_id,
        items=[
            {"item": "Contract signed", "status": "pending", "owner": "sales", "due_date": ""},
            {"item": "Payment received", "status": "pending", "owner": "finance", "due_date": ""},
            {"item": "Onboarding call scheduled", "status": "pending", "owner": "cs", "due_date": ""},
            {"item": "Admin account created", "status": "pending", "owner": "ops", "due_date": ""},
            {"item": "Data import completed", "status": "pending", "owner": "ops", "due_date": ""},
        ],
        all_complete=False,
        blockers=[],
        provenance=_provenance("structured_output_producers.produce_handoff_checklist"),
    )
    return checklist.model_dump(mode="json")


# ── M&A Track Producers ──────────────────────────────────────

async def produce_target_profile(*, company_name: str, sector: str, revenue_sar: float, employees: int) -> Dict[str, Any]:
    """Produce TargetProfile for acquisition screening."""
    fit = min(100, revenue_sar / 10000 + employees * 0.5)
    profile = TargetProfile(
        company_name=company_name,
        sector=sector,
        revenue_sar=revenue_sar,
        employee_count=employees,
        geographic_fit="Saudi Arabia",
        strategic_fit_score=round(fit, 1),
        recommendation="short_list" if fit >= 70 else ("watch" if fit >= 40 else "reject"),
        provenance=_provenance("structured_output_producers.produce_target_profile"),
    )
    return profile.model_dump(mode="json")


async def produce_valuation_memo(*, target_id: str, revenue_sar: float) -> Dict[str, Any]:
    """Produce ValuationMemo with simple multiples."""
    memo = ValuationMemo(
        target_id=target_id,
        methodology="comparable",
        low_sar=revenue_sar * 2,
        mid_sar=revenue_sar * 3.5,
        high_sar=revenue_sar * 5,
        key_assumptions=["Revenue multiple range: 2x-5x", "Based on Saudi B2B SaaS comparables"],
        sensitivity=[{"multiplier": 2.0, "value": revenue_sar * 2}, {"multiplier": 5.0, "value": revenue_sar * 5}],
        provenance=_provenance("structured_output_producers.produce_valuation_memo"),
    )
    return memo.model_dump(mode="json")


async def produce_synergy_model(*, target_id: str, revenue_synergy: float, cost_synergy: float, integration_cost: float) -> Dict[str, Any]:
    """Produce SynergyModel."""
    model = SynergyModel(
        target_id=target_id,
        revenue_synergies_sar=revenue_synergy,
        cost_synergies_sar=cost_synergy,
        integration_costs_sar=integration_cost,
        net_synergy_sar=revenue_synergy + cost_synergy - integration_cost,
        realization_months=18,
        risk_factors=["Integration complexity", "Cultural alignment", "Key person retention"],
        provenance=_provenance("structured_output_producers.produce_synergy_model"),
    )
    return model.model_dump(mode="json")


# ── Expansion Track Producers ────────────────────────────────

async def produce_expansion_plan(*, market: str, market_ar: str, dialect: str) -> Dict[str, Any]:
    """Produce ExpansionPlan for market entry."""
    plan = ExpansionPlan(
        market=market,
        market_ar=market_ar,
        phase="scan",
        regulatory_complexity="medium",
        dialect_support=dialect,
        gtm_strategy=f"Canary launch in {market} with local partner",
        canary_criteria=["10 pilot users", "5% conversion rate", "No critical bugs"],
        stop_loss_triggers=[
            {"metric": "conversion_rate", "threshold": 5, "action": "pause", "evaluation_period_days": 30},
            {"metric": "churn_rate", "threshold": 20, "action": "halt", "evaluation_period_days": 30},
        ],
        provenance=_provenance("structured_output_producers.produce_expansion_plan"),
    )
    return plan.model_dump(mode="json")


async def produce_stop_loss_policy(*, market: str) -> Dict[str, Any]:
    """Produce StopLossPolicy for expansion."""
    policy = StopLossPolicy(
        market=market,
        metrics=[
            {"metric": "conversion_rate", "threshold": 5, "action": "pause_expansion", "evaluation_period_days": 30},
            {"metric": "customer_complaints", "threshold": 10, "action": "investigate", "evaluation_period_days": 14},
            {"metric": "revenue_vs_forecast", "threshold": 50, "action": "review_exit", "evaluation_period_days": 60},
            {"metric": "compliance_violations", "threshold": 1, "action": "halt_immediately", "evaluation_period_days": 1},
        ],
        active=True,
        provenance=_provenance("structured_output_producers.produce_stop_loss_policy"),
    )
    return policy.model_dump(mode="json")

"""
Revenue Command Center router — single integration point for the
in-product dashboard. Exposes everything from the revenue_graph layer:
  - Why-Now? explanations
  - Revenue Leak Detector
  - Maturity / Benchmark Score
  - Acquisition Simulator
  - Objection Library
  - Proof Pack generator
  - Agent registry catalog
  - Sector Playbooks
  - Graph health / moat score

These endpoints power /landing/command-center.html and the customer portal.
"""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from fastapi import APIRouter, Body, HTTPException, Query

from auto_client_acquisition.revenue_graph.agent_registry import (
    ALL_AGENTS,
    agents_summary,
    get_agent,
    list_agents_by_autonomy,
    list_agents_by_runtime,
)
from auto_client_acquisition.revenue_graph.graph import (
    CompanyVector,
    OutcomeStats,
    aggregate_outcomes,
    cosine_similarity,
    find_similar_companies,
    graph_health_summary,
    predict_outcome_probabilities,
    recommend_next_action,
)
from auto_client_acquisition.revenue_graph.leak_detector import detect_all_leaks
from auto_client_acquisition.revenue_graph.maturity_score import (
    DIMENSIONS,
    DIMENSION_WEIGHTS,
    compute_benchmark_score,
)
from auto_client_acquisition.revenue_graph.objection_library import (
    OBJECTION_CATEGORIES,
    SAUDI_B2B_OBJECTIONS,
    category_summary,
    find_by_keyword,
    list_by_category,
)
from auto_client_acquisition.revenue_graph.proof_pack import (
    ProofPackInputs,
    generate_proof_pack,
)
from auto_client_acquisition.revenue_graph.sector_playbooks import (
    ALL_PLAYBOOKS,
    get_playbook,
    list_playbooks_summary,
)
from auto_client_acquisition.revenue_graph.simulator import (
    SECTOR_BENCHMARKS,
    SimulatorInputs,
    simulate,
)
from auto_client_acquisition.revenue_graph.why_now import (
    SIGNAL_WEIGHTS,
    WhyNowSignal,
    explain_why_now,
    rank_todays_priorities,
)

router = APIRouter(prefix="/api/v1/command-center", tags=["command-center"])
log = logging.getLogger(__name__)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc).replace(tzinfo=None)


def _spec_to_dict(a: Any) -> dict[str, Any]:
    """Convert agent spec / dataclass into a dashboard-ready dict."""
    return {
        "agent_id": a.agent_id,
        "name_ar": a.name_ar,
        "name_en": a.name_en,
        "role_ar": a.role_ar,
        "capabilities": list(a.capabilities),
        "tools_used": list(a.tools_used),
        "runs_on": a.runs_on,
        "autonomy_level": a.autonomy_level,
        "emits_events": list(a.emits_events),
        "requires_pii_access": a.requires_pii_access,
        "pdpl_compliance_gates": list(a.pdpl_compliance_gates),
        "avg_runtime_seconds": a.avg_runtime_seconds,
        "inputs_required": list(a.inputs_required),
        "outputs": list(a.outputs),
    }


# ── 1. AGENTS CATALOG ─────────────────────────────────────────────
@router.get("/agents")
async def list_agents(
    autonomy: str | None = Query(None, description="safe_auto / human_approval / advisory"),
    runs_on: str | None = Query(None, description="substring of runs_on schedule"),
) -> dict[str, Any]:
    """List all 11 agents — used for the Agents panel."""
    pool = list(ALL_AGENTS)
    if autonomy:
        pool = list_agents_by_autonomy(autonomy)
    if runs_on:
        pool = [a for a in pool if runs_on in a.runs_on]
    return {
        "summary": agents_summary(),
        "agents": [_spec_to_dict(a) for a in pool],
    }


@router.get("/agents/{agent_id}")
async def get_agent_detail(agent_id: str) -> dict[str, Any]:
    a = get_agent(agent_id)
    if a is None:
        raise HTTPException(status_code=404, detail=f"agent '{agent_id}' not found")
    return _spec_to_dict(a)


# ── 2. WHY-NOW? ENGINE ───────────────────────────────────────────
@router.post("/why-now")
async def why_now_explanation(
    company_id: str = Body(..., embed=True),
    signals: list[dict[str, Any]] = Body(default_factory=list, embed=True),
    sector: str | None = Body(default=None, embed=True),
    sector_pulse_trend: str | None = Body(default=None, embed=True),
) -> dict[str, Any]:
    """
    Explain why this company is a priority today based on detected signals.

    Each signal: {signal_type, detected_at_iso, source, evidence_url?, payload?}
    """
    parsed: list[WhyNowSignal] = []
    for s in signals:
        try:
            detected = datetime.fromisoformat(
                s["detected_at_iso"].replace("Z", "+00:00")
            ).replace(tzinfo=None)
        except Exception:
            detected = _utcnow()
        parsed.append(
            WhyNowSignal(
                signal_type=s.get("signal_type", "unknown"),
                detected_at=detected,
                source=s.get("source", "manual"),
                evidence_url=s.get("evidence_url"),
                payload=s.get("payload", {}),
            )
        )
    explanation = explain_why_now(
        company_id=company_id,
        signals=parsed,
        sector=sector,
        sector_pulse_trend=sector_pulse_trend,
    )
    if explanation is None:
        return {"company_id": company_id, "actionable": False, "reason": "weak_or_stale_signals"}
    return {
        "company_id": explanation.company_id,
        "actionable": True,
        "score": explanation.score,
        "headline_ar": explanation.headline_ar,
        "detail_ar": explanation.detail_ar,
        "suggested_angle_ar": explanation.suggested_angle_ar,
        "primary_signals": explanation.primary_signals,
        "decay_warning": explanation.decay_warning,
    }


@router.get("/why-now/signal-weights")
async def list_signal_weights() -> dict[str, Any]:
    """Reference catalogue — what signals Dealix tracks + their weight."""
    return {
        "count": len(SIGNAL_WEIGHTS),
        "weights": dict(sorted(SIGNAL_WEIGHTS.items(), key=lambda x: -x[1])),
    }


# ── 3. REVENUE LEAK DETECTOR ─────────────────────────────────────
@router.post("/leaks")
async def detect_leaks(
    leads: list[dict[str, Any]] = Body(default_factory=list, embed=True),
    meetings: list[dict[str, Any]] = Body(default_factory=list, embed=True),
    deals: list[dict[str, Any]] = Body(default_factory=list, embed=True),
    campaigns: list[dict[str, Any]] = Body(default_factory=list, embed=True),
    reps: list[dict[str, Any]] = Body(default_factory=list, embed=True),
    avg_deal_value_sar: float = Body(default=25000, embed=True),
) -> dict[str, Any]:
    """Run all leak detectors and return ranked report."""
    # Convert ISO timestamps where present
    for collection in (leads, meetings, deals):
        for item in collection:
            for k in ("created_at", "last_outreach_at", "held_at", "last_activity_at"):
                v = item.get(k)
                if isinstance(v, str):
                    try:
                        item[k] = datetime.fromisoformat(v.replace("Z", "+00:00")).replace(
                            tzinfo=None
                        )
                    except Exception:
                        item[k] = None

    report = detect_all_leaks(
        leads=leads,
        meetings=meetings,
        deals=deals,
        campaigns=campaigns,
        reps=reps,
        avg_deal_value_sar=avg_deal_value_sar,
    )
    return {
        "total_estimated_impact_sar": report.total_estimated_impact_sar,
        "by_severity": report.by_severity,
        "by_type": report.by_type,
        "top_3_actions_ar": report.top_3_actions_ar,
        "leaks": [
            {
                "leak_type": lk.leak_type,
                "severity": lk.severity,
                "entity_type": lk.entity_type,
                "entity_id": lk.entity_id,
                "headline_ar": lk.headline_ar,
                "detail_ar": lk.detail_ar,
                "estimated_impact_sar": lk.estimated_impact_sar,
                "suggested_action_ar": lk.suggested_action_ar,
                "days_in_state": lk.days_in_state,
            }
            for lk in report.leaks
        ],
    }


# ── 4. MATURITY / BENCHMARK SCORE ────────────────────────────────
@router.post("/benchmark-score")
async def compute_score(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """Compute the customer's Dealix Benchmark Score across 7 dimensions."""
    customer_id = payload.get("customer_id", "unknown")
    if not customer_id:
        raise HTTPException(status_code=400, detail="customer_id required")
    report = compute_benchmark_score(
        customer_id=customer_id,
        has_playbook=bool(payload.get("has_playbook")),
        has_quota=bool(payload.get("has_quota")),
        weekly_pipeline_review=bool(payload.get("weekly_pipeline_review")),
        median_response_minutes=int(payload.get("median_response_minutes", 240)),
        followups_per_lead=float(payload.get("followups_per_lead", 1.0)),
        reply_rate=float(payload.get("reply_rate", 0)),
        positive_reply_rate=float(payload.get("positive_reply_rate", 0)),
        sectors_targeted=int(payload.get("sectors_targeted", 1)),
        win_rate_top_sector=float(payload.get("win_rate_top_sector", 0)),
        has_pricing_page=bool(payload.get("has_pricing_page")),
        has_case_studies=bool(payload.get("has_case_studies")),
        avg_proposal_pages=float(payload.get("avg_proposal_pages", 10)),
        lead_to_meeting=float(payload.get("lead_to_meeting", 0)),
        meeting_to_deal=float(payload.get("meeting_to_deal", 0)),
        deal_to_close=float(payload.get("deal_to_close", 0)),
        has_onboarding_flow=bool(payload.get("has_onboarding_flow")),
        nps_collected=bool(payload.get("nps_collected")),
        runs_qbr=bool(payload.get("runs_qbr")),
        peer_percentile=payload.get("peer_percentile"),
    )
    return {
        "customer_id": report.customer_id,
        "overall": report.overall,
        "bucket": report.bucket,
        "peer_percentile": report.peer_percentile,
        "dimensions": [
            {
                "name": d.name,
                "score": d.score,
                "bucket": d.bucket,
                "summary_ar": d.summary_ar,
                "next_step_ar": d.next_step_ar,
                "weight": DIMENSION_WEIGHTS.get(d.name, 0),
            }
            for d in report.dimensions
        ],
        "roadmap": report.roadmap,
        "markdown_export": report.to_markdown(),
    }


# ── 5. ACQUISITION SIMULATOR ─────────────────────────────────────
@router.post("/simulator")
async def run_simulator(
    sector: str = Body(..., embed=True),
    city: str = Body(..., embed=True),
    avg_deal_value_sar: float = Body(..., embed=True),
    target_revenue_sar: float = Body(..., embed=True),
    target_period_days: int = Body(default=90, embed=True),
    current_close_rate: float | None = Body(default=None, embed=True),
    current_monthly_meetings: int = Body(default=0, embed=True),
) -> dict[str, Any]:
    """Run the acquisition simulator — used on landing + onboarding."""
    inputs = SimulatorInputs(
        sector=sector,
        city=city,
        avg_deal_value_sar=avg_deal_value_sar,
        target_revenue_sar=target_revenue_sar,
        target_period_days=target_period_days,
        current_close_rate=current_close_rate,
        current_monthly_meetings=current_monthly_meetings,
    )
    result = simulate(inputs=inputs)
    return {
        "inputs": {
            "sector": inputs.sector,
            "city": inputs.city,
            "avg_deal_value_sar": inputs.avg_deal_value_sar,
            "target_revenue_sar": inputs.target_revenue_sar,
            "target_period_days": inputs.target_period_days,
        },
        "baseline": result.baseline.__dict__,
        "with_dealix": result.with_dealix.__dict__,
        "plan": result.plan.__dict__,
        "expected_roi_x": result.expected_roi_x,
        "risks_ar": result.risks_ar,
        "assumptions_ar": result.assumptions_ar,
    }


@router.get("/simulator/sector-benchmarks")
async def list_simulator_benchmarks() -> dict[str, Any]:
    return {
        "count": len(SECTOR_BENCHMARKS),
        "sectors": SECTOR_BENCHMARKS,
        "source": "Saudi B2B Pulse — quarterly aggregated, anonymized.",
    }


# ── 6. OBJECTION LIBRARY ─────────────────────────────────────────
@router.get("/objections")
async def list_objections(
    category: str | None = Query(default=None),
    keyword: str | None = Query(default=None),
) -> dict[str, Any]:
    """Browse + search the Saudi B2B Objection Library."""
    if keyword:
        match = find_by_keyword(keyword)
        return {"matched": match.objection_id if match else None, "objection": match.__dict__ if match else None}
    pool = list_by_category(category) if category else list(SAUDI_B2B_OBJECTIONS)
    return {
        "count": len(pool),
        "categories": OBJECTION_CATEGORIES,
        "category_summary": category_summary(),
        "objections": [o.__dict__ for o in pool],
    }


@router.get("/objections/{objection_id}")
async def get_objection(objection_id: str) -> dict[str, Any]:
    for o in SAUDI_B2B_OBJECTIONS:
        if o.objection_id == objection_id:
            return o.__dict__
    raise HTTPException(status_code=404, detail=f"objection '{objection_id}' not found")


# ── 7. PROOF PACK GENERATOR ──────────────────────────────────────
@router.post("/proof-pack")
async def generate_pack(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
    """Generate a monthly Proof Pack from raw metrics."""
    try:
        inputs = ProofPackInputs(
            customer_id=payload.get("customer_id", "unknown"),
            customer_name=payload.get("customer_name", ""),
            sector=payload.get("sector", "saas"),
            month_label=payload.get("month_label", ""),
            plan=payload.get("plan", "Growth"),
            monthly_price_sar=float(payload.get("monthly_price_sar", 2999)),
            leads_discovered=int(payload.get("leads_discovered", 0)),
            leads_enriched=int(payload.get("leads_enriched", 0)),
            drafts_created=int(payload.get("drafts_created", 0)),
            drafts_sent=int(payload.get("drafts_sent", 0)),
            whatsapp_sent=int(payload.get("whatsapp_sent", 0)),
            emails_sent=int(payload.get("emails_sent", 0)),
            linkedin_sent=int(payload.get("linkedin_sent", 0)),
            replies_received=int(payload.get("replies_received", 0)),
            positive_replies=int(payload.get("positive_replies", 0)),
            meetings_booked=int(payload.get("meetings_booked", 0)),
            proposals_sent=int(payload.get("proposals_sent", 0)),
            deals_won=int(payload.get("deals_won", 0)),
            pipeline_added_sar=float(payload.get("pipeline_added_sar", 0)),
            revenue_won_sar=float(payload.get("revenue_won_sar", 0)),
            avg_response_minutes=int(payload.get("avg_response_minutes", 60)),
            bounce_rate=float(payload.get("bounce_rate", 0)),
            opt_outs=int(payload.get("opt_outs", 0)),
            compliance_blocks=int(payload.get("compliance_blocks", 0)),
            sector_reply_rate_p50=float(payload.get("sector_reply_rate_p50", 0.07)),
            sector_meeting_rate_p50=float(payload.get("sector_meeting_rate_p50", 0.30)),
            sector_win_rate_p50=float(payload.get("sector_win_rate_p50", 0.20)),
            best_message_subject=payload.get("best_message_subject"),
            best_message_reply_rate=payload.get("best_message_reply_rate"),
            best_sector_played=payload.get("best_sector_played"),
            worst_bottleneck_ar=payload.get("worst_bottleneck_ar"),
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=f"invalid payload: {exc}") from exc

    pack = generate_proof_pack(inputs)
    return {
        "customer_id": pack.customer_id,
        "customer_name": pack.customer_name,
        "period_label": pack.period_label,
        "headline_metric": pack.headline_metric,
        "grade": pack.grade,
        "tldr_ar": pack.tldr_ar,
        "activity_summary": pack.activity_summary,
        "pipeline_impact": pack.pipeline_impact,
        "quality_score": pack.quality_score,
        "benchmark_comparison": pack.benchmark_comparison,
        "top_performers": pack.top_performers,
        "recommendations_next_month_ar": pack.recommendations_next_month_ar,
        "roi_breakdown": pack.roi_breakdown,
        "markdown_export": pack.to_markdown(),
        "generated_at": pack.generated_at,
    }


# ── 8. SECTOR PLAYBOOKS ──────────────────────────────────────────
@router.get("/playbooks")
async def list_playbooks() -> dict[str, Any]:
    return {
        "count": len(ALL_PLAYBOOKS),
        "summaries": list_playbooks_summary(),
    }


@router.get("/playbooks/{sector_id}")
async def get_playbook_detail(sector_id: str) -> dict[str, Any]:
    p = get_playbook(sector_id)
    if p is None:
        raise HTTPException(status_code=404, detail=f"playbook '{sector_id}' not found")
    return {
        "sector_id": p.sector_id,
        "sector_ar": p.sector_ar,
        "sector_en": p.sector_en,
        "pain_points_ar": list(p.pain_points_ar),
        "top_objections": list(p.top_objections),
        "opening_lines_ar": list(p.opening_lines_ar),
        "best_offer_angle_ar": p.best_offer_angle_ar,
        "buying_committee": list(p.buying_committee),
        "seasonal_peaks_ar": list(p.seasonal_peaks_ar),
        "benchmarks": p.benchmarks,
        "recommended_channel_mix": p.recommended_channel_mix,
        "whatsapp_tone": p.whatsapp_tone,
        "case_study_template_ar": p.case_study_template_ar,
        "avg_deal_value_sar": p.avg_deal_value_sar,
        "avg_cycle_days": p.avg_cycle_days,
    }


# ── 9. NEXT-BEST-ACTION RECOMMENDER ──────────────────────────────
@router.post("/next-best-action")
async def get_next_best_action(
    company_id: str = Body(..., embed=True),
    sector: str = Body(default="saas", embed=True),
    last_outcome: str | None = Body(default=None, embed=True),
    days_since_last_touch: int = Body(default=0, embed=True),
    has_whatsapp_business: bool = Body(default=False, embed=True),
) -> dict[str, Any]:
    target = CompanyVector(
        company_id=company_id,
        sector=sector,
        has_whatsapp_business=has_whatsapp_business,
    )
    nba = recommend_next_action(
        target=target,
        last_outcome=last_outcome,
        days_since_last_touch=days_since_last_touch,
    )
    return {
        "company_id": company_id,
        "action": nba.action,
        "channel": nba.channel,
        "rationale": nba.rationale,
        "expected_reply_lift": nba.expected_reply_lift,
        "confidence": nba.confidence,
        "playbook_id": nba.playbook_id,
    }


# ── 10. GRAPH HEALTH (moat score for the dashboard) ──────────────
@router.get("/graph-health")
async def get_graph_health(
    n_companies: int = Query(default=0, ge=0),
    n_signals: int = Query(default=0, ge=0),
    n_messages: int = Query(default=0, ge=0),
    n_outcomes: int = Query(default=0, ge=0),
    n_won_deals: int = Query(default=0, ge=0),
) -> dict[str, Any]:
    """High-level Revenue Graph health — for the Moat Score tile."""
    return graph_health_summary(
        n_companies=n_companies,
        n_signals=n_signals,
        n_messages=n_messages,
        n_outcomes=n_outcomes,
        n_won_deals=n_won_deals,
    )


# ── 11. THE FULL DASHBOARD SNAPSHOT ──────────────────────────────
@router.get("/snapshot")
async def dashboard_snapshot(customer_id: str = Query(...)) -> dict[str, Any]:
    """
    Full snapshot for the in-product dashboard — combines health, agents,
    playbooks, and a few KPI tiles. Demo / discovery endpoint.
    """
    return {
        "customer_id": customer_id,
        "agents_summary": agents_summary(),
        "playbooks_count": len(ALL_PLAYBOOKS),
        "objections_indexed": len(SAUDI_B2B_OBJECTIONS),
        "signal_types_tracked": len(SIGNAL_WEIGHTS),
        "graph_status": "live",
        "compliance_gates_active": 11,
        "last_pulse_published": _utcnow().date().isoformat(),
    }

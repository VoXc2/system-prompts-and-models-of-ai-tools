"""Service Excellence OS router — feature matrix + score + gates + research."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Body

from auto_client_acquisition.service_excellence import (
    build_backlog,
    build_demo_script,
    build_feature_matrix,
    build_landing_page_outline,
    build_monthly_service_review,
    build_onboarding_checklist,
    build_proof_pack_template_excellence,
    build_sales_script,
    build_service_launch_package,
    build_service_research_brief,
    calculate_service_excellence_score,
    calculate_service_roi_estimate,
    classify_features,
    compare_against_categories,
    convert_feedback_to_backlog,
    generate_feature_hypotheses,
    prioritize_backlog_items,
    recommend_missing_features,
    recommend_next_experiments,
    recommend_weekly_improvements,
    required_proof_metrics,
    review_service_before_launch,
    summarize_proof_ar,
)
from auto_client_acquisition.service_tower import ALL_SERVICES

router = APIRouter(prefix="/api/v1/service-excellence", tags=["service-excellence"])


# ── Feature matrix ───────────────────────────────────────────
@router.get("/{service_id}/feature-matrix")
async def feature_matrix(service_id: str) -> dict[str, Any]:
    return build_feature_matrix(service_id)


@router.get("/{service_id}/feature-classification")
async def feature_classification(service_id: str) -> dict[str, Any]:
    return classify_features(service_id)


@router.get("/{service_id}/missing-features")
async def missing_features(service_id: str) -> dict[str, Any]:
    return {"recommendations": recommend_missing_features(service_id)}


# ── Scoring ──────────────────────────────────────────────────
@router.get("/{service_id}/score")
async def score(service_id: str) -> dict[str, Any]:
    return calculate_service_excellence_score(service_id)


# ── Gates / quality review ──────────────────────────────────
@router.get("/{service_id}/quality-review")
async def quality_review(service_id: str) -> dict[str, Any]:
    return review_service_before_launch(service_id)


@router.get("/review/all")
async def review_all() -> dict[str, Any]:
    """Review every catalogued service."""
    out = [review_service_before_launch(s.id) for s in ALL_SERVICES]
    counts: dict[str, int] = {}
    for r in out:
        v = str(r.get("verdict", "?"))
        counts[v] = counts.get(v, 0) + 1
    return {"total": len(out), "by_verdict": counts, "results": out}


# ── Proof metrics ────────────────────────────────────────────
@router.get("/{service_id}/proof-metrics")
async def proof_metrics(service_id: str) -> dict[str, Any]:
    return {
        "service_id": service_id,
        "metrics": required_proof_metrics(service_id),
        "template": build_proof_pack_template_excellence(service_id),
    }


@router.post("/{service_id}/roi-estimate")
async def roi_estimate(
    service_id: str,
    metrics: dict[str, Any] = Body(default_factory=dict),
) -> dict[str, Any]:
    out = calculate_service_roi_estimate(service_id, metrics)
    if "error" not in out:
        out["proof_summary_ar"] = summarize_proof_ar(service_id, metrics)
    return out


# ── Competitor gap ───────────────────────────────────────────
@router.get("/{service_id}/gap-analysis")
async def gap_analysis(service_id: str) -> dict[str, Any]:
    return compare_against_categories(service_id)


# ── Research lab ─────────────────────────────────────────────
@router.get("/{service_id}/research-brief")
async def research_brief(service_id: str) -> dict[str, Any]:
    return build_service_research_brief(service_id)


@router.get("/{service_id}/feature-hypotheses")
async def feature_hypotheses(service_id: str) -> dict[str, Any]:
    return {"hypotheses": generate_feature_hypotheses(service_id)}


@router.get("/{service_id}/experiments")
async def experiments(service_id: str) -> dict[str, Any]:
    return recommend_next_experiments(service_id)


@router.get("/{service_id}/monthly-review")
async def monthly_review(service_id: str) -> dict[str, Any]:
    return build_monthly_service_review(service_id)


# ── Backlog ──────────────────────────────────────────────────
@router.get("/{service_id}/backlog")
async def backlog(service_id: str) -> dict[str, Any]:
    return build_backlog(service_id)


@router.post("/{service_id}/backlog/from-feedback")
async def backlog_from_feedback(
    service_id: str,
    feedback: list[dict[str, Any]] = Body(..., embed=True),
) -> dict[str, Any]:
    return {
        "service_id": service_id,
        "items": convert_feedback_to_backlog(feedback),
    }


@router.post("/{service_id}/backlog/prioritize")
async def backlog_prioritize(
    service_id: str,
    items: list[dict[str, Any]] = Body(..., embed=True),
) -> dict[str, Any]:
    return {"items": prioritize_backlog_items(items)}


@router.get("/{service_id}/weekly-improvements")
async def weekly_improvements(service_id: str) -> dict[str, Any]:
    return recommend_weekly_improvements(service_id)


# ── Launch package ───────────────────────────────────────────
@router.get("/{service_id}/launch-package")
async def launch_package(service_id: str) -> dict[str, Any]:
    return build_service_launch_package(service_id)


@router.get("/{service_id}/landing-outline")
async def landing_outline(service_id: str) -> dict[str, Any]:
    return build_landing_page_outline(service_id)


@router.get("/{service_id}/sales-script")
async def sales_script(service_id: str) -> dict[str, Any]:
    return build_sales_script(service_id)


@router.get("/{service_id}/demo-script")
async def demo_script(service_id: str) -> dict[str, Any]:
    return build_demo_script(service_id)


@router.get("/{service_id}/onboarding-checklist")
async def onboarding_checklist(service_id: str) -> dict[str, Any]:
    return build_onboarding_checklist(service_id)

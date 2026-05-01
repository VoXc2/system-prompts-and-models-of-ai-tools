"""Service Excellence OS API — scoring, matrices, launch packages (deterministic)."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter

from auto_client_acquisition.service_excellence.competitor_gap import compare_against_categories
from auto_client_acquisition.service_excellence.feature_matrix import build_feature_matrix, classify_features
from auto_client_acquisition.service_excellence.launch_package import (
    build_demo_script,
    build_landing_page_outline,
    build_onboarding_checklist,
    build_sales_script,
    build_service_launch_package,
)
from auto_client_acquisition.service_excellence.proof_metrics import (
    build_proof_pack_template,
    required_proof_metrics,
    summarize_proof_ar,
)
from auto_client_acquisition.service_excellence.quality_review import review_all_services, review_service_before_launch
from auto_client_acquisition.service_excellence.research_lab import build_service_research_brief
from auto_client_acquisition.service_excellence.service_improvement_backlog import build_backlog, prioritize_backlog_items
from auto_client_acquisition.service_excellence.service_scoring import calculate_service_excellence_score
from auto_client_acquisition.service_excellence.workflow_builder import (
    build_approval_steps,
    build_day_by_day_execution_plan,
    build_workflow,
    validate_workflow,
)

router = APIRouter(prefix="/api/v1/service-excellence", tags=["service_excellence"])


@router.get("/review/all")
async def review_all() -> dict[str, Any]:
    return review_all_services()


@router.get("/{service_id}/feature-matrix")
async def feature_matrix(service_id: str) -> dict[str, Any]:
    fm = build_feature_matrix(service_id)
    fm["classified"] = classify_features(service_id)
    return fm


@router.get("/{service_id}/score")
async def excellence_score(service_id: str) -> dict[str, Any]:
    return calculate_service_excellence_score(service_id)


@router.get("/{service_id}/workflow")
async def excellence_workflow(service_id: str) -> dict[str, Any]:
    wf = build_workflow(service_id)
    wf["validation"] = validate_workflow(service_id)
    wf["day_plan"] = build_day_by_day_execution_plan(service_id)
    wf["approval"] = build_approval_steps(service_id)
    return wf


@router.get("/{service_id}/proof-metrics")
async def proof_metrics(service_id: str) -> dict[str, Any]:
    return {
        "required": required_proof_metrics(service_id),
        "template": build_proof_pack_template(service_id),
        "summary_example_ar": summarize_proof_ar(service_id, {"pipeline_sar": 15000}),
        "demo": True,
    }


@router.get("/{service_id}/gap-analysis")
async def gap_analysis(service_id: str) -> dict[str, Any]:
    return compare_against_categories(service_id)


@router.get("/{service_id}/launch-package")
async def launch_package(service_id: str) -> dict[str, Any]:
    return {
        "package": build_service_launch_package(service_id),
        "landing": build_landing_page_outline(service_id),
        "sales_script": build_sales_script(service_id),
        "demo_script": build_demo_script(service_id),
        "onboarding": build_onboarding_checklist(service_id),
        "demo": True,
    }


@router.get("/{service_id}/backlog")
async def backlog(service_id: str) -> dict[str, Any]:
    items = build_backlog(service_id)
    return {"service_id": service_id, "items": prioritize_backlog_items(items), "demo": True}


@router.get("/{service_id}/research-brief")
async def research_brief(service_id: str) -> dict[str, Any]:
    return build_service_research_brief(service_id)


@router.get("/{service_id}/review")
async def review_one(service_id: str) -> dict[str, Any]:
    return review_service_before_launch(service_id)

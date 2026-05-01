"""Tests for Service Excellence OS."""

from __future__ import annotations

from auto_client_acquisition.service_excellence.competitor_gap import compare_against_categories
from auto_client_acquisition.service_excellence.feature_matrix import build_feature_matrix, classify_features
from auto_client_acquisition.service_excellence.launch_package import build_sales_script
from auto_client_acquisition.service_excellence.quality_review import review_all_services, review_service_before_launch
from auto_client_acquisition.service_excellence.service_scoring import calculate_service_excellence_score
from auto_client_acquisition.service_excellence.workflow_builder import validate_workflow


def test_feature_matrix_has_must_have() -> None:
    fm = build_feature_matrix("list_intelligence")
    buckets = classify_features("list_intelligence")
    assert len(buckets.get("must_have") or []) >= 1
    assert len(fm.get("features") or []) >= 4


def test_excellence_score_returns_status() -> None:
    sc = calculate_service_excellence_score("first_10_opportunities")
    assert "total_score" in sc
    assert sc["status"] in ("launch_ready", "beta_only", "needs_work")


def test_workflow_has_approval_gate() -> None:
    v = validate_workflow("growth_os")
    assert v.get("has_approval_step") is True


def test_review_all_counts_services() -> None:
    r = review_all_services()
    assert r.get("count", 0) >= 10
    assert r.get("ok_count", 0) >= 1


def test_single_review_ok_for_known_service() -> None:
    r = review_service_before_launch("list_intelligence")
    assert r.get("ok") is True


def test_gap_analysis_do_not_copy() -> None:
    g = compare_against_categories("growth_os")
    assert "do_not_copy" in g
    assert "scraping" in " ".join(g["do_not_copy"]).lower() or "linkedin" in str(g).lower()


def test_launch_sales_script_non_empty() -> None:
    s = build_sales_script("partner_sprint")
    assert len(s.get("script_ar") or "") > 20

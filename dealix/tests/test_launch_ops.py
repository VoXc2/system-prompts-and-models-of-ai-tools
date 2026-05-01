"""Tests for launch_ops and related go/no-go."""

from __future__ import annotations

from auto_client_acquisition.launch_ops.demo_flow import build_demo_script
from auto_client_acquisition.launch_ops.go_no_go import evaluate_go_no_go
from auto_client_acquisition.launch_ops.launch_scorecard import build_launch_scorecard
from auto_client_acquisition.launch_ops.outreach_messages import build_first_twenty_outreach
from auto_client_acquisition.launch_ops.private_beta import build_private_beta_offer


def test_private_beta_offer_exists():
    o = build_private_beta_offer()
    assert o.get("title_ar")
    assert o.get("live_send_default") is False
    assert "included_ar" in o


def test_demo_script_twelve_minutes():
    d = build_demo_script()
    assert d["duration_minutes"] == 12
    assert len(d["sections"]) >= 4


def test_first_twenty_outreach():
    m = build_first_twenty_outreach()
    assert m["count"] == 20
    assert len(m["messages"]) >= 4


def test_go_no_go_blocks_when_critical_fails():
    g = evaluate_go_no_go({"tests_pass": False})
    assert g["go"] is False
    assert "tests_pass" in g["blockers"]


def test_go_no_go_passes_when_critical_ok():
    g = evaluate_go_no_go({"staging_health_ok": False})
    assert g["go"] is True
    assert g["warnings_ar"]


def test_scorecard_readiness():
    s = build_launch_scorecard()
    assert 0 <= s["readiness_score"] <= 100
    assert s["status"] in ("ready", "needs_work")
    assert "go_no_go" in s


def test_launch_routes_registered():
    from api.main import create_app

    app = create_app()
    paths = app.openapi().get("paths") or {}
    assert "/api/v1/launch/private-beta/offer" in paths
    assert "/api/v1/launch/go-no-go" in paths


def test_service_tower_static_routes():
    from api.main import create_app

    app = create_app()
    paths = app.openapi().get("paths") or {}
    assert "/api/v1/services/verticals" in paths
    assert "/api/v1/services/upgrade-paths" in paths
    assert "/api/v1/services/contracts/templates" in paths

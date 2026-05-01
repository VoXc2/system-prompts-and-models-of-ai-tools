"""Stack tests: security curator, growth curator, operators, tool gateway extensions."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from api.main import create_app
from auto_client_acquisition.connectors.connector_catalog import build_connector_catalog
from auto_client_acquisition.growth_curator.message_curator import grade_message
from auto_client_acquisition.model_router.task_router import route_task
from auto_client_acquisition.platform_services import execute_tool
from auto_client_acquisition.security_curator.patch_firewall import inspect_diff
from auto_client_acquisition.security_curator.secret_redactor import redact_secrets, scan_payload
from auto_client_acquisition.security_curator.trace_redactor import redact_trace_payload


def test_redact_github_token() -> None:
    raw = "token ghp_abcdefghijklmnopqrstuvwxyz1234567890abcd"
    out = redact_secrets(raw)
    assert "ghp_<REDACTED>" in out or "<REDACTED>" in out


def test_patch_firewall_blocks_env() -> None:
    diff = "+.env\n+OPENAI_API_KEY=sk-xxxxx\n"
    r = inspect_diff(diff)
    assert r["allowed"] is False


def test_scan_payload_detects_token() -> None:
    findings = scan_payload({"x": "ghp_abcdefghijklmnopqrst"})
    assert "possible_github_token" in findings


def test_tool_gateway_gmail_send_blocked() -> None:
    r = execute_tool("gmail_send", {})
    assert r["status"] == "blocked"


def test_tool_gateway_calendar_insert_requires_approval() -> None:
    r = execute_tool("calendar_insert", {})
    assert r["status"] == "approval_required"


def test_connector_catalog_has_twelve_plus() -> None:
    c = build_connector_catalog()
    assert c["count"] >= 12


def test_model_router_compliance_guardrail() -> None:
    r = route_task("compliance_guardrail")
    assert r["ok"] is True
    assert r["needs_guardrail"] is False


def test_grade_message_detects_guarantee() -> None:
    g = grade_message("نضمن لك 100% نتائج خلال أسبوع")
    assert g["score"] < 70


@pytest.fixture()
def client() -> TestClient:
    return TestClient(create_app())


def test_growth_operator_missions_and_proof(client: TestClient) -> None:
    m = client.get("/api/v1/growth-operator/missions")
    assert m.status_code == 200
    assert "missions" in m.json()
    p = client.get("/api/v1/growth-operator/proof-pack/demo")
    assert p.status_code == 200


def test_security_curator_redact_route(client: TestClient) -> None:
    tok = "ghp_" + "a" * 36
    r = client.post("/api/v1/security-curator/redact", json={"text": tok})
    assert r.status_code == 200
    body = r.json()
    assert "<REDACTED>" in body.get("redacted", "") or "ghp_<REDACTED>" in body.get("redacted", "")


def test_platform_events_ingest(client: TestClient) -> None:
    r = client.post(
        "/api/v1/platform/events/ingest",
        json={
            "event_type": "lead_received",
            "source": "trusted_simulation",
            "channel_id": "website_form",
            "lead_name": "x",
        },
    )
    assert r.status_code == 200
    assert r.json().get("ok") is True


def test_trace_redactor_nested() -> None:
    out = redact_trace_payload({"nested": {"token": "ghp_" + "b" * 36}})
    assert "nested" in out


def test_security_trace_sanitize_route(client: TestClient) -> None:
    r = client.post(
        "/api/v1/security-curator/trace/sanitize",
        json={"payload": {"x": "ghp_" + "c" * 36}},
    )
    assert r.status_code == 200
    assert "sanitized" in r.json()


def test_growth_curator_skills_and_missions_demo(client: TestClient) -> None:
    s = client.get("/api/v1/growth-curator/skills/demo")
    assert s.status_code == 200
    assert s.json().get("skills")
    m = client.get("/api/v1/growth-curator/missions/curate/demo")
    assert m.status_code == 200

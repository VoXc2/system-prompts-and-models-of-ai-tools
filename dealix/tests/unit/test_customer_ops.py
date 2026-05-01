"""Unit tests for Customer Ops."""

from __future__ import annotations

import pytest

from auto_client_acquisition.customer_ops import (
    SUPPORT_PRIORITIES,
    SUPPORTED_CONNECTORS,
    build_at_risk_alert,
    build_connector_setup_summary,
    build_customer_success_plan,
    build_first_response_template,
    build_incident_response_plan,
    build_onboarding_checklist,
    build_sla_health_report,
    build_weekly_check_in,
    classify_sla_breach,
    classify_ticket_priority,
    record_sla_event,
    route_ticket,
    triage_incident,
    update_connector_status,
    update_onboarding_step,
)


# ── Onboarding ───────────────────────────────────────────────
def test_onboarding_checklist_has_8_steps():
    out = build_onboarding_checklist(customer_id="c1")
    assert out["total_steps"] == 8
    assert out["current_step_id"] == "select_goal"


def test_update_onboarding_step_completes():
    cl = build_onboarding_checklist(customer_id="c1")
    cl = update_onboarding_step(cl, step_id="select_goal", completed=True)
    assert cl["progress_pct"] == 12.5
    assert cl["current_step_id"] == "select_bundle"


def test_update_onboarding_step_unknown():
    cl = build_onboarding_checklist(customer_id="c1")
    cl = update_onboarding_step(cl, step_id="bogus_step")
    assert "error" in cl


def test_complete_all_onboarding_steps():
    cl = build_onboarding_checklist(customer_id="c1")
    for s in list(cl["steps"]):
        cl = update_onboarding_step(cl, step_id=s["id"], completed=True)
    assert cl["progress_pct"] == 100.0
    assert cl["current_step_id"] == "done"


# ── Connectors ───────────────────────────────────────────────
def test_supported_connectors_includes_critical():
    keys = {c["key"] for c in SUPPORTED_CONNECTORS}
    for required in ("gmail", "google_calendar", "moyasar", "whatsapp_cloud",
                     "google_sheets", "website_forms", "linkedin_lead_forms"):
        assert required in keys


def test_connector_summary_with_blocking_missing():
    out = build_connector_setup_summary(
        customer_id="c1",
        statuses={"gmail": {"state": "connected_draft_only"}},
    )
    assert "whatsapp_cloud" in out["blocking_missing"]
    assert out["ready_for_first_service"] is False


def test_connector_summary_ready():
    out = build_connector_setup_summary(
        customer_id="c1",
        statuses={
            "gmail": {"state": "connected_draft_only"},
            "whatsapp_cloud": {"state": "connected_draft_only"},
        },
    )
    assert out["ready_for_first_service"] is True


def test_update_connector_status_validates():
    statuses: dict = {}
    with pytest.raises(ValueError):
        update_connector_status(statuses, connector_key="gmail",
                                state="totally_invalid")


def test_update_connector_status_writes():
    statuses: dict = {}
    update_connector_status(statuses, connector_key="gmail",
                            state="connected_draft_only")
    assert statuses["gmail"]["state"] == "connected_draft_only"


# ── Support routing ──────────────────────────────────────────
def test_classify_p0_for_security_keywords():
    out = classify_ticket_priority("اكتشفت تسريب في trace logs")
    assert out["priority"] == "P0"


def test_classify_p0_for_unauthorized_send():
    out = classify_ticket_priority("Dealix أرسل رسالة بدون موافقتي")
    assert out["priority"] == "P0"


def test_classify_p1_for_service_down():
    out = classify_ticket_priority("Pilot stopped working today")
    assert out["priority"] == "P1"


def test_classify_p2_for_connector_issue():
    out = classify_ticket_priority("My Gmail connector won't authenticate")
    assert out["priority"] == "P2"


def test_classify_p3_default():
    out = classify_ticket_priority("سؤال بسيط عن الأسعار")
    assert out["priority"] == "P3"


def test_classify_empty_returns_p3():
    out = classify_ticket_priority("")
    assert out["priority"] == "P3"


def test_route_ticket_includes_sla():
    out = route_ticket(text="تسريب أمان", customer_id="c1")
    assert out["priority"] == "P0"
    assert out["sla"]["first_response_minutes"] == 30
    assert out["live_send_allowed"] is False


def test_first_response_p0_arabic():
    out = build_first_response_template("P0")
    assert "30 دقيقة" in out["body_ar"]
    assert out["live_send_allowed"] is False


def test_support_priorities_count():
    assert len(SUPPORT_PRIORITIES) == 4


# ── SLA ──────────────────────────────────────────────────────
def test_sla_event_validates():
    with pytest.raises(ValueError):
        record_sla_event(ticket_id="t1", priority="P0", event="bogus")


def test_sla_event_appends_to_log():
    log: list = []
    record_sla_event(ticket_id="t1", priority="P0", event="opened", log=log)
    assert len(log) == 1


def test_classify_breach_within_target():
    out = classify_sla_breach(
        priority="P0", minutes_to_first_response=20, hours_to_resolve=3,
    )
    assert out["breached"] is False


def test_classify_breach_exceeded():
    out = classify_sla_breach(
        priority="P0", minutes_to_first_response=120, hours_to_resolve=10,
    )
    assert out["breached"] is True
    assert len(out["breaches"]) == 2


def test_sla_health_report_aggregates():
    out = build_sla_health_report(tickets=[
        {"priority": "P0", "first_response_min": 12, "resolution_hours": 2},
        {"priority": "P1", "first_response_min": 90, "resolution_hours": 18},
        {"priority": "P3", "first_response_min": 1500, "resolution_hours": 200},
    ])
    assert out["total_tickets"] == 3
    assert out["total_breached"] == 1  # only P3 breached


def test_sla_health_verdict_critical():
    out = build_sla_health_report(tickets=[
        {"priority": "P0", "first_response_min": 60, "resolution_hours": 10},
        {"priority": "P0", "first_response_min": 120, "resolution_hours": 20},
        {"priority": "P0", "first_response_min": 180, "resolution_hours": 30},
        {"priority": "P0", "first_response_min": 240, "resolution_hours": 40},
    ])
    assert out["verdict"] == "critical"


# ── Incidents ───────────────────────────────────────────────
def test_triage_data_leak_is_sev1():
    out = triage_incident(
        title="Possible data exposure",
        has_data_leak=True,
    )
    assert out["severity"] == "SEV1"


def test_triage_unauthorized_send_is_sev1():
    out = triage_incident(
        title="Unauthorized message",
        has_unauthorized_send=True,
    )
    assert out["severity"] == "SEV1"


def test_triage_many_customers_is_sev2():
    out = triage_incident(
        title="Service outage",
        affected_customers=10,
    )
    assert out["severity"] == "SEV2"


def test_triage_single_customer_is_sev3():
    out = triage_incident(title="Customer X has issue", affected_customers=1)
    assert out["severity"] == "SEV3"


def test_incident_response_plan_sev1_includes_pdpl():
    out = build_incident_response_plan(severity="SEV1")
    text = " ".join(out["plan_ar"])
    assert "PDPL" in text


# ── Customer Success ────────────────────────────────────────
def test_weekly_check_in_arabic():
    out = build_weekly_check_in(
        customer_id="c1", company_name="Acme",
        metrics={"drafts_approved": 5, "replies": 2,
                 "meetings": 1, "risks_blocked": 3, "pipeline_sar": 18000},
    )
    assert out["type"] == "weekly_check_in"
    assert any("Pipeline" in tp for tp in out["talking_points_ar"])


def test_at_risk_alert_high_severity():
    out = build_at_risk_alert(
        customer_id="c1", days_inactive=20,
        drafts_pending=15, last_proof_pack_days_ago=21,
    )
    assert out["severity"] == "high"
    assert out["risk_score"] >= 60


def test_at_risk_alert_low_severity():
    out = build_at_risk_alert(
        customer_id="c1", days_inactive=2,
        drafts_pending=1, last_proof_pack_days_ago=3,
    )
    assert out["severity"] == "low"


def test_customer_success_plan_for_growth_starter():
    out = build_customer_success_plan(
        customer_id="c1", bundle_id="growth_starter",
    )
    assert any("Day 1" in line for line in out["cadence_ar"])


def test_customer_success_plan_for_executive():
    out = build_customer_success_plan(
        customer_id="c1", bundle_id="executive_growth_os",
    )
    assert any("Founder Shadow Board" in line for line in out["cadence_ar"])

"""Unit tests for the Autonomous Service Operator."""

from __future__ import annotations

import pytest

from auto_client_acquisition.autonomous_service_operator import (
    OperatorMemory,
    SUPPORTED_INTENTS,
    add_agency_client,
    build_agency_dashboard,
    build_approval_card,
    build_ceo_command_center,
    build_client_dashboard,
    build_co_branded_proof_pack,
    build_executive_daily_brief,
    build_intake_questions_for_intent,
    build_new_session,
    build_revenue_risks_summary,
    build_service_pipeline,
    build_session_context,
    build_upsell_card,
    classify_intent,
    dispatch_proof_pack,
    handle_message,
    intent_to_service,
    list_agency_revenue_share,
    list_bundles,
    plan_tool_action,
    process_approval_decision,
    recommend_bundle,
    recommend_upsell_after_service,
    render_approval_card_for_whatsapp,
    render_card_for_whatsapp,
    render_daily_brief_for_whatsapp,
    transition_session,
    validate_intake_completeness,
)


# ── Intent classification ────────────────────────────────────
def test_intent_want_more_customers():
    out = classify_intent("أبغى عملاء أكثر لشركتي")
    assert out["intent"] == "want_more_customers"


def test_intent_has_contact_list():
    out = classify_intent("عندي قائمة أرقام كبيرة")
    assert out["intent"] == "has_contact_list"


def test_intent_partnerships():
    out = classify_intent("أبغى شراكات مع وكالات")
    assert out["intent"] == "want_partnerships"


def test_intent_whatsapp_setup():
    out = classify_intent("نستخدم واتساب بدون opt-in")
    assert out["intent"] == "want_whatsapp_setup"


def test_intent_pricing():
    out = classify_intent("بكم السعر؟")
    assert out["intent"] == "ask_pricing"


def test_intent_approve():
    out = classify_intent("اعتمد")
    assert out["intent"] == "approve_action"


def test_intent_unknown_falls_back_to_services():
    out = classify_intent("xyz random text")
    assert out["intent"] == "ask_services"


def test_intent_to_service_mapping():
    assert intent_to_service("want_more_customers") == "first_10_opportunities_sprint"
    assert intent_to_service("has_contact_list") == "list_intelligence"
    assert intent_to_service("want_partnerships") == "partner_sprint"


def test_supported_intents_count():
    assert len(SUPPORTED_INTENTS) == 16


# ── Conversation router ──────────────────────────────────────
def test_handle_message_recommends_first_10_for_want_more_customers():
    out = handle_message("أبغى عملاء أكثر")
    assert out["service_id"] == "first_10_opportunities_sprint"
    assert out["live_send_allowed"] is False


def test_handle_message_uses_agency_bundle_for_agency():
    out = handle_message("أبغى شراكات", is_agency=True)
    assert out["bundle_recommendation"]["recommended_bundle_id"] == "partnership_growth"


def test_handle_message_uses_data_to_revenue_when_list_provided():
    out = handle_message("أبغى أستخدم قائمتي", has_contact_list=True)
    assert out["bundle_recommendation"]["recommended_bundle_id"] == "data_to_revenue"


def test_handle_message_approval_processes_decision():
    out = handle_message("اعتمد")
    assert "decision_processed" in out
    assert out["decision_processed"]["state"] == "approved"


# ── Sessions ────────────────────────────────────────────────
def test_new_session_has_uuid():
    s = build_new_session(customer_id="cust_1")
    assert s.session_id
    assert s.state == "new"
    assert s.customer_id == "cust_1"


def test_session_transition_audit_trail():
    s = build_new_session()
    transition_session(s, new_state="intent_classified", note="initial")
    assert s.state == "intent_classified"
    assert len(s.history) == 1
    assert s.history[0]["from"] == "new"


def test_session_transition_unknown_raises():
    s = build_new_session()
    with pytest.raises(ValueError):
        transition_session(s, new_state="bogus_state")


def test_operator_memory_stores_session():
    mem = OperatorMemory()
    s = build_new_session(customer_id="cust_1")
    mem.upsert_session(s)
    assert mem.get_session(s.session_id) is s
    ctx = build_session_context(memory=mem, session_id=s.session_id)
    assert ctx["session"]["session_id"] == s.session_id


# ── Intake ──────────────────────────────────────────────────
def test_intake_questions_for_known_intent():
    out = build_intake_questions_for_intent("want_more_customers")
    assert len(out["questions"]) >= 4


def test_intake_questions_unknown_intent_falls_back():
    out = build_intake_questions_for_intent("totally_unknown_intent")
    assert out["questions"]


def test_intake_validation_detects_missing():
    out = validate_intake_completeness(
        "want_more_customers",
        {"sector": "training"},  # only one field
    )
    assert out["complete"] is False
    assert "company_name" in out["missing_fields"]


def test_intake_validation_complete():
    out = validate_intake_completeness(
        "want_more_customers",
        {"company_name": "X", "sector": "training", "city": "Riyadh",
         "offer": "Pilot 7 أيام", "ideal_customer": "B2B"},
    )
    assert out["complete"] is True


# ── Approval manager ────────────────────────────────────────
def test_approval_card_has_three_buttons():
    card = build_approval_card(
        action_type="send_email", title_ar="إرسال إيميل",
        summary_ar="إيميل لـ Acme",
    )
    assert len(card["buttons_ar"]) <= 3
    assert card["live_send_allowed"] is False


def test_approval_decision_approve():
    card = build_approval_card(action_type="x", title_ar="x", summary_ar="x")
    out = process_approval_decision(card, decision="approve")
    assert out["state"] == "approved"
    assert out["next_action"] == "execute_with_audit"


def test_approval_decision_arabic_skip():
    card = build_approval_card(action_type="x", title_ar="x", summary_ar="x")
    out = process_approval_decision(card, decision="تخطي")
    assert out["state"] == "rejected"


def test_approval_decision_unknown_returns_error():
    card = build_approval_card(action_type="x", title_ar="x", summary_ar="x")
    out = process_approval_decision(card, decision="bogus")
    assert "error" in out


# ── Service pipeline ────────────────────────────────────────
def test_service_pipeline_starts_at_intake():
    p = build_service_pipeline("first_10_opportunities_sprint")
    assert p["current_step"] == "intake"
    assert any(s["step_id"] == "approval" for s in p["steps"])


# ── Tool action planner ─────────────────────────────────────
def test_plan_blocks_linkedin_scrape():
    out = plan_tool_action(tool="linkedin.scrape_profile")
    assert out["verdict"] == "blocked"


def test_plan_blocks_linkedin_auto_dm():
    out = plan_tool_action(tool="linkedin.auto_dm")
    assert out["verdict"] == "blocked"


def test_plan_high_risk_requires_approval():
    out = plan_tool_action(tool="whatsapp.send_message")
    assert out["verdict"] == "approval_required"
    assert out["live_send_allowed"] is False


def test_plan_draft_safe_returns_draft_only():
    out = plan_tool_action(tool="gmail.create_draft")
    assert out["verdict"] == "draft_only"


def test_plan_unknown_defaults_to_approval_required():
    out = plan_tool_action(tool="bogus.tool")
    assert out["verdict"] == "approval_required"


# ── Bundles ─────────────────────────────────────────────────
def test_list_bundles_returns_six():
    out = list_bundles()
    assert out["total"] == 6


def test_recommend_bundle_for_agency():
    out = recommend_bundle(is_agency=True)
    assert out["recommended_bundle_id"] == "partnership_growth"


def test_recommend_bundle_for_local_business():
    out = recommend_bundle(is_local_business=True)
    assert out["recommended_bundle_id"] == "local_growth_os"


def test_recommend_bundle_with_list():
    out = recommend_bundle(has_contact_list=True)
    assert out["recommended_bundle_id"] == "data_to_revenue"


def test_recommend_bundle_default():
    out = recommend_bundle(budget_sar=500)
    assert out["recommended_bundle_id"] == "growth_starter"


# ── Modes ───────────────────────────────────────────────────
def test_ceo_command_center_arabic():
    out = build_ceo_command_center(company_name="Acme")
    assert out["mode"] == "ceo"
    assert any("؀" <= ch <= "ۿ" for ch in out["daily_brief"]["title_ar"])


def test_executive_daily_brief_three_decisions():
    out = build_executive_daily_brief(company_name="Acme")
    assert len(out["priority_decisions_ar"]) == 3
    assert len(out["buttons_ar"]) <= 3


def test_revenue_risks_summary_three_risks():
    out = build_revenue_risks_summary()
    assert len(out["risks"]) == 3


def test_client_dashboard_has_panels():
    out = build_client_dashboard(customer_id="c1", company_name="Acme")
    assert out["mode"] == "client"
    assert len(out["today_panels_ar"]) >= 3


def test_agency_dashboard_aggregates():
    clients = [
        {"client_company_name": "A", "monthly_subscription_sar": 2999,
         "revenue_share_pct": 20, "status": "active"},
        {"client_company_name": "B", "monthly_subscription_sar": 1500,
         "revenue_share_pct": 25, "status": "onboarding"},
    ]
    out = build_agency_dashboard(agency_id="ag1", clients=clients)
    assert out["metrics"]["total_clients"] == 2
    assert out["metrics"]["monthly_revenue_sar"] == 4499.0


def test_agency_revenue_share_calculation():
    clients = [
        {"client_company_name": "A", "monthly_subscription_sar": 2999,
         "revenue_share_pct": 20},
    ]
    out = list_agency_revenue_share(clients=clients)
    assert out["total_share_sar"] == 599.8


def test_agency_add_client_appends():
    clients: list = []
    add_agency_client(
        agency_id="ag1", client_company_name="Acme",
        monthly_subscription_sar=2999, revenue_share_pct=20,
        clients=clients,
    )
    assert len(clients) == 1


def test_co_branded_proof_pack_includes_both_names():
    out = build_co_branded_proof_pack(
        agency_name="Vortex", client_company_name="Acme",
    )
    assert out["co_branded"] is True
    assert out["agency_name"] == "Vortex"


# ── WhatsApp renderer ────────────────────────────────────────
def test_render_card_for_whatsapp_no_live_send():
    card = build_approval_card(
        action_type="x", title_ar="فرصة", summary_ar="ملخص",
    )
    out = render_card_for_whatsapp(card)
    assert out["live_send_allowed"] is False
    assert any("؀" <= ch <= "ۿ" for ch in out["body_ar"])


def test_render_approval_card_has_3_buttons():
    card = build_approval_card(
        action_type="x", title_ar="فرصة", summary_ar="ملخص",
    )
    out = render_approval_card_for_whatsapp(card)
    assert len(out["buttons_ar"]) == 3


def test_render_daily_brief_arabic():
    brief = build_executive_daily_brief(company_name="Acme")
    out = render_daily_brief_for_whatsapp(brief)
    assert "صباح" in out["body_ar"]
    assert out["live_send_allowed"] is False


# ── Proof + Upsell ──────────────────────────────────────────
def test_proof_pack_dispatch_returns_draft():
    out = dispatch_proof_pack(
        service_id="first_10_opportunities_sprint",
        customer_id="c1",
    )
    assert out["status"] == "draft"
    assert out["live_send_allowed"] is False


def test_upsell_recommends_growth_os_after_first_10():
    out = recommend_upsell_after_service(
        completed_service_id="first_10_opportunities_sprint",
        pilot_metrics={"pipeline_sar": 30000, "meetings": 3, "csat": 9},
    )
    assert out["recommended_next_service_id"] == "growth_os_monthly"
    assert out["verdict"] == "upsell_now"


def test_upsell_iterate_for_weak_outcome():
    out = recommend_upsell_after_service(
        completed_service_id="first_10_opportunities_sprint",
        pilot_metrics={"pipeline_sar": 1000, "meetings": 0, "csat": 5},
    )
    assert out["verdict"] == "iterate_first"


def test_upsell_card_has_three_buttons():
    out = build_upsell_card(
        completed_service_id="first_10_opportunities_sprint",
    )
    assert len(out["buttons_ar"]) == 3
    assert out["live_send_allowed"] is False

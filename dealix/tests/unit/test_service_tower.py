"""Unit tests for Service Tower."""

from __future__ import annotations

from auto_client_acquisition.service_tower import (
    ALL_SERVICES,
    build_ceo_daily_service_brief,
    build_client_report_outline,
    build_deliverables,
    build_intake_questions,
    build_internal_operator_checklist,
    build_proof_pack_template,
    build_risk_alert_card,
    build_service_approval_card,
    build_service_scorecard,
    build_service_workflow,
    build_upsell_message_ar,
    calculate_monthly_offer,
    calculate_setup_fee,
    catalog_summary,
    get_service,
    list_all_services,
    map_service_to_growth_mission,
    map_service_to_subscription,
    quote_service,
    recommend_next_step,
    recommend_plan_after_service,
    recommend_service,
    recommend_upgrade,
    summarize_recommendation_ar,
    summarize_scorecard_ar,
    validate_service_inputs,
)


# ── Catalog ──────────────────────────────────────────────────
def test_catalog_has_at_least_12_services():
    out = list_all_services()
    assert out["total"] >= 12


def test_catalog_includes_critical_services():
    ids = {s.id for s in ALL_SERVICES}
    for required in (
        "free_growth_diagnostic", "list_intelligence",
        "first_10_opportunities_sprint", "self_growth_operator",
        "growth_os_monthly", "email_revenue_rescue",
        "meeting_booking_sprint", "partner_sprint",
        "agency_partner_program", "whatsapp_compliance_setup",
        "linkedin_lead_gen_setup", "executive_growth_brief",
    ):
        assert required in ids


def test_every_service_has_pricing():
    for s in ALL_SERVICES:
        assert s.pricing_min_sar >= 0
        assert s.pricing_max_sar >= s.pricing_min_sar


def test_every_service_has_proof_metrics():
    for s in ALL_SERVICES:
        assert s.proof_metrics, f"{s.id} missing proof_metrics"


def test_every_service_has_deliverables():
    for s in ALL_SERVICES:
        assert s.deliverables_ar, f"{s.id} missing deliverables"


def test_every_service_has_approval_policy():
    for s in ALL_SERVICES:
        assert s.approval_policy


def test_summary_aggregates_pricing_models():
    s = catalog_summary()
    assert s["total"] == len(ALL_SERVICES)
    assert "by_pricing_model" in s
    assert "free_growth_diagnostic" in s["free_offers"]


# ── Wizard ───────────────────────────────────────────────────
def test_wizard_recommends_partner_sprint_for_agency():
    out = recommend_service(company_type="agency", goal="expand_partners")
    assert out["recommended_service_id"] in ("partner_sprint",
                                             "agency_partner_program")


def test_wizard_recommends_list_intelligence_when_has_list():
    out = recommend_service(company_type="b2b", has_contact_list=True)
    assert out["recommended_service_id"] == "list_intelligence"


def test_wizard_recommends_growth_os_for_monthly_budget():
    out = recommend_service(company_type="b2b saas", budget_sar=3500)
    assert out["recommended_service_id"] == "growth_os_monthly"


def test_wizard_default_falls_back_to_kill_feature():
    out = recommend_service(company_type="random", budget_sar=500)
    assert out["recommended_service_id"] == "first_10_opportunities_sprint"


def test_intake_questions_for_known_service():
    out = build_intake_questions("first_10_opportunities_sprint")
    assert len(out["questions"]) >= 5


def test_intake_questions_unknown_service():
    out = build_intake_questions("totally_made_up")
    assert "error" in out


def test_validate_service_inputs_missing_field():
    out = validate_service_inputs("list_intelligence", {"sector": "training"})
    assert out["valid"] is False


def test_summarize_recommendation_arabic():
    out = recommend_service(company_type="b2b saas", budget_sar=3500)
    summary = summarize_recommendation_ar(out)
    assert any("؀" <= ch <= "ۿ" for ch in summary)


# ── Mission templates ────────────────────────────────────────
def test_workflow_includes_approval():
    w = build_service_workflow("first_10_opportunities_sprint")
    step_ids = [s["step_id"] for s in w["workflow_steps"]]
    assert "approval" in step_ids


def test_workflow_links_to_growth_mission():
    w = build_service_workflow("first_10_opportunities_sprint")
    assert w["linked_growth_mission"] == "first_10_opportunities"


def test_map_service_to_subscription():
    sub = map_service_to_subscription("free_growth_diagnostic")
    assert sub  # always returns something


# ── Pricing engine ───────────────────────────────────────────
def test_quote_free_service_returns_zero():
    q = quote_service("free_growth_diagnostic")
    assert q.get("is_free") is True
    assert q["estimated_min_sar"] == 0


def test_quote_paid_service_scales_with_size():
    q_small = quote_service("first_10_opportunities_sprint", company_size="small")
    q_large = quote_service("first_10_opportunities_sprint", company_size="large")
    assert q_large["estimated_max_sar"] > q_small["estimated_max_sar"]


def test_quote_unknown_service_errors():
    q = quote_service("bogus_service")
    assert "error" in q


def test_setup_fee_only_for_monthly():
    fee_monthly = calculate_setup_fee("growth_os_monthly")
    fee_sprint = calculate_setup_fee("first_10_opportunities_sprint")
    assert fee_monthly["setup_fee_sar"] > 0
    assert fee_sprint["setup_fee_sar"] == 0


def test_monthly_offer_only_for_monthly_services():
    out_m = calculate_monthly_offer("growth_os_monthly")
    out_s = calculate_monthly_offer("first_10_opportunities_sprint")
    assert out_m["is_monthly"] is True
    assert out_s["is_monthly"] is False


# ── Deliverables ─────────────────────────────────────────────
def test_deliverables_returns_arabic_list():
    out = build_deliverables("first_10_opportunities_sprint")
    assert out["deliverables_ar"]


def test_proof_pack_template_lists_metrics():
    out = build_proof_pack_template("first_10_opportunities_sprint")
    assert out["metrics_to_track"]


def test_client_report_outline_includes_executive_summary():
    out = build_client_report_outline("growth_os_monthly")
    assert "ملخص تنفيذي (10 أسطر)" in out["sections_ar"]


def test_operator_checklist_blocks_live_actions():
    out = build_internal_operator_checklist("growth_os_monthly")
    assert any("live" in s.lower() for s in out["do_not_do_ar"])


# ── Scorecard ────────────────────────────────────────────────
def test_scorecard_strong_outcome():
    out = build_service_scorecard("first_10_opportunities_sprint", {
        "drafts_approved": 5, "positive_replies": 3,
        "meetings": 2, "pipeline_sar": 25000,
        "risks_blocked": 4, "customer_satisfaction": 9,
    })
    assert out["score"] >= 50


def test_scorecard_summarize_arabic():
    out = build_service_scorecard("first_10_opportunities_sprint",
                                   {"meetings": 3, "pipeline_sar": 30000})
    summary = summarize_scorecard_ar(out)
    assert any("؀" <= ch <= "ۿ" for ch in summary)


# ── CEO control ──────────────────────────────────────────────
def test_ceo_daily_brief_buttons_capped_at_three():
    out = build_ceo_daily_service_brief()
    assert len(out["buttons_ar"]) <= 3


def test_approval_card_blocks_live_send():
    out = build_service_approval_card("first_10_opportunities_sprint",
                                       "send_email")
    assert out["live_send_allowed"] is False
    assert len(out["buttons_ar"]) <= 3


def test_risk_alert_card_marks_high_risk():
    out = build_risk_alert_card()
    assert out["risk_level"] == "high"


# ── Upgrade paths ────────────────────────────────────────────
def test_upgrade_recommends_next_service():
    out = recommend_upgrade("first_10_opportunities_sprint")
    assert out["recommended_service_id"] in ("growth_os_monthly",
                                             "self_growth_operator")


def test_upsell_message_arabic():
    msg = build_upsell_message_ar("first_10_opportunities_sprint",
                                   "growth_os_monthly")
    assert any("؀" <= ch <= "ۿ" for ch in msg)

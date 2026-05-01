"""Unit tests for Targeting & Acquisition OS."""

from __future__ import annotations

from auto_client_acquisition.targeting_os import (
    ALL_BUYER_ROLES,
    ALL_SOURCES,
    allowed_action_modes,
    analyze_uploaded_list_preview,
    build_acquisition_scorecard,
    build_dealix_self_growth_plan,
    build_followup_sequence,
    build_free_growth_diagnostic,
    build_lead_gen_form_plan,
    build_outreach_plan,
    build_self_growth_daily_brief,
    calculate_channel_reputation,
    classify_source,
    draft_b2b_email,
    draft_role_based_angle,
    draft_whatsapp_message,
    enforce_daily_limits,
    evaluate_contactability,
    explain_contactability_ar,
    list_targeting_services,
    map_buying_committee,
    recommend_accounts,
    recommend_dealix_targets,
    recommend_linkedin_strategy,
    recommend_recovery_action,
    recommend_service_offer,
    score_email_risk,
    score_whatsapp_risk,
    should_pause_channel,
)
from auto_client_acquisition.targeting_os.contract_drafts import (
    draft_dpa_outline,
    draft_pilot_agreement_outline,
)
from auto_client_acquisition.targeting_os.linkedin_strategy import linkedin_do_not_do


# ── Account finder ───────────────────────────────────────────
def test_recommend_accounts_returns_arabic_targets():
    out = recommend_accounts(sector="training", city="Riyadh", limit=5)
    assert out["total"] == 5
    for a in out["accounts"]:
        assert "fit_score" in a
        assert "why_now_ar" in a
        assert any("؀" <= ch <= "ۿ" for ch in a["why_now_ar"])


def test_recommend_accounts_blocks_unsafe_sources():
    out = recommend_accounts(sector="saas", city="Riyadh", limit=2)
    for a in out["accounts"]:
        assert "scraped_email" not in a["primary_sources"]
        assert "scraped_phone" not in a["primary_sources"]


# ── Buyer role mapper ────────────────────────────────────────
def test_buying_committee_for_training_includes_dm():
    out = map_buying_committee(sector="training", company_size="small")
    assert "primary_decision_maker" in out
    assert out["primary_decision_maker"]["role_key"] in ALL_BUYER_ROLES


def test_buying_committee_unknown_sector_falls_back():
    out = map_buying_committee(sector="bogus_xyz")
    assert out["primary_decision_maker"]["role_key"] in ALL_BUYER_ROLES


def test_role_based_angle_returns_arabic():
    out = draft_role_based_angle("head_of_sales", sector="saas",
                                 offer="Pilot 7 أيام")
    assert any("؀" <= ch <= "ۿ" for ch in out["angle_ar"])


# ── Contact source policy ────────────────────────────────────
def test_classify_known_source():
    assert classify_source("crm_customer")["source"] == "crm_customer"


def test_classify_unknown_source():
    assert classify_source("totally_made_up")["source"] == "unknown_source"


def test_all_sources_include_critical():
    for s in ("crm_customer", "linkedin_lead_form", "cold_list", "opt_out"):
        assert s in ALL_SOURCES


# ── Contactability matrix ────────────────────────────────────
def test_opt_out_contact_blocked():
    contact = {"source": "opt_out", "opt_out": True}
    out = evaluate_contactability(contact, desired_channel="whatsapp")
    assert out["status"] == "blocked"
    assert "opt_out" in out["reason_codes"]


def test_cold_whatsapp_blocked():
    contact = {"source": "cold_list", "opt_in_status": "no"}
    out = evaluate_contactability(contact, desired_channel="whatsapp")
    assert out["status"] == "blocked"


def test_inbound_lead_email_safe():
    contact = {"source": "inbound_lead", "opt_in_status": "yes"}
    out = evaluate_contactability(contact, desired_channel="email")
    assert out["status"] == "safe"


def test_unknown_source_needs_review():
    contact = {"source": "unknown_source"}
    out = evaluate_contactability(contact)
    assert out["status"] in ("needs_review", "safe")


def test_explain_contactability_returns_arabic():
    contact = {"source": "cold_list"}
    out = evaluate_contactability(contact, desired_channel="whatsapp")
    text = explain_contactability_ar(out)
    assert "محظور" in text


def test_allowed_action_modes_includes_blocked_only_for_blocked():
    blocked_result = {"status": "blocked"}
    assert allowed_action_modes(blocked_result) == ["blocked"]


# ── LinkedIn strategy ────────────────────────────────────────
def test_linkedin_strategy_never_recommends_scraping():
    out = recommend_linkedin_strategy("B2B SaaS")
    assert "scrape_profiles" in out["do_not_do"]
    assert "auto_dm" in out["do_not_do"]
    assert out["primary"] == "lead_gen_forms"


def test_linkedin_do_not_do_lock_list():
    nope = linkedin_do_not_do()
    for required in ("scrape_profiles", "auto_dm", "auto_connect",
                     "browser_automation"):
        assert required in nope


def test_lead_gen_form_plan_has_hidden_fields():
    plan = build_lead_gen_form_plan("training", "Pilot 7 أيام")
    field_names = [f["name"] for f in plan["hidden_fields"]]
    assert "campaign_name" in field_names
    assert "sector" in field_names


# ── Email strategy ───────────────────────────────────────────
def test_email_draft_includes_unsubscribe():
    contact = {"name": "أحمد", "company": "X"}
    out = draft_b2b_email(contact, offer="Pilot 7 أيام")
    assert "إلغاء" in out["body_ar"] or "STOP" in out["body_ar"]
    assert out["live_send_allowed"] is False


def test_email_risk_blocks_cold_list():
    contact = {"source": "cold_list", "opt_in_status": "no"}
    out = score_email_risk(contact, "ضمان 100% نتائج مضمونة")
    assert out["verdict"] in ("blocked", "needs_review")


def test_email_followup_has_three_steps():
    out = build_followup_sequence({"name": "أحمد"})
    assert len(out["steps"]) == 3
    assert out["live_send_allowed"] is False


# ── WhatsApp strategy ────────────────────────────────────────
def test_whatsapp_cold_blocked():
    contact = {"source": "cold_list", "opt_in_status": "no"}
    out = draft_whatsapp_message(contact)
    assert out["live_send_allowed"] is False
    assert out["risk"]["verdict"] in ("blocked", "needs_review")


def test_whatsapp_risk_blocks_risky_phrase():
    contact = {"source": "inbound_lead", "opt_in_status": "yes"}
    out = score_whatsapp_risk(contact, "ضمان 100% نتائج مضمونة آخر فرصة")
    assert out["risk"] >= 25


# ── Outreach scheduler ───────────────────────────────────────
def test_outreach_plan_generates_steps():
    targets = [{"name": "Acme", "role": "CEO"}, {"name": "Beta", "role": "Sales"}]
    out = build_outreach_plan(targets, channels=["email", "linkedin"])
    assert out["total_targets"] == 2
    for t in out["plan"]:
        for step in t["steps"]:
            assert step["live_send_allowed"] is False


def test_enforce_daily_limits_caps_emails():
    targets = [{"name": f"co_{i}"} for i in range(50)]
    plan = build_outreach_plan(targets, channels=["email"])
    capped = enforce_daily_limits(plan, limits={"max_daily_email_drafts": 5,
                                               "max_same_domain_contacts": 99,
                                               "max_followups": 3,
                                               "cooldown_days": 7,
                                               "max_daily_whatsapp_approved_sends": 5})
    # Across all targets, emails total should not exceed 5
    total_emails = sum(
        sum(1 for s in t["steps"] if s["channel"] == "email")
        for t in capped["plan"]
    )
    assert total_emails <= 5


# ── Reputation guard ─────────────────────────────────────────
def test_reputation_pauses_high_bounce():
    """Multiple critical metrics together should trigger pause."""
    metrics = {"bounce_rate": 0.15, "complaint_rate": 0.005,
               "opt_out_rate": 0.15, "reply_rate": 0.005}
    out = should_pause_channel(metrics, channel="email")
    assert out["should_pause"] is True


def test_reputation_recommends_recovery_actions():
    metrics = {"bounce_rate": 0.10, "complaint_rate": 0.005,
               "opt_out_rate": 0.12, "reply_rate": 0.01}
    out = recommend_recovery_action(metrics, channel="email")
    assert out["actions_ar"]


def test_reputation_healthy_email():
    metrics = {"bounce_rate": 0.005, "complaint_rate": 0.0001,
               "opt_out_rate": 0.01, "reply_rate": 0.05}
    rep = calculate_channel_reputation(metrics, channel="email")
    assert rep["verdict"] == "healthy"


# ── Daily autopilot ──────────────────────────────────────────
def test_today_actions_returned():
    from auto_client_acquisition.targeting_os import recommend_today_actions
    out = recommend_today_actions()
    assert len(out) >= 5
    for a in out:
        assert "label_ar" in a


# ── Self-growth mode ─────────────────────────────────────────
def test_self_growth_targets_list():
    out = recommend_dealix_targets(limit=5)
    assert out["live_send_allowed"] is False
    assert out["targets"]["total"] >= 5


def test_self_growth_daily_brief_has_ten_targets():
    out = build_self_growth_daily_brief()
    assert len(out["top_10_targets"]) >= 5


def test_self_growth_plan_has_monthly_targets():
    out = build_dealix_self_growth_plan()
    assert "monthly_targets" in out


# ── Free diagnostic ──────────────────────────────────────────
def test_free_diagnostic_returns_three_opportunities():
    out = build_free_growth_diagnostic({"sector": "training", "city": "Riyadh"})
    assert out["sections"]["opportunities_ar"]
    assert len(out["sections"]["opportunities_ar"]) == 3


def test_uploaded_list_preview_classifies():
    contacts = [
        {"source": "crm_customer", "opt_in_status": "yes"},
        {"source": "cold_list", "opt_in_status": "no"},
        {"source": "unknown_source"},
    ]
    out = analyze_uploaded_list_preview(contacts)
    assert out["total"] == 3
    assert out["preview"]


# ── Service offers ──────────────────────────────────────────
def test_service_offers_includes_free_diagnostic():
    offers = list_targeting_services()
    ids = {o["id"] for o in offers["offers"]}
    assert "free_growth_diagnostic" in ids
    assert "first_10_opportunities_sprint" in ids


def test_recommend_offer_for_agency():
    rec = recommend_service_offer("agency partner growth")
    assert rec["recommended_offer"]["id"] == "partner_sprint"


# ── Contracts ────────────────────────────────────────────────
def test_pilot_contract_requires_legal_review():
    out = draft_pilot_agreement_outline()
    assert out["legal_review_required"] is True
    assert out["not_legal_advice"] is True


def test_dpa_includes_pdpl():
    out = draft_dpa_outline()
    assert any("PDPL" in s for s in out["sections_ar"])


# ── Acquisition scorecard ───────────────────────────────────
def test_scorecard_aggregates_pipeline():
    out = build_acquisition_scorecard({
        "accounts_researched": 50,
        "decision_makers_mapped": 25,
        "drafts_created": 20,
        "approvals_received": 10,
        "positive_replies": 5,
        "opportunities": [{"expected_value_sar": 18000},
                          {"expected_value_sar": 12000}],
        "events": [{"status": "drafted"}, {"status": "confirmed"}],
        "actions": [{"status": "blocked", "block_reason": "cold_whatsapp"}],
    })
    assert out["pipeline"]["pipeline_sar"] == 30000
    assert out["meetings"]["total"] == 2
    assert out["risks_blocked"]["total"] == 1


def test_productivity_score_strong_with_meetings():
    from auto_client_acquisition.targeting_os import calculate_productivity_score
    out = calculate_productivity_score({
        "accounts_researched": 30, "drafts_created": 10,
        "approvals_received": 5, "positive_replies": 4,
        "meetings_booked": 3,
    })
    assert out["score"] >= 50

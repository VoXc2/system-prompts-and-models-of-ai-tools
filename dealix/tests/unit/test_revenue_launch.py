"""Unit tests for Revenue Launch."""

from __future__ import annotations

import pytest

from auto_client_acquisition.revenue_launch import (
    PIPELINE_STAGES,
    add_prospect,
    build_24h_delivery_plan,
    build_499_pilot_offer,
    build_case_study_free_offer,
    build_client_intake_form,
    build_client_summary,
    build_first_10_opportunities_delivery,
    build_first_20_segments_v2,
    build_followup_1,
    build_followup_2,
    build_growth_diagnostic_delivery,
    build_growth_os_pilot_offer,
    build_list_intelligence_delivery,
    build_moyasar_invoice_instructions,
    build_next_step_recommendation,
    build_outreach_message_v2,
    build_payment_confirmation_checklist,
    build_payment_link_message,
    build_pipeline_schema,
    build_private_beta_offer,
    build_private_beta_proof_pack,
    build_reply_handlers_v2,
    recommend_offer_for_segment,
    summarize_pipeline,
    update_stage,
)


# ── Offers ───────────────────────────────────────────────────
def test_499_pilot_has_correct_price():
    o = build_499_pilot_offer()
    assert o["price_sar"] == 499
    assert o["live_send_allowed"] is False
    assert o["no_live_charge"] is True


def test_growth_os_pilot_30_days():
    o = build_growth_os_pilot_offer()
    assert o["duration_days"] == 30
    assert o["price_sar_min"] == 1500
    assert o["price_sar_max"] == 3000


def test_case_study_free_requires_consent():
    o = build_case_study_free_offer()
    assert o["price_sar"] == 0
    assert o["case_study_required"] is True


def test_recommend_offer_for_agency():
    out = recommend_offer_for_segment("agency_b2b")
    assert out["primary_offer"] == "growth_os_pilot_30d"


def test_recommend_offer_for_training():
    out = recommend_offer_for_segment("training_consulting")
    assert out["primary_offer"] == "pilot_499_7d"


def test_recommend_offer_unknown_segment_default():
    out = recommend_offer_for_segment("totally_unknown")
    assert out["primary_offer"] == "pilot_499_7d"


def test_private_beta_offer_re_export():
    o = build_private_beta_offer()
    assert o["price_sar"] == 499


# ── Pipeline ─────────────────────────────────────────────────
def test_pipeline_schema_has_8_stages():
    s = build_pipeline_schema()
    assert len(s["stages"]) == 8
    assert "paid" in s["stages"]
    assert "lost" in s["stages"]


def test_add_prospect_starts_at_identified():
    p = add_prospect(company="Acme", segment="saas_tech_small")
    assert p["stage"] == "identified"
    assert p["paid"] is False


def test_update_stage_to_paid_marks_paid_true():
    p = add_prospect(company="Acme")
    update_stage(prospect=p, new_stage="paid", notes="Moyasar 499")
    assert p["stage"] == "paid"
    assert p["paid"] is True
    assert "Moyasar" in str(p["notes"])


def test_update_stage_invalid_raises():
    p = add_prospect(company="Acme")
    with pytest.raises(ValueError):
        update_stage(prospect=p, new_stage="bogus_stage")


def test_summarize_pipeline_counts_revenue():
    pipeline = []
    p1 = add_prospect(pipeline=pipeline, company="A", segment="agency_b2b")
    p2 = add_prospect(pipeline=pipeline, company="B", segment="training")
    p1["price_sar"] = 499
    update_stage(prospect=p1, new_stage="paid")
    update_stage(prospect=p2, new_stage="lost")
    s = summarize_pipeline(pipeline)
    assert s["total_prospects"] == 2
    assert s["revenue_paid_sar"] == 499.0
    assert s["by_stage"]["paid"] == 1
    assert s["by_stage"]["lost"] == 1
    assert s["win_rate"] == 0.5


# ── Outreach ─────────────────────────────────────────────────
def test_first_20_segments_v2():
    out = build_first_20_segments_v2()
    assert out["total_targets"] == 20


def test_outreach_message_v2_arabic():
    out = build_outreach_message_v2("agency_b2b")
    assert any("؀" <= ch <= "ۿ" for ch in out["body_ar"])


def test_followup_1_and_2_differ():
    s1 = build_followup_1("training_consulting")
    s2 = build_followup_2("training_consulting")
    assert s1["body_ar"] != s2["body_ar"]


def test_reply_handlers_v2_includes_unsubscribe():
    h = build_reply_handlers_v2()
    assert "unsubscribe" in h


# ── Pilot delivery ───────────────────────────────────────────
def test_intake_form_has_required_fields():
    f = build_client_intake_form()
    keys = {q["key"] for q in f["fields"]}
    for required in ("company_name", "sector", "city", "primary_offer",
                     "approval_owner"):
        assert required in keys


def test_24h_delivery_plan_has_5_phases():
    p = build_24h_delivery_plan("first_10_opportunities_sprint")
    assert len(p["phases"]) == 5
    assert p["live_send_allowed"] is False


def test_first_10_delivery_has_proof():
    out = build_first_10_opportunities_delivery({"sector": "training"})
    assert "Proof Pack v1" in out["deliverables"]
    assert out["approval_required"] is True


def test_list_intelligence_delivery_includes_50_targets():
    out = build_list_intelligence_delivery({"sector": "real_estate"})
    assert any("50" in d for d in out["deliverables"])


def test_growth_diagnostic_delivery_24h():
    out = build_growth_diagnostic_delivery({"sector": "saas"})
    assert "24" in out["delivery_time"] or "ساعة" in out["delivery_time"]


# ── Payment manual flow ──────────────────────────────────────
def test_invoice_instructions_correct_halalas():
    out = build_moyasar_invoice_instructions(amount_sar=499)
    assert out["amount_sar"] == 499
    assert out["amount_halalas"] == 49900
    assert out["no_live_charge"] is True


def test_invoice_instructions_warns_no_card_storage():
    out = build_moyasar_invoice_instructions(amount_sar=499)
    text = " ".join(out["do_not_do_ar"])
    assert "بطاقة" in text or "card" in text.lower()


def test_payment_link_message_arabic_and_no_live_send():
    out = build_payment_link_message(
        customer_name="أحمد", invoice_url="https://example.com/inv/1",
    )
    assert any("؀" <= ch <= "ۿ" for ch in out["body_ar"])
    assert out["live_send_allowed"] is False


def test_payment_confirmation_checklist_blocks_premature_delivery():
    out = build_payment_confirmation_checklist()
    text = " ".join(out["do_not_do_ar"])
    assert "paid" in text.lower() or "تأكيد" in text


# ── Proof Pack ───────────────────────────────────────────────
def test_proof_pack_template_has_metrics():
    out = build_private_beta_proof_pack(company_name="Acme")
    assert "opportunities_generated" in out["metrics_to_include"]
    assert out["approval_required"] is True


def test_client_summary_returns_5_lines():
    out = build_client_summary(
        company_name="Acme", opportunities_count=10,
        approved_drafts=4, meetings=2, pipeline_sar=18000,
        risks_blocked=3,
    )
    assert len(out["summary_ar"]) == 5
    assert any("18000" in line or "18,000" in line or "18000" in str(line)
               for line in out["summary_ar"])


def test_next_step_upsell_for_strong_outcome():
    out = build_next_step_recommendation(pilot_metrics={
        "pipeline_sar": 30000, "meetings": 3, "csat": 9,
    })
    assert out["next_action"] == "upsell_growth_os_monthly"


def test_next_step_iterate_for_weak_outcome():
    out = build_next_step_recommendation(pilot_metrics={
        "pipeline_sar": 1000, "meetings": 0, "csat": 5,
    })
    assert out["next_action"] == "iterate_or_archive"


def test_next_step_extend_for_promising_outcome():
    out = build_next_step_recommendation(pilot_metrics={
        "pipeline_sar": 12000, "meetings": 1, "csat": 7,
    })
    assert out["next_action"] == "extend_pilot"


# ── Constants ───────────────────────────────────────────────
def test_pipeline_stages_constant_exposed():
    assert "identified" in PIPELINE_STAGES
    assert "paid" in PIPELINE_STAGES
    assert "lost" in PIPELINE_STAGES

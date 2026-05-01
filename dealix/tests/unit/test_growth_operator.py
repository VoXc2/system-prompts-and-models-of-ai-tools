"""Unit tests for the Arabic Growth Operator layer."""

from __future__ import annotations

import pytest

from auto_client_acquisition.growth_operator import (
    build_calendar_draft,
    build_demo_profile,
    build_meeting_agenda,
    build_moyasar_payment_link_draft,
    build_post_meeting_followup,
    build_weekly_proof_pack,
    classify_contact_source,
    contactability_summary,
    dedupe_contacts,
    detect_opt_out,
    draft_arabic_message,
    draft_followup,
    draft_objection_response,
    draft_partner_outreach,
    list_missions,
    normalize_phone,
    partner_scorecard,
    profile_from_dict,
    rank_targets,
    recommend_top_10,
    run_mission,
    sar_to_halalas,
    score_contactability,
    segment_contacts,
    suggest_partner_types,
    summarize_import,
)


# ── 1. Phone normalization ───────────────────────────────────────
def test_normalize_phone_country_prefix_kept():
    assert normalize_phone("+966500000001") == "966500000001"


def test_normalize_phone_local_zero_to_country():
    assert normalize_phone("0500000001") == "966500000001"


def test_normalize_phone_bare_9_digits():
    assert normalize_phone("500000001") == "966500000001"


def test_normalize_phone_double_zero():
    assert normalize_phone("00966500000001") == "966500000001"


def test_normalize_phone_strips_punctuation():
    assert normalize_phone("+966 (50) 000-0001") == "966500000001"


def test_normalize_phone_invalid_returns_empty():
    assert normalize_phone("") == ""
    assert normalize_phone("abc") == ""


# ── 2. Dedupe ────────────────────────────────────────────────────
def test_dedupe_drops_exact_phone_duplicates():
    out = dedupe_contacts([
        {"name": "X", "phone": "0500000001"},
        {"name": "X duplicate", "phone": "+966 50 000 0001"},
    ])
    assert len(out) == 1


def test_dedupe_keeps_richer_record():
    out = dedupe_contacts([
        {"name": "X", "phone": "0500000001"},
        {"name": "X full", "phone": "0500000001", "email": "x@example.sa", "company": "Co"},
    ])
    assert len(out) == 1
    assert out[0].get("email") == "x@example.sa"


# ── 3. Source classification ─────────────────────────────────────
def test_classify_existing_customer():
    assert classify_contact_source({"relationship_status": "customer"}) == "existing_customer"


def test_classify_inbound():
    assert classify_contact_source({"source": "website_form"}) == "inbound_lead"


def test_classify_event():
    assert classify_contact_source({"source": "exhibition"}) == "event_lead"


def test_classify_cold():
    assert classify_contact_source({"source": "cold"}) == "cold_list"


def test_classify_unknown_default():
    assert classify_contact_source({}) == "unknown"


# ── 4. Opt-out detection ─────────────────────────────────────────
def test_detect_opt_out_via_status():
    assert detect_opt_out({"opt_in_status": "opted_out"}) is True


def test_detect_opt_out_via_arabic_notes():
    assert detect_opt_out({"notes": "العميل طلب إيقاف الرسائل"}) is True


def test_detect_opt_out_clean():
    assert detect_opt_out({"name": "X"}) is False


# ── 5. Summarize import ──────────────────────────────────────────
def test_summarize_import_aggregates():
    contacts = [
        {"name": "A", "phone": "0500000001", "source": "customer"},
        {"name": "A dup", "phone": "0500000001", "source": "customer"},  # dup
        {"name": "B", "phone": "0500000002", "source": "cold"},
        {"name": "C", "phone": "0500000003", "opt_in_status": "opted_out"},
    ]
    s = summarize_import(contacts)
    assert s["raw_total"] == 4
    assert s["after_dedupe"] == 3
    assert s["duplicates_removed"] == 1
    assert s["opt_out_count"] == 1


# ── 6. Contactability — core safety rules ───────────────────────
def test_contactability_blocks_opt_out():
    out = score_contactability({"opt_in_status": "opted_out", "phone": "0500000001"})
    assert out["label"] == "blocked"


def test_contactability_blocks_cold_whatsapp_by_default():
    """No cold WhatsApp without lawful basis — that's the policy."""
    out = score_contactability(
        {"phone": "0500000001", "source": "cold", "name": "X"},
        channel="whatsapp",
    )
    assert out["label"] == "blocked"
    assert any("PDPL" in r or "lawful" in r or "بدون" in r for r in out["reasons"])


def test_contactability_unknown_source_needs_review():
    out = score_contactability(
        {"phone": "0500000001", "name": "X"},
        channel="whatsapp",
    )
    assert out["label"] == "needs_review"


def test_contactability_existing_customer_safe():
    out = score_contactability(
        {"phone": "0500000001", "name": "X", "relationship_status": "customer"},
        channel="whatsapp",
    )
    assert out["label"] == "safe"


def test_contactability_inbound_lead_safe():
    out = score_contactability(
        {"phone": "0500000001", "name": "X", "source": "website_form"},
        channel="whatsapp",
    )
    assert out["label"] == "safe"


def test_contactability_summary_aggregates():
    s = contactability_summary(
        [
            {"phone": "0500000001", "relationship_status": "customer"},
            {"phone": "0500000002", "source": "cold"},
            {"phone": "0500000003", "opt_in_status": "opted_out"},
        ],
        channel="whatsapp",
    )
    assert s["by_label"]["safe"] >= 1
    assert s["by_label"]["blocked"] >= 2  # cold + opt-out


# ── 7. Targeting + ranking ──────────────────────────────────────
def test_rank_targets_filters_unsafe():
    contacts = [
        {"phone": "0500000001", "relationship_status": "customer"},
        {"phone": "0500000002", "source": "cold"},
    ]
    ranked = rank_targets(contacts, sector_hint="real_estate", channel="whatsapp")
    assert len(ranked) == 1  # only the safe customer survives


def test_recommend_top_10_returns_at_most_10():
    contacts = [
        {"phone": f"05000000{i:02d}", "relationship_status": "customer", "name": f"X{i}"}
        for i in range(15)
    ]
    out = recommend_top_10(contacts, sector_hint="real_estate")
    assert out["candidates_evaluated"] == 15
    assert len(out["top"]) == 10


def test_segment_contacts_buckets():
    segs = segment_contacts([
        {"phone": "0500000001", "relationship_status": "customer"},
        {"phone": "0500000002", "source": "exhibition"},
        {"phone": "0500000003", "source": "cold"},
        {"phone": "0500000004", "opt_in_status": "opted_out"},
    ])
    assert len(segs["existing_customer"]) == 1
    assert len(segs["event_lead"]) == 1
    assert len(segs["cold_list"]) == 1
    assert len(segs["blocked_or_invalid"]) == 1


# ── 8. Message planner — Arabic + approval invariant ────────────
def test_arabic_message_always_pending_approval():
    out = draft_arabic_message(
        {"phone": "0500000001", "name": "سامي", "city": "الرياض", "sector": "real_estate"},
    )
    assert out["approval_required"] is True
    assert out["approval_status"] == "pending_approval"


def test_arabic_message_contains_arabic():
    out = draft_arabic_message({"phone": "0500000001", "name": "X", "sector": "clinics"})
    assert any("؀" <= ch <= "ۿ" for ch in out["body_ar"]), "body must contain Arabic"


def test_arabic_message_no_overhyped_phrases():
    """The default templates must not contain 'ضمان 100%' / 'مضمونة' etc."""
    out = draft_arabic_message({"phone": "0500000001", "name": "X"})
    body = out["body_ar"]
    for banned in ("ضمان 100", "نتائج مضمونة", "آخر فرصة", "اضغط هنا فوراً"):
        assert banned not in body


def test_followup_returns_pending_approval():
    out = draft_followup({"phone": "0500000001", "name": "X"}, days_since_last=3)
    assert out["approval_required"] is True


def test_objection_response_known():
    out = draft_objection_response("send_offer_whatsapp")
    assert "next_action" in out
    assert out["approval_required"] is True


def test_objection_response_unknown_diagnostic():
    out = draft_objection_response("totally_unknown_objection")
    assert out["next_action"] == "diagnostic_question"


# ── 9. Partnership planner ──────────────────────────────────────
def test_partnership_suggestions_smb_emphasizes_agencies():
    out = suggest_partner_types(customer_size="smb")
    top_keys = [s["key"] for s in out["suggestions"][:3]]
    # SMB should prioritize agency / consultant / community
    assert any(k in ("marketing_agency", "sales_consultant", "founder_community") for k in top_keys)


def test_partnership_outreach_pending():
    out = draft_partner_outreach(partner_type_key="marketing_agency", partner_name="Test Agency")
    assert out["approval_required"] is True


def test_partnership_outreach_unknown_type():
    out = draft_partner_outreach(partner_type_key="bogus_type")
    assert "error" in out


def test_partner_scorecard_grading():
    high = partner_scorecard(
        partner_id="p1", intros_made=10, deals_influenced=4,
        revenue_share_paid_sar=50_000, relationship_age_months=6,
    )
    low = partner_scorecard(partner_id="p2")
    assert high["overall_score"] > low["overall_score"]
    assert high["tier"] in ("platinum", "gold")
    assert low["tier"] == "bronze"


# ── 10. Meeting planner — no live event ─────────────────────────
def test_meeting_agenda_returns_slots():
    out = build_meeting_agenda(
        contact_name="سامي", company="Test Co.",
        purpose_ar="تأهيل أولي", duration_minutes=20,
    )
    assert out["agenda_ar"]
    assert out["approval_required"] is True


def test_meeting_calendar_draft_not_inserted():
    out = build_calendar_draft(
        contact_email="x@test.sa", contact_name="X", company="Test Co.",
        duration_minutes=30,
    )
    assert out["live_inserted"] is False
    assert out["approval_required"] is True
    # Required Google Calendar shape
    assert "summary" in out and "start" in out and "end" in out
    assert out["start"]["timeZone"] == "Asia/Riyadh"


def test_post_meeting_followup_pending():
    out = build_post_meeting_followup(
        contact_name="X", company="Test", summary_ar="مهتم في pilot.",
    )
    assert out["approval_required"] is True


# ── 11. Payment offer — no live charge ──────────────────────────
def test_sar_to_halalas_basic():
    assert sar_to_halalas(1) == 100
    assert sar_to_halalas(2999) == 299_900


def test_sar_to_halalas_negative_raises():
    with pytest.raises(ValueError):
        sar_to_halalas(-5)


def test_payment_draft_does_not_charge():
    out = build_moyasar_payment_link_draft(
        plan_key="growth_os", customer_id="c1", contact_email="x@test.sa",
    )
    assert out["live_charged"] is False
    assert out["approval_required"] is True
    # Moyasar payload uses halalas
    assert out["moyasar_request_draft"]["amount"] == 299_900
    assert out["moyasar_request_draft"]["currency"] == "SAR"


def test_payment_draft_unknown_plan():
    out = build_moyasar_payment_link_draft(plan_key="bogus", customer_id="c1")
    assert "error" in out
    assert out["live_charged"] is False


# ── 12. Proof pack ──────────────────────────────────────────────
def test_proof_pack_structure():
    out = build_weekly_proof_pack(
        customer_id="c1", customer_name="Test Co.", week_label="W18-2026",
        plan_cost_weekly_sar=750,
        opportunities_discovered=42, messages_drafted=38,
        messages_approved=33, messages_sent=33,
        replies_received=11, positive_replies=4,
        meetings_booked=3, meetings_held=2,
        proposals_sent=1, deals_won=0,
        pipeline_added_sar=185_000, revenue_won_sar=0,
        risky_drafts_blocked=5, revenue_leaks_recovered=2,
        avg_response_minutes=42,
    )
    assert out["grade"] in ("A+", "A", "B", "C", "D")
    assert "activity" in out and "money" in out and "quality" in out
    assert out["next_week_plan_ar"]
    assert "Dealix Proof Pack" in out["markdown_export"]


# ── 13. Missions ────────────────────────────────────────────────
def test_missions_include_first_10_opportunities():
    out = list_missions()
    ids = {m["id"] for m in out["missions"]}
    assert "first_10_opportunities" in ids
    assert "recover_stalled_deals" in ids
    assert "partnership_sprint" in ids
    assert "safe_whatsapp_campaign" in ids
    assert out["kill_feature_id"] == "first_10_opportunities"


def test_run_mission_known():
    out = run_mission("first_10_opportunities", payload={"sector": "real_estate"})
    assert out["mission_id"] == "first_10_opportunities"
    assert out["next_step_ar"]
    assert out["primary_endpoint"]
    assert out["approval_required"] is True


def test_run_mission_unknown():
    out = run_mission("bogus_mission")
    assert "error" in out


# ── 14. Profile ─────────────────────────────────────────────────
def test_demo_profile_specialized():
    p = build_demo_profile()
    assert p.is_specialized()
    assert "compliance_rules" in p.to_dict()


def test_profile_from_dict_partial_not_specialized():
    p = profile_from_dict({"customer_id": "c1", "company_name": "X"})
    assert not p.is_specialized()


def test_profile_default_compliance_blocks_keywords():
    p = profile_from_dict({"customer_id": "c1"})
    rules = p.compliance_rules
    assert "blocked_keywords" in rules
    assert "ضمان 100" in rules["blocked_keywords"]
    assert rules["no_cold_whatsapp_without_lawful_basis"] is True

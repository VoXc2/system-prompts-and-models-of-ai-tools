"""Tests for the Public Launch Gate (Layer 13)."""

from __future__ import annotations

from auto_client_acquisition.public_launch import (
    PUBLIC_LAUNCH_CRITERIA,
    GateVerdict,
    evaluate_public_launch_gate,
    pilot_tracker_summary,
    PilotRecord,
    compute_pdpl_compliance,
    compute_brand_moat_score,
)


# ===== Gate evaluation =====

def test_criteria_count_is_nine():
    assert len(PUBLIC_LAUNCH_CRITERIA) == 9


def test_gate_all_passing_yields_go_public_launch():
    state = {
        "pilots_completed": 7,
        "paid_customers": 3,
        "unsafe_sends": 0,
        "proof_cadence_weeks": 4,
        "support_first_response_minutes_p1": 60,
        "funnel_visible": True,
        "staging_uptime_days": 21,
        "billing_webhook_verified": True,
        "legal_complete": True,
    }
    v = evaluate_public_launch_gate(state)
    assert v.decision == "GO_PUBLIC_LAUNCH"
    assert v.score_passed == v.score_total == 9
    assert not v.blockers
    assert "جاهز للإطلاق العام" in v.summary_ar


def test_gate_unsafe_sends_triggers_blocked():
    state = {
        "pilots_completed": 7,
        "paid_customers": 3,
        "unsafe_sends": 1,  # ← hard block
        "proof_cadence_weeks": 4,
        "support_first_response_minutes_p1": 60,
        "funnel_visible": True,
        "staging_uptime_days": 21,
        "billing_webhook_verified": True,
        "legal_complete": True,
    }
    v = evaluate_public_launch_gate(state)
    assert v.decision == "BLOCKED"
    assert "Hard block" in v.summary_ar


def test_gate_partial_yields_no_go_with_blockers():
    state = {
        "pilots_completed": 2,
        "paid_customers": 1,
        "unsafe_sends": 0,
        "proof_cadence_weeks": 1,
        "support_first_response_minutes_p1": 60,
        "funnel_visible": True,
        "staging_uptime_days": 5,
        "billing_webhook_verified": False,
        "legal_complete": False,
    }
    v = evaluate_public_launch_gate(state)
    assert v.decision == "NO_GO"
    assert v.score_passed < v.score_total
    blocker_keys = {b["key"] for b in v.blockers}
    assert "pilots_completed" in blocker_keys
    assert "billing_webhook_verified" in blocker_keys
    assert "legal_complete" in blocker_keys
    assert v.next_actions_ar  # has Arabic actions


def test_gate_empty_state_blocks_everything():
    v = evaluate_public_launch_gate({})
    assert v.decision != "GO_PUBLIC_LAUNCH"
    assert len(v.blockers) >= 8


def test_gate_support_response_is_max_threshold_lower_better():
    state_good = {"support_first_response_minutes_p1": 30}
    state_bad = {"support_first_response_minutes_p1": 200}
    # 30 ≤ 120 → pass; 200 > 120 → fail
    keys_good = {r["key"] for r in evaluate_public_launch_gate(state_good).criteria_results if r["passed"]}
    keys_bad = {r["key"] for r in evaluate_public_launch_gate(state_bad).criteria_results if r["passed"]}
    assert "support_first_response_minutes_p1" in keys_good
    assert "support_first_response_minutes_p1" not in keys_bad


# ===== Pilot tracker =====

def test_pilot_summary_basic_aggregation():
    pilots = [
        {
            "pilot_id": "p1", "company": "A", "sector": "agency", "city": "RUH",
            "started_at": "2026-04-25", "stage": "completed",
            "paid": True, "pilot_price_sar": 499,
            "proof_pack_sent": True, "proof_pack_sent_at": "2026-05-01",
            "upgrade_outcome": "growth_os_monthly", "upgrade_value_sar": 2999,
        },
        {
            "pilot_id": "p2", "company": "B", "sector": "training", "city": "JED",
            "started_at": "2026-04-20", "stage": "stalled",
            "paid": False, "pilot_price_sar": 0,
            "proof_pack_sent": False, "proof_pack_sent_at": None,
            "upgrade_outcome": None,
        },
    ]
    s = pilot_tracker_summary(pilots)
    assert s.total_pilots == 2
    assert s.completed_pilots == 1
    assert s.proof_packs_delivered == 1
    assert s.paid_pilots == 1
    assert s.paid_revenue_sar == 499
    assert s.upgrade_revenue_sar == 2999
    assert s.growth_os_subscribers == 1
    assert s.stalled_pilots == 1
    assert s.by_sector == {"agency": 1, "training": 1}
    assert s.by_city == {"RUH": 1, "JED": 1}


def test_pilot_summary_empty_returns_zeros():
    s = pilot_tracker_summary([])
    assert s.total_pilots == 0
    assert s.completion_rate == 0.0
    assert s.paid_conversion_rate == 0.0
    assert s.upgrade_conversion_rate == 0.0


def test_pilot_summary_avg_proof_days_computed():
    pilots = [
        {
            "pilot_id": "p1", "company": "A", "sector": "saas", "city": "RUH",
            "started_at": "2026-04-25T00:00:00", "stage": "completed",
            "paid": True, "pilot_price_sar": 499,
            "proof_pack_sent": True,
            "proof_pack_sent_at": "2026-05-02T00:00:00",
            "upgrade_outcome": "case_study",
        }
    ]
    s = pilot_tracker_summary(pilots)
    assert s.average_proof_pack_days == 7.0


def test_pilot_summary_accepts_pilotrecord_instances():
    rec = PilotRecord(
        pilot_id="p1", company="A", sector="agency", city="RUH",
        started_at="2026-04-25", stage="completed",
        paid=True, pilot_price_sar=499,
        proof_pack_sent=True, proof_pack_sent_at="2026-05-01",
        upgrade_outcome="growth_os_monthly", upgrade_value_sar=2999,
    )
    s = pilot_tracker_summary([rec])
    assert s.total_pilots == 1
    assert s.paid_pilots == 1


# ===== PDPL compliance =====

def test_pdpl_full_compliance_yields_compliant():
    state = {
        "data_residency_saudi": True,
        "whatsapp_opt_in_audit": True,
        "email_opt_in_audit": True,
        "breach_notification_72h_ready": True,
        "dpa_template_published": True,
        "privacy_policy_bilingual": True,
        "data_retention_policy": True,
        "trace_redaction_active": True,
        "action_ledger_audit": True,
        "consent_revocation_path": True,
    }
    r = compute_pdpl_compliance(state)
    assert r.overall_status == "compliant"
    assert r.score_passed == r.score_total
    assert not r.critical_failures


def test_pdpl_critical_failure_yields_non_compliant():
    state = {
        "data_residency_saudi": False,  # critical
        "whatsapp_opt_in_audit": True,
        "email_opt_in_audit": True,
        "breach_notification_72h_ready": True,
        "dpa_template_published": True,
        "privacy_policy_bilingual": True,
        "data_retention_policy": True,
        "trace_redaction_active": True,
        "action_ledger_audit": True,
        "consent_revocation_path": True,
    }
    r = compute_pdpl_compliance(state)
    assert r.overall_status == "non_compliant"
    assert any(f["key"] == "data_residency_saudi" for f in r.critical_failures)


def test_pdpl_high_only_yields_needs_fixes():
    state = {
        "data_residency_saudi": True,
        "whatsapp_opt_in_audit": True,
        "email_opt_in_audit": False,  # high
        "breach_notification_72h_ready": True,
        "dpa_template_published": True,
        "privacy_policy_bilingual": True,
        "data_retention_policy": True,
        "trace_redaction_active": True,
        "action_ledger_audit": True,
        "consent_revocation_path": True,
    }
    r = compute_pdpl_compliance(state)
    assert r.overall_status == "needs_fixes"
    assert not r.critical_failures
    assert any(f["key"] == "email_opt_in_audit" for f in r.high_failures)


# ===== Brand moat score =====

def test_brand_moat_zero_state_yields_fragile():
    score = compute_brand_moat_score({})
    assert score.tier == "fragile"
    assert score.overall_score < 35


def test_brand_moat_high_state_yields_dominant():
    state = {
        "events_logged_count": 5_000,
        "messages_per_sector_count": 200,
        "sectors_covered_count": 15,
        "linkedin_followers": 10_000,
        "newsletter_subscribers": 3_000,
        "monthly_branded_searches": 1_500,
        "case_studies_published": 30,
        "pdpl_compliance_pct": 100,
        "iso_27001_progress_pct": 100,
        "audit_count_last_year": 6,
        "dpa_signed_with_customers_pct": 100,
        "agency_partners_count": 50,
        "active_referring_agencies_count": 25,
        "agency_revenue_share_paid_sar": 200_000,
        "certified_operators_count": 200,
        "operators_active_last_30d": 100,
        "operator_revenue_share_paid_sar": 100_000,
    }
    score = compute_brand_moat_score(state)
    assert score.tier == "dominant"
    assert score.overall_score >= 80


def test_brand_moat_identifies_weakest_dimension():
    state = {
        # Strong everywhere except network
        "events_logged_count": 5_000,
        "messages_per_sector_count": 200,
        "sectors_covered_count": 15,
        "linkedin_followers": 10_000,
        "newsletter_subscribers": 3_000,
        "monthly_branded_searches": 1_500,
        "case_studies_published": 30,
        "pdpl_compliance_pct": 100,
        "iso_27001_progress_pct": 100,
        "audit_count_last_year": 6,
        "dpa_signed_with_customers_pct": 100,
        # network = 0
        "agency_partners_count": 0,
        "active_referring_agencies_count": 0,
        "agency_revenue_share_paid_sar": 0,
        # distribution = 0
        "certified_operators_count": 0,
        "operators_active_last_30d": 0,
        "operator_revenue_share_paid_sar": 0,
    }
    score = compute_brand_moat_score(state)
    assert score.weakest_dimension in ("network_moat", "distribution_moat")


def test_brand_moat_returns_arabic_summary():
    score = compute_brand_moat_score({})
    assert "Brand Moat Score" in score.summary_ar
    assert "fragile" in score.summary_ar or "هش" in score.summary_ar


# ===== GateVerdict serialization =====

def test_gate_verdict_serializes_to_dict():
    v = evaluate_public_launch_gate({"pilots_completed": 5, "paid_customers": 2})
    d = v.to_dict()
    assert "decision" in d
    assert "criteria_results" in d
    assert "next_actions_ar" in d
    assert isinstance(d["criteria_results"], list)

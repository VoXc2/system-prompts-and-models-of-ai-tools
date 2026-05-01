"""Smoke tests for compliance gate + reply classifier + targeting helpers."""

from __future__ import annotations

import pytest

from auto_client_acquisition.email.compliance import (
    ComplianceCheck,
    append_opt_out_line,
    check_outreach,
)
from auto_client_acquisition.email.reply_classifier import (
    build_classification,
    classify_rule_based,
    classify_reply,
)
from auto_client_acquisition.email.daily_targeting import (
    angle_for,
    select_top_n_diversified,
)


# ── Compliance gate ───────────────────────────────────────────────
def test_compliance_blocks_no_email():
    chk = check_outreach(to_email=None, allowed_use="business_contact_research_only")
    assert chk.allowed is False
    assert "no_recipient_email" in chk.blocked_reasons


def test_compliance_blocks_invalid_email():
    chk = check_outreach(to_email="not-an-email", allowed_use="business_contact_research_only")
    assert chk.allowed is False
    assert "invalid_email_format" in chk.blocked_reasons


def test_compliance_blocks_opt_out():
    chk = check_outreach(
        to_email="x@dealix.me", contact_opt_out=True,
        allowed_use="business_contact_research_only",
    )
    assert chk.allowed is False
    assert "contact_opt_out_true" in chk.blocked_reasons


def test_compliance_blocks_suppression():
    chk = check_outreach(
        to_email="x@dealix.me",
        suppression_emails={"x@dealix.me"},
        allowed_use="business_contact_research_only",
    )
    assert chk.allowed is False
    assert "email_suppressed" in chk.blocked_reasons


def test_compliance_blocks_high_risk():
    chk = check_outreach(
        to_email="x@dealix.me", risk_score=80,
        allowed_use="business_contact_research_only",
    )
    assert chk.allowed is False
    assert any("risk_score_too_high" in r for r in chk.blocked_reasons)


def test_compliance_blocks_no_allowed_use():
    chk = check_outreach(to_email="x@dealix.me", allowed_use=None)
    assert chk.allowed is False
    assert "allowed_use_missing" in chk.blocked_reasons


def test_compliance_blocks_daily_limit():
    chk = check_outreach(
        to_email="x@dealix.me", sent_today_count=50,
        allowed_use="business_contact_research_only",
    )
    assert chk.allowed is False
    assert any("daily_limit_hit" in r for r in chk.blocked_reasons)


def test_compliance_blocks_batch_size():
    chk = check_outreach(
        to_email="x@dealix.me", sent_in_current_batch=10,
        allowed_use="business_contact_research_only",
    )
    assert chk.allowed is False
    assert any("batch_size_hit" in r for r in chk.blocked_reasons)


def test_compliance_blocks_batch_cooldown():
    chk = check_outreach(
        to_email="x@dealix.me",
        seconds_since_last_batch=600,  # 10 min, cooldown is 90 min
        allowed_use="business_contact_research_only",
    )
    assert chk.allowed is False
    assert any("batch_cooldown" in r for r in chk.blocked_reasons)


def test_compliance_personal_email_review_required():
    chk = check_outreach(
        to_email="x@gmail.com",
        allowed_use="business_contact_research_only",
    )
    assert chk.requires_human_review is True
    assert chk.allowed is False
    assert any("personal_email_domain_review_required" in n for n in chk.notes)


def test_compliance_allows_clean_business_email():
    chk = check_outreach(
        to_email="x@aramco.com",
        allowed_use="business_contact_research_only",
        risk_score=10,
        sent_today_count=5,
        sent_in_current_batch=2,
        seconds_since_last_batch=10000,
    )
    assert chk.allowed is True
    assert chk.blocked_reasons == []


# ── Opt-out line appender ─────────────────────────────────────────
def test_append_opt_out_adds_line():
    body = "مرحباً، تجربة Dealix"
    out = append_opt_out_line(body)
    assert "STOP" in out or "إيقاف" in out


def test_append_opt_out_idempotent():
    body = "مرحباً، تجربة Dealix\n\n— STOP لإلغاء"
    out = append_opt_out_line(body)
    # Already has STOP — shouldn't double-append
    assert out.count("STOP") == 1


# ── Reply classifier (rule-based, no LLM needed) ──────────────────
def test_classify_unsubscribe_arabic():
    cat, conf = classify_rule_based("STOP")
    assert cat == "unsubscribe"
    assert conf >= 0.5


def test_classify_unsubscribe_english():
    cat, conf = classify_rule_based("Please unsubscribe me")
    assert cat == "unsubscribe"


def test_classify_interested():
    cat, conf = classify_rule_based("نعم تجربة، نبدأ متى؟")
    assert cat == "interested"


def test_classify_ask_price():
    cat, conf = classify_rule_based("كم السعر؟")
    assert cat == "ask_price"


def test_classify_ask_demo():
    cat, conf = classify_rule_based("can we book a demo?")
    assert cat == "ask_demo"


def test_classify_objection_budget():
    cat, conf = classify_rule_based("غالي علينا، الميزانية محدودة")
    assert cat == "objection_budget"


def test_classify_objection_ai():
    cat, conf = classify_rule_based("نبي إنسان حقيقي مو روبوت")
    assert cat == "objection_ai"


def test_classify_partnership():
    cat, conf = classify_rule_based("نبي نكون شركاء توزيع")
    assert cat == "partnership"


def test_classify_unclear_for_empty():
    cat, conf = classify_rule_based("")
    assert cat == "unclear"


def test_classify_already_has_crm():
    cat, conf = classify_rule_based("عندنا HubSpot أصلاً، شكراً")
    assert cat == "already_has_crm"


def test_build_classification_unsubscribe_auto_send_allowed():
    rc = build_classification("unsubscribe", 0.95, "STOP")
    # Auto-send the ack is allowed (mandatory courtesy)
    assert rc.auto_send_allowed is True
    assert rc.followup_days is None


def test_build_classification_angry_requires_review():
    rc = build_classification("angry", 0.9, "this is spam complaint")
    assert rc.requires_human_review is True
    assert rc.auto_send_allowed is False


def test_build_classification_low_confidence_requires_review():
    rc = build_classification("interested", 0.2, "?")
    assert rc.requires_human_review is True


@pytest.mark.asyncio
async def test_classify_reply_async_falls_back_to_rules():
    rc = await classify_reply("STOP", prefer_llm=True)
    # No LLM key in test env → falls back to rules
    assert rc.category == "unsubscribe"


# ── Daily targeting helpers ───────────────────────────────────────
def test_angle_for_known_sector():
    assert "عقاري" in angle_for("real_estate_developer")
    assert "حفل" in angle_for("events")
    assert "RFQ" in angle_for("logistics") or "شحن" in angle_for("logistics")


def test_angle_for_unknown_falls_back():
    msg = angle_for("xyz_unknown")
    assert "Dealix" in msg


def test_select_top_n_diversified_caps_per_sector():
    candidates = [
        {"id": str(i), "sector": "real_estate", "total_score": 90 - i, "data_quality_score": 50}
        for i in range(20)
    ] + [
        {"id": f"l{i}", "sector": "logistics", "total_score": 60 - i, "data_quality_score": 40}
        for i in range(20)
    ]
    chosen = select_top_n_diversified(candidates, target_count=20)
    sectors = [c["sector"] for c in chosen]
    # Default cap = max(20//4, 10) = 10 per sector
    assert sectors.count("real_estate") <= 10
    assert sectors.count("logistics") <= 10
    assert len(chosen) == 20


def test_select_top_n_respects_total_count():
    candidates = [
        {"id": str(i), "sector": "logistics", "total_score": 100 - i, "data_quality_score": 50}
        for i in range(50)
    ]
    chosen = select_top_n_diversified(candidates, target_count=15)
    # default cap = max(15//4, 10) = 10. So we can pick 10 logistics, the rest none
    assert len(chosen) == 10  # bounded by cap, not target_count

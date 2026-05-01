"""Unit tests for Meeting Intelligence."""

from __future__ import annotations

from auto_client_acquisition.meeting_intelligence import (
    build_post_meeting_followup,
    build_pre_meeting_brief,
    compute_deal_risk,
    extract_objections,
    parse_transcript_entries,
    summarize_meeting,
)


# ── Transcript Parser ───────────────────────────────────────
def test_parser_handles_meet_entries():
    entries = [
        {"participantId": "alice", "text": "ما رأيكم في السعر؟"},
        {"participantId": "bob", "text": "السعر مرتفع لنا الآن."},
    ]
    p = parse_transcript_entries(entries)
    assert p["total_turns"] == 2
    assert "alice" in p["speakers"]


def test_parser_handles_plain_text():
    text = "Alice: مرحباً\nBob: السعر مرتفع لنا"
    p = parse_transcript_entries(text)
    assert p["total_turns"] == 2


def test_summarize_returns_arabic_summary():
    parsed = parse_transcript_entries([
        {"participantId": "a", "text": "نحتاج أن نفهم نموذج التسعير بشكل أوضح."},
        {"participantId": "b", "text": "ممتاز، أقترح اجتماع ثاني الأسبوع القادم."},
    ])
    s = summarize_meeting(parsed)
    assert s["approval_required"] is True
    assert any("اجتماع" in line or "نقاش" in line for line in s["summary_ar"])


# ── Brief ───────────────────────────────────────────────────
def test_brief_returns_six_sections():
    b = build_pre_meeting_brief(
        company={"name": "Acme", "sector": "saas"},
        contact={"name": "أحمد", "role": "VP"},
        opportunity={"expected_value_sar": 25_000},
    )
    assert b["company_name"] == "Acme"
    assert len(b["questions_ar"]) >= 5
    assert len(b["likely_objections_ar"]) >= 5
    assert b["approval_required"] is True


def test_brief_works_with_empty_input():
    b = build_pre_meeting_brief()
    assert b["company_name"] == "?"
    assert b["questions_ar"]


# ── Objection Extractor ─────────────────────────────────────
def test_extracts_price_objection():
    out = extract_objections("هذا الحل غالي ولا يناسب الميزانية.")
    cats = out["categories_found"]
    assert "price" in cats


def test_extracts_authority_objection():
    out = extract_objections("نحتاج موافقة المدير قبل أي قرار.")
    assert "authority" in out["categories_found"]


def test_no_objection_in_clean_text():
    out = extract_objections("اجتماع رائع، نتطلع للخطوة القادمة.")
    assert out["count"] == 0


# ── Followup Builder ────────────────────────────────────────
def test_followup_returns_email_and_whatsapp_drafts():
    out = build_post_meeting_followup(
        next_steps=["إرسال عرض السعر", "تحديد اجتماع ثانٍ"],
        contact_name="أحمد",
        company_name="Acme",
    )
    assert "email" in out["channel_drafts"]
    assert "whatsapp" in out["channel_drafts"]
    assert out["channel_drafts"]["email"]["live_send_allowed"] is False
    assert "أحمد" in out["channel_drafts"]["email"]["body_ar"]


def test_followup_addresses_objections():
    out = build_post_meeting_followup(
        next_steps=["متابعة"],
        contact_name="سارة",
        objections=[{"label_ar": "السعر/الميزانية"},
                    {"label_ar": "صاحب القرار"}],
    )
    assert "السعر" in out["channel_drafts"]["email"]["body_ar"]
    assert out["objections_addressed"]


# ── Deal Risk ───────────────────────────────────────────────
def test_high_risk_when_no_next_step_and_authority_objection():
    out = compute_deal_risk(
        objections=[{"category": "authority"}, {"category": "price"}],
        next_step_set=False,
        decision_maker_present=False,
    )
    assert out["risk_score"] >= 50
    assert out["risk_level"] in ("medium", "high")


def test_low_risk_with_clean_meeting():
    out = compute_deal_risk(
        objections=[],
        next_step_set=True,
        decision_maker_present=True,
        days_since_last_touch=0,
    )
    assert out["risk_level"] == "low"

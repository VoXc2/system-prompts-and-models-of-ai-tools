"""Smoke tests for signal detector + next-action engine + quota guard."""

from __future__ import annotations

import os

import pytest

from auto_client_acquisition.intelligence.next_action import (
    compute_priority, decide,
)
from auto_client_acquisition.intelligence.quota_guard import QuotaGuard
from auto_client_acquisition.intelligence.signals import (
    BuyingSignal, detect_signals, signals_to_intent_lift,
)


# ── Signal detector ───────────────────────────────────────────────
def test_signal_sector_urgency_high():
    sigs = detect_signals(sector="real_estate_developer")
    assert any(s.type == "sector_urgency" and "high" in s.value for s in sigs)


def test_signal_sector_urgency_medium():
    sigs = detect_signals(sector="restaurant")
    assert any(s.type == "sector_urgency" and "medium" in s.value for s in sigs)


def test_signal_whatsapp_detected():
    html = '<a href="https://wa.me/966500000000">WhatsApp us</a>'
    sigs = detect_signals(sector="restaurant", website_html=html)
    assert any(s.type == "whatsapp_button" for s in sigs)


def test_signal_booking_detected():
    html = '<a href="https://calendly.com/x">Book</a>'
    sigs = detect_signals(sector="hospitality", website_html=html)
    assert any(s.type == "booking_link" for s in sigs)


def test_signal_form_detected_arabic():
    html = "<form action='/contact'>تواصل معنا</form>"
    sigs = detect_signals(sector="real_estate", website_html=html)
    assert any(s.type == "website_form" for s in sigs)


def test_signal_crm_hubspot_detected():
    html = "<script src='https://js.hsforms.net/forms/v2.js'></script>"
    sigs = detect_signals(sector="saas", website_html=html)
    assert any(s.type == "crm_in_use" and s.value == "hubspot" for s in sigs)


def test_signal_payment_moyasar_detected():
    html = '<script src="https://cdn.moyasar.com/mpf/1.0.0/moyasar.js"></script>'
    sigs = detect_signals(sector="restaurant", website_html=html)
    assert any(s.type == "payment_mena" and s.value == "moyasar" for s in sigs)


def test_signal_ecom_salla_detected():
    html = '<link href="https://salla.sa/cdn/assets/x.css">'
    sigs = detect_signals(sector="restaurant", website_html=html)
    assert any(s.type == "ecom_mena" and s.value == "salla" for s in sigs)


def test_signal_ads_pixel_detected():
    html = '<script src="https://connect.facebook.net/en_US/fbevents.js"></script>'
    sigs = detect_signals(sector="real_estate", website_html=html)
    assert any(s.type == "ads_pixel" and s.value == "meta_pixel" for s in sigs)


def test_signal_high_review_count():
    sigs = detect_signals(sector="restaurant", google_reviews_count=350)
    assert any(s.type == "high_review_count" for s in sigs)


def test_signal_high_rating():
    sigs = detect_signals(
        sector="restaurant", google_rating=4.7, google_reviews_count=120,
    )
    assert any(s.type == "high_rating" for s in sigs)


def test_signal_multi_branch():
    sigs = detect_signals(sector="restaurant", branches_hint=4)
    assert any(s.type == "multi_branch" for s in sigs)


def test_signal_no_html_no_website_signals():
    sigs = detect_signals(sector="real_estate")
    types = {s.type for s in sigs}
    # only sector_urgency from sector alone
    assert "whatsapp_button" not in types
    assert "website_form" not in types


def test_intent_lift_from_signals_capped():
    sigs = [
        BuyingSignal("whatsapp_button", "x", 1.0, None, "rule"),
        BuyingSignal("booking_link", "x", 1.0, None, "rule"),
        BuyingSignal("website_form", "x", 1.0, None, "rule"),
        BuyingSignal("careers_hiring", "x", 1.0, None, "rule"),
        BuyingSignal("crm_in_use", "x", 1.0, None, "rule"),
        BuyingSignal("payment_mena", "x", 1.0, None, "rule"),
        BuyingSignal("ecom_mena", "x", 1.0, None, "rule"),
        BuyingSignal("multi_branch", "x", 1.0, None, "rule"),
        BuyingSignal("sector_urgency", "high:x", 1.0, None, "rule"),
        BuyingSignal("high_review_count", "x", 1.0, None, "rule"),
    ]
    lift = signals_to_intent_lift(sigs)
    assert lift == 30.0  # capped


def test_intent_lift_dedup_per_type():
    sigs = [
        BuyingSignal("whatsapp_button", "a", 1.0, None, "rule"),
        BuyingSignal("whatsapp_button", "b", 1.0, None, "rule"),
    ]
    lift = signals_to_intent_lift(sigs)
    # only one whatsapp_button counted
    assert lift == 4.0


# ── Priority formula ──────────────────────────────────────────────
def test_priority_weighted_formula():
    score = compute_priority(
        fit_score=40, intent_score=30, urgency_score=30,
        revenue_score=15, risk_score=0,
    )
    # 0.30*40 + 0.25*30 + 0.20*30 + 0.15*15 = 12 + 7.5 + 6 + 2.25 = 27.75
    assert score == 27.8


def test_priority_risk_subtracts():
    base = compute_priority(fit_score=40, intent_score=30, urgency_score=30,
                            revenue_score=15, risk_score=0)
    with_risk = compute_priority(fit_score=40, intent_score=30, urgency_score=30,
                                 revenue_score=15, risk_score=50)
    assert with_risk < base


def test_priority_clamped():
    # Negatives clamp to 0
    assert compute_priority(fit_score=0, intent_score=0, urgency_score=0,
                            revenue_score=0, risk_score=99) == 0


# ── Next-best-action ──────────────────────────────────────────────
def test_next_action_blocks_opt_out():
    na = decide(opt_out=True, has_business_email=True,
                allowed_use="business_contact_research_only")
    assert na.action == "block"
    assert na.priority_bucket == "BLOCKED"


def test_next_action_blocks_high_risk():
    na = decide(risk_score=80, has_business_email=True,
                allowed_use="business_contact_research_only")
    assert na.action == "block"
    assert "risk_score_too_high" in na.rationale


def test_next_action_blocks_no_allowed_use():
    na = decide(fit_score=40, intent_score=30, allowed_use=None,
                has_business_email=True)
    assert na.action == "block"
    assert na.rationale == "allowed_use_missing"


def test_next_action_p0_email_chooses_gmail():
    na = decide(
        fit_score=40, intent_score=30, urgency_score=30, revenue_score=15,
        risk_score=0, has_business_email=True, has_phone=True,
        allowed_use="business_contact_research_only",
    )
    # Score = 27.75 → P3 actually. Let me bump to ensure P0
    na2 = decide(
        fit_score=40, intent_score=30, urgency_score=30, revenue_score=15,
        risk_score=0, has_business_email=True,
        allowed_use="business_contact_research_only",
    )
    assert na2.priority_score == 27.8
    # That's P3 → wait_followup
    # Try a higher mix to land in P0
    na3 = decide(
        fit_score=200, intent_score=200, urgency_score=200, revenue_score=200,
        risk_score=0, has_business_email=True,
        allowed_use="business_contact_research_only",
    )
    # All clamped to 100 → score = 0.30+0.25+0.20+0.15 = 0.9 * 100 = 90
    assert na3.priority_bucket == "P0"
    assert na3.action == "gmail_draft"


def test_next_action_partner_path():
    na = decide(
        fit_score=80, intent_score=60, urgency_score=40, revenue_score=20,
        risk_score=0, has_business_email=True, is_potential_partner=True,
        allowed_use="business_contact_research_only",
    )
    assert na.action == "partner_intro"


def test_next_action_p2_with_linkedin():
    na = decide(
        fit_score=50, intent_score=40, urgency_score=20, revenue_score=10,
        risk_score=0, has_linkedin_handle=True, has_business_email=False,
        has_phone=False,
        allowed_use="business_contact_research_only",
    )
    # 0.30*50 + 0.25*40 + 0.20*20 + 0.15*10 - 0 = 15 + 10 + 4 + 1.5 = 30.5 → P2
    assert na.priority_bucket == "P2"
    assert na.action == "linkedin_manual"


def test_next_action_p3_waits():
    na = decide(
        fit_score=10, intent_score=10, urgency_score=10, revenue_score=10,
        risk_score=0, has_business_email=True,
        allowed_use="business_contact_research_only",
    )
    assert na.priority_bucket == "P3"
    assert na.action == "wait_followup"


# ── Quota guard ───────────────────────────────────────────────────
def test_quota_guard_consume_until_limit():
    g = QuotaGuard()
    # Set a low limit via env
    os.environ["DEALIX_QUOTA_GOOGLE_SEARCH_DAILY"] = "3"
    try:
        assert g.consume("google_search") is True
        assert g.consume("google_search") is True
        assert g.consume("google_search") is True
        # 4th call hits cap
        assert g.consume("google_search") is False
        assert g.remaining("google_search") == 0
    finally:
        os.environ.pop("DEALIX_QUOTA_GOOGLE_SEARCH_DAILY", None)


def test_quota_guard_status_shape():
    g = QuotaGuard()
    s = g.status()
    assert "providers" in s
    assert "google_search" in s["providers"]
    assert {"used", "limit", "remaining"} <= set(s["providers"]["google_search"].keys())


def test_quota_guard_independent_providers():
    g = QuotaGuard()
    os.environ["DEALIX_QUOTA_GROQ_DAILY"] = "2"
    try:
        assert g.consume("groq") is True
        assert g.consume("groq") is True
        assert g.consume("groq") is False
        # Other providers unaffected
        assert g.consume("google_search") is True
    finally:
        os.environ.pop("DEALIX_QUOTA_GROQ_DAILY", None)

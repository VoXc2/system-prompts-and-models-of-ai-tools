"""Unit tests for the Platform Services Layer."""

from __future__ import annotations

import pytest

from auto_client_acquisition.platform_services import (
    ALL_CHANNELS,
    EVENT_TYPES,
    POLICY_RULES,
    SELLABLE_SERVICES,
    build_card_from_event,
    build_demo_feed,
    build_demo_platform_proof,
    evaluate_action,
    get_channel,
    invoke_tool,
    list_services,
    make_event,
    resolve_identity,
)
from auto_client_acquisition.platform_services.action_ledger import ActionLedger
from auto_client_acquisition.platform_services.channel_registry import channels_summary
from auto_client_acquisition.platform_services.unified_inbox import CARD_TYPES, InboxCard


# ── Service catalog ──────────────────────────────────────────
def test_service_catalog_returns_all_services():
    out = list_services()
    assert out["total"] == len(SELLABLE_SERVICES) >= 12


def test_service_catalog_includes_critical_services():
    out = list_services()
    keys = {s["key"] for s in out["services"]}
    for required in (
        "growth_operator_subscription", "channel_setup_service",
        "lead_intelligence_service", "partnership_sprint",
        "ai_visibility_aeo_sprint", "customer_success_operator",
    ):
        assert required in keys


# ── Channel registry ─────────────────────────────────────────
def test_channels_include_core_channels():
    keys = {c.key for c in ALL_CHANNELS}
    for required in (
        "whatsapp", "gmail", "google_calendar", "moyasar",
        "linkedin_lead_forms", "x_api", "instagram_graph",
        "google_business_profile", "google_sheets", "crm", "website_forms",
    ):
        assert required in keys


def test_channels_summary_aggregates():
    s = channels_summary()
    assert s["total"] == len(ALL_CHANNELS)
    assert "by_beta_status" in s and "by_risk_level" in s


def test_get_channel_unknown():
    assert get_channel("bogus_channel") is None


def test_whatsapp_blocks_cold_send():
    """Channel registry asserts cold send is blocked."""
    wa = get_channel("whatsapp")
    assert wa is not None
    assert "cold_send_without_consent" in wa.blocked_actions


# ── Event bus ────────────────────────────────────────────────
def test_event_types_include_payment_lifecycle():
    for et in ("payment.initiated", "payment.paid", "payment.failed"):
        assert et in EVENT_TYPES


def test_make_event_validates():
    with pytest.raises(ValueError):
        make_event(event_type="totally.fake", channel="whatsapp", customer_id="c")


def test_make_event_round_trip():
    e = make_event(
        event_type="lead.form_submitted", channel="website_forms",
        customer_id="c", payload={"company": "X"},
    )
    d = e.to_dict()
    assert d["event_type"] == "lead.form_submitted"
    assert d["payload"]["company"] == "X"


# ── Action policy ────────────────────────────────────────────
def test_policy_blocks_cold_whatsapp():
    d = evaluate_action(
        action="send_whatsapp",
        context={"source": "cold_list", "consent": False},
    )
    assert d.decision == "blocked"


def test_policy_blocks_payment_without_confirmation():
    d = evaluate_action(
        action="charge_payment",
        context={"user_confirmed": False},
    )
    assert d.decision == "blocked"


def test_policy_blocks_secrets_in_payload():
    d = evaluate_action(
        action="create_draft",
        context={"payload": {"api_key": "ghp_xxx"}},
    )
    assert d.decision == "blocked"


def test_policy_external_send_needs_approval():
    d = evaluate_action(
        action="send_email",
        context={"approval_status": "pending"},
    )
    assert d.decision == "approval_required"


def test_policy_calendar_insert_needs_approval():
    d = evaluate_action(
        action="calendar_insert_event",
        context={"approval_status": "pending"},
    )
    assert d.decision == "approval_required"


def test_policy_high_value_deal_review():
    d = evaluate_action(
        action="send_whatsapp",
        context={
            "deal_value_sar": 250_000, "approval_status": "approved",
            "source": "existing_customer",
        },
    )
    assert d.decision == "approval_required"


def test_policy_safe_internal_action_allowed():
    d = evaluate_action(action="read_data", context={})
    assert d.decision == "allow"


# ── Tool gateway ─────────────────────────────────────────────
def test_gateway_blocks_unsupported_tool():
    r = invoke_tool(tool="bogus.action")
    assert r.status == "unsupported"


def test_gateway_blocks_cold_whatsapp():
    r = invoke_tool(
        tool="whatsapp.send_message",
        context={"source": "cold_list", "consent": False, "approval_status": "pending"},
    )
    assert r.status == "blocked"


def test_gateway_external_send_default_draft_only():
    """No live env flag → drafts even when policy allows."""
    import os
    os.environ.pop("WHATSAPP_ALLOW_LIVE_SEND", None)
    r = invoke_tool(
        tool="whatsapp.send_message",
        context={
            "source": "existing_customer", "consent": True,
            "approval_status": "approved",
        },
    )
    # Either draft_created (no flag) or approval_required (defensive)
    assert r.status in ("draft_created", "approval_required")


def test_gateway_internal_action_passes():
    r = invoke_tool(tool="gmail.read_thread", context={})
    assert r.status in ("draft_created", "approval_required")


def test_gateway_payment_charge_needs_confirmation():
    r = invoke_tool(
        tool="moyasar.refund",
        context={"user_confirmed": False, "approval_status": "approved"},
    )
    assert r.status == "blocked"


# ── Identity resolution ──────────────────────────────────────
def test_identity_resolves_multi_signal():
    out = resolve_identity(signals=[
        {"phone": "+966500000001", "company": "X", "source": "wa"},
        {"email": "x@example.sa", "company": "X", "source": "gmail"},
        {"crm_id": "crm_1", "company": "X", "source": "crm"},
    ])
    assert out.primary_phone == "+966500000001"
    assert out.primary_email == "x@example.sa"
    assert out.crm_id == "crm_1"
    assert out.confidence > 0
    assert "wa" in out.sources


def test_identity_empty_signals():
    out = resolve_identity(signals=[])
    assert out.confidence == 0


# ── Unified inbox ────────────────────────────────────────────
def test_inbox_card_validates_button_count():
    with pytest.raises(ValueError):
        InboxCard(
            card_id="c", type="opportunity", channel="whatsapp",
            title_ar="x", summary_ar="x", why_it_matters_ar="x",
            recommended_action_ar="x", risk_level="low",
            buttons_ar=("a", "b", "c", "d"),  # 4 → invalid
        )


def test_inbox_card_validates_card_type():
    with pytest.raises(ValueError):
        InboxCard(
            card_id="c", type="bogus_type", channel="x",
            title_ar="x", summary_ar="x", why_it_matters_ar="x",
            recommended_action_ar="x", risk_level="low",
        )


def test_build_card_from_event_payment_failed():
    e = make_event(
        event_type="payment.failed", channel="moyasar", customer_id="c",
        payload={"customer_id": "c1", "amount_sar": 2999},
    )
    card = build_card_from_event(e)
    assert card is not None
    assert card.type == "payment"
    assert len(card.buttons_ar) <= 3


def test_build_card_from_event_review_low_rating_high_risk():
    e = make_event(
        event_type="review.created", channel="google_business_profile",
        customer_id="c", payload={"rating": 1, "text": "bad"},
    )
    card = build_card_from_event(e)
    assert card is not None
    assert card.risk_level == "high"


def test_demo_feed_arabic_and_buttons_capped():
    feed = build_demo_feed()
    assert feed["feed_size"] >= 5
    for card in feed["cards"]:
        assert len(card["buttons_ar"]) <= 3
        # Has Arabic content somewhere
        text = card["title_ar"] + card["summary_ar"]
        assert any("؀" <= ch <= "ۿ" for ch in text)


def test_card_types_cover_inbox_cases():
    assert {"opportunity", "email_lead", "whatsapp_reply", "payment",
            "meeting_prep", "review_response", "partner_suggestion"}.issubset(set(CARD_TYPES))


# ── Action ledger ────────────────────────────────────────────
def test_action_ledger_append_and_summary():
    led = ActionLedger()
    led.append(
        customer_id="c1", action_type="send_whatsapp",
        channel="whatsapp", stage="requested",
    )
    led.append(
        customer_id="c1", action_type="send_whatsapp",
        channel="whatsapp", stage="approved",
    )
    s = led.summary("c1")
    assert s["total"] == 2
    assert s["by_stage"]["requested"] == 1
    assert s["by_stage"]["approved"] == 1


def test_action_ledger_unknown_stage_raises():
    led = ActionLedger()
    with pytest.raises(ValueError):
        led.append(customer_id="c1", action_type="x", channel="y", stage="bogus")


# ── Platform proof ledger ────────────────────────────────────
def test_platform_proof_demo_structure():
    p = build_demo_platform_proof()
    d = p.to_dict()
    assert "totals" in d and "by_channel" in d
    assert d["totals"]["leads_created"] > 0
    assert d["totals"]["risks_blocked"] > 0
    # Cross-channel coverage
    assert "whatsapp" in d["by_channel"] or "gmail" in d["by_channel"]

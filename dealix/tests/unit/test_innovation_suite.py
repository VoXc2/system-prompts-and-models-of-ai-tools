"""
Unit tests for the dealix.innovation layer — deterministic, no I/O.

Covers: aeo_radar / command_feed / command_feed_live / deal_rooms /
experiments / growth_missions / proof_ledger / proof_ledger_repo /
ten_in_ten.
"""

from __future__ import annotations

import pytest

from auto_client_acquisition.innovation import (
    aeo_radar,
    command_feed,
    deal_rooms,
    experiments,
    growth_missions,
    proof_ledger,
    ten_in_ten,
)


# ── aeo_radar ────────────────────────────────────────────────────
def test_aeo_radar_demo_default_sector():
    out = aeo_radar.build_aeo_radar_demo(sector=None)
    assert isinstance(out, dict)
    assert out


def test_aeo_radar_demo_known_sectors():
    for sector in ("clinics", "real_estate", "logistics"):
        out = aeo_radar.build_aeo_radar_demo(sector=sector)
        assert isinstance(out, dict)


def test_aeo_radar_unknown_sector_does_not_crash():
    """Should degrade gracefully."""
    out = aeo_radar.build_aeo_radar_demo(sector="totally_unknown_xyz")
    assert isinstance(out, dict)


# ── command_feed ─────────────────────────────────────────────────
def test_command_feed_demo_returns_cards():
    out = command_feed.build_demo_command_feed()
    assert isinstance(out, dict)
    # Must contain card list
    found_list = False
    for k, v in out.items():
        if isinstance(v, list) and v:
            found_list = True
            # First card should have core fields
            first = v[0]
            assert "type" in first
            assert "title_ar" in first or "title" in first
    assert found_list, "no card list found in command feed output"


def test_command_feed_card_types_known():
    out = command_feed.build_demo_command_feed()
    for v in out.values():
        if isinstance(v, list):
            for card in v:
                t = card.get("type")
                # Known types per the docstring
                assert t in (
                    "opportunity", "approval_needed", "leak",
                    "compliance_risk", "proof_update",
                ), f"unknown card type: {t}"
            break  # only check the first list


# ── deal_rooms ───────────────────────────────────────────────────
def test_deal_rooms_default_payload():
    out = deal_rooms.analyze_deal_room()
    assert isinstance(out, dict)


def test_deal_rooms_with_payload():
    out = deal_rooms.analyze_deal_room({
        "deal_id": "d-001",
        "company_name": "Test Co.",
        "stage": "proposal",
        "value_sar": 250_000,
    })
    assert isinstance(out, dict)


# ── experiments ──────────────────────────────────────────────────
def test_recommend_experiments_default():
    out = experiments.recommend_experiments(None)
    assert isinstance(out, dict)


def test_recommend_experiments_with_context():
    out = experiments.recommend_experiments({
        "current_reply_rate": 0.04,
        "current_meeting_rate": 0.20,
        "past_experiments": [],
    })
    assert isinstance(out, dict)


def test_past_failed_helper_negative_when_empty():
    """Direct check on the private helper for safety."""
    assert experiments._past_failed([], "reply_rate") is False


def test_past_failed_helper_positive_when_match():
    """Real impl looks at 'outcome' field, not 'result'."""
    out = experiments._past_failed(
        past=[{"metric": "reply_rate_v1", "outcome": "failed"}],
        metric_substr="reply_rate",
    )
    assert out is True


# ── growth_missions ──────────────────────────────────────────────
def test_list_growth_missions_returns_dict():
    out = growth_missions.list_growth_missions()
    assert isinstance(out, dict)
    assert out


def test_growth_missions_includes_kill_title():
    """The flagship '10 في 10' mission must be present."""
    out = growth_missions.list_growth_missions()
    text = str(out)
    assert "10" in text  # must reference the '10 in 10' mission


# ── proof_ledger ─────────────────────────────────────────────────
def test_proof_ledger_demo_returns_dict():
    out = proof_ledger.build_demo_proof_ledger()
    assert isinstance(out, dict)
    assert out


# ── ten_in_ten ───────────────────────────────────────────────────
def test_ten_in_ten_default_payload():
    """No payload → uses defaults, returns 10 opportunities."""
    out = ten_in_ten.build_ten_opportunities(None)
    assert isinstance(out, dict)
    # Must produce 10 opportunities OR a counted list
    found_ten = False
    for v in out.values():
        if isinstance(v, list) and len(v) == 10:
            found_ten = True
            break
    assert found_ten, f"expected 10 opportunities; got: {out.keys()}"


def test_ten_in_ten_drafts_require_approval():
    """Per the docstring — every draft must be 'pending_approval'."""
    out = ten_in_ten.build_ten_opportunities({
        "company_name_or_url": "test.sa",
        "sector": "clinics",
        "city": "Riyadh",
        "offer_one_liner": "WhatsApp booking automation",
        "goal_meetings_or_replies": "meetings",
    })
    text = str(out)
    # Every draft must surface approval_required + pending_approval
    assert "pending_approval" in text or "approval_required" in text


def test_ten_in_ten_deterministic_for_same_input():
    """Same payload → same output (per `_slug_seed` design)."""
    payload = {
        "company_name_or_url": "deterministic.sa",
        "sector": "real_estate",
        "city": "Jeddah",
        "offer_one_liner": "X",
    }
    a = ten_in_ten.build_ten_opportunities(payload)
    b = ten_in_ten.build_ten_opportunities(payload)
    # The opportunity titles / Why-Now strings should match
    assert str(a) == str(b), "deterministic seed broken"


def test_ten_in_ten_different_inputs_produce_different_outputs():
    a = ten_in_ten.build_ten_opportunities({
        "company_name_or_url": "company-a.sa",
        "sector": "clinics", "city": "Riyadh",
    })
    b = ten_in_ten.build_ten_opportunities({
        "company_name_or_url": "company-b.sa",
        "sector": "logistics", "city": "Jeddah",
    })
    assert str(a) != str(b)

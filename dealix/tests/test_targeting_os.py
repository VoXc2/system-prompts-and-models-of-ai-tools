"""Targeting OS — policy, LinkedIn compliance, no live actions."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from api.main import create_app
from auto_client_acquisition.targeting_os.contactability_matrix import evaluate_contactability
from auto_client_acquisition.targeting_os.linkedin_strategy import recommend_linkedin_strategy
from auto_client_acquisition.targeting_os.reputation_guard import should_pause_channel


def test_linkedin_strategy_no_scrape_no_auto_dm() -> None:
    r = recommend_linkedin_strategy("b2b", "leads")
    dnd = r.get("do_not_do") or []
    assert "scraping_profiles" in dnd
    assert "auto_dm" in dnd


def test_opt_out_blocked() -> None:
    ev = evaluate_contactability({"source": "inbound_lead", "opted_out": True, "email": "a@b.co"})
    assert ev["status"] == "blocked"


def test_unknown_source_needs_review() -> None:
    ev = evaluate_contactability({"source": "unknown", "email": "a@b.co", "phone": "+966501234567"})
    assert ev["status"] == "needs_review"


def test_cold_whatsapp_blocked() -> None:
    ev = evaluate_contactability(
        {"source": "inbound_lead", "phone": "+966501234567", "cold_whatsapp": True},
    )
    assert ev["status"] == "blocked"


def test_scraped_source_blocked() -> None:
    ev = evaluate_contactability({"source": "scraped", "email": "x@y.com"})
    assert ev["status"] == "blocked"


def test_buying_committee_has_roles() -> None:
    from auto_client_acquisition.targeting_os.buyer_role_mapper import map_buying_committee

    m = map_buying_committee("training", "smb", "book_more_b2b_meetings")
    assert m["primary_decision_makers"]


def test_outreach_plan_requires_approval() -> None:
    from auto_client_acquisition.targeting_os.outreach_scheduler import build_outreach_plan

    p = build_outreach_plan([{"id": "1"}], ["email"], "growth")
    assert all(s.get("approval_required") for s in p.get("steps", []))


def test_reputation_guard_pauses_bad_channel() -> None:
    bad = {"bounce_rate": 0.2, "opt_out_rate": 0.05, "complaint_rate": 0.01, "reply_rate": 0.0}
    assert should_pause_channel(bad) is True


def test_free_diagnostic_three_opportunities() -> None:
    from auto_client_acquisition.targeting_os.free_diagnostic import build_free_growth_diagnostic

    d = build_free_growth_diagnostic({"sector": "saas", "city": "الرياض"})
    assert len(d.get("opportunities") or []) <= 3


def test_contract_templates_require_legal_review() -> None:
    from auto_client_acquisition.targeting_os.contract_drafts import draft_pilot_agreement_outline

    o = draft_pilot_agreement_outline()
    assert o.get("legal_review_required") is True


@pytest.fixture()
def client() -> TestClient:
    return TestClient(create_app())


def test_targeting_routes(client: TestClient) -> None:
    r = client.post("/api/v1/targeting/accounts/recommend", json={"sector": "training", "city": "الرياض", "offer": "x", "goal": "g"})
    assert r.status_code == 200
    assert r.json().get("count", 0) >= 1

    m = client.post("/api/v1/targeting/buying-committee/map", json={"sector": "training"})
    assert m.status_code == 200

    ev = client.post(
        "/api/v1/targeting/contacts/evaluate",
        json={"contact": {"source": "website_form", "email": "a@b.co", "opt_in_status": "explicit"}},
    )
    assert ev.status_code == 200

    lg = client.post("/api/v1/targeting/linkedin/strategy", json={"segment": "b2b", "goal": "leads", "include_lead_gen_plan": True})
    assert lg.status_code == 200
    assert "do_not_do" in lg.json()

    sv = client.get("/api/v1/targeting/services")
    assert sv.status_code == 200
    assert sv.json().get("count", 0) >= 1

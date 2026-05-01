"""طبقة الابتكار — دوال ومسارات API."""

from __future__ import annotations

import pytest

from auto_client_acquisition.innovation import (
    analyze_deal_room,
    build_demo_command_feed,
    build_demo_proof_ledger,
    list_growth_missions,
    recommend_experiments,
)
from auto_client_acquisition.innovation.aeo_radar import build_aeo_radar_demo
from auto_client_acquisition.innovation.ten_in_ten import build_ten_opportunities


def test_build_demo_command_feed_card_types() -> None:
    data = build_demo_command_feed()
    assert "cards" in data
    cards = data["cards"]
    assert isinstance(cards, list)
    types = {c["type"] for c in cards}
    assert types == {"opportunity", "approval_needed", "leak", "compliance_risk", "proof_update"}
    for c in cards:
        for key in ("title_ar", "why", "risk", "suggested_action", "cta"):
            assert key in c


def test_list_growth_missions_kill_feature() -> None:
    data = list_growth_missions()
    assert "missions" in data
    titles = [m["title_ar"] for m in data["missions"]]
    assert "10 فرص في 10 دقائق" in titles
    kill = next(m for m in data["missions"] if m.get("is_kill_feature"))
    assert kill["id"] == "ten_opps_ten_minutes"


def test_recommend_experiments_shape() -> None:
    data = recommend_experiments({"sector": "صحة", "focus": "growth"})
    assert "experiments" in data
    assert len(data["experiments"]) == 3
    for ex in data["experiments"]:
        for key in ("hypothesis", "metric", "action", "risk", "horizon_days"):
            assert key in ex
        assert ex["horizon_days"] == 30


def test_recommend_experiments_past_failures_adapt() -> None:
    data = recommend_experiments(
        {
            "past_experiments": [
                {"metric": "reply_rate_7d", "outcome": "failed"},
                {"metric": "meetings_booked_per_100_outreach", "outcome": "failure"},
            ]
        }
    )
    notes = data["context_echo"].get("adaptation_notes", [])
    assert "past_reply_rate_failure" in notes
    assert "past_meetings_failure" in notes
    assert data["experiments"][0]["metric"] == "reply_rate_7d"


def test_build_ten_opportunities() -> None:
    out = build_ten_opportunities(
        {
            "company_name_or_url": "شركة تجريب",
            "sector": "clinics",
            "city": "Riyadh",
            "offer_one_liner": "أتمتة متابعة العملاء",
            "goal_meetings_or_replies": "اجتماعان",
        }
    )
    assert out["count"] == 10
    assert out["approval_required"] is True
    assert out["no_outbound_sent"] is True
    assert all(o["approval_status"] == "pending_approval" for o in out["opportunities"])


def test_aeo_radar_demo() -> None:
    d = build_aeo_radar_demo("clinics")
    assert d["sector_key"] == "clinics"
    assert d["no_live_search"] is True
    assert "content_gaps" in d


def test_proof_ledger_events() -> None:
    data = build_demo_proof_ledger()
    assert "events" in data
    for ev in data["events"]:
        for key in ("event_type", "ts", "revenue_influenced_sar_estimate", "notes_ar"):
            assert key in ev


def test_analyze_deal_room_keys() -> None:
    out = analyze_deal_room(
        {"deal_id": "x-1", "stage": "proposal", "notes": "طلب تأجيل أسبوع", "budget_range": "50-100k"}
    )
    assert out["deal_id"] == "x-1"
    assert isinstance(out["risk_score"], int)
    assert 0 <= out["risk_score"] <= 100
    assert isinstance(out["missing_info"], list)
    assert isinstance(out["next_action_ar"], str)
    assert isinstance(out["stakeholders_hint"], list)


@pytest.mark.asyncio
async def test_innovation_routes(async_client) -> None:
    r = await async_client.get("/api/v1/innovation/command-feed/demo")
    assert r.status_code == 200
    body = r.json()
    assert "cards" in body

    r = await async_client.get("/api/v1/innovation/growth-missions")
    assert r.status_code == 200
    assert "10 فرص في 10 دقائق" in str(r.json())

    r = await async_client.post("/api/v1/innovation/experiments/recommend", json={})
    assert r.status_code == 200
    assert len(r.json()["experiments"]) == 3

    r = await async_client.get("/api/v1/innovation/proof-ledger/demo")
    assert r.status_code == 200
    assert r.json()["events"]

    r = await async_client.post("/api/v1/innovation/deal-room/analyze", json={"deal_id": "api-test"})
    assert r.status_code == 200
    assert "risk_score" in r.json()

    r = await async_client.post(
        "/api/v1/innovation/opportunities/ten-in-ten",
        json={"company": "TestCo", "sector": "logistics", "city": "Jeddah"},
    )
    assert r.status_code == 200
    body = r.json()
    assert body["count"] == 10

    r = await async_client.get("/api/v1/innovation/aeo/radar/demo?sector=real_estate")
    assert r.status_code == 200
    assert r.json()["sector_key"] == "real_estate"

    r = await async_client.get("/api/v1/innovation/command-feed/live")
    assert r.status_code == 200
    cf = r.json()
    assert "cards" in cf
    assert cf.get("source") in ("demo_fallback", "database")

    r = await async_client.post(
        "/api/v1/innovation/proof-ledger/events",
        json={
            "tenant_id": "test-tenant",
            "event_type": "positive_reply",
            "revenue_influenced_sar_estimate": 5000,
            "notes_ar": "رد تجريبي",
        },
    )
    assert r.status_code == 200
    assert r.json()["id"]

    r = await async_client.get("/api/v1/innovation/proof-ledger/events?tenant_id=test-tenant")
    assert r.status_code == 200
    assert len(r.json()["events"]) >= 1

    r = await async_client.get("/api/v1/innovation/proof-ledger/report/week?tenant_id=test-tenant")
    assert r.status_code == 200
    rep = r.json()
    assert rep["window_days"] == 7
    assert "disclaimer_ar" in rep

    r = await async_client.post(
        "/api/v1/innovation/experiments/recommend",
        json={"past_experiments": [{"metric": "approval_rate_first_pass", "outcome": "fail"}]},
    )
    assert r.status_code == 200
    assert "past_approval_failure" in r.json()["context_echo"].get("adaptation_notes", [])


@pytest.mark.asyncio
async def test_root_lists_innovation_link(async_client) -> None:
    r = await async_client.get("/")
    assert r.status_code == 200
    assert r.json().get("innovation_command_feed_demo") == "/api/v1/innovation/command-feed/demo"

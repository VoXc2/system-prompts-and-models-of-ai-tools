"""Tests for Revenue Company OS — cards, RWU, weekly loop."""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from api.main import create_app
from auto_client_acquisition.revenue_company_os.event_to_card import event_to_card
from auto_client_acquisition.revenue_company_os.revenue_work_units import demo_work_units
from auto_client_acquisition.revenue_company_os.self_improvement_loop import weekly_growth_curator_report_ar


def test_event_card_arabic_three_buttons_max() -> None:
    card = event_to_card("email.received", {"from": "a@b.com"})
    assert "title_ar" in card
    buttons = card.get("buttons_ar") or []
    assert len(buttons) <= 3


def test_revenue_work_units_generated() -> None:
    data = demo_work_units()
    assert len(data["work_units"]) >= 1
    assert data["work_units"][0].get("unit_id")


def test_self_improvement_report_recommendations() -> None:
    rep = weekly_growth_curator_report_ar()
    assert "weekly_growth_curator_report_ar" in rep
    assert rep.get("service_improvement_backlog")


@pytest.mark.asyncio
async def test_company_os_command_feed_demo() -> None:
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.get("/api/v1/revenue-os/company-os/command-feed/demo")
    assert r.status_code == 200
    body = r.json()
    assert "cards" in body
    assert len(body["cards"]) >= 5


@pytest.mark.asyncio
async def test_company_os_events_ingest_post() -> None:
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.post(
            "/api/v1/revenue-os/company-os/events/ingest",
            json={"type": "risk.blocked", "payload": {"reason": "cold_whatsapp"}},
        )
    assert r.status_code == 200
    card = r.json()["card"]
    assert card.get("event_type") == "risk.blocked"
    assert len(card.get("buttons_ar") or []) <= 3

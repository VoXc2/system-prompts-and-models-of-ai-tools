"""Tests for customer_ops package and API router."""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from api.main import create_app
from auto_client_acquisition.customer_ops.connector_setup_status import build_connector_status
from auto_client_acquisition.customer_ops.onboarding_checklist import build_onboarding_checklist
from auto_client_acquisition.customer_ops.support_ticket_router import route_ticket


def test_onboarding_has_steps_and_approval() -> None:
    d = build_onboarding_checklist("first_10_opportunities")
    assert d["service_id"] == "first_10_opportunities"
    assert isinstance(d["steps_ar"], list)
    assert len(d["steps_ar"]) >= 5
    assert d["approval_required"] is True
    assert d["live_send_default"] is False


def test_connectors_status_lists_whatsapp_gmail() -> None:
    d = build_connector_status()
    ids = [c["id"] for c in d["connectors"]]
    assert "whatsapp" in ids
    assert "gmail" in ids


def test_route_ticket_p0_on_send_keyword() -> None:
    r = route_ticket("حصل إرسال live بالخطأ")
    assert r["priority"] == "P0"


@pytest.mark.asyncio
async def test_customer_ops_endpoints() -> None:
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.get("/api/v1/customer-ops/onboarding/checklist")
        assert r.status_code == 200
        assert r.json().get("approval_required") is True
        r2 = await client.get("/api/v1/customer-ops/support/sla")
        assert r2.status_code == 200
        assert "tiers" in r2.json()
        r3 = await client.get("/api/v1/customer-ops/connectors/status")
        assert r3.status_code == 200
        r4 = await client.post("/api/v1/customer-ops/support/route", json={"issue_ar": "خطأ في النظام"})
        assert r4.status_code == 200
        assert r4.json().get("priority") in {"P0", "P1", "P2", "P3"}

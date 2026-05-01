"""Tests for revenue_launch package and API — deterministic, no live actions."""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from api.main import create_app
from auto_client_acquisition.revenue_launch.offer_builder import (
    build_499_pilot_offer,
    build_growth_os_pilot_offer,
)
from auto_client_acquisition.revenue_launch.payment_manual_flow import build_moyasar_invoice_instructions
from auto_client_acquisition.revenue_launch.pipeline_tracker import STAGES, build_pipeline_schema


@pytest.mark.asyncio
async def test_revenue_launch_offer_endpoint() -> None:
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r = await client.get("/api/v1/revenue-launch/offer")
    assert r.status_code == 200
    data = r.json()
    assert data.get("no_live_charge") is True
    assert data.get("no_live_send") is True
    assert data.get("locale") == "ar"
    assert data["pilot_499"]["price_sar"] == 499
    assert "title_en" not in data["pilot_499"]


@pytest.mark.asyncio
async def test_revenue_launch_offer_lang_en_adds_english_labels() -> None:
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r = await client.get("/api/v1/revenue-launch/offer?lang=en")
    assert r.status_code == 200
    data = r.json()
    assert data["locale"] == "en"
    assert data["pilot_499"]["title_ar"]
    assert data["pilot_499"]["title_en"] == "Pilot — 7 days (499 SAR)"
    assert "summary_en" in data["pilot_499"]


@pytest.mark.asyncio
async def test_revenue_launch_payment_manual_no_charge() -> None:
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r = await client.get("/api/v1/revenue-launch/payment/manual-flow")
    assert r.status_code == 200
    body = r.json()
    assert body.get("no_live_charge") is True
    inst = body["instructions"]
    assert inst.get("no_live_charge") is True
    assert inst.get("manual_or_dashboard_only") is True


@pytest.mark.asyncio
async def test_revenue_launch_demo_flow_12_minutes() -> None:
    app = create_app()
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r = await client.get("/api/v1/revenue-launch/demo-flow")
    assert r.status_code == 200
    flow = r.json()["flow"]
    assert flow["duration_minutes"] == 12
    assert len(flow["steps_ar"]) >= 5


def test_499_offer_exists() -> None:
    o = build_499_pilot_offer()
    assert o["price_sar"] == 499
    assert o.get("no_live_send") is True


def test_growth_os_pilot_range() -> None:
    o = build_growth_os_pilot_offer()
    assert o["price_range_sar"]["min"] == 1500
    assert o["price_range_sar"]["max"] == 3000


def test_pipeline_stages() -> None:
    schema = build_pipeline_schema()
    assert schema["stages"] == STAGES
    assert "paid" in STAGES


def test_proof_pack_template_endpoint() -> None:
    # sync check via module
    from auto_client_acquisition.revenue_launch.proof_pack_template import build_private_beta_proof_pack

    p = build_private_beta_proof_pack()
    assert "sections_ar" in p
    assert p.get("demo") is True


def test_moyasar_instructions_no_live_charge() -> None:
    m = build_moyasar_invoice_instructions()
    assert m["no_live_charge"] is True


def test_openapi_includes_revenue_launch_paths() -> None:
    app = create_app()
    paths = app.openapi()["paths"]
    assert "/api/v1/revenue-launch/offer" in paths
    assert "/api/v1/revenue-launch/payment/manual-flow" in paths

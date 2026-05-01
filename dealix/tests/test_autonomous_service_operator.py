"""Tests for Autonomous Service Operator — intents, bundles, safe tools."""

from __future__ import annotations

import pytest
from httpx import ASGITransport, AsyncClient

from api.main import create_app
from auto_client_acquisition.autonomous_service_operator import intent_classifier as ic
from auto_client_acquisition.autonomous_service_operator import service_orchestrator as so
from auto_client_acquisition.autonomous_service_operator import tool_action_planner as tap
from auto_client_acquisition.autonomous_service_operator.proof_pack_dispatcher import build_proof_pack
from auto_client_acquisition.autonomous_service_operator.service_bundles import list_bundles
from auto_client_acquisition.service_excellence.service_scoring import calculate_service_excellence_score


def test_want_more_customers_recommends_first_10() -> None:
    r = so.recommend_for_intent(ic.INTENT_WANT_MORE_CUSTOMERS)
    assert r["recommended_service_id"] == "first_10_opportunities"


def test_has_contact_list_recommends_list_intelligence() -> None:
    r = so.recommend_for_intent(ic.INTENT_HAS_CONTACT_LIST)
    assert r["recommended_service_id"] == "list_intelligence"


def test_partnerships_recommends_partner_sprint() -> None:
    r = so.recommend_for_intent(ic.INTENT_WANT_PARTNERSHIPS)
    assert r["recommended_service_id"] == "partner_sprint"


def test_classify_ar_training_company() -> None:
    msg = "أبغى عملاء أكثر لشركة تدريب في الرياض"
    assert ic.classify_intent(msg) == ic.INTENT_WANT_MORE_CUSTOMERS


def test_classify_contact_list() -> None:
    assert ic.classify_intent("عندي قائمة أرقام") == ic.INTENT_HAS_CONTACT_LIST


def test_classify_partnerships() -> None:
    assert ic.classify_intent("أبغى شراكات") == ic.INTENT_WANT_PARTNERSHIPS


def test_cold_whatsapp_blocked_response() -> None:
    msg = "أبغى أرسل واتساب بارد"
    assert ic.classify_intent(msg) == ic.INTENT_COLD_WHATSAPP_REQUEST
    body = so.cold_whatsapp_response()
    assert body["blocked"] is True


def test_ask_services_bundles_list() -> None:
    data = list_bundles()
    assert data["demo"] is True
    assert len(data["bundles"]) >= 6


def test_gmail_send_blocked_gmail_draft_allowed() -> None:
    assert tap.evaluate_tool("gmail_send")["mode"] == tap.MODE_BLOCKED
    assert tap.evaluate_tool("gmail_draft")["mode"] == tap.MODE_DRAFT_ONLY


def test_linkedin_scrape_and_auto_dm_blocked() -> None:
    assert tap.evaluate_tool("linkedin_scrape")["mode"] == tap.MODE_BLOCKED
    assert tap.evaluate_tool("linkedin_auto_dm")["mode"] == tap.MODE_BLOCKED


def test_cold_whatsapp_tool_blocked() -> None:
    assert tap.evaluate_tool("cold_whatsapp")["mode"] == tap.MODE_BLOCKED


def test_payment_charge_blocked_link_draft_allowed() -> None:
    assert tap.evaluate_tool("moyasar_charge")["mode"] == tap.MODE_BLOCKED
    assert tap.evaluate_tool("moyasar_payment_link_draft")["mode"] == tap.MODE_DRAFT_ONLY


def test_proof_pack_has_metrics() -> None:
    pack = build_proof_pack("first_10_opportunities")
    assert "metrics" in pack
    assert len(pack["metrics"]) >= 1


def test_service_score_gates_high_risk_service() -> None:
    s = calculate_service_excellence_score("whatsapp_compliance_setup")
    assert s["total_score"] >= 0
    assert s["status"] in ("beta_only", "needs_work", "launch_ready")


@pytest.mark.asyncio
async def test_operator_chat_message_post() -> None:
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.post(
            "/api/v1/operator/chat/message",
            json={"message": "أبغى عملاء أكثر"},
        )
    assert r.status_code == 200
    data = r.json()
    assert data["intent"] == ic.INTENT_WANT_MORE_CUSTOMERS
    assert data["recommendation"]["recommended_service_id"] == "first_10_opportunities"


@pytest.mark.asyncio
async def test_operator_bundles_get() -> None:
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.get("/api/v1/operator/bundles")
    assert r.status_code == 200
    assert r.json()["demo"] is True

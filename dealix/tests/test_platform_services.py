"""Tests for platform_services and platform router behaviors."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from api.main import create_app
from auto_client_acquisition.platform_services import (
    evaluate_action,
    event_to_inbox_card,
    execute_tool,
    validate_event,
)
from auto_client_acquisition.platform_services.channel_registry import list_channels
from auto_client_acquisition.platform_services.contact_import_preview import build_import_preview
from auto_client_acquisition.platform_services.lead_form_ingest import ingest_lead_form
from auto_client_acquisition.platform_services.proof_overview import build_proof_overview


def test_cold_whatsapp_blocked() -> None:
    out = evaluate_action(
        action="send",
        channel_id="whatsapp",
        context={"intent": "cold", "audience": "purchased_list"},
    )
    assert out["state"] == "blocked"


def test_inbox_card_max_three_actions() -> None:
    card = event_to_inbox_card(
        {
            "event_type": "lead_received",
            "source": "trusted_simulation",
            "channel_id": "website_form",
        }
    )
    assert len(card["actions"]) <= 3


def test_tool_gateway_never_live_send_status() -> None:
    r = execute_tool(
        "send_message",
        {"channel_id": "email", "action": "external_send", "context": {}},
    )
    assert r["status"] in ("approval_required", "draft_created", "blocked")
    assert r["status"] != "sent"


def test_ingest_lead_form_to_card() -> None:
    body = {
        "source": "trusted_simulation",
        "channel_id": "website_form",
        "lead_name": "أحمد",
        "lead_email": "a@example.com",
    }
    out = ingest_lead_form(body)
    assert out["ok"] is True
    assert out["inbox_card"]["title_ar"]
    assert out["approval_required"] is True


def test_event_validate_lead() -> None:
    v = validate_event(
        {
            "event_type": "lead_received",
            "source": "trusted_simulation",
            "channel_id": "linkedin_lead_form",
        }
    )
    assert v["valid"] is True


def test_event_validate_email_received() -> None:
    v = validate_event(
        {
            "event_type": "email.received",
            "channel_id": "gmail",
            "subject_ar": "استفسار",
        }
    )
    assert v["valid"] is True


def test_omni_event_inbox_card_three_actions() -> None:
    card = event_to_inbox_card(
        {
            "event_type": "payment.paid",
            "amount_halalas": 299900,
            "currency": "SAR",
        }
    )
    assert len(card["actions"]) <= 3
    assert card.get("event_type") == "payment.paid"


def test_social_channels_registered_only() -> None:
    data = list_channels()
    ids = {c["id"] for c in data["channels"]}
    assert "instagram" in ids
    ig = next(c for c in data["channels"] if c["id"] == "instagram")
    assert "auto_reply" in ig["blocked_actions"]


@pytest.fixture()
def client() -> TestClient:
    return TestClient(create_app())


def test_proof_overview_merges_sources() -> None:
    out = build_proof_overview()
    assert out["innovation_ledger_summary"]["event_count"] >= 1
    assert out["business_proof_pack_excerpt"].get("executive_summary_ar")


def test_contact_import_preview_buckets() -> None:
    out = build_import_preview(
        {
            "rows": [
                {"phone": "+966501112233", "email": "a@ex.com", "source": "inbound_form"},
                {"phone": "+966501112233", "source": "inbound_form"},
                {"phone": "+966501112244", "source": "unknown"},
                {"phone": "+966501112255", "source": "purchased_list"},
                {"cold_whatsapp": True, "phone": "+966501112266", "source": "inbound_form"},
            ]
        }
    )
    assert out["ok"] is True
    c = out["counts"]
    assert c["safe"] >= 1
    assert c["needs_review"] >= 1
    assert c["blocked"] >= 2
    assert c["invalid_duplicate"] >= 1


def test_platform_routes_exist(client: TestClient) -> None:
    r = client.get("/api/v1/platform/service-catalog")
    assert r.status_code == 200
    assert "services" in r.json()

    r2 = client.post(
        "/api/v1/platform/integrations/moyasar/payment-draft",
        json={"amount_halalas": 1000, "currency": "SAR"},
    )
    assert r2.status_code == 200
    body = r2.json()
    assert body.get("approval_required") is True
    assert body.get("valid") is True
    assert "payment_link_draft" in body and body["payment_link_draft"]


def test_actions_approve_writes_ledger(client: TestClient) -> None:
    r = client.post(
        "/api/v1/platform/actions/approve",
        json={"action_id": "draft_email_1", "actor": "tester", "approved": True},
    )
    assert r.status_code == 200
    body = r.json()
    assert body.get("ok") is True
    assert body.get("ledger_entry", {}).get("outcome") == "approved"


def test_actions_evaluate_alias_matches_policy(client: TestClient) -> None:
    body = {"action": "send", "channel_id": "whatsapp", "context": {"intent": "cold", "audience": "purchased_list"}}
    a = client.post("/api/v1/platform/policy/evaluate", json=body).json()
    b = client.post("/api/v1/platform/actions/evaluate", json=body).json()
    assert a == b


def test_platform_inbox_feed_and_proof_overview_routes(client: TestClient) -> None:
    r = client.get("/api/v1/platform/inbox/feed")
    assert r.status_code == 200
    assert r.json().get("items")

    r2 = client.get("/api/v1/platform/proof/overview")
    assert r2.status_code == 200
    assert "innovation_ledger_summary" in r2.json()

    r3 = client.post(
        "/api/v1/platform/contacts/import-preview",
        json={"rows": [{"phone": "+966509998877", "source": "website_form"}]},
    )
    assert r3.status_code == 200
    assert r3.json()["ok"] is True

"""Role-based Revenue Command Cards — schema, safety, API."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from api.main import create_app
from auto_client_acquisition.revenue_company_os.card_factory import build_role_command_feed
from auto_client_acquisition.revenue_company_os.cards import (
    UserRole,
    assert_safe_card_copy,
    is_known_role,
    normalize_card,
    normalize_role_param,
)


def _every_card(role: str) -> list[dict]:
    return build_role_command_feed(role)["cards"]


@pytest.mark.parametrize("role", [e.value for e in UserRole])
def test_each_role_has_cards(role: str) -> None:
    cards = _every_card(role)
    assert len(cards) >= 1


@pytest.mark.parametrize("role", [e.value for e in UserRole])
def test_buttons_max_three(role: str) -> None:
    for c in _every_card(role):
        assert len(c.get("buttons") or []) <= 3


@pytest.mark.parametrize("role", [e.value for e in UserRole])
def test_arabic_titles_present(role: str) -> None:
    for c in _every_card(role):
        t = c.get("title_ar")
        assert isinstance(t, str) and len(t.strip()) >= 2


def test_no_forbidden_patterns_in_demo_cards() -> None:
    for role in UserRole:
        for c in _every_card(role.value):
            blob = " ".join(
                str(x)
                for x in (
                    c.get("recommended_action_ar"),
                    c.get("why_now_ar"),
                    c.get("title_ar"),
                )
                if x
            ).lower()
            assert "linkedin_scrape" not in blob
            assert "cold_whatsapp" not in blob


def test_normalize_rejects_unsafe_card() -> None:
    bad = {
        "card_id": "x",
        "tenant_id": "t",
        "role": "ceo",
        "type": "risk",
        "title_ar": "bad",
        "why_now_ar": "bad",
        "recommended_action_ar": "use linkedin_scrape now",
        "risk_level": "high",
        "buttons": [{"label_ar": "ok", "action": "a"}],
        "action_mode": "blocked",
        "proof_impact": [],
        "status": "pending",
    }
    with pytest.raises(ValueError):
        normalize_card(bad)


def test_normalize_role_param_aliases() -> None:
    assert normalize_role_param("Agency") == "agency_partner"
    assert normalize_role_param("SERVICE-DELIVERY") == "service_delivery"


def test_is_known_role() -> None:
    assert is_known_role("ceo")
    assert not is_known_role("cfo")


def test_decision_requires_approval_returns_draft_only() -> None:
    client = TestClient(create_app())
    cid = "sales_manager_deal_1"
    r = client.post(
        f"/api/v1/cards/{cid}/decision",
        json={"action": "approve", "button_action": "draft_followup_email"},
    )
    assert r.status_code == 200
    data = r.json()
    assert data.get("execution_mode") == "draft_only"
    assert "draft_export_ar" in data
    assert "proof_events" in data
    assert any("decision_recorded" in x for x in data["proof_events"])


def test_unknown_card_returns_404() -> None:
    client = TestClient(create_app())
    r = client.post("/api/v1/cards/unknown_id/decision", json={"action": "skip"})
    assert r.status_code == 404


def test_feed_unknown_role_400() -> None:
    client = TestClient(create_app())
    r = client.get("/api/v1/cards/feed?role=cfo")
    assert r.status_code == 400
    body = r.json()
    detail = body.get("detail", body)
    if isinstance(detail, dict):
        assert detail.get("error") == "unknown_role" or "allowed" in detail
    else:
        assert "unknown" in str(detail).lower()


def test_whatsapp_brief_no_auto_send_flag() -> None:
    client = TestClient(create_app())
    r = client.get("/api/v1/cards/whatsapp/daily-brief?role=ceo")
    assert r.status_code == 200
    body = r.json()
    assert body.get("no_auto_send") is True
    assert isinstance(body.get("lines_ar"), list)


def test_api_feed_matches_factory() -> None:
    client = TestClient(create_app())
    for role in ("ceo", "agency_partner"):
        api = client.get(f"/api/v1/cards/feed?role={role}").json()
        direct = build_role_command_feed(role)
        assert api["card_count"] == direct["card_count"]


def test_assert_safe_card_copy_passes_demo() -> None:
    for role in UserRole:
        for c in _every_card(role.value):
            assert_safe_card_copy(c)

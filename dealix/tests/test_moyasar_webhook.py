"""Moyasar webhook verification and endpoint smoke (no live keys)."""

from __future__ import annotations

import pytest

from dealix.payments.moyasar import verify_webhook


def test_verify_webhook_accepts_matching_secret(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MOYASAR_WEBHOOK_SECRET", "shared-secret-xyz")
    body = {"id": "evt_1", "secret_token": "shared-secret-xyz", "type": "payment_paid"}
    assert verify_webhook(body) is True


def test_verify_webhook_rejects_wrong_secret(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MOYASAR_WEBHOOK_SECRET", "shared-secret-xyz")
    body = {"id": "evt_2", "secret_token": "wrong", "type": "payment_paid"}
    assert verify_webhook(body) is False


def test_verify_webhook_rejects_missing_secret_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("MOYASAR_WEBHOOK_SECRET", raising=False)
    body = {"id": "evt_3", "secret_token": "anything", "type": "payment_paid"}
    assert verify_webhook(body) is False


@pytest.mark.asyncio
async def test_moyasar_webhook_endpoint_accepts_valid_body(
    async_client, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("MOYASAR_WEBHOOK_SECRET", "whsec_integration_test")
    payload = {
        "id": "evt_integration_1",
        "type": "payment_paid",
        "secret_token": "whsec_integration_test",
        "data": {"object": "payment", "status": "paid", "amount": 1000},
    }
    res = await async_client.post("/api/v1/webhooks/moyasar", json=payload)
    assert res.status_code == 200
    data = res.json()
    assert data.get("status") == "ok"


@pytest.mark.asyncio
async def test_moyasar_webhook_endpoint_rejects_bad_signature(
    async_client, monkeypatch: pytest.MonkeyPatch
) -> None:
    monkeypatch.setenv("MOYASAR_WEBHOOK_SECRET", "whsec_integration_test")
    payload = {
        "id": "evt_integration_2",
        "type": "payment_paid",
        "secret_token": "wrong-token",
        "data": {},
    }
    res = await async_client.post("/api/v1/webhooks/moyasar", json=payload)
    assert res.status_code == 401

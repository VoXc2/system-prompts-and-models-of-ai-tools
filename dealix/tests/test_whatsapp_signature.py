"""Meta WhatsApp X-Hub-Signature-256 and webhook safety helpers."""

from __future__ import annotations

import hashlib
import hmac

import pytest
from httpx import ASGITransport, AsyncClient

from api.main import create_app
from core.config.settings import get_settings
from integrations.whatsapp import WhatsAppClient


@pytest.fixture(autouse=True)
def _reset_settings_cache():
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def _meta_sig(body: bytes, app_secret: str) -> str:
    digest = hmac.new(app_secret.encode(), body, hashlib.sha256).hexdigest()
    return f"sha256={digest}"


def test_verify_signature_accepts_valid_header(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("WHATSAPP_APP_SECRET", "unit-test-secret")
    app_secret = "unit-test-secret"
    body = b'{"entry":[{"changes":[]}]}'
    client = WhatsAppClient()
    sig = _meta_sig(body, app_secret)
    assert client.verify_signature(body, sig) is True


def test_verify_signature_rejects_tampered_body(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("WHATSAPP_APP_SECRET", "unit-test-secret")
    get_settings.cache_clear()
    client = WhatsAppClient()
    sig = _meta_sig(b"original", "unit-test-secret")
    assert client.verify_signature(b"tampered", sig) is False


@pytest.mark.asyncio
async def test_whatsapp_webhook_rejects_missing_signature_on_staging(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    monkeypatch.setenv("APP_ENV", "staging")
    monkeypatch.setenv("WHATSAPP_APP_SECRET", "staging-webhook-secret")
    get_settings.cache_clear()
    app = create_app()
    try:
        payload = {"entry": []}
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            r = await client.post("/api/v1/webhooks/whatsapp", json=payload)
        assert r.status_code == 403
        assert r.json().get("detail") == "missing_or_invalid_signature"
    finally:
        get_settings.cache_clear()


@pytest.mark.asyncio
async def test_whatsapp_meta_send_blocked_when_flag_off(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("WHATSAPP_ALLOW_LIVE_SEND", "false")
    monkeypatch.setenv("WHATSAPP_ACCESS_TOKEN", "dummy-token")
    monkeypatch.setenv("WHATSAPP_PHONE_NUMBER_ID", "123456")
    get_settings.cache_clear()
    try:
        client = WhatsAppClient()
        result = await client.send_text("+966500000001", "hello")
        assert result.success is False
        assert result.error == "whatsapp_allow_live_send_false"
    finally:
        get_settings.cache_clear()

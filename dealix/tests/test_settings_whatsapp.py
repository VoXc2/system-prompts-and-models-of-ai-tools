"""WhatsApp live-send feature flag."""

from __future__ import annotations

import pytest

from core.config.settings import Settings, get_settings


@pytest.fixture(autouse=True)
def _clear_settings_cache():
    get_settings.cache_clear()
    yield
    get_settings.cache_clear()


def test_whatsapp_allow_live_send_default_false(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("WHATSAPP_ALLOW_LIVE_SEND", raising=False)
    s = Settings()
    assert s.whatsapp_allow_live_send is False


def test_whatsapp_allow_live_send_env_true(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("WHATSAPP_ALLOW_LIVE_SEND", "true")
    s = Settings()
    assert s.whatsapp_allow_live_send is True

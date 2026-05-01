"""Unit tests for webhook signature verification."""

from __future__ import annotations

import base64
import hashlib
import hmac

from api.security.webhook_signatures import (
    verify_calendly_signature,
    verify_hubspot_signature,
    verify_n8n_signature,
)


def _hs(secret: str, method: str, url: str, body: bytes, ts: str) -> str:
    src = f"{method}{url}{body.decode()}{ts}"
    d = hmac.new(secret.encode(), src.encode(), hashlib.sha256).digest()
    return base64.b64encode(d).decode()


def test_hubspot_valid():
    s = "topsecret"
    body = b'{"x":1}'
    ts = "1700000000"
    sig = _hs(s, "POST", "https://api.dealix.sa/webhook", body, ts)
    assert verify_hubspot_signature(
        method="POST",
        url="https://api.dealix.sa/webhook",
        body=body,
        timestamp=ts,
        signature=sig,
        secret=s,
    )


def test_hubspot_invalid():
    assert not verify_hubspot_signature(
        method="POST",
        url="https://api.dealix.sa/webhook",
        body=b"x",
        timestamp="1",
        signature="wrong",
        secret="s",
    )


def test_calendly_valid():
    s = "calendly_secret"
    body = b'{"event":"x"}'
    ts = "1700000000"
    sig = hmac.new(s.encode(), f"{ts}.{body.decode()}".encode(), hashlib.sha256).hexdigest()
    header = f"t={ts},v1={sig}"
    assert verify_calendly_signature(body=body, header=header, secret=s)


def test_n8n_valid():
    s = "n8n_secret"
    body = b'{"x":1}'
    sig = hmac.new(s.encode(), body, hashlib.sha256).hexdigest()
    assert verify_n8n_signature(body=body, signature=f"sha256={sig}", secret=s)
    assert verify_n8n_signature(body=body, signature=sig, secret=s)

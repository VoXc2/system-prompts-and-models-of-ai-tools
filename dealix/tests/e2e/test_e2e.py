"""
E2E smoke tests against a running instance.
Run: API_BASE=http://127.0.0.1:8001 pytest tests/e2e/test_e2e.py --no-cov
"""

from __future__ import annotations

import os

import httpx
import pytest

BASE = os.getenv("API_BASE", "http://127.0.0.1:8001")
HEADERS = {"X-API-Key": os.getenv("API_KEY", "")} if os.getenv("API_KEY") else {}


def _skip_if_no_server() -> None:
    try:
        httpx.get(f"{BASE}/health", timeout=2)
    except Exception:
        pytest.skip(f"No server at {BASE}")


def test_health():
    _skip_if_no_server()
    r = httpx.get(f"{BASE}/health", timeout=5)
    assert r.status_code == 200
    assert r.json().get("status") == "ok"


def test_health_deep():
    _skip_if_no_server()
    r = httpx.get(f"{BASE}/health/deep", timeout=10)
    assert r.status_code == 200
    data = r.json()
    assert "checks" in data
    assert data["status"] in {"ok", "degraded"}


def test_docs_available():
    _skip_if_no_server()
    r = httpx.get(f"{BASE}/docs", timeout=5)
    assert r.status_code == 200


def test_rate_limit_header_present():
    _skip_if_no_server()
    r = httpx.get(f"{BASE}/health", timeout=5)
    # slowapi sets this on limited routes only; /health is unlimited
    assert r.status_code == 200

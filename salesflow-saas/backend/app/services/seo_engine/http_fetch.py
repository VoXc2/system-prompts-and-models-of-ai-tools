"""Controlled HTTP fetch for competitor / public URL checks (timeouts, no auth secrets)."""

from __future__ import annotations

import re
from typing import Any, Dict, Optional
from urllib.parse import urlparse

import httpx


async def fetch_page_summary(url: str, timeout_s: float = 12.0) -> Dict[str, Any]:
    """GET HTML and extract lightweight signals (title, h1 count, has json-ld)."""
    out: Dict[str, Any] = {"url": url, "ok": False}
    try:
        parsed = urlparse(url)
        if parsed.scheme not in ("http", "https"):
            out["error"] = "invalid_scheme"
            return out
        async with httpx.AsyncClient(timeout=timeout_s, follow_redirects=True) as client:
            r = await client.get(url, headers={"User-Agent": "DealixSeoBot/1.0 (+https://dealix.sa)"})
        out["status_code"] = r.status_code
        out["ok"] = 200 <= r.status_code < 400
        text = r.text or ""
        title_m = re.search(r"<title[^>]*>([^<]+)</title>", text, re.I)
        out["title"] = title_m.group(1).strip()[:300] if title_m else None
        out["h1_count"] = len(re.findall(r"<h1[^>]*>", text, re.I))
        out["has_jsonld"] = "application/ld+json" in text or 'type="application/ld+json"' in text
        out["html_length"] = len(text)
    except Exception as exc:  # noqa: BLE001
        out["error"] = str(exc)[:500]
    return out


async def check_url_reachability(url: str) -> Dict[str, Any]:
    try:
        async with httpx.AsyncClient(timeout=10.0, follow_redirects=True) as client:
            r = await client.head(url, headers={"User-Agent": "DealixSeoBot/1.0"})
        return {"url": url, "status_code": r.status_code, "ok": 200 <= r.status_code < 400}
    except Exception as exc:  # noqa: BLE001
        return {"url": url, "ok": False, "error": str(exc)[:300]}


def robots_allows_fetch(robots_body: str, user_agent: str = "*") -> bool:
    """Very small parser: if Disallow: / for our UA, treat as disallow all."""
    if not robots_body.strip():
        return True
    # Simplified — production could use urllib.robotparser with sync IO
    lower = robots_body.lower()
    if "disallow: /" in lower and "disallow:" in lower:
        return False
    return True

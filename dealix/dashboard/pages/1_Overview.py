"""Overview page — KPIs + system health."""

from __future__ import annotations

import os
from typing import Any

import httpx
import streamlit as st

st.title("نظرة عامة")

API = os.getenv("DEALIX_API_URL", "http://127.0.0.1:8001")
API_KEY = os.getenv("DEALIX_ADMIN_API_KEY", "")


def _headers() -> dict[str, str]:
    return {"X-API-Key": API_KEY} if API_KEY else {}


def _get(path: str) -> Any:
    try:
        r = httpx.get(f"{API}{path}", headers=_headers(), timeout=5)
        return r.json() if r.status_code == 200 else {"error": r.status_code}
    except Exception as e:
        return {"error": str(e)}


health = _get("/health/deep")
costs = _get("/api/v1/admin/costs?window_hours=24")

c1, c2, c3, c4 = st.columns(4)
c1.metric("حالة النظام", health.get("status", "?"))
totals = costs.get("totals", {}) if isinstance(costs, dict) else {}
c2.metric("إنفاق 24 ساعة", f"${totals.get('usd', 0)}")
c3.metric("نداءات LLM", totals.get("calls", 0))
c4.metric("cache hit", f"{int(totals.get('cache_hit_ratio', 0) * 100)}%")

st.subheader("فحص صحة عميق")
if isinstance(health, dict) and "checks" in health:
    for name, info in health["checks"].items():
        status = info.get("status", "?")
        emoji = "✅" if status == "ok" else ("⚠️" if status == "skip" else "❌")
        st.write(f"{emoji} **{name}** — {info}")
else:
    st.warning("تعذر الوصول إلى /health/deep")

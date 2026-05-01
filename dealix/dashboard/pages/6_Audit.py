"""Audit page — live operational audit snapshot from health and admin endpoints."""

from __future__ import annotations

import os
from typing import Any

import httpx
import pandas as pd
import streamlit as st

st.title("التدقيق التشغيلي")

API = os.getenv("DEALIX_API_URL", "http://127.0.0.1:8001")
API_KEY = os.getenv("DEALIX_ADMIN_API_KEY", "")


def _headers() -> dict[str, str]:
    return {"X-API-Key": API_KEY} if API_KEY else {}


def _get(path: str) -> Any:
    try:
        response = httpx.get(f"{API}{path}", headers=_headers(), timeout=8)
        return response.json() if response.status_code == 200 else {"error": response.status_code}
    except Exception as exc:
        return {"error": str(exc)}


health = _get("/health/deep")
costs = _get("/api/v1/admin/costs?window_hours=24")
approvals = _get("/api/v1/admin/approvals/stats")
dlq = _get("/api/v1/admin/dlq/stats")

c1, c2, c3, c4 = st.columns(4)
c1.metric("الحالة العامة", health.get("status", "?") if isinstance(health, dict) else "?")
c2.metric(
    "الموافقات المعلقة",
    approvals.get("pending", 0) if isinstance(approvals, dict) else 0,
)
totals = costs.get("totals", {}) if isinstance(costs, dict) else {}
c3.metric("إنفاق 24 ساعة", f"${totals.get('usd', 0)}")
c4.metric(
    "عمق DLQ",
    (sum(queue.get("depth", 0) for queue in dlq.values()) if isinstance(dlq, dict) else 0),
)

st.subheader("فحوصات الصحة")
checks = health.get("checks", {}) if isinstance(health, dict) else {}
if checks:
    rows = []
    for name, info in checks.items():
        rows.append(
            {
                "check": name,
                "status": info.get("status"),
                "latency_ms": info.get("latency_ms", ""),
                "detail": info,
            }
        )
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
else:
    st.info("لا توجد بيانات صحة متاحة حالياً.")

st.subheader("ملخص طوابير الفشل")
if isinstance(dlq, dict) and dlq:
    rows = []
    for queue_name, info in dlq.items():
        rows.append(
            {
                "queue": queue_name,
                "depth": info.get("depth", 0),
                "last_error": info.get("last_error", ""),
            }
        )
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
else:
    st.info("لا توجد بيانات DLQ متاحة حالياً.")

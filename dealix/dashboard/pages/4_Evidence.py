"""Evidence page — governance evidence from live approvals and DLQ state."""

from __future__ import annotations

import os
from typing import Any

import httpx
import pandas as pd
import streamlit as st

st.title("الدليل التشغيلي")

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


approval_stats = _get("/api/v1/admin/approvals/stats")
pending = _get("/api/v1/admin/approvals/pending")
dlq_stats = _get("/api/v1/admin/dlq/stats")

c1, c2 = st.columns(2)
c1.metric(
    "موافقات معلقة",
    approval_stats.get("pending", 0) if isinstance(approval_stats, dict) else 0,
)
c2.metric(
    "إجمالي عناصر DLQ",
    (
        sum(queue.get("depth", 0) for queue in dlq_stats.values())
        if isinstance(dlq_stats, dict)
        else 0
    ),
)

st.subheader("الأدلة الحالية على القرارات المعلقة")
items = pending.get("items", []) if isinstance(pending, dict) else []
if items:
    rows = []
    for item in items:
        rows.append(
            {
                "id": item.get("id"),
                "action": item.get("action"),
                "requested_by": item.get("requested_by"),
                "risk_score": item.get("risk_score"),
                "reason": item.get("reason"),
                "requested_at": item.get("requested_at"),
            }
        )
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
else:
    st.info("لا توجد قرارات معلقة حالياً.")

st.subheader("حالة طوابير الفشل")
if isinstance(dlq_stats, dict) and dlq_stats:
    rows = []
    for queue_name, stats in dlq_stats.items():
        rows.append(
            {
                "queue": queue_name,
                "depth": stats.get("depth", 0),
                "last_error": stats.get("last_error", ""),
                "last_seen_at": stats.get("last_seen_at", ""),
            }
        )
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
else:
    st.info("لا توجد بيانات DLQ متاحة حالياً.")

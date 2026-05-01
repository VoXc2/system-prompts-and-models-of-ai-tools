"""Approvals page — live control surface for pending approvals."""

from __future__ import annotations

import os
from typing import Any

import httpx
import streamlit as st

st.title("الموافقات")

API = os.getenv("DEALIX_API_URL", "http://127.0.0.1:8001")
API_KEY = os.getenv("DEALIX_ADMIN_API_KEY", "")
DECIDER = os.getenv("DEALIX_APPROVER_NAME", "dashboard_admin")


def _headers() -> dict[str, str]:
    return {"X-API-Key": API_KEY} if API_KEY else {}


def _fetch_pending() -> list[dict[str, Any]]:
    try:
        response = httpx.get(f"{API}/api/v1/admin/approvals/pending", headers=_headers(), timeout=8)
        if response.status_code != 200:
            st.error(f"فشل جلب الطلبات: {response.status_code}")
            return []
        data = response.json()
        return data.get("items", []) if isinstance(data, dict) else []
    except Exception as exc:
        st.warning(f"تعذر الجلب: {exc}")
        return []


def _decide(request_id: str, approved: bool, note: str) -> bool:
    payload = {
        "approved": approved,
        "decided_by": DECIDER,
        "note": note,
    }
    try:
        response = httpx.post(
            f"{API}/api/v1/admin/approvals/{request_id}/decide",
            headers=_headers(),
            json=payload,
            timeout=8,
        )
        if response.status_code == 200:
            return True
        st.error(f"فشل تحديث الطلب #{request_id}: {response.status_code}")
    except Exception as exc:
        st.error(str(exc))
    return False


pending = _fetch_pending()
st.caption(f"الموافق المسؤول: {DECIDER}")
st.metric("الموافقات المعلقة", len(pending))

if not pending:
    st.info("لا توجد موافقات معلّقة.")
    st.stop()

for item in pending:
    request_id = item.get("id", "?")
    action = item.get("action", "?")
    requested_by = item.get("requested_by", "?")
    reason = item.get("reason", "")
    risk_score = item.get("risk_score", 0)
    payload = item.get("payload", {})

    with st.expander(f"#{request_id} — {action}"):
        c1, c2, c3 = st.columns(3)
        c1.metric("الجهة الطالبة", requested_by)
        c2.metric("درجة المخاطر", risk_score)
        c3.metric("الحالة", item.get("status", "pending"))

        if reason:
            st.write(f"**سبب التصعيد:** {reason}")
        st.json(payload)

        note = st.text_input("ملاحظة القرار", key=f"note_{request_id}")
        b1, b2 = st.columns(2)
        if b1.button("قبول", key=f"approve_{request_id}", use_container_width=True):
            if _decide(request_id, approved=True, note=note):
                st.success("تمت الموافقة")
                st.rerun()
        if b2.button("رفض", key=f"reject_{request_id}", use_container_width=True):
            if _decide(request_id, approved=False, note=note):
                st.warning("تم الرفض")
                st.rerun()

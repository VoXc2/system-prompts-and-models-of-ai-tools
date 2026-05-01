"""Leads page — list leads and update status."""

from __future__ import annotations

import os
from typing import Any

import httpx
import pandas as pd
import streamlit as st

st.title("العملاء المحتملون")

API = os.getenv("DEALIX_API_URL", "http://127.0.0.1:8001")
API_KEY = os.getenv("DEALIX_ADMIN_API_KEY", "")
H = {"X-API-Key": API_KEY} if API_KEY else {}


@st.cache_data(ttl=30)
def _leads() -> list[dict[str, Any]]:
    try:
        r = httpx.get(f"{API}/api/v1/leads", headers=H, timeout=10)
        if r.status_code == 200:
            data = r.json()
            return data if isinstance(data, list) else data.get("leads", [])
    except Exception:
        pass
    return []


leads = _leads()
if not leads:
    st.info("لا يوجد عملاء بعد، أو تعذر الاتصال بالـ API.")
    st.stop()

df = pd.DataFrame(leads)
st.dataframe(df, use_container_width=True, hide_index=True)

st.subheader("تحديث حالة عميل")
col1, col2, col3 = st.columns(3)
with col1:
    lead_id = st.text_input("Lead ID")
with col2:
    new_status = st.selectbox(
        "الحالة الجديدة",
        ["new", "qualified", "discovery", "proposal", "won", "lost"],
    )
with col3:
    st.write(" ")
    if st.button("تحديث"):
        try:
            r = httpx.patch(
                f"{API}/api/v1/leads/{lead_id}",
                headers=H,
                json={"status": new_status},
                timeout=10,
            )
            if r.status_code in (200, 204):
                st.success(f"تم تحديث {lead_id} → {new_status}")
                st.cache_data.clear()
            else:
                st.error(f"فشل: {r.status_code}")
        except Exception as e:
            st.error(str(e))

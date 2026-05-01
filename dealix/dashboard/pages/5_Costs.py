"""Costs page — LLM spend analysis."""

from __future__ import annotations

import os

import httpx
import pandas as pd
import streamlit as st

st.title("تكاليف النماذج")

API = os.getenv("DEALIX_API_URL", "http://127.0.0.1:8001")
H = (
    {"X-API-Key": os.getenv("DEALIX_ADMIN_API_KEY", "")}
    if os.getenv("DEALIX_ADMIN_API_KEY")
    else {}
)

col1, col2 = st.columns(2)
with col1:
    window = st.selectbox(
        "النافذة الزمنية", [1, 6, 24, 72, 168, 720], index=2, format_func=lambda h: f"{h} ساعة"
    )
with col2:
    group_by = st.selectbox("تجميع حسب", ["model", "provider", "task"])

try:
    r = httpx.get(
        f"{API}/api/v1/admin/costs?window_hours={window}&group_by={group_by}", headers=H, timeout=10
    )
    data = r.json() if r.status_code == 200 else {"error": r.status_code}
except Exception as e:
    data = {"error": str(e)}

if "totals" in data:
    t = data["totals"]
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("إنفاق", f"${t['usd']}")
    c2.metric("نداءات", t["calls"])
    c3.metric("تكاليف toks", f"{t['input_tokens']:,}")
    c4.metric("cache hit", f"{int(t.get('cache_hit_ratio', 0) * 100)}%")

    st.subheader(f"حسب {group_by}")
    rows = [{group_by: k, **v} for k, v in data.get("by_group", {}).items()]
    if rows:
        df = pd.DataFrame(rows).sort_values("usd", ascending=False)
        st.dataframe(df, use_container_width=True, hide_index=True)
        st.bar_chart(df.set_index(group_by)["usd"])
else:
    st.error(data)

# Dealix Admin Dashboard

لوحة تحكم Streamlit لإدارة Dealix.

## التشغيل المحلي

```bash
pip install streamlit pandas httpx
export DEALIX_API_URL=http://127.0.0.1:8001
export DEALIX_ADMIN_API_KEY=<your-admin-key>
streamlit run dashboard/app.py --server.port 8501
```

## الصفحات
- `1_Overview` — KPIs عامة + فحص صحة عميق
- `2_Leads` — جدول العملاء + تحديث الحالة
- `3_Approvals` — موافقات Policy Engine
- `4_Evidence` — سجل القرارات والدليل
- `5_Costs` — تحليل إنفاق LLM
- `6_Audit` — سجل التكاملات

## الإنتاج

تُخدم على `dashboard.dealix.me` عبر reverse-proxy من nginx إلى port 8501.

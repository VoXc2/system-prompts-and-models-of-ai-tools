# Dashboard Guide — Dealix v3.0.0

## النظرة العامة
لوحة Streamlit لمتابعة الإنتاج وإدارة العملاء.

## الصفحات

| الصفحة | المصدر | الوصف |
|-------|--------|------|
| Overview | `/health/deep` + `/admin/costs` | حالة عامة + KPIs |
| Leads | `/api/v1/leads` | جدول + تحديث الحالة |
| Approvals | `/api/v1/cro/approvals` | قبول/رفض قرارات Policy Engine |
| Evidence | `/api/v1/cro/evidence` | سجل القرارات والدليل |
| Costs | `/api/v1/admin/costs` | تحليل إنفاق LLM (model/provider/task) |
| Audit | `/api/v1/admin/audit` | سجل التكاملات |

## التشغيل

```bash
# dependencies
pip install streamlit pandas httpx

# environment
export DEALIX_API_URL=https://api.dealix.sa
export DEALIX_ADMIN_API_KEY=<admin-key>

# run
streamlit run dashboard/app.py --server.port 8501
```

## Reverse Proxy (nginx)

```nginx
server {
    listen 443 ssl http2;
    server_name dashboard.dealix.sa;
    location / {
        proxy_pass http://127.0.0.1:8501;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";
        proxy_set_header Host $host;
        proxy_read_timeout 600s;
    }
}
```

## صلاحيات الوصول
- الدخول عبر X-API-Key (يُستخدم من مفتاح في `DEALIX_ADMIN_API_KEY` جانب الخادم)
- Dashboard يتصل بـ API من الداخل فقط

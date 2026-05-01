# Dealix — Launch Master Runbook (AR)

> **الهدف:** إخراج Dealix من «جاهزية الكود» إلى «إطلاق تجاري حقيقي» بـ 10 خطوات واضحة.
> **الجمهور:** سامي (المؤسس) + أي عضو فريق onboarding مستقبلي.
> **آخر تحديث:** 2026-05-01

---

## ✅ ما تم بالفعل (مرفوع على GitHub `ai-company`)

- [x] **Backend:** 28 router · 266 endpoint · 24 DB table
- [x] **Modules:** revenue_memory · orchestrator · market_intelligence · copilot · revenue_science · compliance_os · vertical_os · revenue_graph · customer_success · ecosystem · personal_operator · v3 · business · innovation · ai
- [x] **Frontend:** 33 صفحة landing (privacy, terms, signup, welcome, payment success/cancel, 404, 500 — كلها أُضيفت اليوم)
- [x] **Tests:** 477 passed, 2 skipped على Python 3.10 venv
- [x] **CI:** Dealix API CI خضراء على GitHub
- [x] **Compat:** Python 3.10 + 3.11+ shim
- [x] **Legal:** privacy.html + terms.html (PDPL-aligned)
- [x] **Security:** SECURITY.md + LICENSE
- [x] **Sitemap + robots** محدّث

---

## 🚦 ما يحتاج خطوات يدوية للإطلاق التجاري

### 1️⃣ النطاق و DNS

- [ ] شراء/تأكيد ملكية `dealix.sa` (الأولوية) أو `dealix.me` (مؤقت)
- [ ] DNS records:
  - `A`     → IP الخادم Railway/Cloudflare
  - `CNAME api` → Railway public domain
  - `CNAME www` → root
  - `MX`    → Google Workspace / Zoho Mail
  - `TXT`   → SPF + DMARC + DKIM (لإيميلات outbound)
- [ ] SSL certificate (Railway/Cloudflare auto)
- [ ] Cloudflare proxy + WAF rules

### 2️⃣ Railway / Hosting

- [ ] إنشاء مشروع Railway باسم `dealix-api`
- [ ] ربط GitHub repo: `VoXc2/system-prompts-and-models-of-ai-tools`
- [ ] **Root directory:** `dealix/`
- [ ] **Branch:** `ai-company` (ثم نحول إلى `main` بعد الاستقرار)
- [ ] **Build command:** auto (Railway يلتقط Dockerfile)
- [ ] **Start command:** `uvicorn api.main:app --host 0.0.0.0 --port $PORT`
- [ ] إضافة Postgres add-on (Saudi-region لو متاح، أو EU/Bahrain)
- [ ] إضافة Redis add-on (للجلسات + rate limiting)

### 3️⃣ Environment Variables (Railway → Variables)

من `dealix/.env.example`، الحرجة للإطلاق:

```bash
# Core
APP_ENV=production
APP_NAME=Dealix
APP_HOST=0.0.0.0
APP_PORT=$PORT
DATABASE_URL=$RAILWAY_POSTGRES_URL
REDIS_URL=$RAILWAY_REDIS_URL

# Security
API_KEY_PRIMARY=<generate via openssl rand -hex 32>
JWT_SECRET=<generate via openssl rand -hex 32>
CORS_ORIGINS=https://dealix.sa,https://www.dealix.sa

# LLM (one provider minimum)
ANTHROPIC_API_KEY=sk-ant-...
GROQ_API_KEY=gsk_...

# WhatsApp (one provider minimum)
GREEN_API_INSTANCE_ID=...
GREEN_API_TOKEN=...
# OR Meta WhatsApp Cloud:
META_WHATSAPP_PHONE_ID=...
META_WHATSAPP_TOKEN=...
META_WHATSAPP_VERIFY_TOKEN=<random>

# Gmail OAuth (per-customer flow)
GOOGLE_OAUTH_CLIENT_ID=...
GOOGLE_OAUTH_CLIENT_SECRET=...
GOOGLE_OAUTH_REDIRECT_URI=https://api.dealix.sa/auth/google/callback

# Moyasar (Saudi billing)
MOYASAR_PUBLIC_KEY=pk_live_...
MOYASAR_SECRET_KEY=sk_live_...
MOYASAR_WEBHOOK_SECRET=<set in Moyasar dashboard>

# Observability
SENTRY_DSN=https://...@sentry.io/...
LANGFUSE_PUBLIC_KEY=...
LANGFUSE_SECRET_KEY=...
POSTHOG_API_KEY=phc_...

# Supabase (project memory + pgvector)
SUPABASE_URL=https://....supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJ... (server only — never client)
```

### 4️⃣ Database Migrations

- [ ] تنفيذ `alembic upgrade head` على Railway Postgres
- [ ] تنفيذ `supabase/migrations/202605010001_v3_project_memory.sql` على Supabase
- [ ] تأكيد الفهارس على pgvector (HNSW) للمحادثات

### 5️⃣ Domain → API → Frontend

- [ ] `api.dealix.sa` → Railway service
- [ ] `dealix.sa` و `www.dealix.sa` → static hosting من `landing/` (Cloudflare Pages أو Netlify)
- [ ] إعادة توجيه `dealix.me` → `dealix.sa` (لو الاثنين موجودان)
- [ ] تحديث `CORS_ORIGINS` ليشمل النطاق الفعلي

### 6️⃣ المدفوعات (Moyasar)

- [ ] حساب Moyasar مفعّل (يحتاج CR + IBAN سعودي)
- [ ] webhook URL: `https://api.dealix.sa/api/v1/webhooks/moyasar`
- [ ] اختبار الدفع بمبلغ رمزي (1 ريال) قبل الإطلاق
- [ ] تأكد من ZATCA invoice template (15% VAT تلقائي)

### 7️⃣ WhatsApp Business Account

- [ ] WABA verified عبر Meta أو موزع معتمد (مثل Green API بحساب Saudi)
- [ ] رقم سعودي (+966) موثّق
- [ ] template messages معتمدة بالعربية:
  - `welcome_v1` — تأكيد الاشتراك
  - `daily_brief_v1` — التقرير اليومي
  - `approval_pending_v1` — تنبيه drafts بحاجة موافقة
- [ ] webhook signature verified

### 8️⃣ Email Deliverability

- [ ] Google Workspace أو Zoho Mail لـ `@dealix.sa`
- [ ] SPF: `v=spf1 include:_spf.google.com ~all`
- [ ] DKIM: تفعيل من Google Workspace
- [ ] DMARC: `v=DMARC1; p=quarantine; rua=mailto:dmarc@dealix.sa`
- [ ] التسخين (warm-up) لمدة 14 يوم قبل الإرسال الكثيف

### 9️⃣ Observability live

- [ ] Sentry — إنشاء project + DSN
- [ ] Langfuse — حساب + public/secret keys
- [ ] PostHog — موقع
- [ ] Status page (statusapi.io أو internal `/status.html` يربط بـ `/health/deep`)
- [ ] Uptime monitor (Better Uptime / UptimeRobot) → `/health`

### 🔟 Beta Launch Day (T-Day)

- [ ] **T-7 days:** smoke test كامل على staging
- [ ] **T-3 days:** invite-only beta (5 شركات أصدقاء)
- [ ] **T-1 day:** dry run — 24h لتشغيل النظام بصمت
- [ ] **T-Day morning:**
  - [ ] post على LinkedIn (announcement)
  - [ ] WhatsApp blast لقائمة الـ 50 شركة
  - [ ] إرسال press release لـ TechCrunch Arabia / Wamda
- [ ] **T+1:** مراقبة active 24/7 لأول 72 ساعة
- [ ] **T+7:** retrospective + fix top-3 bugs

---

## 🧪 Smoke Test Manual (قبل الإطلاق)

```bash
# 1. Health
curl https://api.dealix.sa/health
# expected: {"status": "ok", ...}

# 2. Deep health
curl https://api.dealix.sa/health/deep -H "X-API-Key: $API_KEY_PRIMARY"
# expected: db, redis, llm checks all OK

# 3. Public landing pages
for page in / /pricing.html /privacy.html /terms.html /signup.html /command-center.html; do
  echo -n "$page: "
  curl -s -o /dev/null -w "%{http_code}\n" https://dealix.sa$page
done
# expected: all 200

# 4. Trigger a workflow (with API key)
curl -X POST https://api.dealix.sa/api/v1/revenue-os/workflows/run \
  -H "X-API-Key: $API_KEY_PRIMARY" -H "Content-Type: application/json" \
  -d '{"customer_id":"smoke","autonomy_mode":"draft_and_approve"}'
# expected: 8 tasks created, all awaiting_approval (since draft mode)

# 5. Copilot ask
curl -X POST https://api.dealix.sa/api/v1/revenue-os/copilot/ask \
  -H "X-API-Key: $API_KEY_PRIMARY" -H "Content-Type: application/json" \
  -d '{"question_ar":"وش أسوي اليوم؟","customer_id":"smoke","context":{}}'
# expected: intent=what_to_do_today + answer + 3 actions

# 6. Compliance risk gate
curl -X POST https://api.dealix.sa/api/v1/revenue-os/compliance/campaign-risk \
  -H "X-API-Key: $API_KEY_PRIMARY" -H "Content-Type: application/json" \
  -d '{"target_count":100,"contacts_with_consent":80,"contacts_opted_out":20,
       "contacts_no_lawful_basis":0,"template_body":"ضمان 100% رقم الهوية",
       "has_unsubscribe_link":false}'
# expected: risk_band="blocked" + 2 blockers
```

---

## 📊 KPIs لأول 30 يوم

| المقياس | الهدف |
|---|---|
| Uptime | ≥99.5% |
| API p95 latency | <200ms |
| Beta signups | 10-20 شركة |
| First Daily Run completed | ≥80% من الـ signups |
| First WhatsApp draft approved | ≥50% |
| Errors / 1000 requests | <5 |
| Stripe/Moyasar successful payment rate | ≥95% |
| NPS من أول 5 عملاء | ≥30 |

---

## 🆘 خطة الطوارئ (Rollback Plan)

لو حصلت مشكلة كارثية:

1. **Database:** استرجاع من Railway snapshot (آخر 24 ساعة)
2. **API:** إرجاع لآخر commit مستقر عبر Railway → Deployments → rollback
3. **Frontend:** rollback CDN إلى آخر deploy stable
4. **WhatsApp:** تعطيل الـ outbound حتى توضّح المشكلة (PDPL gate)
5. **التواصل:** post status update فوراً + إيميل لكل المتأثرين خلال ساعة

**جهات الاتصال الطارئة:**
- Railway support: support@railway.app
- Moyasar: support@moyasar.com (24/7)
- Sentry: support.sentry.io
- WhatsApp Cloud / Green API: حسب الموزع

---

## 🎯 الجملة الأخيرة قبل الإطلاق

> **"البرنامج جاهز. النظام جاهز. الباكد إند والفرونت إند جاهزون.
> الآن: ربط الحسابات + اختبار يدوي + إطلاق صامت 7 أيام، ثم إعلان كبير."**

— Dealix · Saudi Autonomous Revenue Platform · 🇸🇦

# Dealix — Universal Deployment Guide

دليل نشر Dealix على أي منصة: Railway, Render, Fly.io, Heroku, DigitalOcean, AWS, Docker self-hosted.

---

## 🎯 TL;DR — نشر خلال 10 دقائق

1. أي منصة تدعم Docker → استخدم `Dockerfile` الموجود في root
2. عيّن env vars من `.env.example` (انسخه كبداية)
3. Health check: `GET /health`
4. التطبيق يستمع على `${PORT:-8000}`
5. يتطلب PostgreSQL (اختياري — التطبيق يعمل بدونه في dev mode)

---

## 📦 المتغيرات المطلوبة (Minimum للإنتاج)

### الإلزامية (بدونها الدفع ما يشتغل)

```bash
# Security
APP_SECRET_KEY=CHANGE_ME_64_byte_hex  # generate: python -c "import secrets; print(secrets.token_hex(32))"
ENVIRONMENT=production
LOG_LEVEL=INFO

# Database (Railway/Render/Heroku postgres auto-normalize لـ asyncpg)
DATABASE_URL=postgresql://user:pass@host:5432/dealix

# Moyasar Payments
MOYASAR_SECRET_KEY=sk_live_xxxxx
MOYASAR_WEBHOOK_SECRET=CHANGE_ME_shared_with_moyasar_dashboard

# PostHog Analytics (اختياري لكن موصى به)
POSTHOG_API_KEY=phc_xxxxx
POSTHOG_HOST=https://us.i.posthog.com

# Calendly
CALENDLY_URL=https://calendly.com/sami-assiri11/dealix-demo
CALENDLY_WEBHOOK_SECRET=xxxxx

# CORS (أضف domain الـ landing)
CORS_ORIGINS=https://dealix.sa,https://www.dealix.sa
```

### الاختيارية

```bash
API_KEYS=key1,key2  # إذا بدك حماية admin endpoints
APP_URL=https://dealix.sa  # للـ checkout callback
SENTRY_DSN=https://...@sentry.io/...
```

---

## 🚀 نشر على المنصات المختلفة

### 1) Railway (الموصى به — مجاني تقريباً)

**إعداد أولي:**
1. افتح https://railway.com → **New Project** → **Deploy from GitHub** → اختر `VoXc2/dealix`
2. Railway يكتشف `Dockerfile` تلقائياً
3. أضف Postgres: **+ New** → **Database** → **PostgreSQL**
4. اذهب لخدمة `dealix` → **Variables** → **Raw Editor**
5. الصق محتوى `dealix_railway_vars.txt` (يُرفق مع الحزمة)
6. **Settings** → **Deploy** → **Start Command**: اتركه فارغ (يستخدم Dockerfile)
7. احفظ → Railway ينشر تلقائياً

**التحقق:**
```bash
curl https://<your-app>.up.railway.app/health
# {"status":"ok"}
```

### 2) Render

1. https://render.com → **New** → **Web Service** → Connect GitHub → `VoXc2/dealix`
2. اختر **Docker** runtime
3. Add environment variables من `.env.example`
4. **Health Check Path:** `/health`
5. Add PostgreSQL من Render marketplace
6. Deploy

### 3) Fly.io

```bash
fly launch --dockerfile Dockerfile
fly secrets set APP_SECRET_KEY=... MOYASAR_SECRET_KEY=...
fly postgres create --name dealix-db
fly postgres attach dealix-db
fly deploy
```

### 4) Heroku

```bash
heroku create dealix-api
heroku stack:set container
heroku addons:create heroku-postgresql:mini
heroku config:set APP_SECRET_KEY=... MOYASAR_SECRET_KEY=...
git push heroku main
```

### 5) DigitalOcean App Platform

1. https://cloud.digitalocean.com/apps → **Create App** → GitHub → `VoXc2/dealix`
2. App Platform يكتشف Dockerfile
3. أضف managed PostgreSQL
4. أضف env vars
5. Deploy

### 6) Docker self-hosted (أي VPS)

```bash
# على السيرفر:
git clone https://github.com/VoXc2/dealix.git
cd dealix
cp .env.example .env
# عبّي المتغيرات في .env
docker build -t dealix .
docker run -d --name dealix -p 8000:8000 --env-file .env dealix

# مع PostgreSQL:
docker-compose up -d  # إذا استخدمت docker-compose.yml (راجع docker-compose.example.yml)
```

### 7) AWS (ECS Fargate)

1. ادفع صورة Docker لـ ECR: `docker build -t dealix . && docker push <ecr-url>/dealix:latest`
2. أنشئ ECS Cluster + Task Definition بالصورة
3. أضف RDS Postgres
4. عيّن env vars في Task Definition
5. أنشئ Service مع Application Load Balancer
6. Route 53 → ربط الدومين

---

## 🔗 ربط Landing Page مع Backend

Landing في مجلد `landing/` يقرأ عنوان API من `window.DEALIX_API_BASE`.

### خيار A — نشر منفصل (Netlify / Vercel / Cloudflare Pages)

1. انشر مجلد `landing/` كـ static site
2. قبل النشر، عدّل `landing/index.html`:
   ```html
   <script>
     window.DEALIX_API_BASE = 'https://your-backend-url.com';
   </script>
   ```
3. أضف domain `dealix.sa` في CORS_ORIGINS في backend

### خيار B — نشر مع الـ Backend على نفس المنصة

في Railway أو Render: أضف `landing/` كـ static serving.
أو استخدم nginx reverse proxy (راجع `nginx.example.conf`).

---

## 💳 إعداد Moyasar Webhook

**مطلوب حتى الدفع يعمل نهاية إلى نهاية:**

1. افتح https://dashboard.moyasar.com/webhooks
2. **Add Webhook**:
   - **URL:** `https://<your-backend-url>/api/v1/webhooks/moyasar`
   - **Events:** `payment_paid`, `payment_failed`, `payment_refunded`
   - **Secret:** القيمة اللي عيّنتها في `MOYASAR_WEBHOOK_SECRET` env var (نفس القيمة بالضبط)
3. **Save**
4. Moyasar يرسل ping اختباري → يجب أن يرجع 200

---

## 🧪 اختبار بعد النشر

```bash
BASE_URL=https://your-backend-url.com

# 1. Health
curl $BASE_URL/health
# {"status":"ok"}

# 2. Pricing
curl $BASE_URL/api/v1/pricing/plans

# 3. Demo request (landing form simulation)
curl -X POST $BASE_URL/api/v1/public/demo-request \
  -H "Content-Type: application/json" \
  -d '{"name":"تجربة","company":"Test Co","email":"test@example.com","phone":"+966500000000","consent":true}'

# 4. Checkout (1 SAR pilot — دفع حقيقي)
curl -X POST $BASE_URL/api/v1/checkout \
  -H "Content-Type: application/json" \
  -d '{"plan":"pilot_1sar","email":"you@example.com"}'
# returns payment_url — افتحه في المتصفح وادفع
```

---

## 🐛 المشاكل الشائعة

### Railway: `Invalid value for '--port': '${PORT:-8000}' is not a valid integer`
**السبب:** Railway UI Start Command override يتجاوز shell expansion.
**الحل:** في **Settings** → **Deploy** → **Start Command**: امسحه أو ضع `/app/start.sh`

### Healthcheck فاشل بعد deploy
**السبب:** المتغيرات ناقصة أو app crash at startup.
**الحل:** راجع logs — إذا `email-validator is not installed` فأعد النشر (PR #68 حلّها).

### Moyasar webhook 401
**السبب:** `MOYASAR_WEBHOOK_SECRET` مختلف في Moyasar dashboard والـ env.
**الحل:** تأكد من تطابقهما بالضبط.

### DB connection refused
**السبب:** `DATABASE_URL` بصيغة خاطئة.
**الحل:** التطبيق يحوّل `postgres://` → `postgresql+asyncpg://` تلقائياً. تأكد أن الـ URL صحيح.

---

## 📚 مسارات API الجاهزة

| Route | Method | الوصف |
|-------|--------|-------|
| `/health` | GET | Health check (public) |
| `/api/v1/public/health` | GET | Health للـ landing (public) |
| `/api/v1/public/demo-request` | POST | Landing form → Calendly (public) |
| `/api/v1/pricing/plans` | GET | قائمة الباقات (public) |
| `/api/v1/checkout` | POST | توليد Moyasar invoice |
| `/api/v1/webhooks/moyasar` | POST | استقبال أحداث Moyasar |
| `/api/v1/webhooks/whatsapp` | POST/GET | WhatsApp Meta webhook |
| `/api/v1/webhooks/calendly` | POST | Calendly lifecycle events |
| `/api/v1/leads` | POST | إنشاء lead (يتطلب API key) |
| `/api/v1/sales/*` | * | Sales ops (API key) |
| `/api/v1/admin/*` | * | Admin (API key) |
| `/docs` | GET | Swagger UI |

---

## 🔐 الأمان — قواعد صارمة

- **لا تدفع** `.env` أو مفاتيح لـ Git (موجود `.gitignore`)
- Rotate `APP_SECRET_KEY` إذا أي شخص شافه
- `MOYASAR_SECRET_KEY` = `sk_live_*` للإنتاج فقط (استخدم `sk_test_*` للاختبار)
- `API_KEYS` للحماية — ابدأ بدونها لكن فعّلها قبل الإطلاق العام
- CORS_ORIGINS صارم — ما في wildcard `*` في الإنتاج

---

## 📞 الدعم

- Issues: https://github.com/VoXc2/dealix/issues
- Owner: sami.assiri11@gmail.com

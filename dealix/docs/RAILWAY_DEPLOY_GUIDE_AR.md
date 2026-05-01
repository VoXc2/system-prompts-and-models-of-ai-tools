# دليل نشر Dealix على Railway (بالعربي)

## لماذا Railway؟

- ✅ لا SSH — نشر مباشر من GitHub
- ✅ PostgreSQL مبني
- ✅ SSL تلقائي
- ✅ دومين مجاني
- ✅ $5 مجاني شهرياً
- ✅ لا يتأثر بحجب ISP

---

## الخطوات (15 دقيقة)

### 1. إنشاء الحساب

افتح [railway.com](https://railway.com) → **Login with GitHub** (بحسابك VoXc2).

### 2. إنشاء المشروع

- اضغط **New Project**
- اختر **Deploy from GitHub repo**
- اختر `VoXc2/dealix`
- Railway يكتشف Dockerfile تلقائياً ويبدأ البناء

### 3. إضافة PostgreSQL

داخل المشروع:

- اضغط **+ New** → **Database** → **Add PostgreSQL**
- Railway يولد `DATABASE_URL` تلقائياً ويربطه بالتطبيق

### 4. إضافة Environment Variables

في service الـ API → **Variables** → **+ New Variable** (أو Raw Editor للصق دفعة واحدة):

```
POSTHOG_API_KEY=<from Computer chat>
POSTHOG_HOST=https://us.i.posthog.com
POSTHOG_ENABLED=true
MOYASAR_PUBLIC_KEY=<from Computer chat>
MOYASAR_SECRET_KEY=<from Computer chat>
MOYASAR_WEBHOOK_SECRET=<from Computer chat>
CALENDLY_WEBHOOK_SECRET=<from Computer chat>
CALENDLY_OAUTH_CLIENT_ID=<from Computer chat>
CALENDLY_OAUTH_CLIENT_SECRET=<from Computer chat>
ENV=production
APP_ENV=production
DATABASE_URL=${{Postgres.DATABASE_URL}}
```

> All real values are in the Computer chat message that contains this guide. Paste them into Railway's Raw Editor.


**مهم**: القيمة `${{Postgres.DATABASE_URL}}` هذي مرجع ديناميكي لقاعدة البيانات اللي ضفتها.

### 5. تشغيل alembic migrations

بعد أول نشر ناجح:

- Service → **Settings** → **Deploy** → **Start Command**
- تأكد إنه: `alembic upgrade head && uvicorn api.main:app --host 0.0.0.0 --port $PORT`

أو استخدم **Deploy Triggers** → أضف pre-deploy command: `alembic upgrade head`

### 6. توليد رابط عام

- Service → **Settings** → **Networking** → **Generate Domain**
- Railway يعطيك شي مثل: `dealix-production-abc.up.railway.app`
- احفظ الرابط

### 7. اختبار API

```
https://dealix-production-abc.up.railway.app/healthz
https://dealix-production-abc.up.railway.app/readyz
```

لازم يرجع `200 OK`.

### 8. ربط الدومين dealix.me

**Railway**:

- Settings → Networking → **Custom Domain** → `dealix.me`
- Railway يعطيك CNAME مثل: `abc123.up.railway.app`

**GoDaddy**:

- Domain dealix.me → **DNS Records** → أضف:
  - Type: `CNAME`
  - Name: `@` (أو `www`)
  - Value: `abc123.up.railway.app`
  - TTL: 600

ملاحظة: CNAME على root domain أحياناً يسمى **ALIAS** أو **ANAME** في GoDaddy.

### 9. تحديث Webhooks

**Moyasar** ([dashboard.moyasar.com/webhooks](https://dashboard.moyasar.com/webhooks)):

- URL: `https://dealix.me/api/v1/webhooks/moyasar`
- Secret: قيمة `MOYASAR_WEBHOOK_SECRET` من Railway Variables

**Calendly** (webhook مسجل مسبقاً بـ PAT — نحدث URL):

- تلقائي إذا URL الـ endpoint ما تغير (`/api/v1/webhooks/calendly`)

### 10. اختبار Pilot Payment (1 SAR)

```bash
curl -X POST https://dealix.me/api/v1/checkout \
  -H "Content-Type: application/json" \
  -d '{"plan": "pilot_1sar"}'
```

---

## المراقبة

### Logs حية

داخل Service → **Deployments** → اختر آخر deployment → **View Logs**

### Restart

Service → **Settings** → **Restart**

### Rollback

Deployments → اختر deployment قديم → **Redeploy**

---

## التكلفة

- **Free trial**: $5 رصيد
- **Hobby plan**: $5/شهر بعد انتهاء Free trial
- **PostgreSQL**: محسوبة من نفس الرصيد (~$1-2/شهر للاستخدام البسيط)

---

## استكشاف الأخطاء

| المشكلة | الحل |
|---------|------|
| Build failed | افحص logs → غالباً requirements.txt |
| 503 Service Unavailable | API لم يبدأ — افحص Variables |
| Healthcheck failing | غيّر path في railway.json لـ `/health` |
| Database connection failed | تأكد إن `DATABASE_URL=${{Postgres.DATABASE_URL}}` |

---

## الخطوات التالية

1. ✅ نشر على Railway
2. ✅ ربط dealix.me
3. ✅ تسجيل webhooks (Moyasar + Calendly)
4. ✅ اختبار pilot payment
5. ⏳ تحديث gates من 18/30 إلى 22/30

# 🚦 Dealix — Launch Gates Checklist (للتنفيذ الفوري)

**القاعدة:** لا توجد "launch partial". إما كل الـ gates مغلقة أو الـ launch غير مكتمل.
**المدة المتوقعة:** 2-4 ساعات من وقتك الفعلي، موزّعة على 72 ساعة.

---

## 🔴 Gate 1 — Backend Deploy (10 دقائق)

### الخطوات:
- [ ] افتح `https://railway.com/project/54bb60b4-d059-4dd1-af57-bc44c702b9f0`
- [ ] اختر خدمة `dealix`
- [ ] Settings → Deploy → Start Command → **اتركه فارغاً** (أو اكتب `/app/start.sh`)
- [ ] Variables → Raw Editor → الصق محتوى `dealix_railway_vars.txt` من workspace
- [ ] احفظ
- [ ] انتظر Deploy Status = `Active` (2-3 دقائق)
- [ ] Settings → Networking → Generate Public Domain

### Definition of Done:
```bash
curl https://<your-domain>.up.railway.app/api/v1/pricing/plans
# يجب أن يرجع: JSON مع plans (Starter, Growth, Scale)
```

**إذا Failed:** أرسل screenshot من Railway Deployments → Logs

---

## 🔴 Gate 2 — Moyasar Webhook (5 دقائق)

### الخطوات:
- [ ] افتح `https://dashboard.moyasar.com/webhooks`
- [ ] اضغط `+ Add Webhook`
- [ ] **URL:** `https://<your-domain>.up.railway.app/api/v1/webhooks/moyasar`
- [ ] **Events:** اختر `payment_paid`, `payment_failed`, `payment_refunded`
- [ ] **Secret:** انسخ قيمة `MOYASAR_WEBHOOK_SECRET` من `dealix_railway_vars.txt`
- [ ] احفظ
- [ ] Send Test Event من Moyasar

### Definition of Done:
- [ ] Test event في Moyasar يظهر `Delivered`
- [ ] Railway logs تظهر `moyasar webhook received`

---

## 🔴 Gate 3 — 1 SAR End-to-End Test (15 دقائق)

### الخطوات:
- [ ] Terminal:
  ```bash
  cd /path/to/workspace
  bash dealix_1_riyal_test.sh https://<your-domain>.up.railway.app
  ```
- [ ] السكريبت ينشئ invoice + يعرض رابط دفع
- [ ] افتح الرابط في المتصفح
- [ ] ادفع ببطاقة Moyasar test:
  - Card: `4111 1111 1111 1111`
  - CVV: `123`
  - Expiry: `12/30`
  - OTP: `1234`
- [ ] ارجع للـ terminal + اضغط Enter للتحقق

### Definition of Done:
- [ ] Payment يظهر في Moyasar dashboard (status: `paid`)
- [ ] Webhook event في Railway logs
- [ ] Record جديد في DB (سأعطيك SQL للفحص)
- [ ] `payment_succeeded` event في PostHog

**إذا الـ DB check غير ممكن من الواجهة:** OK، نعتمد على Moyasar + Webhook logs فقط للـ MVP.

---

## 🔴 Gate 4 — Monitoring (45 دقيقة)

### PostHog Verification (15 دقيقة):
- [ ] افتح `https://app.posthog.com` (أو self-hosted)
- [ ] تأكد project key نفسه في `POSTHOG_PROJECT_KEY` env var
- [ ] من Railway logs، تأكد أن الـ backend يرسل events
- [ ] شاهد "Live events" في PostHog — يجب ظهور events كل دقائق

### Sentry Verification (15 دقيقة):
- [ ] افتح `https://sentry.io`
- [ ] Trigger خطأ عمداً (مثلاً: `curl <domain>/api/v1/nonexistent`)
- [ ] تحقق Sentry استلم الخطأ
- [ ] أنشئ Alert Rule: Email me on any 5xx error

### UptimeRobot Setup (15 دقيقة):
- [ ] أنشئ حساب مجاني على `https://uptimerobot.com`
- [ ] Add Monitor:
  - Type: HTTPS
  - URL: `https://<your-domain>.up.railway.app/health`
  - Interval: 5 دقائق
- [ ] أضف Alert Contacts: Email + SMS
- [ ] Send Test Alert

### Definition of Done:
- [ ] PostHog: يظهر live events من الـ backend
- [ ] Sentry: alert email وصل لبريدك
- [ ] UptimeRobot: test alert وصل على الجوال

---

## 🔴 Gate 5 — First Real Lead (20 دقيقة)

### الخطوات:
- [ ] افتح `dealix_personalized_messages.md`
- [ ] اقرأ الرسالة المخصصة لـ **عبدالله العسيري / Lucidya**
- [ ] افتح LinkedIn
- [ ] ابحث عن: `Abdullah Asiri Lucidya`
- [ ] افتح profile → Connect → Add a note
- [ ] الصق الرسالة (مع قراءتها مرة أخيرة)
- [ ] اضغط Send
- [ ] سجّل في tracking sheet:

### Tracking Sheet Format:
```
| # | التاريخ | الشركة | الاسم | القناة | الحالة | ملاحظات |
|---|---------|---------|-------|---------|---------|----------|
| 1 | 2026-04-24 | Lucidya | عبدالله العسيري | LinkedIn | Sent | قرابة الاسم |
```

### Definition of Done:
- [ ] LinkedIn يُظهر ✓✓ (double check mark = delivered)
- [ ] الرسالة في tracking sheet
- [ ] Calendar reminder: Follow up after 3 days if no reply

---

## ✅ كل شي مُغلق — Launch Status: LIVE

بعد إكمال الـ 5 gates:

### ما تحقق:
- ✅ Backend يقبل traffic حقيقي
- ✅ نظام دفع حي يعمل
- ✅ Monitoring + Alerting نشط
- ✅ أول رسالة outreach مُرسلة
- ✅ Pipeline بدأ

### ما يجب أن يحدث تلقائياً:
- كل lead جديد → PostHog event
- كل error → Sentry + Email
- كل downtime → UptimeRobot SMS
- كل payment → Moyasar webhook → DB

### الخطوة التالية الأوتوماتيكية:
- اليوم 1: انتظر رد عبدالله
- اليوم 2: أرسل للـ 2 التاليين (Ahmad Al-Zaini, Nawaf Hariri)
- اليوم 3-4: أرسل للـ 2 الأخيرين (Hisham Al-Falih, Ibrahim Manna)
- اليوم 5-7: متابعة لمن لم يرد

---

## 📞 إذا علقت في أي gate

أرسل لي:
1. **رقم الـ gate** (1-5)
2. **Screenshot من الـ error**
3. **وصف ما جربته**

أحلّها خلال دقائق.

---

## 🎯 Final Rule

**لا تقل "Dealix launched" قبل الـ 5 gates كلها مُغلقة.**

Pre-launch = الحالة الحالية
Launching = الآن وأنت تنفّذ
Launched = كل الـ 5 gates DONE

**إذا ما نفّذت هذه في 72 ساعة:** لا يوجد حجة.
إما هناك blocker تقني حقيقي (نحلّه) أو تسويف (يجب مواجهته).

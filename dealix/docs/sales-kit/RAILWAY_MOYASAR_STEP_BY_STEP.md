# 🚀 Dealix — Deploy نهائي خطوة بخطوة

**وقت التنفيذ المتوقع:** 12 دقيقة بالضبط
**المطلوب منك:** لابتوب + جوال + حساب Railway + حساب Moyasar
**النتيجة:** Backend شغّال + يستقبل مدفوعات حقيقية

---

# ⏱️ الجدول الزمني

| الخطوة | المدة | الحالة |
|--------|-------|---------|
| A. Railway Start Command | 1 دقيقة | ⬜ |
| B. Railway Env Vars | 3 دقائق | ⬜ |
| C. انتظار Deploy | 2 دقيقة | ⬜ |
| D. Smoke Test | 1 دقيقة | ⬜ |
| E. Moyasar Webhook | 3 دقائق | ⬜ |
| F. اختبار 1 ريال | 2 دقيقة | ⬜ |
| **الإجمالي** | **12 دقيقة** | |

---

# 🅰️ الخطوة A — Railway Start Command

## A.1 افتح المشروع
1. روح على: **https://railway.com/project/54bb60b4-d059-4dd1-af57-bc44c702b9f0**
2. لو طلب تسجيل دخول — سجّل بحسابك

## A.2 اختر الخدمة
1. في الصفحة الرئيسية للمشروع، اضغط على **البطاقة اللي مكتوب عليها `dealix`**
2. تفتح لك صفحة تفاصيل الخدمة

## A.3 افتح Settings
1. في الشريط العلوي للخدمة، اضغط **Settings** (آخر تاب)
2. انزل لقسم **Deploy**

## A.4 عدّل Start Command
1. ابحث عن حقل **Custom Start Command**
2. **احذف** أي محتوى موجود فيه
3. **اكتب بدلاً:** `/app/start.sh`
4. اضغط خارج الحقل — يحفظ تلقائياً
5. **أو بدل الكتابة:** اترك الحقل فاضي تماماً — هذا أفضل (يستخدم الـ Dockerfile CMD الافتراضي)

### ✅ علامة النجاح
- يظهر toast أخضر: `Service updated`
- أو الحقل يحفظ بدون خطأ

---

# 🅱️ الخطوة B — Env Vars Raw Editor

## B.1 افتح Variables
1. في نفس الخدمة `dealix`، اضغط تاب **Variables**
2. في أعلى يمين الصفحة، اضغط زر **Raw Editor** (أو ⚙️ → Raw Editor)

## B.2 الصق المتغيرات
1. **امسح كل المحتوى** الحالي
2. افتح ملف `dealix_railway_vars.txt` من workspace بتاعك (الموجود من الجلسة السابقة)
3. **انسخ محتواه بالكامل والصق** في Raw Editor

### ⚠️ تذكير أمان
الملف يحتوي مفاتيحك الحية: APP_SECRET_KEY, DATABASE_URL, MOYASAR_SECRET_KEY, POSTHOG_PROJECT_KEY. لا تشاركه مع أحد.

## B.3 حفظ
1. اضغط **Update Variables** (زر أزرق أسفل النافذة)
2. Railway يبدأ redeploy تلقائياً

### ✅ علامة النجاح
- تشوف رسالة `Variables updated`
- بعد ثواني: Deploy جديد يبدأ في تاب **Deployments**

---

# 🅾️ الخطوة C — انتظر Deploy Active

## C.1 راقب Deployment
1. اضغط تاب **Deployments**
2. أعلى القائمة → الـ deployment الجديد حالته `Building` ثم `Deploying`
3. انتظر 60–120 ثانية

### ✅ علامة النجاح
- Status يصير **Active** (أخضر)
- يظهر رابط الخدمة (`https://dealix-xxxx.up.railway.app`) — **انسخه**

### ❌ علامة الفشل
- Status: `Crashed` أو `Failed`
- افتح Logs → شوف السطر الأحمر
- **أشهر الأخطاء:**
  - `port binding` → تأكد من Step A
  - `DATABASE_URL` → تحقق من Step B
  - `email-validator` → هذا مُصلح بالفعل في PR #68، لا يظهر إلا لو repo قديم

---

# 🔵 الخطوة D — Smoke Test

## D.1 جهّز المسار
1. افتح Terminal
2. `cd` إلى workspace تبعك (حيث `dealix_smoke_test.sh`)
3. **عدّل الـ URL داخل السكريبت** ليطابق رابط Railway الجديد

## D.2 شغّل
```bash
bash dealix_smoke_test.sh
```

### ✅ النتيجة المتوقعة
```
[1/5] /health ............. 200 OK ✅
[2/5] /pricing/plans ...... 200 OK ✅
[3/5] /api/v1/sectors ..... 200 OK ✅
[4/5] /docs ............... 200 OK ✅
[5/5] CORS preflight ...... 200 OK ✅

🎉 Backend جاهز للإنتاج
```

---

# 🟣 الخطوة E — Moyasar Webhook

## E.1 افتح Moyasar Dashboard
1. روح على: **https://dashboard.moyasar.com**
2. سجّل دخول

## E.2 افتح Webhooks
1. من الشريط الجانبي → **Settings** ثم **Webhooks**
2. أو رابط مباشر: **https://dashboard.moyasar.com/settings/webhooks**

## E.3 أضف Webhook
1. اضغط **+ Add Webhook** (يمين أعلى)
2. املأ النموذج:

| الحقل | القيمة |
|-------|---------|
| URL | `https://<railway-url>/api/v1/webhooks/moyasar` |
| Events | ✅ `payment_paid` ✅ `payment_failed` ✅ `payment_refunded` |
| Secret | (انسخ من ملف `dealix_railway_vars.txt` قيمة `MOYASAR_WEBHOOK_SECRET`) |
| Active | ✅ (مُفعّل) |

3. اضغط **Save**

### ⚠️ تذكير مهم
- استبدل `<railway-url>` بالرابط الحقيقي من خطوة C
- **Secret نفسه** المستخدم في Railway وإلا webhook ما يشتغل

## E.4 Test Ping
1. بعد الحفظ، اضغط على Webhook اللي أنشأته
2. اضغط **Send Test Event**
3. يجب أن يرجع **200 OK** خلال ثواني

### ✅ علامة النجاح
- Event status: `Delivered`
- إذا `Failed`: افتح Railway Logs → ابحث عن `moyasar webhook` → شوف الخطأ

---

# 🟢 الخطوة F — اختبار 1 ريال حقيقي

هذا يختبر end-to-end: Checkout → Moyasar → Webhook → DB

## F.1 جهّز بطاقة اختبار
Moyasar يوفر بطاقات test:

| النتيجة | الرقم | CVV | تاريخ |
|----------|-------|-----|-------|
| نجاح | `4111 1111 1111 1111` | `123` | `12/30` |
| فشل | `4000 0000 0000 0002` | `123` | `12/30` |

## F.2 شغّل test script
```bash
bash dealix_1_riyal_test.sh
```
(موجود في workspace، جاهز للتنفيذ)

### الخطوات داخل السكريبت
1. ينشئ invoice في `/api/v1/checkout` بمبلغ 1 ريال
2. يطبع رابط الدفع
3. تفتح الرابط في المتصفح → تدفع ببطاقة التست
4. السكريبت ينتظر webhook ثم يتحقق من DB

### ✅ علامة النجاح النهائية
- الدفع يظهر في Moyasar Dashboard
- السطر في DB: `payment.status = "paid"`
- السكريبت يطبع: `🎉 أول دفعة ناجحة`

---

# 🎯 بعد ما تنتهي

**المتحقق الآن:**
- ✅ Backend منشور على Railway
- ✅ Moyasar يرسل webhooks بنجاح
- ✅ دورة دفع كاملة end-to-end تعمل
- ✅ النظام جاهز لاستقبال فلوس حقيقية من عملاء حقيقيين

**الخطوة التالية الوحيدة:** ابدأ outreach من `dealix_leads_20_real.md`

---

# 🚨 حل المشاكل الشائعة

## المشكلة: `502 Bad Gateway` بعد Deploy
**السبب:** Railway ما عرف الـ PORT
**الحل:** في Settings → Deploy → تأكد إن Start Command إما فاضي أو `/app/start.sh`. لا تضع `python -m uvicorn` مباشرة.

## المشكلة: Webhook يرجع `401 Unauthorized`
**السبب:** Secret في Moyasar مختلف عن Railway
**الحل:** قارن `MOYASAR_WEBHOOK_SECRET` في Railway Variables مع Secret في Moyasar Webhook → يجب أن يتطابقان حرفياً.

## المشكلة: `database connection failed`
**السبب:** Railway Postgres addon غير مفعّل أو DATABASE_URL تغيّر
**الحل:** في Railway → أضف PostgreSQL service → انسخ `${{Postgres.DATABASE_URL}}` في Variables.

## المشكلة: Smoke test يرجع 404 على كل endpoint
**السبب:** الخدمة غير publicly accessible
**الحل:** في Settings → Networking → فعّل **Public Networking** (Generate Domain).

---

# 📞 إذا حصلت مشكلة

أرسل لي:
1. Screenshot من Railway Deployments → Logs (آخر 50 سطر)
2. Screenshot من Moyasar Dashboard → Webhooks (آخر event)
3. الرسالة الخطأ بالضبط

أقدر أحلّها خلال دقائق بدل ما تقضي ساعات.

---

**آخر نصيحة:** لا توقف في الـ deploy. لو حصلت مشكلة لأكثر من 30 دقيقة — انتقل مباشرة لـ outreach في نفس الوقت. بناء الـ pipeline الصباحي أهم من إصلاح bug صباحي.

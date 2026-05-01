# 🚀 Dealix — حزمة الإقفال النهائية

**الحالة:** كل ما يمكنني تنفيذه برمجياً — تم. يتبقى **3 خطوات يدوية** عليك فقط (تحتاج تسجيل دخول شخصي).

**آخر تحديث:** 23 أبريل 2026، 5:57م +03

---

## ✅ ما تم تنفيذه تلقائياً هذه الجلسة

### 1. Backend جاهز للبيع
- ✅ PR #69 مدموج: `/app/start.sh` wrapper (يحل خطأ Railway port)
- ✅ PR #70 مدموج: `/api/v1/public/demo-request` (landing form → Calendly)
- ✅ `/api/v1/checkout` يولّد Moyasar invoice قابل للدفع (كان موجود مسبقاً)
- ✅ `/api/v1/webhooks/moyasar` يستقبل تأكيد الدفع ويطلق PostHog events
- ✅ `/api/v1/pricing/plans` يعرض الباقات (Starter 999 / Growth 2,999 / Scale 7,999 ريال)
- ✅ CI كاملة خضراء على main

### 2. Landing محدّث ومنشور
- ✅ Form يرسل لـ `/api/v1/public/demo-request`
- ✅ بعد submit → redirect تلقائي لـ Calendly
- ✅ `window.DEALIX_API_BASE` يشير لـ Railway backend
- ✅ منشور جديد على pplx.app (تم مشاركته في هذه الجلسة)

### 3. Outreach package جاهز
- ✅ 3 نسخ رسائل (SaaS / Enterprise / Distribution)
- ✅ نسخة بريد + جدول tracking + قواعد المتابعة
- ✅ سيناريو تحويل من demo → pilot 1 ريال → Starter 999 ريال

---

## 🔴 3 خطوات يدوية (10 دقائق) لتصير دفعة حقيقية

### الخطوة 1 — Railway Settings (3 دقائق)

1. افتح: https://railway.com/project/54bb60b4-d059-4dd1-af57-bc44c702b9f0
2. اختر خدمة `dealix` → **Settings** → **Deploy**
3. **Start Command**: امسحه بالكامل (يستخدم Dockerfile CMD = `/app/start.sh`)
4. اذهب لـ **Variables** → **Raw Editor**
5. افتح الملف `dealix_railway_vars` والصق محتواه كامل
6. **Save** — Railway سيعيد النشر تلقائياً

**تحقق:** بعد 90 ثانية، افتح Deployments → آخر deploy يكون **Active** (أخضر)

### الخطوة 2 — Moyasar Webhook (دقيقتين)

1. افتح: https://dashboard.moyasar.com/webhooks
2. انسخ Railway URL (من Service Settings → Networking → Public Domain)
3. **Add Webhook**:
   - **URL:** `https://<railway-url>/api/v1/webhooks/moyasar`
   - **Events:** `payment_paid`, `payment_failed`, `payment_refunded`
   - **Secret:** قيمة `MOYASAR_WEBHOOK_SECRET` (محفوظة في Railway vars منفصلاً — لا تدفعها لـ Git)
4. **Save**

**تحقق:** Moyasar يرسل ping اختباري → يرجع 200

### الخطوة 3 — تحديث Landing بـ Railway URL (دقيقة)

بعد ما Railway ينشر، شوف الـ public domain. إذا مختلف عن `dealix-production.up.railway.app`:

1. افتح: `/home/user/workspace/dealix-clean/landing/index.html`
2. غيّر السطر:
   ```html
   window.DEALIX_API_BASE = 'https://dealix-production.up.railway.app';
   ```
   لعنوان Railway الفعلي
3. قلي "أعد نشر landing" وسأعيد النشر خلال ثواني

---

## 🧪 اختبار دورة البيع الكاملة (5 دقائق)

بعد إكمال الـ 3 خطوات:

```bash
# 1. Health check
bash /home/user/workspace/dealix_smoke_test.sh

# 2. Pricing check
curl https://<railway-url>/api/v1/pricing/plans

# 3. Test demo request
curl -X POST https://<railway-url>/api/v1/public/demo-request \
  -H "Content-Type: application/json" \
  -d '{"name":"سامي تجربة","company":"Test","email":"test@dealix.me","phone":"+966500000000","consent":true}'

# 4. Test Moyasar checkout (1 SAR pilot)
curl -X POST https://<railway-url>/api/v1/checkout \
  -H "Content-Type: application/json" \
  -d '{"plan":"pilot_1sar","email":"you@dealix.me"}'
```

التوقع: الـ 4 ترجع 200 + `payment_url` قابلة للفتح في متصفح. افتحها وادفع 1 ريال بكارتك → ✅ أول دفعة حقيقية.

---

## 💰 مسار الإيراد من الآن

### هذا الأسبوع (7 أيام)
1. **اليوم:** نفّذ الـ 3 خطوات أعلاه + دفع 1 ريال تجريبي (يثبت النظام شغّال)
2. **غداً:** استخدم `dealix_day1_outreach` → ابعت 20 رسالة
3. **يوم 3-5:** 5 demos محجوزة
4. **يوم 6-7:** 1-2 pilot بـ 1 ريال

### الأسبوع الثاني (يوم 8-14)
1. **pilot → Starter conversion** — أول 999 ريال
2. تابع 30 lead جديد
3. الهدف: **3 عملاء مدفوعين × 999 = 2,997 ريال/شهر MRR**

### تذكير — Feature Freeze 14 يوم
- ❌ لا Next.js frontend
- ❌ لا dashboard جديد
- ❌ لا auth flows
- ✅ Operation + Sell + Measure فقط

بعد أول 3 عملاء مدفوعين → نقرر هل نبني dashboard أو نزيد 10 عملاء أولاً.

---

## 📦 الملفات المسلمة هذه الجلسة

| الملف | الوصف |
|-------|-------|
| `dealix_final_closeout` | هذا الملف — خريطة الإقفال |
| `dealix_railway_vars` | env vars كاملة للصق في Railway |
| `dealix_smoke_test` | سكريبت اختبار بعد redeploy |
| `dealix_day1_outreach` | رسائل + قواعد outreach |
| `dealix-clean/landing` | Landing منشور مع backend hook |

---

## ⚠️ ما لم أستطع تنفيذه (لأنه يتطلب دخولك الشخصي)

| الإجراء | لماذا يحتاج منك | الوقت |
|---------|----------------|------|
| Railway UI (Start Command + Vars) | dashboard بتسجيل دخولك | 3 دقائق |
| Moyasar webhook setup | dashboard بتسجيل دخولك | 2 دقائق |
| Outreach فعلي (إرسال رسائل) | WhatsApp/LinkedIn بحسابك | 2 ساعة |
| Demos live | تحتاج أنت في المكالمة | 30 د لكل demo |

**كل شي غير هذا — جاهز. البيع الآن مسؤوليتك فقط.**

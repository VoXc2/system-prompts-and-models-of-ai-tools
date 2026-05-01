# 💳 Dealix — Moyasar Hosted Checkout (بدون Backend)

**المشكلة:** Railway backend لسه غير منشور، ما تقدر تستقبل payments عبر API.
**الحل:** Moyasar يوفّر **hosted invoices** — رابط دفع جاهز بدون أي code.
**الوقت:** 5 دقائق setup، ثم تستقبل فلوس فوراً.

---

## 🚀 الطريقة 1 — Moyasar Invoices API (الأسرع)

### الخطوة 1: تأكد حسابك Moyasar verified
1. افتح: https://dashboard.moyasar.com
2. Settings → Business → تأكد من:
   - ✅ CR uploaded (أو وثيقة عمل حر)
   - ✅ Bank account linked
   - ✅ Account active

### الخطوة 2: أنشئ Invoice يدوياً (UI)
1. Moyasar Dashboard → Invoices → **Create Invoice**
2. املأ:
   - **Amount:** `1.00 SAR` (للـ pilot) أو `999.00` (Starter)
   - **Description:** `Dealix Pilot — 7 days`
   - **Customer email:** email العميل
   - **Expires:** 7 days
3. Save → احصل على:
   - **Invoice ID:** `inv_xxxx`
   - **Payment URL:** `https://invoice.moyasar.com/invoices/inv_xxxx`

### الخطوة 3: أرسل الرابط للعميل
عبر WhatsApp / Email / LinkedIn:
```
رابط الدفع: https://invoice.moyasar.com/invoices/inv_xxxx
المبلغ: 1 ريال
مدة Pilot: 7 أيام
استرداد: كامل لو ما أعجبك
```

**النتيجة:** العميل يدفع → Moyasar يخبرك → الفلوس تصل بنكك خلال 24 ساعة.

---

## 🔄 الطريقة 2 — Invoice API via curl (للأتمتة الخفيفة)

استخدمها لو تبغى توليد روابط من CLI بدون backend كامل:

```bash
# Set your keys
export MOYASAR_SECRET=sk_live_xxxxxxxxx   # من Moyasar Dashboard → API Keys

# Create an invoice for 1 SAR pilot
curl -X POST https://api.moyasar.com/v1/invoices \
  -u "$MOYASAR_SECRET:" \
  -d "amount=100" \
  -d "currency=SAR" \
  -d "description=Dealix Pilot — 7 days (1 SAR refundable)" \
  -d "callback_url=https://voxc2.github.io/dealix/thank-you.html" \
  -d "metadata[plan]=pilot" \
  -d "metadata[customer_email]=$CUSTOMER_EMAIL"
```

**Response مثال:**
```json
{
  "id": "inv_abc123",
  "amount": 100,
  "url": "https://invoice.moyasar.com/invoices/inv_abc123",
  "status": "initiated"
}
```

**انسخ `url` → أرسله للعميل.**

---

## 📝 قوالب Invoices الجاهزة

### Pilot (1 ريال)
```bash
curl -X POST https://api.moyasar.com/v1/invoices \
  -u "$MOYASAR_SECRET:" \
  -d "amount=100" \
  -d "currency=SAR" \
  -d "description=Dealix Pilot — تجربة 7 أيام (قابل للاسترداد)"
```

### Starter (999 ريال)
```bash
curl -X POST https://api.moyasar.com/v1/invoices \
  -u "$MOYASAR_SECRET:" \
  -d "amount=99900" \
  -d "currency=SAR" \
  -d "description=Dealix Starter — اشتراك شهر أول"
```

### Growth (2,999 ريال)
```bash
curl -X POST https://api.moyasar.com/v1/invoices \
  -u "$MOYASAR_SECRET:" \
  -d "amount=299900" \
  -d "currency=SAR" \
  -d "description=Dealix Growth — اشتراك شهر أول (4-10 مندوبين)"
```

### Scale (7,999 ريال)
```bash
curl -X POST https://api.moyasar.com/v1/invoices \
  -u "$MOYASAR_SECRET:" \
  -d "amount=799900" \
  -d "currency=SAR" \
  -d "description=Dealix Scale — اشتراك شهر أول (Enterprise)"
```

**ملاحظة:** المبلغ في Moyasar API بالـ **halalas** (1 SAR = 100 halalas).

---

## 🔔 Webhook بدون Backend

لأتمتة basic (تنبيه عند الدفع):

### الخيار 1 — Zapier (5 دقائق setup)
1. https://zapier.com → Create Zap
2. Trigger: **Webhooks by Zapier** → Catch Hook
3. انسخ Webhook URL
4. في Moyasar Dashboard → Webhooks → أضف الرابط
5. Action: Send you Email/WhatsApp/Slack عند كل دفعة

### الخيار 2 — Discord/Slack webhook مباشر
Moyasar يدعم webhooks مباشرة. أرسل إشعار لـ Slack:
1. Slack → Incoming Webhooks → Create
2. Moyasar → Webhooks → paste Slack URL

**النتيجة:** إشعار فوري على كل دفعة بدون أي code.

---

## 💰 Flow كامل (Live الآن بدون Railway)

```
1. عميل يفتح: https://voxc2.github.io/dealix/pricing.html
   ↓
2. يختار "Pilot 1 ريال"
   ↓
3. يضغط الـ CTA → (رابط تواصل معك على WhatsApp/Calendly)
   ↓
4. أنت تنشئ invoice يدوياً (30 ثانية)
   ↓
5. ترسل الرابط للعميل عبر WhatsApp
   ↓
6. العميل يدفع → Moyasar يرسل webhook لـ Zapier
   ↓
7. Zapier يرسل لك WhatsApp/Email
   ↓
8. تتواصل مع العميل، تبدأ onboarding manually
   ↓
9. الفلوس تصل بنكك خلال 24 ساعة
```

**ما يحتاج:** Railway، backend، API، كود.
**يحتاج:** Moyasar account + 5 دقائق setup + رد سريع.

---

## 📊 Track Payments يدوياً

حتى backend يصير live، استخدم Google Sheet بسيط:

| التاريخ | العميل | الشركة | المبلغ | Invoice ID | Status | Plan |
|---------|---------|---------|---------|------------|---------|------|
| 2026-04-24 | عبدالله | Lucidya | 1 SAR | inv_abc123 | paid | pilot |
| ... | ... | ... | ... | ... | ... | ... |

---

## 🎯 الخلاصة

**الواقع:** تقدر تستلم أول 10 عملاء بدون Railway deploy.
**الطريقة:** Moyasar hosted invoices + manual onboarding.
**الميزة:** تركّز على البيع + Customer Success، ما تنشغل في deploy.
**متى Railway:** بعد أول 5-10 عملاء (لما الأتمتة تصير قيمة حقيقية).

**الآن:**
1. افتح Moyasar dashboard
2. Create invoice تجريبي 1 ريال بـ email نفسك
3. افتح الرابط + ادفع ببطاقتك
4. تأكد الفلوس وصلت بنكك

**هذا Launch حقيقي.** Railway يصير polish لاحقاً.

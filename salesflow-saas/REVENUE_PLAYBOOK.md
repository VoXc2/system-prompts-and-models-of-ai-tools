# Dealix — Revenue Playbook

## المطلوب قبل البدء
- [ ] Railway deploy شغّال (`curl https://api.dealix.me/health` → `{"status":"ok"}`)
- [ ] SMTP_USER + SMTP_PASSWORD في Railway env vars
- [ ] GREEN_API_INSTANCE_ID + GREEN_API_TOKEN في Railway env vars

## اليوم 1: التفعيل

```bash
# 1. تأكد كل شي شغّال
API_BASE=https://api.dealix.me bash scripts/go_live.sh

# 2. ازرع أول 20 draft (10 email + 10 WhatsApp)
cd salesflow-saas/backend && python scripts/seed_first_batch.py

# 3. شوف الـ drafts
curl https://api.dealix.me/api/v1/drafts?status=draft | python3 -m json.tool

# 4. وافق عليهم
curl -X POST https://api.dealix.me/api/v1/drafts/approve-batch \
  -H "Content-Type: application/json" -d '{"batch_id":"BATCH_ID"}'

# 5. ارسل أول 5 إيميلات
curl -X POST "https://api.dealix.me/api/v1/drafts/send-approved-batch?channel=email&batch_size=5"
```

## اليوم 2-3: المتابعة

```bash
# شوف لو في ردود
curl https://api.dealix.me/api/v1/followups/due | python3 -m json.tool

# ولّد follow-ups تلقائياً
curl -X POST https://api.dealix.me/api/v1/followups/generate

# ارسل ثاني 5 إيميلات
curl -X POST "https://api.dealix.me/api/v1/drafts/send-approved-batch?channel=email&batch_size=5"
```

## اليوم 4-7: التوسيع

```bash
# ولّد 10 targets جديدة
curl -X POST https://api.dealix.me/api/v1/automation/daily-pipeline/run \
  -H "Content-Type: application/json" \
  -d '{"sectors":["real_estate","saas","agency"],"daily_target_count":10}'

# كرر: review → approve → send
```

## لما أحد يرد "مهتم"

```bash
# صنّف الرد
curl -X POST https://api.dealix.me/api/v1/automation/reply/classify \
  -H "Content-Type: application/json" -d '{"reply_text":"مهتم أبي أجرب"}'

# الرد التلقائي: يقترح demo
# أنت: احجز 10 دقائق (استخدم scripts/demo_script.md)
# بعد الـ demo: أرسل رابط الدفع
```

## لما أحد يوافق على Pilot

```bash
# أنشئ checkout link
curl -X POST https://api.dealix.me/api/v1/pricing/checkout \
  -H "Content-Type: application/json" \
  -d '{"plan_id":"pilot","customer_name":"اسم العميل","customer_email":"email@company.com","customer_phone":"966XXXXXXXXX"}'
```

## الجدول اليومي (بتوقيت السعودية)

| الوقت | المهمة |
|-------|--------|
| 09:00 | `daily_cycle.sh morning` — ولّد targets + drafts |
| 09:30 | راجع الـ drafts + عدّل لو لازم |
| 10:00 | وافق + ارسل أول batch (5 إيميلات) |
| 12:00 | ارسل ثاني batch (5 إيميلات) |
| 16:00 | `daily_cycle.sh afternoon` — follow-ups |
| 16:30 | شيك الردود + رد على المهتمين |

## الأهداف الأسبوعية

| الأسبوع | الهدف |
|---------|-------|
| 1 | 20 رسالة مرسلة، 3+ ردود، 1 demo |
| 2 | 40 رسالة، 5+ ردود، 2 demos، 1 pilot |
| 3 | 60 رسالة، أول 499 ريال (pilot) |
| 4 | أول 990 ريال/شهر (subscription) |

## Safety Rules
- إيميل: max 15/يوم أول أسبوع
- واتساب: max 10/يوم أول أسبوع
- كل رسالة فيها opt-out
- لو أحد قال "إيقاف" → لا ترسل له أبداً

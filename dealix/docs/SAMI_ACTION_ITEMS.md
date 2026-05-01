# Dealix — مطلوب من سامي (Action Items)

**آخر تحديث:** 2026-04-23 بعد deploy PR #54 + PR #55
**الحالة:** 16/30 launch gates مغلقة. 4 gates blocked على credentials منك.

---

## 🔴 P0 — blockers تمنع الـ E2E التجاري

هذه الـ 4 مفاتيح كل واحد يفتح gate واحد ضروري لإطلاق حقيقي:

### 1. PostHog API Key → يفتح **O3** (funnel tracking)

**المطلوب:** مفتاح بصيغة `phc_XXXXXXXXXXXXX...` من PostHog Cloud EU (app.posthog.com).

**كيف تجيبه (3 دقائق):**
1. ادخل https://app.posthog.com (أو eu.posthog.com إذا أنشأت حساب EU)
2. Project Settings → API Keys
3. انسخ الـ "Project API Key" (مو الـ Personal API Key)
4. أرسله هنا

**وش نستخدمه:** أول حدث حقيقي في الـ funnel (LEAD_CAPTURED, CHECKOUT_STARTED, PAYMENT_SUCCEEDED). بدونه، كود الـ analytics جاهز بس ما يرسل شي.

---

### 2. Moyasar Secret Key → يفتح **G2** (checkout)

**المطلوب:** مفتاح بصيغة `sk_test_XXX...` (للاختبار) أو `sk_live_XXX...` (للإنتاج).

**كيف تجيبه:**
1. ادخل https://moyasar.com → Dashboard
2. Settings → API Keys
3. انسخ Secret Key (مو Publishable)
4. أرسله هنا + أخبرني test أو live

**وش نستخدمه:** إنشاء invoice حقيقي بـ 1 SAR (plan = `pilot_1sar`)، ندفع فيه كتجربة، نتحقق من webhook signature + idempotency في الإنتاج. هذا هو G2 gate.

---

### 3. HubSpot Private App Token → يفتح **G3** (lead pipeline)

**المطلوب:** token بصيغة `pat-XXX...` من Private App.

**كيف تجيبه:**
1. ادخل HubSpot → Settings → Integrations → Private Apps
2. أنشئ Private App جديد (أو استخدم الموجود)
3. Scopes المطلوبة: `crm.objects.contacts.read`, `crm.objects.contacts.write`, `crm.objects.deals.read`, `crm.objects.deals.write`
4. انسخ Access Token

---

### 4. Calendly Personal Access Token → يفتح **G3** (lead pipeline)

**المطلوب:** PAT من Calendly Developer Portal.

**كيف تجيبه:**
1. ادخل https://calendly.com/integrations/api_webhooks
2. Generate New Token
3. انسخ الـ PAT

---

### 5. UptimeRobot API Key → يفتح **I3** (status page)

**المطلوب:** مفتاح `ur1234567-abcdef...` من Main API Key.

**كيف تجيبه:**
1. ادخل https://uptimerobot.com → My Settings → API Settings
2. استخدم Main API Key (مو Monitor-specific)

**وش نستخدمه:** سكريبت `scripts/infra/setup_uptimerobot.sh` الجاهز يضبط monitors وصفحة عامة تلقائياً.

---

## 🟡 P1 — اختياري لكن يسرّع الإطلاق

### 6. Real test lead
شخص حقيقي (أنت أو صديق) يروح يحجز على Calendly + يدفع 1 SAR. هذا يغلق G3 + G5 مرة واحدة.

### 7. تأكيد DNS
حالياً `dealix.me` ما يشير للسيرفر (`188.245.55.180`). تأكد GoDaddy DNS A-record صحيح.

---

## ✅ ما تسويه أنت الآن (ما يحتاج مني شي)

### أقدر أكمل بدون blockers:
- [x] ~~PR #55 pricing/plans public + middleware 401 fix~~ **MERGED**
- [ ] Redeploy PR #55 للسيرفر (نفس runbook scenario 1)
- [ ] T6: k6 load test ضد prod (يحتاج API_BASE + API_KEY من `.env` السيرفر)
- [ ] T7: Rollback dry-run drill موثق
- [ ] T5 النهائي: DLQ fault-injection E2E
- [ ] O5: SLO skeleton
- [ ] I1: مراجعة RUNBOOK.md + إضافة توقيع Sami في Appendix C

### حالة الـ Launch Gates الحالية (16/30):

```
Technical:     ██████░░ 6/8
Security:      █████░░  5/7
Observability: ██░░░░░  2/5   ← blocked على PostHog
GTM:           █░░░░░   1/5   ← blocked على Moyasar + HubSpot + Calendly
Support:       ░░░░     0/4   ← partially blocked على UptimeRobot
Governance:    ██       2/2 ✅
Recovery:      █░░      1/3
```

---

## Next Step من عندك

أسرع مسار للإطلاق الحقيقي (paid deal):
1. أرسل **PostHog + Moyasar** أولاً → يفتحان O3 + G2 (أسرع gates)
2. أرسل **HubSpot + Calendly** → يفتحان G3 (يحتاج real lead)
3. أرسل **UptimeRobot** → يفتح I3

بعد هذي الـ 4 → نصل **22-24/30 gates** خلال يومين، وباقي فقط الـ commercial (G4, G5).

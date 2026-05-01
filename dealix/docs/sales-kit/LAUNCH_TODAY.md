# 🚀 Dealix — قائمة التدشين النهائية (اليوم)

**الهدف:** من "Launch-Ready in Docs" إلى "Launch-Live in Market" خلال 4 ساعات فعلية.

---

## ⏱️ 4-Hour Launch Sprint

### الساعة 1: Backend LIVE (الأولوية القصوى)

#### Step 1.1 — Railway (15 دقيقة)
1. افتح: `https://railway.com/project/54bb60b4-d059-4dd1-af57-bc44c702b9f0`
2. Settings → Deploy → Start Command: **امسحه** أو اكتب `/app/start.sh`
3. Variables → Raw Editor → الصق من `dealix_railway_vars.txt`
4. Settings → Networking → Generate Public Domain
5. انتظر Deploy = `Active`

**Verification:**
```bash
curl https://<your-domain>/api/v1/pricing/plans
# Must return JSON with plans
```

#### Step 1.2 — Add /healthz (5 دقائق)
افتح `api/routers/health.py` في المستودع، أضف المحتوى من:
[dealix_healthz_patch.py](dealix_healthz_patch.py)

Commit + push → CI يعيد النشر تلقائياً.

**Verification:**
```bash
curl https://<your-domain>/healthz
# Must return: {"status":"ok","service":"dealix"}
```

#### Step 1.3 — Moyasar Webhook (10 دقائق)
1. افتح `https://dashboard.moyasar.com/webhooks`
2. Add Webhook:
   - URL: `https://<your-domain>/api/v1/webhooks/moyasar`
   - Secret: نفس قيمة `MOYASAR_WEBHOOK_SECRET` في Railway
   - Events: `payment_paid`, `payment_failed`, `payment_refunded`
3. Send Test Event → يجب أن يرجع 200 في Railway logs

#### Step 1.4 — 1 SAR E2E Test (15 دقيقة)
```bash
bash dealix_1_riyal_test.sh https://<your-domain>
```
- يولّد invoice 1 ريال
- ادفع ببطاقتك الحقيقية (أو test card: 4111 1111 1111 1111)
- تحقق: payment في Moyasar ✅ + webhook في logs ✅ + record في DB ✅

#### Step 1.5 — Rotate Moyasar Secret (5 دقائق)
⚠️ **مهم:** الـ secret كان مسرّب في git history سابقاً.
1. Moyasar dashboard → API Keys → **Rotate Secret**
2. Update في Railway Variables فوراً
3. Update Moyasar Webhook Secret أيضاً

---

### الساعة 2: Monitoring LIVE

#### Step 2.1 — Sentry → Slack (15 دقيقة)
1. افتح Sentry → Settings → Integrations → Slack
2. Connect workspace
3. Alert Rules → New Alert:
   - Condition: `event.level == "error"`
   - Action: Notify Slack channel `#dealix-alerts`
4. Trigger test: `curl https://<domain>/_test_sentry`
5. تأكد الـ alert وصل Slack

#### Step 2.2 — UptimeRobot (10 دقائق)
1. `https://uptimerobot.com` → Signup (free)
2. Add New Monitor:
   - Type: HTTPS
   - URL: `https://<your-domain>/healthz`
   - Interval: 5 minutes
   - Alert: Email + SMS
3. Send Test Alert → تأكد وصل جوالك

#### Step 2.3 — PostHog Verification (15 دقيقة)
1. Add `posthog_snippet.html` content to `landing/index.html` (replace `YOUR_POSTHOG_KEY`)
2. Apply same to `marketers.html`, `pricing.html`, `partners.html`
3. Open landing page in browser
4. Check PostHog dashboard → Live events → يجب ظهور `$pageview`

#### Step 2.4 — Add robots.txt + sitemap.xml (5 دقائق)
1. Copy `dealix_robots.txt` to `landing/robots.txt`
2. Copy `dealix_sitemap.xml` to `landing/sitemap.xml`
3. Commit + push to deploy

---

### الساعة 3: Outreach LIVE

#### Step 3.1 — First LinkedIn DM (15 دقيقة)
1. افتح LinkedIn
2. ابحث: `Abdullah Asiri Lucidya`
3. Open profile → Message (لو متصلين) أو Connect with note
4. الصق الرسالة من `dealix_personalized_messages.md` (المخصصة له)
5. **قبل Send:** اقرأها مرة أخيرة، تأكد من اسمه ومنصبه صحيح
6. Send

#### Step 3.2 — Log in Tracking (5 دقائق)
افتح `dealix_14day_tracker.html` في المتصفح:
- Pipeline → Lucidya row → check "أُرسل"
- ملاحظات: "قرابة الاسم — رسالة مخصصة"

#### Step 3.3 — Schedule Follow-ups (5 دقائق)
Calendar reminders:
- يوم +3: Follow-up #1 ("رسالتي قبل 3 أيام")
- يوم +7: Value-add (إحصائية Gartner)
- يوم +11: Case snippet
- يوم +15: Strategic question

#### Step 3.4 — LinkedIn Post #1 (30 دقيقة)
انشر Post اليوم 1 من `dealix_content_calendar.md`:
- Hook: "أنا سامي. قررت أبني AI sales rep بالعربي الخليجي..."
- End: اطلب متابعة + like

---

### الساعة 4: Partner/Marketers LIVE

#### Step 4.1 — Deploy Landing Pages (20 دقيقة)
الخيار 1 — Vercel (الأسرع):
```bash
npm i -g vercel
cd landing/
vercel --prod
```

الخيار 2 — Netlify:
- Drag & drop `landing/` folder at netlify.com
- Custom domain → `dealix.ai`

التحقق:
- `https://dealix.ai/` → index.html loads
- `https://dealix.ai/marketers` → marketers.html
- `https://dealix.ai/pricing` → pricing.html
- `https://dealix.ai/partners` → partners.html

#### Step 4.2 — Partner Form → Formspree (10 دقيقة)
1. `https://formspree.io` → Create account → New Form
2. Copy Form ID
3. Replace `YOUR_ID` in `partners.html` action URL
4. Test submission → email arrives

#### Step 4.3 — Google Search Console (10 دقيقة)
1. `https://search.google.com/search-console`
2. Add property: `https://dealix.ai`
3. Verify via DNS TXT record
4. Submit sitemap: `https://dealix.ai/sitemap.xml`
5. Request indexing for key pages

#### Step 4.4 — First Partner Outreach (20 دقيقة)
من `dealix_agency_partnerships.md` — Tier 2:
- Peak Content (LinkedIn DM للـ founder)
- Digital8 (email intro)

---

## ✅ End-of-Sprint Verification

بعد 4 ساعات، كل هذه يجب أن تكون TRUE:

- [ ] `curl https://<domain>/api/v1/pricing/plans` = 200 JSON
- [ ] `curl https://<domain>/healthz` = 200 OK
- [ ] Moyasar dashboard يظهر test payment 1 SAR
- [ ] Sentry alert في Slack (من `_test_sentry`)
- [ ] UptimeRobot alert في SMS/Email
- [ ] PostHog يظهر live events
- [ ] `https://dealix.ai` يفتح ويلود
- [ ] LinkedIn DM للـ عبدالله العسيري مُرسل (double check mark)
- [ ] LinkedIn post publicly visible
- [ ] First partner email/DM sent

**إذا كل الـ 10 = TRUE → Dealix launched.** 🎉

**إذا أقل من 7 = TRUE → لا زلت في Pre-Launch.** عد للخطوات الناقصة.

---

## 📊 بعد الساعة 4: Monitor للـ 24 ساعة التالية

### Dashboard الفحص اليومي (5 دقائق/ساعة لـ 24 ساعة):
1. PostHog → live events (يجب > 0)
2. Moyasar → transactions (watching for first real customer)
3. Sentry → errors (should be 0 for stable run)
4. UptimeRobot → uptime (should be 100%)
5. LinkedIn → notifications (waiting for reply)

### Action triggers:
- لو Sentry error → fix خلال ساعة
- لو UptimeRobot downtime → restart Railway service
- لو lead replied → respond within 30 minutes
- لو partner interested → book meeting within 24 hours

---

## 🚨 إذا حصل مشكلة

### المشكلة: Railway deploy fails
**الحل:**
1. افتح Logs في Railway Deployments
2. ابحث عن أول ERROR line
3. أرسل لي screenshot → أحلّها

### المشكلة: Moyasar test payment fails
**الحل:**
1. تحقق merchant account status في Moyasar dashboard
2. تحقق API keys صحيحة
3. جرّب test card قبل بطاقتك الحقيقية

### المشكلة: CI red on GitHub
**الحل:**
1. `git log` — آخر commit
2. Actions tab → failed run → read error
3. أرسل error message → أحلّها

### المشكلة: Abdullah Asiri ما رد بعد 7 أيام
**الحل:**
- طبيعي — 40% معدل رد بعد الـ follow-up #1
- أرسل رسالة #2 من `dealix_followup_cadence.md`
- أكمل outreach لـ 4 الآخرين (Ahmad, Nawaf, Hisham, Ibrahim)

---

## 🎯 Final Truth

**Dealix اليوم:**
- ✅ كود موجود (72 PRs)
- ✅ محتوى موجود (50+ files)
- ✅ استراتيجية موجودة
- ❌ ليس live في السوق

**Dealix بعد 4 ساعات من الآن (لو نفذت):**
- ✅ Live backend
- ✅ Live payments
- ✅ Live monitoring
- ✅ Live landing page
- ✅ First outreach sent

**الفرق = 4 ساعات.**

**ابدأ الآن: Step 1.1.**

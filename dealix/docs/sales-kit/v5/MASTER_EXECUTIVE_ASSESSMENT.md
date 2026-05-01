# Dealix — Master Executive Assessment
> Operating under the Master Executive Operator Constitution
> Date: 2026-04-23 | Phase: Primitive Launch Completion

---

## 1) Executive Summary

**Where we are**: Dealix هو **code-complete تقنيًا** لكنه **ليس launch-ready تجاريًا** بعد.
البنية التحتية موجودة (FastAPI + Streamlit + Railway + CI + Sentry + PostHog + Moyasar client). لكن **مسار الإيراد الفعلي (lead → booking → paid invoice) غير موصول end-to-end بعد**، و**صفحة المسوقين/الوكالات لم تُنشر على الموقع الأساسي بعد**، و**alerts حقيقية لم تُفعّل** (Sentry مُعدّ لكن لا توجد قنوات تنبيه متصلة).

**القرار التنفيذي الآن**: نغلق Launch Gaps P0 أولاً (CI + alerts + payment E2E)، ثم ننشر marketers.html على الموقع، ثم نفعّل Partner Motion يدويًا (قبل أي أتمتة)، ثم نبدأ outreach حقيقي. لا نبني أي feature جديدة قبل إتمام هذه السلسلة.

---

## 2) Current Launch Assessment

### A. Product
| البند | الحالة | الدليل |
|---|---|---|
| API (FastAPI) live | ✅ جاهز | `api/main.py` + Railway deployment |
| Dashboard (Streamlit) | ✅ جاهز | `dashboard/pages/*.py` — 6 pages |
| Landing (ar) | ✅ جاهز | `landing/index.html` |
| Marketers page | 🟡 **مبنية لكن غير منشورة** | `sales_kit_v5/marketers.html` — لم تُرفع إلى `landing/` |
| Pricing page access | ❌ **غير موجود مرئياً** | لا يوجد `/pricing` علني |
| Booking flow | 🟡 جزئي | Calendly link موجود، لا webhook |
| Self-service signup | ❌ غير موجود | كل شيء يدوي عبر demo |

### B. Operations
| البند | الحالة | الدليل |
|---|---|---|
| CI green | ❌ **فاشل الآن** | Black formatting على 5 ملفات (مُصلَح في هذا PR) |
| Sentry SDK | ✅ مُعدّ | `dealix/observability/sentry.py` |
| Sentry alerts wired | ❌ **لا قنوات تنبيه** | DSN فقط، لا Slack/email routing |
| DLQ + retry | ✅ موجود | `dealix/reliability/dlq.py`, `retry.py` |
| DLQ drain/replay | 🟡 موجود كود غير مختبر تحت حمل | لا drill موثّق |
| Backups | ❌ غير موثّق | لا runbook |
| Restore drill | ❌ **لم يُجرَّب** | |
| Webhook signatures | ✅ موجود | `api/security/webhook_signatures.py` |
| Moyasar webhook secret rotated | ❌ **لم يُدار** | المستخدم يعرف، لم يُنفَّذ |
| Incident runbook | 🟡 جزئي | `DEPLOYMENT.md` فقط |

### C. Commercial / Revenue
| البند | الحالة | الدليل |
|---|---|---|
| Moyasar Payments API integrated | ✅ | `dealix/payments/moyasar.py` |
| Moyasar Invoices API integrated | ✅ | `create_invoice()` موجودة |
| Payment webhook handler | ✅ موجود | `api/routers/webhooks.py` |
| Payment → CRM sync | ❌ **غير موصول** | webhook يستقبل لكن لا update لـ lead status |
| 1 SAR test paid | ❌ **لم يُنفَّذ** | |
| First real invoice issued | ❌ | |
| ZATCA compliance plan | 🟡 موجود كمخطط | لم يُطبَّق |
| Pilot agreement signed | ❌ | template موجود فقط |
| First paying customer | ❌ | 0 leads, 0 paid |

### D. Measurement
| البند | الحالة | الدليل |
|---|---|---|
| PostHog SDK | ✅ مُعدّ | `dealix/analytics/posthog_client.py` |
| Events fired server-side | 🟡 بعض النقاط | lead_created, webhook_received |
| Landing page events | ❌ **غير مفعّلة** | لا PostHog snippet في `landing/index.html` |
| Funnel dashboard | ❌ | لا dashboard منشور |
| Conversion tracking | ❌ | |
| Weekly KPI review | ❌ | |

### E. Governance
| البند | الحالة | الدليل |
|---|---|---|
| Approval flows | ✅ موجود | `dashboard/pages/3_Approvals.py` |
| Audit log | ✅ موجود | `dashboard/pages/6_Audit.py` |
| Outbound rate limits | 🟡 جزئي | per-integration config |
| Partner permissions | ❌ غير موجود | لا نظام partners حالياً |

---

## 3) What Must Be Closed First (P0 Launch Gates)

1. **CI أخضر** — Black formatting (**مُصلَح في هذا الـ PR الحالي**)
2. **Alerts حقيقية** — ربط Sentry بقناة Slack/Email واحدة على الأقل + health check + uptime monitor
3. **Payment E2E test** — 1 SAR test كامل من الصفحة حتى webhook حتى CRM update
4. **Marketers page منشورة** — `marketers.html` داخل `landing/` مع رابط من `index.html`
5. **Pricing page علنية** — `/pricing.html` واضحة بالأسعار الأربعة
6. **Booking webhook** — Calendly webhook يحدّث lead في CRM
7. **Moyasar secret rotated** — (يدوي من المستخدم، مُوثَّق)

---

## 4) Priority Matrix

### P0 (يجب إغلاقها خلال 24 ساعة)
- CI green (Black fix) — **done in this PR**
- Marketers page live on `landing/marketers.html`
- Pricing page live `landing/pricing.html`
- Sentry → Slack webhook (قناة تنبيه واحدة على الأقل)
- UptimeRobot على `/healthz`
- 1 SAR payment E2E test
- Link marketers + pricing from main landing

### P1 (7 أيام)
- PostHog snippet in landing pages + funnel dashboard
- Calendly webhook → CRM sync
- Partner application form (Airtable/Notion)
- 10 first outreach messages sent (SMEs + 2 agencies + 1 VC)
- Moyasar Invoice generation tested (`create_invoice` E2E)
- ZATCA readiness note (when & how to register)
- Backup + restore drill documented

### P2 (30 يوم)
- Self-service signup flow
- Automated onboarding emails
- Agency dashboard (separate role)
- Service catalog as landing sections
- Case study template (even if empty)
- Content: 4 articles

### Backlog (لا نلمسها الآن)
- AI-CRO autonomous features
- Sovereign LLM / on-prem
- Multi-tenant white-label
- Mobile app
- Full automation of partner commissions

---

## 5) Marketers Page Plan

**Positioning**: "نظام تشغيل مبيعات AI للمسوقين والوكالات — بيع خدماتك، نفّذ حملاتك، واربط عملاءك بمسار إيراد قابل للقياس."

**Audience segments**:
- مسوّق فريلانسر (individual)
- وكالة تسويق صغيرة (2–20 موظف)
- وكالة أداء (performance agency)
- فريق مبيعات داخلي (in-house growth team)

**Page sections** (موجودة فعلاً في `marketers.html`):
1. Hero — عرض مباشر + CTA مزدوجة (احجز demo / سجّل كشريك)
2. من نستهدف (4 شرائح)
3. Use cases (6 سيناريوهات)
4. How it works (3 خطوات)
5. Partner tiers (3 مستويات)
6. Service swap (تبادل خدمات)
7. Proof / trust (شعارات + أرقام عند توفرها)
8. Pricing teaser + رابط للـ pricing
9. FAQ (8 أسئلة)
10. CTA نهائي

**Conversion goals**:
- Primary: Partner application submission
- Secondary: Book demo
- Tertiary: Pricing page view

---

## 6) Agency / Partner Motion

### Three tiers
- **Tier 1 — Referral Partner**: 10% commission, 30 يوم cookie, بدون حد أدنى
- **Tier 2 — Certified Partner**: 15% + co-marketing + onboarding مشترك (يتطلب 3 عملاء مفعّلين)
- **Tier 3 — Strategic Partner**: 20% + 5% revenue share + co-product input (3 slots فقط)

### Service exchange model
الشريك يقدم: تنفيذ حملات، SEO، SEM، CRM setup، content
ديلِكس يقدم: license + onboarding + تدريب + commission
نظام التبادل: كل طرف يُسعّر خدماته ويتبادل value مقابل credits أو commission.

### What we deliver to partners
- Partner dashboard (Q2: manual, Q3: automated)
- Collateral pack (AR/EN) — pitch deck, one-pager, demo script
- Monthly office hours
- White-label co-brand (Tier 3 only)

### Direct vs partner-led
- **Direct**: SMEs 50k–500k SAR/month revenue, logistics-first, KSA
- **Partner-led**: everything else (agencies handle), ROW markets

---

## 7) Revenue Readiness Plan

### Pricing path
```
Pilot (7 days)   → 1 SAR
Starter          → 999 SAR/mo
Growth           → 2,999 SAR/mo
Scale            → 7,999 SAR/mo
```
ARPU target mix (40/30/10): **2,099 SAR/mo**.

### Invoice path (Moyasar Invoices API)
1. Sales confirms deal (manual today)
2. POST to `/invoices` via `MoyasarClient.create_invoice(...)`
3. Invoice URL sent to customer (WhatsApp/email)
4. Customer pays → webhook fires
5. Webhook handler updates lead status → paid
6. (Manual) ZATCA e-invoice if applicable

### Payment path
- Moyasar Payments API (hosted) — PCI offloaded
- Webhook signature verified (`api/security/webhook_signatures.py`)
- Retry on failure via existing DLQ

### Booking path
- Calendly: https://calendly.com/sami-assiri11/dealix-demo
- Calendly webhook → Lead stage = "demo_booked"
- Reminder 24h + 1h (manual today)

### CRM path
- CRM = internal DB (`api/routers/leads.py`)
- Stages: new → qualified → demo_booked → proposal → paid → onboarding → active
- Sync to HubSpot (future, P2)

### Proof path
- First 3 pilots = case study targets
- Video testimonial within 30 days of go-live
- "trust bar" updated weekly

### Follow-up path
- Day 1: WhatsApp + email
- Day 3: WhatsApp if no response
- Day 7: final email
- Day 14: archive (cold)

---

## 8) Business Operations Plan

| Area | Who | Manual now | Auto later |
|---|---|---|---|
| Onboarding | Sami | ✅ manual call + checklist | self-serve signup (P2) |
| Support | Sami | ✅ WhatsApp + email | ticketing (30d+) |
| Invoice handling | Sami | ✅ Moyasar manual create | auto-invoice on signup (P1) |
| Payment reconciliation | Sami | ✅ via webhook log | daily auto-reconcile |
| Proposal/Quote | Sami | ✅ template docx | self-serve quote tool (backlog) |
| Partner comms | Sami | ✅ email | partner portal (30d+) |

---

## 9) Exact Next Actions (in execution order)

1. ✅ Fix Black formatting → CI green (this PR)
2. Copy `marketers.html` into `landing/` directory
3. Create `landing/pricing.html`
4. Create `landing/partners.html` (partner application form)
5. Add navigation links from `landing/index.html` to marketers + pricing
6. Add PostHog snippet to all landing pages
7. Configure Sentry → Slack webhook (manual, 1 env var)
8. Add `UptimeRobot` monitor on `/healthz` (manual)
9. Run 1 SAR test payment (user action)
10. Send first 3 outreach messages
11. Log first partner application in tracker

---

## 10) Definition of Done

| Action | DoD |
|---|---|
| CI green | جميع jobs خضراء على main |
| Marketers live | زيارة `/marketers.html` تعطي 200 + الصفحة تظهر RTL كاملة |
| Pricing live | زيارة `/pricing.html` تظهر 4 خطط + CTA عاملة |
| Alerts wired | إحداث خطأ متعمد يصل Slack خلال 60 ثانية |
| 1 SAR test | lead تم إنشاؤه + webhook استقبل + lead status = paid |
| Partner form | submission تصل Airtable/sheet + email confirmation |

---

## 11) Verification / Tests

- `curl -I https://<domain>/marketers.html` → 200
- `curl -I https://<domain>/pricing.html` → 200
- `curl -I https://<domain>/healthz` → 200 + uptime monitor يراها
- `curl -X POST https://<domain>/api/webhooks/moyasar -d '{...}'` → 200 مع توقيع صحيح، 401 بدونه
- `pytest tests/e2e/ -v` → pass
- `black --check . && ruff check . && mypy dealix/` → all green

---

## 12) Risks

1. **Regulatory (ZATCA)** — إذا وصل الإيراد للحد الخاضع للفوترة الإلكترونية قبل التسجيل، غرامات.
2. **Payment webhook silent failure** — Moyasar يرسل webhook واحد، إذا فشل retry غير كافٍ → فقدان confirmation.
3. **Secret in git history** — webhook secret القديم ما زال في history (rotation بعد اليوم لا يلغي تاريخياً).
4. **No paid customer yet** — كل الادعاءات نظرية حتى يوجد أول دفع.
5. **Partner motion بدون legal framework** — commission agreement غير موقّع.

---

## 13) Final Executive Decision

**Launch phase is NOT complete. Do not claim otherwise.**

Execute P0 list in next 24 hours. Do not start any P2 work until P0+P1 are closed and at least one real paying customer exists (even at 1 SAR pilot).

**الشرط الصريح للانتقال للمرحلة التالية**:
- CI أخضر لمدة 7 أيام متواصلة
- Marketers + Pricing + Partners live على الـ landing domain
- 1 SAR test ناجح end-to-end
- Sentry alerts واصلة لقناة حقيقية
- PostHog تسجّل events من landing
- على الأقل 10 رسائل outreach مُرسلة
- على الأقل 1 partner application واصلة

فقط عند اكتمال كل هذا نقول: **Launch closed, Phase 2 begins**.

---

## Top 5 actions now
1. إصلاح CI (done)
2. نشر marketers + pricing + partners على landing
3. ربط Sentry بـ Slack
4. تنفيذ 1 SAR test
5. إرسال أول 3 رسائل outreach

## Top 5 things NOT to touch now
1. AI-CRO autonomous features
2. Sovereign LLM
3. Mobile app
4. White-label UI
5. Multi-tenant refactor

## Top 3 risks
1. ZATCA غير مُعالَج
2. Moyasar secret في history
3. لا يوجد customer دافع

## Exact condition to move to next stage
> CI أخضر × 7d + marketers/pricing/partners منشورة + 1 SAR test ناجح + Sentry→Slack يعمل + PostHog يسجّل + 10 outreach + 1 partner app.

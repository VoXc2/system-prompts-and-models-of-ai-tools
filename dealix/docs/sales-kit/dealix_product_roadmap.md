# 🗺️ Dealix — Product Roadmap Q2-Q4 2026

**مبدأ البناء:** Ship → Measure → Iterate (أسبوعياً)
**فلسفة التركيز:** Revenue-first features فقط
**القيد:** لا feature بدون customer request موثّق (3+ طلبات)

---

## 🎯 رؤية المنتج

**في Q4 2026، Dealix يكون:**
- AI sales rep الأكثر دقة في اللهجة الخليجية
- متكامل مع 15+ أداة sales/CRM
- يخدم 120+ شركة سعودية/خليجية
- Net Revenue Retention > 120%
- مُعيار Category في "AI BDR للسوق العربي"

---

## Q2 2026 (مايو - يوليو) — "Foundation + First Revenue"

### الأولويات:
1. **Launch Production** — الانتقال من beta لـ production
2. **First 20 customers** — stress test الـ product
3. **Core integrations** — HubSpot + Zoho + WhatsApp

### Features (Q2)

#### مايو — Stabilization
- [x] Backend production على Railway
- [x] Moyasar payment flow
- [ ] Customer admin dashboard (basic)
- [ ] Email notifications للـ new leads
- [ ] Weekly report automation
- [ ] Customer onboarding flow

#### يونيو — Integrations v1
- [ ] HubSpot integration (read/write contacts)
- [ ] Zoho CRM integration
- [ ] Google Calendar direct booking
- [ ] Calendly native integration
- [ ] WhatsApp Business API (send/receive)

#### يوليو — Polish
- [ ] Analytics dashboard للعملاء (conversion funnel)
- [ ] A/B test framework للـ prompts
- [ ] Multi-language support (عربي + انجليزي hybrid)
- [ ] Role-based access (admin/user/viewer)
- [ ] API للعملاء (BYO use cases)

### Q2 Milestones
- 🎯 20 عميل مدفوع
- 🎯 60K MRR
- 🎯 NPS > 50
- 🎯 Zero critical outages

---

## Q3 2026 (أغسطس - أكتوبر) — "Growth + Polish"

### الأولويات:
1. **Inbound engine** — content + SEO
2. **Self-serve signup** — لا founder touch
3. **Retention features** — prevent churn

### Features (Q3)

#### أغسطس — Self-Serve
- [ ] Public signup (dealix.ai/signup)
- [ ] Free trial flow (7 days, credit card-free)
- [ ] In-app onboarding tutorial
- [ ] Self-service integrations (no code)
- [ ] Template library (BANT questions per industry)

#### سبتمبر — Advanced AI
- [ ] Sentiment analysis (know if lead is frustrated)
- [ ] Multi-turn reasoning (complex sales scenarios)
- [ ] Voice mode (AI يتكلم بالصوت للـ WhatsApp)
- [ ] Personality tuning (formal/casual per brand)
- [ ] Memory per lead (remembers previous conversations)

#### أكتوبر — Retention
- [ ] Health score (predict churn)
- [ ] Success manager workflows (proactive check-ins)
- [ ] Usage alerts (low activity triggers)
- [ ] Expansion prompts (upsell opportunities)
- [ ] Referral program launch

### Q3 Milestones
- 🎯 60 عميل
- 🎯 165K MRR
- 🎯 Churn < 3%
- 🎯 50% من الـ signups self-serve

---

## Q4 2026 (نوفمبر - يناير 2027) — "Scale + Expansion"

### الأولويات:
1. **Geographic expansion** — UAE
2. **Enterprise features** — F500 ready
3. **Fundraise** — Seed round closing

### Features (Q4)

#### نوفمبر — Enterprise
- [ ] SSO (SAML, Google, Microsoft)
- [ ] Role hierarchy (multi-team orgs)
- [ ] Audit logs
- [ ] Custom domain (chat.yourcompany.com)
- [ ] White-label option
- [ ] SLA guarantees

#### ديسمبر — UAE Launch
- [ ] Arabic dialect UAE tuning
- [ ] Telr/PayTabs integration (UAE payments)
- [ ] UAE-specific onboarding content
- [ ] Partnership with 1 UAE VC/accelerator
- [ ] Case studies from UAE

#### يناير 2027 — Intelligence Layer
- [ ] Lead scoring AI (beyond BANT)
- [ ] Conversation insights (what works, what doesn't)
- [ ] Industry benchmarks (see how you compare)
- [ ] Predictive pipeline (forecast next quarter)
- [ ] Auto-optimization (AI improves itself)

### Q4 Milestones
- 🎯 120 عميل
- 🎯 360K MRR (4.3M ARR)
- 🎯 10 عميل UAE
- 🎯 Seed round closed ($1-2M)

---

## 🚫 ما نُؤجّله (Not Now)

لضمان التركيز، هذه الأشياء **ممنوعة** قبل Y2:

- ❌ Mobile app (web-only)
- ❌ Voice-only interface (chat/WhatsApp كافٍ)
- ❌ Video AI (غير ضروري للـ B2B sales)
- ❌ Custom ML models (Claude كافٍ)
- ❌ On-premise deployment (SaaS only)
- ❌ Support for English-only customers
- ❌ Free tier (premium positioning)

---

## 📊 Framework للقرارات

### قبل أي feature جديد، اسأل:

1. **Revenue Impact:** هل يجلب عملاء جدد أو يحتفظ بحاليين؟
2. **Frequency:** كم عميل طلبه؟ (minimum 3)
3. **Effort:** هل ينجز في < 2 أسابيع؟
4. **Opportunity Cost:** ما الذي لن نفعله بدلاً؟
5. **Competitive:** هل يُميّزنا أم يلحق بالمنافس؟

### Scoring:
- Revenue impact (40%)
- Customer requests (25%)
- Dev effort inverse (20%)
- Strategic differentiation (15%)

**Minimum score: 7/10 to ship**

---

## 🔄 Release Cadence

### Weekly (كل ثلاثاء):
- Bug fixes
- Minor improvements
- A/B test results applied

### Monthly:
- 1 major feature launch
- Customer newsletter مع updates
- Webinar demo لعملاء حاليين

### Quarterly:
- Roadmap review مع team
- Customer advisory board meeting
- Retrospective + planning

---

## 📈 تتبع التقدم

### OKRs لكل quarter

**Q2 OKRs (مثال):**
- **O:** Launch Dealix للإنتاج بنجاح
  - **KR1:** 20 عميل مدفوع (pilot → Starter)
  - **KR2:** 99.9% uptime
  - **KR3:** 3 integrations live
  - **KR4:** NPS > 50

**تحديث أسبوعي، مراجعة شهرية، retrospective quarterly.**

---

## 🧪 Experiments Queue

### Pending tests (نجربها بعد MVP):

1. **Pricing A/B test:** 999 vs 1,299 لـ Starter
2. **Free trial length:** 7 vs 14 يوم
3. **Onboarding video:** مع vs بدون
4. **BANT questions:** 5 vs 8 vs 12
5. **Handoff timing:** فوراً vs 1 دقيقة delay
6. **Booking friction:** 1-click vs verify-then-book
7. **Language mix:** عربي فقط vs ثنائي
8. **Voice hybrid:** نص + صوت notes

كل experiment: 2 أسابيع، minimum 50 عينة، إما ship أو kill.

---

## 🎨 UX Principles

كل feature يُبنى على هذه المبادئ:

1. **Arabic-first:** الـ UI عربي افتراضي، RTL صحيح
2. **3-click rule:** أي action أساسي في < 3 clicks
3. **No jargon:** لغة بسيطة، ليست تقنية
4. **Mobile-responsive:** يشتغل على جوال الـ CEO
5. **Empty states:** كل شاشة بلا بيانات = tutorial
6. **Error messages:** مفيدة، ليست "Error 500"
7. **Feedback loops:** كل action يعطي confirmation
8. **Undo-able:** كل destructive action قابل للتراجع

---

## 🏗️ Technical Debt Backlog

نعترف بها، نعالجها بذكاء:

### High priority:
- [ ] Refactor conversation memory (scalability)
- [ ] Improve test coverage (currently 70%, target 90%)
- [ ] API rate limiting per customer

### Medium:
- [ ] Migrate من Postgres لـ Postgres + Redis للـ caching
- [ ] Add observability (distributed tracing)
- [ ] Refactor email templates (maintainability)

### Low:
- [ ] Migrate to Python 3.13 (when stable)
- [ ] Evaluate serverless for specific endpoints

**قاعدة:** 20% من كل sprint لـ tech debt.

---

## 🤝 الشراكات المستهدفة

### Q2-Q3:
- **Salla App Store** — Dealix كـ app في منصتهم
- **Zid** — مشابه
- **STC Business** — bundle في عروضهم للـ SMBs
- **Misk Academy** — تدريب founders

### Q4:
- **SDAIA** — certification حكومية
- **Monshaat** — subsidized pricing للـ startups
- **Y Combinator Alumni Saudi** — warm intros

---

## 💬 Customer Feedback Channels

- **In-app:** Intercom-style chat widget
- **Monthly:** 1:1 call مع كل عميل Growth+
- **Weekly:** Async Slack/WhatsApp
- **Quarterly:** NPS survey
- **Annual:** Customer Advisory Board (top 5 accounts)

**كل feedback → Notion database → priority review weekly.**

---

## 🎯 نقاط التحقق النجاح

### Q2 end:
- [ ] 20 عملاء
- [ ] زمن رد أول lead: < 60 ثانية
- [ ] 0 outages >5 دقائق
- [ ] 3+ positive case studies

### Q3 end:
- [ ] 60 عميل
- [ ] Self-serve: 50%+ signups
- [ ] Organic inbound > paid acquisition
- [ ] Arabic dialect accuracy > 95% (measured)

### Q4 end:
- [ ] 120 عملاء
- [ ] UAE market: 10 عملاء
- [ ] Seed round: closed
- [ ] Team: 5-7 شخص

---

## 🚀 Long-term Vision (2027-2030)

**2027:** $24M ARR، 500 عملاء، 3 أسواق (KSA, UAE, Kuwait)
**2028:** $60M ARR، 1,200 عملاء، 5 أسواق، Voice AI
**2029:** $120M ARR، 2,500 عملاء، الخليج كامل، AI-native
**2030:** $300M ARR، الرائد في MENA للـ sales automation

**Exit options (2030+):**
- IPO على Saudi Exchange (Tadawul)
- Acquisition من Salesforce / HubSpot / Local tech giant
- Continue as independent profitable business

---

## 📝 Roadmap Review Cadence

- **Weekly (الاثنين):** progress check
- **Monthly (آخر أسبوع):** adjust priorities
- **Quarterly:** major revision + customer advisory input
- **Annual:** strategic re-planning

---

**اكتمال هذا الـ roadmap = خارطة طريق واضحة. الحين نحتاج نمشي عليها.**

ابدأ بـ Q2 بأولوية واحدة فقط: **Launch Production.**

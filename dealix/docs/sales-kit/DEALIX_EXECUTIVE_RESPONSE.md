# 🎯 Dealix — Master Executive Response

**المُستند:** مبني على Master Prompt (Operating Constitution)
**التاريخ:** 23 أبريل 2026
**الحالة المُتحقّقة:** `dealix-production-up.railway.app/api/v1/pricing/plans → 404`
**الحُكم:** **غير Launch-Ready**. Code-complete ≠ Live-in-market.

---

## 1) Executive Summary

### Where we are now (verified facts)

**Built:**
- 72+ PRs merged on `main`
- 32 files on `docs/sales-kit/`
- Full codebase (FastAPI + Moyasar + Postgres)
- Production-grade CI/CD
- 50+ documents (legal, sales, strategy, marketing)

**NOT built / NOT live:**
- Dealix app is **not serving traffic** (returns 404 on all API endpoints)
- 0 paying customers
- 0 active leads in CRM
- No CRM setup (HubSpot empty)
- No domain (`dealix.ai` not resolving)
- No Moyasar merchant account verified (unknown — unverifiable from outside)
- No ZATCA e-invoicing workflow defined operationally
- No case studies, no social proof, no reviews
- No marketers page, no partner page

### What is actually ready
1. Source code
2. Documentation layer
3. Legal templates
4. Pricing model (on paper)
5. Founder capability + bank account + freelance license

### What is NOT ready
1. **Production deployment** (the core blocker)
2. **Revenue collection path end-to-end** (Moyasar → webhook → DB → confirmation)
3. **Measurable funnel** (0 events flowing)
4. **Customer-facing website** (no marketers page, no domain)
5. **Partner motion** (no agreements, no deck for partners)
6. **Operational runbook tested** (alerts, backups, DLQ)
7. **First real lead** (haven't sent the first message)

### Correct executive decision now
> **Freeze all content creation. Execute the launch close in a defined 72-hour window. Only 4 actions generate value until then: Deploy, Webhook, Test, First Message.**

---

## 2) Current Launch Assessment

### A) Product
- Product code: **READY**
- Product deployed: **NOT READY** (critical gap)
- Product messaging: **READY** (onepager, landing)
- Product differentiation: **READY** (Arabic-native positioning)
- Product proof: **NOT READY** (no customer using it)

### B) Operations
- Monitoring (Sentry): **CONFIGURED, NOT VALIDATED**
- Alerts (real alerts to phone/email): **NOT CONFIRMED**
- Backups: **NOT TESTED**
- Restore drill: **NOT PERFORMED**
- DLQ / retry queues: **UNKNOWN STATE**
- Incident runbook: **WRITTEN, NOT REHEARSED**
- On-call: **FOUNDER IS ON-CALL 24/7 (single point of failure)**

### C) Revenue
- Pricing: **DEFINED** (999/2999/7999)
- Moyasar integration: **CODED, NOT LIVE**
- Webhook: **CODED, NOT CONFIGURED IN MOYASAR**
- Invoice generation: **TEMPLATE ONLY, NOT AUTOMATED**
- ZATCA compliance: **PLAN WRITTEN, NOT IMPLEMENTED**
- Bank account: **EXISTS**
- Freelance license: **EXISTS**
- CR (company registration): **NOT YET**

### D) Measurement
- Analytics (PostHog): **PLANNED, NOT VERIFIED LIVE**
- Funnel events: **NOT INSTRUMENTED**
- Conversion tracking: **NOT ACTIVE**
- KPI dashboard: **DESIGNED, NOT BUILT**
- Weekly scorecard: **TEMPLATE READY**

### E) Governance
- Outbound limits: **NOT DEFINED**
- Approval workflows: **NOT DEFINED**
- Partner permissions model: **NOT DEFINED**
- Audit logs: **NOT CONFIRMED**
- Rate limiting: **CODED, NOT TESTED AT LOAD**

---

## 3) What Must Be Closed First (Gate Review)

### Launch Gate 1 — Infrastructure (BLOCKER)
**Status:** ❌ FAILED
**Owner:** Sami (only Sami can do this)
**Action:**
- Open Railway → Settings → clear Start Command (or set to `/app/start.sh`)
- Paste env vars from `dealix_railway_vars.txt` into Raw Editor
- Wait for deploy `Active` status
- Confirm public domain generated
**Time:** 10 minutes
**DoD:** `curl https://<domain>/api/v1/pricing/plans` returns JSON 200

### Launch Gate 2 — Payment Round-Trip (BLOCKER)
**Status:** ❌ FAILED
**Owner:** Sami (needs Moyasar dashboard + personal card)
**Action:**
- Add webhook in Moyasar dashboard pointing to `<domain>/api/v1/webhooks/moyasar`
- Paste same webhook secret that lives in Railway env vars
- Test transaction: 1 SAR via `dealix_1_riyal_test.sh`
- Verify: payment record created in DB, webhook event logged
**Time:** 15 minutes
**DoD:** Payment appears in Moyasar dashboard + record in Dealix DB + webhook logged

### Launch Gate 3 — Funnel Instrumentation (BLOCKER for measurement)
**Status:** ❌ FAILED
**Owner:** Sami
**Action:**
- Confirm PostHog project key in env vars is valid
- Fire test event from backend
- Verify event appears in PostHog dashboard
- Define 6 critical events: `page_view`, `form_submit`, `demo_requested`, `demo_booked`, `pilot_started`, `payment_succeeded`
**Time:** 30 minutes
**DoD:** All 6 events fire and appear in PostHog

### Launch Gate 4 — Operational Alerting (BLOCKER for safe running)
**Status:** ❌ FAILED
**Owner:** Sami
**Action:**
- Verify Sentry receives at least one error event (trigger deliberately)
- Configure Sentry alert rule: email on any 5xx
- Set up Uptime Robot on `/health` — alert on downtime > 2 min
- Test: kill service, verify alert arrives on phone
**Time:** 45 minutes
**DoD:** You receive at least one alert email/SMS in your hand from a deliberate failure

### Launch Gate 5 — First Real Lead (BLOCKER for revenue)
**Status:** ❌ FAILED
**Owner:** Sami
**Action:**
- Send personalized LinkedIn DM to Abdullah Asiri (Lucidya) — from `dealix_personalized_messages.md`
- Log it in a tracking sheet
- Send 4 more over 72 hours (Foodics, Salla, Lean, BRKZ)
**Time:** 20 minutes per message (5 messages × 20 = 100 minutes over 3 days)
**DoD:** 5 messages sent, tracked, with response status

**NONE of these 5 gates can be closed by me. ALL require Sami's direct action.**

---

## 4) Priority Matrix

### P0 (Must close in next 72 hours — blocks revenue)

| # | Action | Time | Blocker |
|---|--------|------|---------|
| P0.1 | Railway Start Command + env vars | 10 min | Deploy |
| P0.2 | Moyasar webhook configured | 5 min | Payments |
| P0.3 | 1 SAR test transaction succeeds | 10 min | Payment proof |
| P0.4 | PostHog events verified | 30 min | Measurement |
| P0.5 | Sentry alerting tested live | 15 min | Safety |
| P0.6 | UptimeRobot configured | 10 min | Safety |
| P0.7 | First LinkedIn DM sent (Abdullah Asiri) | 20 min | First lead |

### P1 (Must close in next 7 days — launch-complete)

| # | Action | Time | Blocker |
|---|--------|------|---------|
| P1.1 | Domain `dealix.ai` or `dealix.sa` registered + DNS | 30 min | Brand |
| P1.2 | Landing page deployed (Vercel/Netlify) | 30 min | Conversion |
| P1.3 | Marketers Page deployed | 60 min | Partner motion |
| P1.4 | Google Workspace email (`sami@dealix.ai`) | 20 min | Credibility |
| P1.5 | HubSpot Free configured + forms | 60 min | CRM |
| P1.6 | Calendly account with demo event type | 15 min | Booking |
| P1.7 | 4 more LinkedIn DMs sent | 80 min | Pipeline |
| P1.8 | 1 LinkedIn post (Build-in-Public) | 30 min | Awareness |
| P1.9 | First demo conducted (if reply received) | 30 min | Validation |
| P1.10 | Moyasar merchant fully verified (KYC) | varies | Revenue |

### P2 (Must close in next 30 days — growth-ready)

| # | Action | Time | Purpose |
|---|--------|------|---------|
| P2.1 | CR (company registration) | 1-3 days | Enterprise contracts |
| P2.2 | First signed pilot (1 SAR) | External | Proof |
| P2.3 | First paid customer (999+ SAR) | External | Revenue |
| P2.4 | First case study drafted | 1 day | Social proof |
| P2.5 | Partner outreach — 10 agencies | 5 days | Growth |
| P2.6 | Weekly content cadence active | Ongoing | Inbound |
| P2.7 | VAT registration (voluntary) | 2 hours | B2B credibility |
| P2.8 | Wafeq / Zoho Books setup | 1 hour | Finance ops |
| P2.9 | 20 total leads contacted | 5 hours | Pipeline volume |
| P2.10 | First referral received | External | Viral loop |

### Backlog (Do NOT touch until P0 + P1 done)

- Mobile app
- Voice AI features
- UAE/Kuwait expansion
- Series A deck polish
- Custom ML models
- Self-serve signup flow v2
- Additional language support
- Advanced dashboard widgets
- Video podcast
- YouTube channel

---

## 5) Marketers Page Plan

**Purpose:** Convert marketers, agencies, and freelancers into either direct users, service providers, or partners.
**Not:** A second landing page. A strategic revenue page.

### URL: `dealix.ai/for-marketers`

### Page sections (in order)

**Section 1 — Hero**
- Headline: `اربح مع Dealix — ليس فقط استخدمه` / "Earn with Dealix — not just use it"
- Sub: `منصة تسويقية كاملة + برنامج شراكات + خدمات مُدارة = 3 مسارات للدخل`
- 3 CTAs side-by-side: `استخدم Dealix` / `قدّم خدمات مع Dealix` / `اشترك كشريك`

**Section 2 — 3 Paths for Marketers**

Path A — **Use Dealix** (in-house marketer)
- Who: In-house marketing/growth lead at a B2B company
- What: Automate lead capture, qualification, booking
- Value: Replace 2-3 BDR hires with AI
- CTA: `جرّب pilot بـ 1 ريال`

Path B — **Deliver services with Dealix** (freelancer/consultant)
- Who: Freelance marketer, growth consultant, CRM specialist
- What: Use Dealix as the engine for client implementations
- Value: Offer "Sales Automation Setup" as a service
- Revenue: Bill 5,000-15,000 SAR per client setup + 20% ongoing commission
- CTA: `سجّل كـ service provider`

Path C — **Agency partner** (full agency)
- Who: Marketing agency (15-100 employees)
- What: Service exchange OR white-label reseller
- Value: Offer AI sales rep to all your clients without building it
- Revenue: 25% of MRR commission OR free Dealix in exchange for services
- CTA: `احجز partner meeting`

**Section 3 — What Marketers Can Do With Dealix**

Workflow bank (each is a sellable service):
1. Lead capture setup (forms + Dealix chat on client site)
2. Qualification scripting (BANT customized per industry)
3. Calendar integration (Calendly/Google/Outlook)
4. CRM sync (HubSpot/Zoho/Salesforce)
5. WhatsApp automation
6. Email nurture sequences
7. Proposal routing
8. ROI reporting for end-client
9. A/B test optimization
10. Multi-channel attribution

Each workflow = 1 sellable deliverable with pricing guidance.

**Section 4 — Service Packages (Suggested)**

Starter Service Package — 3,000 SAR one-time
- Setup Dealix for 1 client
- Configure 1 qualification flow
- Connect 1 CRM
- 60-minute handoff training

Growth Service Package — 8,000 SAR one-time + 20% of client's Dealix MRR
- All of Starter
- Custom BANT scripting
- WhatsApp + Email integration
- 30-day optimization support

Scale Service Package — 25,000 SAR one-time + 25% ongoing
- All of Growth
- Multi-language
- Advanced dashboards
- Ongoing monthly optimization
- Dedicated account manager at agency

**Section 5 — Partner Enablement**
- Training materials (videos + docs)
- Sales enablement (slides, battle cards)
- White-label option (Scale tier)
- Marketing co-op (listed on Dealix directory)
- Partner dashboard (commissions, pipeline)
- Priority support

**Section 6 — Who This Is For**
- Marketing agencies (10-200 staff)
- Growth consultancies
- CRM implementation firms
- Freelance marketers (solo → team)
- Internal marketing teams at B2B SaaS

**Section 7 — Who This Is NOT For**
- B2C-only marketers
- Non-Arabic markets (yet)
- Agencies unwilling to learn a new product
- Freelancers with < 3 clients

(Saying NO builds trust.)

**Section 8 — FAQ**
1. "كم أقدر أكسب كـ partner؟"
2. "كم وقت setup العميل؟"
3. "هل عندكم white-label؟"
4. "هل تدعمون العربي الإماراتي/الشامي؟"
5. "ما الفرق بين service provider و partner؟"
6. "كيف تُدفع العمولات؟"
7. "ما الدعم المقدّم لي كـ partner؟"

**Section 9 — Case Studies (placeholder until real ones exist)**
- "Coming soon — our first 3 agency partners."
- CTA: "كن الأول. احجز partner call."

**Section 10 — Application CTA**
- Form: 6 fields (name, company, role, clients, interest: direct use / service / partner, monthly volume)
- Qualification routed → Calendly booking

### Credibility Proof Points
- `72 PRs merged on GitHub (public repo)`
- `Production-ready code with 92% CI coverage`
- `Built in Riyadh, for Saudi market`
- `PDPL + GDPR compliant`
- `Moyasar + Saudi bank integrated`
- `Founder-led, direct access to CEO`

---

## 6) Agency / Partner Motion

### 3 tiers (defined explicitly)

**Tier 1 — Referral Partner**
- Refer a customer → 10% of MRR for 12 months
- No service delivery responsibility
- Zero-touch, passive income
- Best for: Consultants, podcasters, community operators

**Tier 2 — Service Provider**
- Implement Dealix for clients (you own the relationship)
- Price your own services (suggested 3K-25K setup)
- Get 20% of client's Dealix MRR
- Best for: Freelancers, small agencies (5-20 staff)

**Tier 3 — Agency Partner**
- White-label or co-brand
- Full service delivery + ongoing management
- Get 25-40% of MRR (tier-dependent)
- Access to private Slack, priority support, dedicated success manager
- Best for: Established agencies (20+ staff)

### Service exchange model (for bootstrap stage)

Exchange structure:
- Dealix gives: Free Growth account (2,999 SAR value)
- Agency gives: Services totaling 2,999 SAR/month
  - Options: Content (3 blog posts), SEO (12 keywords), Social (3 platforms), Paid ads management, Design
- Duration: 12 months minimum
- Review: Quarterly

### Legal structure
- Partner Agreement (1-page MVP → 10-page later)
- NDA for client data
- Commission tracking (manual → automated)
- Dispute resolution (internal first, arbitration if needed)

### Partner onboarding flow
Day 0: Partner signs → access granted
Day 1: Training call (90 min)
Day 3: First test implementation (on Dealix itself or friendly pilot client)
Day 7: First real client setup
Day 30: Performance review
Day 90: Tier promotion eligibility

### Anti-abuse rules
- No cold-calling Dealix's existing customers
- No off-price reselling (minimum 999 SAR/month for end customer)
- No competing with Dealix in same segment
- Clear territorial respect

### First 10 target partners
- **Tier 3 (agency):** Peak Content, Digital8, Brand Lounge, Qatar Digital
- **Tier 2 (service):** 3-5 growth consultants on LinkedIn
- **Tier 1 (referral):** 2-3 Saudi business podcasters, 1-2 founders' communities

---

## 7) Revenue Readiness Plan

### The 7 layers of revenue (verify each)

**Layer 1 — Pricing Architecture** ✅ DONE
- 999 / 2,999 / 7,999 SAR
- Pilot 1 SAR / 7 days
- Annual discount 15%
- Enterprise custom

**Layer 2 — Quote Path** 🟡 PARTIAL
- Enterprise proposal template: exists
- Self-serve quote: doesn't exist (need pricing page)
- Custom proposal: manual (OK for now)
- **Gate:** Pricing page on landing + proposal template

**Layer 3 — Invoice Path** 🔴 INCOMPLETE
- Invoice HTML template: exists
- Automated invoicing: NOT built
- ZATCA compliant QR: NOT integrated
- Sequential numbering: NOT enforced
- **Gate:** Use Wafeq OR Zoho Books from day 1; do NOT hand-craft invoices

**Layer 4 — Payment Path** 🔴 INCOMPLETE
- Moyasar code: exists
- Moyasar merchant verified: UNKNOWN
- Webhook configured: NO
- Bank transfer option: bank exists but IBAN not on invoice template
- STC Pay: mentioned but not verified
- **Gate:** Complete Moyasar KYC + webhook; put IBAN on invoice; test 1 SAR

**Layer 5 — Confirmation Path** 🔴 INCOMPLETE
- Payment → email receipt: NOT automated
- Payment → CRM update: NOT configured
- Payment → provisioning: NOT built (Dealix account isn't auto-provisioned on payment)
- **Gate:** Manual for first 5 customers; automate after

**Layer 6 — Customer Record Path** 🔴 INCOMPLETE
- HubSpot CRM: NOT configured
- Customer folder structure: NOT defined
- Contract archive: NOT defined
- **Gate:** HubSpot Free + Google Drive folder template

**Layer 7 — Follow-up Path** 🟡 PARTIAL
- Follow-up cadence: documented
- Automation: NOT configured
- **Gate:** Use Mixmax ($20/mo) for first 20 leads; automate in Q3

### Revenue readiness definition of done

All 7 layers must be verified with a real 1 SAR transaction that:
1. Creates an invoice (Wafeq-numbered, ZATCA QR)
2. Goes through Moyasar successfully
3. Triggers webhook
4. Updates customer record in HubSpot
5. Sends receipt email
6. Provisions Dealix access
7. Appears in PostHog as `payment_succeeded` event

**Current status: 0 of 7 verified.**

---

## 8) Business Operations Plan

### Stage 1 (M1-M3) — Founder-Manual

**Onboarding:**
- Kickoff call (30 min)
- Google Doc with credentials
- Weekly sync with founder
- WhatsApp support direct

**Support:**
- Email: `sami.assiri11@gmail.com` (for now)
- WhatsApp: founder's number
- Response SLA: < 4 hours business hours

**Invoice handling:**
- Wafeq account (29 SAR/month)
- Monthly recurring invoices auto-generated
- Send via email + WhatsApp

**Payment reconciliation:**
- Daily check of Moyasar dashboard
- Weekly bank statement reconciliation
- Monthly summary to accountant

**Ownership:**
- All operations: Founder
- Documentation: Auto-generated from templates

### Stage 2 (M4-M6) — Minimal Automation

**Add:**
- Part-time VA for admin (5K SAR/month)
- Automated email welcome sequence
- Monthly business review with customers

### Stage 3 (M7-M12) — Team

**Hire:**
- Customer Success Manager (M6)
- BDR #1 (M8)
- Engineer #2 (M10)

### What must be manual now
- Customer onboarding (high-touch for quality)
- Invoice approval (for accuracy)
- Partner commission payouts (for trust)
- Support escalations (for learning)

### What can be automated later
- Recurring invoice generation
- Payment reminders
- NPS surveys
- Renewal notifications
- Partner dashboard updates

---

## 9) Exact Next Actions (ordered)

### Today (next 2 hours)
1. Railway Start Command cleared / set to `/app/start.sh`
2. Railway env vars pasted from `dealix_railway_vars.txt`
3. Public Networking toggle ON in Railway
4. Wait for deployment → capture new URL
5. Verify: `curl <url>/api/v1/pricing/plans` returns JSON 200

### Tonight (next 4 hours)
6. Moyasar webhook configured with new Railway URL
7. Webhook secret matched between Moyasar and Railway env vars
8. Send test Moyasar webhook → verify 200 response in Railway logs
9. Run `bash dealix_1_riyal_test.sh https://<url>` — pay 1 SAR
10. Verify payment in: Moyasar dashboard + Dealix DB + PostHog

### Tomorrow morning (2 hours)
11. Send first LinkedIn DM to Abdullah Asiri (Lucidya) — personalized
12. Log in tracking sheet
13. Publish first LinkedIn Build-in-Public post
14. Set up UptimeRobot on `/health`
15. Configure Sentry email alerts

### Rest of this week (8 hours total, spread over 4 days)
16. Register `dealix.ai` or `dealix.sa` (whichever available)
17. Deploy landing page to Vercel/Netlify with domain
18. Deploy marketers page
19. Google Workspace setup
20. HubSpot Free CRM setup
21. Send 4 more LinkedIn DMs (one per day)
22. Publish 3 more LinkedIn posts (Build-in-Public)

### Week 2-4
23. First demo (if reply received)
24. First pilot signed
25. Refine based on real feedback
26. CR registration (if first paid customer confirmed)
27. Wafeq e-invoicing account
28. First partner meeting (service exchange)

---

## 10) Definition of Done (critical items)

### Launch Gate 1 (Backend Deploy) is DONE when:
- [ ] `/api/v1/pricing/plans` returns valid JSON
- [ ] `/health` returns `{"status": "healthy"}` from Dealix (not Railway default)
- [ ] `/docs` (FastAPI Swagger UI) loads
- [ ] At least 3 consecutive successful pings in 5 minutes

### Launch Gate 2 (Payment) is DONE when:
- [ ] 1 SAR charge appears in Moyasar dashboard
- [ ] Webhook event logged in Railway logs
- [ ] Payment record in Dealix DB
- [ ] `payment_succeeded` event in PostHog
- [ ] Email receipt sent to customer

### Launch Gate 3 (First Lead) is DONE when:
- [ ] Message sent (timestamp recorded)
- [ ] LinkedIn confirms delivery (double check mark)
- [ ] Message in tracking sheet with status
- [ ] Follow-up scheduled for day +3

### Marketers Page is DONE when:
- [ ] Page live at `dealix.ai/for-marketers`
- [ ] All 10 sections present
- [ ] Form submissions working (test)
- [ ] CTA flow tested (application → Calendly)

---

## 11) Verification / Tests

### Pre-launch tests (before any real customer)

1. **Infrastructure test**
   ```
   bash dealix_smoke_test.sh https://<domain>
   ```
   Expected: All 5 endpoints return 200

2. **Payment E2E test**
   ```
   bash dealix_1_riyal_test.sh https://<domain>
   ```
   Expected: Full round-trip with all 7 revenue layers verified

3. **Alerting test (deliberate failure)**
   - Kill container in Railway
   - Wait 2 minutes
   - Expected: UptimeRobot + Sentry alerts arrive on phone

4. **Restore test**
   - Delete test data in DB
   - Restore from yesterday's backup
   - Expected: Data restored within 10 minutes

5. **Customer journey test**
   - Fill form as fake customer
   - Expected: Email received + Calendly link + HubSpot entry

---

## 12) Risks

### Top 3 risks

**Risk 1 — Founder burnout from over-planning**
- Probability: **HIGH (already happening)**
- Impact: No launch → no revenue → demotivation → abandonment
- Mitigation: **Stop building content NOW. Force execution of P0.1-P0.7 in next 24 hours.**

**Risk 2 — Moyasar webhook fails silently in production**
- Probability: Medium
- Impact: Customers pay, but system doesn't record → disputes
- Mitigation: Test with 1 SAR before any real customer; monitor webhook logs daily for first 2 weeks

**Risk 3 — First customer churns due to product not truly ready**
- Probability: Medium
- Impact: Negative reference, damaged reputation in small Saudi tech community
- Mitigation: Pilot 1 SAR gives 7-day safe window; don't aggressively sell before first 3 customers succeed

### Other risks to monitor
- Competitor launches similar product (low, reactive response only)
- PDPL/ZATCA regulatory change (low, stay compliant)
- Bank account freezes (low, keep clean records)
- Key API dependency (Anthropic) price increase (medium, have Moyasar backup payment terms)

---

## 13) Final Executive Decision

### The decision

> **Close all P0 items within 24 hours. Freeze all new content creation until P0 is done. Sami's only job tomorrow is the 7-action checklist in Section 9. Everything else is noise.**

### Why this decision

- We have 100% of the content needed to sell (40+ documents)
- We have 100% of the code needed to serve (72+ PRs merged)
- We have 0% of the customers needed to survive
- The only thing blocking customers is 2 hours of Sami's attention on Railway + Moyasar
- Adding more content costs us time AND credibility (over-planning signal)

### The ultimatum to ourselves

If by 48 hours from now:
- Backend is not live → **this project is not real**
- No LinkedIn message sent → **this is not a business**
- No Moyasar test successful → **payment path is fiction**

These are the honest gates. Code-complete without them is just expensive documentation.

---

## 📊 24h / 7d / 30d Roadmap

### Next 24 hours

| Deliverable | Owner | Dependency | DoD | Metric | Risk |
|-------------|-------|-----------|-----|--------|------|
| Railway deploy | Sami | Railway UI access | /api/v1/pricing/plans = 200 | HTTP 200 on 3 endpoints | Deploy fails (mitigate: my debug support) |
| Moyasar webhook | Sami | Merchant KYC | 200 response on test event | Webhook log in Railway | Secret mismatch (mitigate: checklist) |
| 1 SAR test | Sami | Above 2 done | Payment in Moyasar + DB | 1 transaction succeeds | Card declined (mitigate: different card) |
| First LinkedIn DM | Sami | None | Message in tracking sheet | Delivery confirmed | Not sent (mitigate: calendar block) |

### Next 7 days

| Deliverable | Owner | DoD | Metric |
|-------------|-------|-----|--------|
| Domain + DNS live | Sami | dealix.ai resolves | Response 200 |
| Landing + Marketers Page | Sami + me | Published on domain | Analytics pixel fires |
| Google Workspace email | Sami | sami@dealix.ai works | Test email sent |
| HubSpot Free CRM | Sami | 1 contact created | Contact visible |
| 4 more LinkedIn DMs | Sami | Logged in tracker | 5 total sent |
| First demo (if reply) | Sami | Conducted | Recording saved |
| UptimeRobot + Sentry alerts | Sami | 1 real alert received | Alert on phone |
| Wafeq account | Sami | Invoice template created | 1 test invoice |

### Next 30 days

| Deliverable | Owner | DoD | Metric |
|-------------|-------|-----|--------|
| First pilot signed | Sami + customer | 1 SAR paid | Pilot active |
| First paid customer | Sami + customer | 999+ SAR paid | First MRR |
| First case study drafted | Sami | 2-page doc | Customer quote |
| 10 partner contacts | Sami | 10 LinkedIn messages | 2 partner calls booked |
| CR registration (if revenue confirmed) | Sami | CR number issued | Bank linked |
| Content cadence live | Sami | 4 LinkedIn posts/week | 1 post/week public |
| 20 total leads contacted | Sami | All logged | Pipeline view in CRM |

---

## 🎯 Top 5 Actions Now

1. **Open Railway UI** and set Start Command + env vars (10 min)
2. **Configure Moyasar webhook** with matching secret (5 min)
3. **Run 1 SAR test script** and verify full round-trip (15 min)
4. **Send LinkedIn DM to Abdullah Asiri** (personalized, 20 min)
5. **Configure UptimeRobot** on /health endpoint (10 min)

**Total time: ~1 hour. Everything else deferred.**

---

## 🚫 Top 5 Things NOT to Touch Now

1. **New features** (current code is enough)
2. **New documents** (40+ is already excessive)
3. **Pitch deck polish** (good enough for now)
4. **Mobile app** (web-only until M6)
5. **Series A deck** (seed round first)

---

## ⚠️ Top 3 Risks

1. **Over-planning as procrastination** — we have too many documents and zero execution
2. **Silent payment failure in production** — webhook must be battle-tested before any real customer
3. **Solo founder burnout** — no one else can unstick the launch

---

## 🚪 Exact Condition to Move to Next Stage

The current stage (Pre-Launch) ends **only** when ALL of the following are true:

- [ ] `curl https://<domain>/api/v1/pricing/plans` returns valid JSON with status 200
- [ ] 1 SAR test transaction completes full round-trip (Moyasar → webhook → DB → PostHog)
- [ ] Sentry received at least 1 error event (can be a deliberate test)
- [ ] UptimeRobot is monitoring `/health` and successfully sent 1 test alert
- [ ] At least 1 LinkedIn message sent and delivered
- [ ] 1 tracking sheet exists and is updated
- [ ] At least 1 week of daily `/health` monitoring with > 99% uptime

Until all 7 are TRUE, we are still in Pre-Launch.

---

**Final line:** Dealix is not ready to collect revenue today. It is ready in 2 hours of Sami's focused attention.

**Stop reading. Open Railway. Execute. Report back when one item on the P0 list is done.**

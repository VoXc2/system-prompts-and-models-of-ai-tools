# Dealix — Master Strategic Plan
## من الى — من Pilot 499 إلى Saudi Revenue Execution OS الفئة المهيمنة

> **القاعدة الذهبية:** Dealix لا يبيع features. يبيع **نتائج إيرادية موثّقة**.
> كل قرار في هذه الوثيقة مبني على هذا المبدأ.

---

## 0. التشخيص الاستراتيجي (Where We Stand — May 2026)

### نقاط القوة الحقيقية
1. **Tech foundation عميقة**: 12 طبقة معمارية، 200+ endpoint، 791 اختبار، CI أخضر، approval-first من البنية لا من الـ wrapper.
2. **Positioning محكم**: Saudi Revenue Execution OS — ليس CRM، ليس bot، ليس scraper. القوة في الوضوح.
3. **Compliance built-in**: PDPL، WhatsApp opt-in، Safety Eval، Saudi Tone Eval، Trace Redactor، Patch Firewall — ميزة لا يعطيها HubSpot ولا Gong محلياً.
4. **Service Tower productized**: 13+ خدمة، كل واحدة فيها workflow + proof + pricing + upsell.
5. **6 service bundles** بـ pricing واضح من 499 ر.س إلى Custom.
6. **Founder-Led Growth جاهز**: المؤسس عربي، يفهم السوق السعودي، يبيع بنفسه.

### الفجوات التي لازم تُسد قبل التوسع
1. **0 paid customers**: المنتج جاهز، السوق غير مُختبَر بعد.
2. **0 case studies**: لا proof خارجي للمشترين.
3. **No pricing validation**: 499/2,999/etc. أرقام منطقية لكن غير مُختبَرة بـ A/B.
4. **No retention data**: Growth OS Monthly = اشتراك، لكن لا churn data بعد.
5. **No partner channel**: الوكالات هي الـ wedge الأقوى لكن لا اتفاقيات.
6. **No content moat**: لا blog، لا newsletter، لا SEO/AEO رصيد.
7. **No data moat**: قاعدة بيانات الفرص لم تتراكم بعد — كل عميل جديد يبدأ من صفر.

### الفرضية الاستراتيجية الكبرى
> **الفائز في السوق السعودي للـ Revenue Execution هو من يبني أعمق Saudi Revenue Graph + أوسع شبكة وكالات قبل أن تقرر HubSpot/Salesforce/Gong الترجمة الفعلية للعربية.**
>
> النافذة الزمنية: **18–24 شهر**. بعدها، إما Dealix هو الـ default للـ B2B السعودي، أو يصبح niche tool.

---

## 1. النية النهائية (North Star — 36 شهراً)

```
Year 1 (2026):  Saudi Private Beta + Paid Beta + 50 paying customers + $300K ARR
Year 2 (2027):  Saudi GA + 500 paying customers + Agency Network 30 partners + $3M ARR
Year 3 (2028):  GCC expansion (UAE, Kuwait, Bahrain) + 2,000 customers + $15M ARR
Year 4 (2029):  Series A + MENA + Arabic LLM moat + $50M ARR target
```

### Vision Statement (داخلي)
> "أن يصبح Dealix الـ Operating System الذي تُدار به مبيعات وشراكات أي شركة سعودية تطمح للنمو، بحيث لا تستطيع HubSpot أو Salesforce المنافسة لأن Dealix يفهم السياق المحلي بعمق لا يستطيعون مجاراته."

### Mission Statement (خارجي)
> "نحوّل بيانات وقنوات الشركات السعودية إلى فرص مدفوعة وشراكات موثّقة، بدون scraping، بدون رسائل عشوائية، بأمان PDPL تام، وبموافقتك على كل تواصل."

### الـ Anti-Mission (ما لا نفعله أبداً)
- ❌ نضمن مبيعات.
- ❌ نسحب بيانات LinkedIn.
- ❌ نرسل WhatsApp بدون opt-in.
- ❌ نخزّن credentials.
- ❌ نسوّق على شاشات بناءً على casino-like dark patterns.
- ❌ نشتغل بدون موافقة العميل على كل action خارجي.

---

## 2. Positioning Architecture (4 طبقات)

### الطبقة 1 — Category Positioning
**Category:** Saudi Revenue Execution OS

**Definition:** "نظام تشغيل النمو والإيرادات للشركات السعودية، يدير الـ pipeline من اكتشاف الفرصة إلى Proof Pack، بأمان PDPL وبصوت سعودي."

**ما هو ليس:**
- CRM (HubSpot, Salesforce, Zoho) — هؤلاء قاعدة بيانات.
- WhatsApp tool (Wati, Twilio) — هؤلاء قنوات إرسال.
- Lead scraper (Apollo, ZoomInfo) — هؤلاء scraping.
- AI chatbot عام (ChatGPT, Claude) — هؤلاء يولّدون نص.
- Agency تقليدية — هؤلاء عمل يدوي.

### الطبقة 2 — Audience Positioning (مَن نخدم)

| Segment | الحجم | الـ pain | الميزة لـ Dealix |
|---------|------|---------|------------------|
| **B2B SMBs السعودية** | 50K+ شركة | لا فريق مبيعات، لا CRM، إيرادات متذبذبة | يحلّ كل ذلك بـ 2,999 ر.س/شهر |
| **Marketing Agencies** | 2K+ وكالة | يفقدون عملاء، Proof ضعيف، Manual | Dealix = Growth OS تبيعه باسم الوكالة |
| **Training/Consulting Firms** | 3K+ شركة | بيع طويل، فرص نادرة | First 10 Opportunities Sprint = حل سريع |
| **B2B SaaS سعودي** | 200+ شركة | sales velocity بطيء | Growth OS Monthly = velocity engine |
| **Logistics/Construction/F&B** | 10K+ شركة | علاقات بشركات، لا outbound | Partnership Sprint = شبكة شراكات |

**ICP الحالي (Beta):** Marketing Agencies في الرياض/جدة (10–50 موظف). لماذا؟ لأنهم قناة توزيع، يفهمون قيمة Pilot، وعندهم عملاء جاهزون.

### الطبقة 3 — Problem Positioning (المشكلة كما يرونها هم)

**ليس:** "نحن نحتاج CRM"
**بل:** "كل شهر نخسر فرص لأنه ما عندنا فريق نمو، والوكالة عندها claims غير مُثبتة، والـ AI tools تكتب رسائل لا تشبه السعودية، والـ WhatsApp tools تخاطر بـ ban، وما عندنا proof نريه للقيادة."

**Dealix كحل واحد لـ 6 مشاكل في وقت واحد**:
1. لا فريق نمو ✅ → Autonomous Service Operator
2. لا proof ✅ → Proof Pack أسبوعي
3. رسائل غير سعودية ✅ → Saudi Tone Eval
4. WhatsApp risk ✅ → opt-in audit + draft only
5. لا ROI mapping ✅ → Revenue Work Units
6. لا multi-channel ✅ → 11 connectors تحت سقف واحد

### الطبقة 4 — Pricing Positioning (Anchor Strategy)

```
0 ر.س   — Free Diagnostic                  (24h tease)
499     — First 10 Opportunities Sprint    (one-time wedge)
1,500   — Data to Revenue                  (data-rich SMB)
2,999/mo— Executive Growth OS              (anchor — most-sold)
3,000-7,500 — Partnership Growth          (agency upsell)
Custom  — Full Growth Control Tower       (enterprise)
```

**القاعدة:** السعر الأساسي = **2,999 ر.س/شهر**. كل شيء آخر يُسوَّق كـ "بداية رخيصة" أو "حالة خاصة". هذا anchoring يجعل 499 يبدو هدية و2,999 يبدو معقول.

---

## 3. Go-To-Market Strategy (12 شهر)

### Phase 1 — Paid Beta Sprint (Months 1–3)
**الهدف:** أول 10 paying customers + 3 case studies + 3 agency partners.

**القنوات (مرتبة حسب الأولوية):**

#### Channel 1 — Founder-Led Outbound (60% من الجهد)
- 25 رسالة manual يومياً (LinkedIn DM يدوي + Email + WhatsApp opt-in).
- Founder voice: المؤسس يبيع بنفسه. لا SDR. لا automation.
- Cadence: 3 messages/prospect over 7 days (initial → value-add → final).
- ICP: Agencies (10/day), Training (5/day), B2B SaaS (5/day), Local services (5/day).
- KPI: 25 messages → 5 replies → 2 demos → 1 pilot → 1 paid (الأسبوع الأول هدف Realistic).

#### Channel 2 — Agency Partnership Program (25% من الجهد)
- Pilot 1 لكل وكالة → case study → revenue share 20% on referrals.
- Co-branded Proof Pack (الوكالة + Dealix logos).
- Monthly partner scorecard.
- KPI: 3 وكالات في 90 يوم → 9 sub-clients → 27% conversion to paid.

#### Channel 3 — Founder Content (10% من الجهد)
- 1 LinkedIn post/day (founder voice، باللغة العربية).
- 1 X (Twitter) post/day (نصائح تشغيلية، arabic).
- Weekly newsletter (10 توصية لكل وكالة سعودية، arabic).
- Long-form: 1 article/week (arabic) عن "كيف تشغّل النمو بدون فريق".
- KPI: 500 followers → 10 inbound leads/شهر بنهاية Phase 1.

#### Channel 4 — Strategic PR (5% من الجهد)
- Aim for: Asharq Business، Saudi Gazette، Wamda، Magnitt.
- Story: "أول Saudi Revenue Execution OS — مؤسس سعودي يبني فئة جديدة".
- Pitch بعد أول 5 paying customers (proof matters).

### Phase 2 — Pilot Expansion (Months 4–6)
**الهدف:** 30 paying customers + Agency network 10 partners + $50K MRR.

- توسيع الـ outbound من 25/يوم إلى 50/يوم (مع SDR واحد part-time).
- إطلاق Public landing pages بالعربية + الإنجليزية.
- إطلاق "Dealix Academy" (محتوى تدريبي مجاني → leads).
- بدء AEO/SEO استثمار جاد (Arabic-first).
- إطلاق "Dealix Marketplace" (الوكالات تنشر عروضها).

### Phase 3 — GA + Series-A Prep (Months 7–12)
**الهدف:** 200 paying customers + $300K ARR + Series A pitch ready.

- Self-serve onboarding (لا يحتاج demo).
- API documentation pública.
- Affiliate program (الوكالات تربح 30% recurring).
- إطلاق Mobile app (PWA على الأقل).
- Series A pitch deck + 18-month plan.

---

## 4. Sales Playbook (5 مراحل)

### Stage 1 — Prospecting
**القناة الأساسية:** LinkedIn Sales Navigator (يدوي) + Apollo (lookup فقط، لا scraping) + Personal Network.

**ICP filters:**
- Industry: Marketing Agency / B2B SaaS / Training / Consulting.
- Size: 10–50 employees.
- Location: SA (Riyadh/Jeddah/Dammam priority).
- Title: Founder, CEO, Head of Growth, Head of Marketing, Head of Sales.
- Signals: Hiring (growth/sales role), Series A funded, Recent product launch, LinkedIn activity.

**Output:** 100 prospects/أسبوع → Operating Board.

### Stage 2 — Qualification (BANT-Saudi)
**B**udget: 499 SAR قادر؟ Pilot accessible. 2,999/mo قادر؟ Growth OS.
**A**uthority: Founder/CEO أو Head of Growth/Sales/Marketing.
**N**eed: محتاج فرص جديدة، أو عنده قائمة، أو يبحث عن شراكات.
**T**iming: يدفع هذا الشهر؟ → MQL. هذا الربع؟ → Nurture.

**Output:** 25% من prospects → MQL.

### Stage 3 — Demo (12 دقيقة, Saudi-pace)
**Structure (12 minutes total):**
- 0–2: تعرّف (الاسم، الشركة، الـ pain).
- 2–6: Show — 3 features حقيقية:
  1. Live Free Diagnostic (يأخذ 30 ثانية).
  2. Saudi Tone Eval على رسالة سيئة (يلوّن المشاكل).
  3. Approval flow على رسالة WhatsApp (يُظهر approval modal).
- 6–9: Pricing — 5 bundles → 499 anchor → 2,999 anchor.
- 9–12: قرار — "نبدأ Pilot 499 يوم الأحد؟" أو "أرسل لك Free Diagnostic أولاً؟"

**القاعدة:** لا تستخدم slides. استخدم المنتج الحي.

**Output:** 50% من demos → Pilot أو Free Diagnostic.

### Stage 4 — Pilot (7 أيام, $499)
**Day 0 (T+0):** intake (15 دقيقة) → سجّل في Operating Board.
**Day 1 (T+24):** Free Diagnostic سُلِّم (3 فرص + رسالة + مخاطرة + توصية).
**Day 2 (T+48):** Pilot كامل (10 فرص + 10 رسائل + خطة متابعة).
**Day 7:** Proof Pack نهائي + جلسة مراجعة 30 دقيقة + 3 upgrade paths.

**Output:** 70% من Pilots → Growth OS Monthly OR Case Study.

### Stage 5 — Expansion (Recurring)
**Month 2:** Quarterly Business Review (QBR).
**Month 3:** Cross-sell Partnership Sprint (3,000–7,500 ر.س).
**Month 6:** Annual upgrade (Growth OS Pro, custom price).
**Month 12:** Renewal + 15% expansion (more channels, more agents).

**KPIs:**
- Net Revenue Retention (NRR) target: 130%.
- Logo Retention target: 90%.
- Time to First Proof Pack: ≤ 48h.

---

## 5. Customer Journey Map (8 مراحل)

```
1. UNAWARE        → 2. PROBLEM-AWARE   → 3. SOLUTION-AWARE
4. PRODUCT-AWARE  → 5. ACTIVATED       → 6. RETAINED
7. EXPANDED       → 8. ADVOCATE
```

| Stage | Trigger | Channel | Asset | Conversion Goal |
|-------|---------|---------|-------|-----------------|
| 1. Unaware | LinkedIn impression | Founder content | Arabic post about pain | Click profile → 2 |
| 2. Problem-aware | "أحتاج فرص" | Newsletter signup | Free Diagnostic CTA | Subscribe → 3 |
| 3. Solution-aware | Visits dealix.sa | landing/companies.html | Demo video 12min | Book demo → 4 |
| 4. Product-aware | Demo done | Live demo + landing | Pilot 499 offer | Pay 499 → 5 |
| 5. Activated | Pilot paid | Onboarding flow | First Proof Pack | Approval rate ≥30% → 6 |
| 6. Retained | Month 2 | QBR call | Growth OS subscription | Upgrade to 2,999/mo → 7 |
| 7. Expanded | Month 3+ | CSM relationship | Partnership Sprint | +3,000 ر.س → 8 |
| 8. Advocate | Month 6+ | Case study + referrals | Co-branded content | 1+ referral/quarter |

---

## 6. Competitive Moat Strategy (5 طبقات)

### Moat 1 — Data Moat (Saudi Revenue Graph)
**كيف يبني:**
- كل event من كل عميل (مع الموافقة) → Revenue Graph عام.
- بعد 100 عميل، Dealix يعرف:
  - أي رسالة عربية تُحوِّل في قطاع X؟
  - أي قناة الأفضل لشركة Y بحجم Z؟
  - متى أفضل وقت للتواصل في رمضان؟
- HubSpot/Salesforce لا يستطيعون بناء هذا — بياناتهم عالمية.

**Time to build:** 12 شهر.

### Moat 2 — Brand Moat (Saudi-First)
**كيف يبني:**
- Founder presence على LinkedIn/X بالعربية يومياً.
- Saudi-only events (دورة "نمو السعودية" شهرية).
- Saudi-only Customer Advisory Board.
- اللغة، الـ examples، الـ tone — كله سعودي.
- HubSpot/Salesforce محتواهم مترجم — Dealix محتواه مولود سعودي.

**Time to build:** 6 شهر.

### Moat 3 — Compliance Moat (PDPL Native)
**كيف يبني:**
- PDPL audit شهري.
- DPA template جاهز لكل عميل.
- Penetration test ربع سنوي.
- ISO 27001 certification (Year 2).
- HubSpot/Salesforce يجاهدون لـ GDPR — Dealix بُني لـ PDPL من اليوم الأول.

**Time to build:** 9 شهر.

### Moat 4 — Network Moat (Agency Channel)
**كيف يبني:**
- 30 وكالة شريكة بنهاية Year 2.
- كل وكالة عندها 10–50 عميل.
- Lock-in: الوكالة تربح 20% recurring → revenue share switching cost عالي.
- HubSpot/Salesforce ليس عندهم agency program عربي.

**Time to build:** 18 شهر.

### Moat 5 — Distribution Moat (Operator Network)
**كيف يبني:**
- 1,000 "Dealix Operator" certified بنهاية Year 3.
- Operators يبيعون Dealix كـ خدمة لعملائهم.
- كل Operator يربح 30% recurring لمدة 2 سنوات.
- يصبح Dealix "AWS لـ Saudi Sales".

**Time to build:** 30 شهر.

---

## 7. Pricing Strategy & Unit Economics

### Pricing Ladder (Final Form)

| Tier | Price | Target | Conversion | LTV/CAC |
|------|-------|--------|------------|---------|
| Free Diagnostic | 0 | Lead magnet | 100% (free) | — |
| First 10 Sprint | 499 | Wedge | 60% from leads | LTV=499, CAC=200 → 2.5x |
| Data to Revenue | 1,500 | Data-rich SMB | 30% from Pilots | LTV=1500, CAC=300 → 5x |
| Growth OS Monthly | 2,999/mo | Anchor | 40% from Pilots | LTV=36K (12mo), CAC=600 → 60x |
| Partnership Growth | 3,000–7,500 | Cross-sell | 20% from Growth OS | LTV=15K avg, CAC=300 → 50x |
| Full Control Tower | Custom (15K+) | Enterprise | 5% from cohort | LTV=180K, CAC=2K → 90x |

### Unit Economics (Year 1 target)

```
ARPU (blended):           1,800 ر.س/شهر
Gross Margin:             82% (مع compute optimized)
CAC (paid + organic):     600 ر.س
CAC Payback:              4 months
LTV (12-month avg):       21,600 ر.س
LTV/CAC:                  36x  (HubSpot benchmark: 5-7x)
Churn (logo):             8%/month → 30%/year (Year 1)
                          → target 15%/year (Year 2)
NRR:                      130% (with cross-sell)
```

### Pricing Experimentation Plan
- Month 1–3: Lock pricing. Measure conversion.
- Month 4: A/B test 2,999 vs 2,499 vs 3,499 (cohort 30 each).
- Month 7: Add annual plan (10× monthly = 16% discount → cash-flow boost).
- Month 10: Add usage-based add-ons (extra connectors, extra agents).
- Year 2: Move 60% to annual contracts.

---

## 8. Tech Roadmap (18 شهر)

### Q2 2026 (Now)
✅ Tech foundation (12 layers, 791 tests, CI green)
✅ Paid Beta operational layer
⏳ Staging deployment + first 5 paying customers
⏳ First 3 case studies

### Q3 2026
- **Staging → Production**: Railway → AWS (PDPL-compliant region)
- **Public Launch Gate module**: criteria check + automated graduation
- **Pilot Tracker dashboard**: real-time view of all 5–10 pilots
- **Saudi Arabic LLM tuning**: fine-tune on 1K Saudi business messages
- **Email sequences engine**: 7-day drip per ICP

### Q4 2026
- **Self-serve onboarding**: no-demo signup flow
- **Mobile PWA**: iOS-installable
- **Public API**: REST + webhooks
- **Marketplace MVP**: agencies list services
- **Stripe + Moyasar dual billing**

### Q1 2027
- **Saudi Revenue Graph v1**: aggregated insights across all customers
- **AI agents marketplace**: 3rd-party agents publish to Dealix
- **GCC localization**: UAE, Kuwait, Bahrain
- **Enterprise SSO**: Okta, Microsoft, Google

### Q2-Q4 2027
- **Series A fundraise**: $5M target
- **Hire VP Engineering, VP Sales, VP CS**
- **Move to multi-region**: SA + UAE
- **ISO 27001 certification**

---

## 9. Hiring Plan (Year 1 → Year 2)

### Month 1–6 (Founder-Led, 0 hires)
- Founder = CEO + Sales + Engineering + Customer Success.
- Outsource: Saudi Arabic copy editor (freelance, 1K/شهر).

### Month 7–12 (First 5 hires)
1. **SDR (Saudi)**: outbound + qualification — 8K/شهر.
2. **Customer Success Manager**: onboarding + retention — 12K/شهر.
3. **Senior Backend Engineer**: scale APIs — 18K/شهر.
4. **Senior Frontend/PWA Engineer**: web app — 15K/شهر.
5. **Content Marketer (Arabic)**: SEO/AEO — 10K/شهر.

**Year 1 burn:** 250K SAR/شهر بنهاية Q4 → cash runway 18 months from $1M seed.

### Year 2 (Scale to 15 hires)
6–8: Account Executives (3) — 12K/شهر/each.
9–10: Engineers (2) — 16K/شهر/each.
11: VP Engineering — 30K/شهر.
12: VP Sales — 30K/شهر.
13: Designer — 14K/شهر.
14: Data Analyst — 12K/شهر.
15: Recruiter (HR) — 10K/شهر.

---

## 10. Compliance & Risk Roadmap

### PDPL Compliance Timeline
- Month 1: DPA template ✅
- Month 3: Privacy policy v2 (Arabic + English)
- Month 6: Annual PDPL audit (external)
- Month 9: SDAIA registration (if data-sharing required)
- Year 2: ISO 27001 certification
- Year 3: SOC 2 Type II

### Risk Matrix (Top 5)

| Risk | Likelihood | Impact | Mitigation |
|------|-----------|--------|-----------|
| Data breach (PDPL fines up to 5M SAR) | Medium | Critical | Trace redaction + encrypted at rest + quarterly pen test |
| WhatsApp account ban | Medium | High | opt-in audit + complaint rate < 0.3% + Meta Business verified |
| Major customer churn (logo concentration) | Medium | High | No customer > 10% of revenue; sign 12-month contracts |
| Founder burnout | High | Critical | Hire CSM by month 7, SDR by month 9 |
| HubSpot/Salesforce launches Saudi-tuned product | Low | Critical | Build Saudi Revenue Graph + Agency Network = irreplaceable |

---

## 11. Marketing & Content Engine

### Content Pillars (4)
1. **Saudi B2B Growth Tactics** (40% من المحتوى) — practical playbooks.
2. **PDPL/Compliance Education** (20%) — كيف تتواصل آمناً.
3. **Customer Stories / Case Studies** (20%) — proof.
4. **Founder Journey** (20%) — building in public.

### Content Cadence
- **Daily:** 1 LinkedIn post + 1 X post (Founder voice, Arabic).
- **Weekly:** 1 long-form article (1,500 words, Arabic) + 1 newsletter.
- **Bi-weekly:** 1 video (12-min demo or interview, Arabic).
- **Monthly:** 1 case study + 1 webinar.
- **Quarterly:** "State of Saudi Revenue" report (downloadable, lead magnet).

### SEO/AEO Strategy (Arabic-First)
- **Primary keywords:** "زيادة المبيعات السعودية"، "نمو B2B سعودي"، "أداة CRM سعودية"، "تواصل واتساب أعمال".
- **Long-tail:** "كيف أحصل على عملاء B2B في الرياض"، "أفضل أداة Pilot للوكالات السعودية".
- **AEO (AI Engine Optimization):** Optimize for ChatGPT/Claude/Perplexity answers — structured Q&A with attribution.
- **Goal Year 1:** Page 1 for top 20 Arabic B2B keywords.

---

## 12. Brand Identity Architecture

### Brand Voice
- **Direct, not flowery.** "نطلع لك 10 فرص" not "نسعى جاهدين لتقديم".
- **Confident, not arrogant.** "هذا ما يفعله Dealix" not "نحن الأفضل".
- **Saudi, not Egyptian/Levantine.** "شلونك"، "تمام"، "ما يصلح".
- **Data-led, not vague.** "499 ر.س = 10 فرص + 10 رسائل" not "حلول مخصصة".

### Brand Pillars
1. **Local Mastery** — نفهم السعودية أعمق من أي أحد.
2. **Approval-First** — كرامة العميل قبل الـ scale.
3. **Proof Over Promise** — Proof Pack أسبوعي، لا claims.
4. **Open by Design** — لا lock-in، API مفتوح.

### Visual Identity Direction
- **Color:** Saudi Gold (#ffd166) + Deep Black (#0f1115) — حداثة + احترافية.
- **Typography:** Tajawal for Arabic, Inter for English — readable + professional.
- **Iconography:** Minimal line icons (Lucide) — لا cliché business clip-art.

---

## 13. Funding Strategy

### Seed Round ($1M target — Q4 2026)
**Use of funds:**
- Hires: 60% (5 hires × 6 months)
- Infrastructure: 15%
- Marketing/Content: 15%
- Compliance/Audits: 5%
- Buffer: 5%

**Investors to target:**
- STV (Saudi Technology Ventures)
- Wa'ed Ventures (Aramco)
- Sanabil Investments (PIF subsidiary)
- 500 Global MENA
- Wamda Capital
- Plus: angels من الـ Saudi B2B founder community.

**Pitch deck core slides (12):**
1. Title — "The Saudi Revenue Execution OS"
2. Problem — "Saudi B2B is 10 years behind in sales tech"
3. Why now — "$50B Saudi Vision 2030 + AI moment"
4. Solution — Live demo (no slides for this)
5. Product — 12 layers + 200 endpoints + 791 tests
6. Traction — first 10 paying customers + 3 case studies
7. Market — TAM 50K SMBs × 36K SAR/year = $480M
8. Business model — 6 bundles + Year 1 unit economics
9. Competition — moat analysis (Section 6)
10. Team — Founder bio + advisors
11. Financials — 18-month projection
12. Ask — $1M for 18 months runway

### Series A ($5M — Q4 2027)
- Trigger: $1M ARR + 200 paying customers + 30 agency partners.
- Use: GCC expansion + 10 more hires + Saudi Revenue Graph data infrastructure.

---

## 14. الـ 7-Day Sprint (الآن — اليوم 1 إلى اليوم 7)

### اليوم 1 (Today — May 1, 2026)
- **AM:** Push 4 pending files (POST_MERGE_VERIFICATION + scorecard + tests + conftest).
- **AM:** Deploy Railway staging.
- **AM:** Add `STAGING_BASE_URL` secret to GitHub Actions.
- **PM:** Run `launch_readiness_check.py --staging-url $STAGING_BASE_URL` → expect `PAID_BETA_READY`.
- **PM:** Send 25 manual outreach (10 agencies + 5 training + 5 SaaS + 5 local).
- **EOD:** Operating Board updated with all 25 prospects.

### اليوم 2
- **AM:** Follow-up wave 1 (any replies from Day 1).
- **AM:** Send 25 more outreach (different segments).
- **PM:** First 1–2 demos.
- **PM:** Send Free Diagnostic to first 1 interested prospect.
- **EOD:** scorecard.py — expect 2+ replies, 1+ demo.

### اليوم 3
- **AM:** Deliver first Free Diagnostic (T+24h SLA).
- **AM:** 5 follow-ups + 5 new outreach.
- **PM:** First Pilot 499 offer to most-engaged prospect.

### اليوم 4
- **AM:** Pilot 499 sales call.
- **AM:** Send Moyasar invoice manual.
- **PM:** Send payment reminder + start Pilot delivery prep.
- **EOD:** Target — 1 invoice paid OR 1 written commitment.

### اليوم 5 (Pilot Day 1)
- **AM:** Receive intake from paid customer.
- **AM:** Run First 10 Opportunities Sprint workflow.
- **PM:** Generate 10 opportunities + 10 Arabic messages.
- **EOD:** Send Approval Pack to customer.

### اليوم 6 (Pilot Day 2)
- **AM:** Process customer approvals.
- **AM:** Run follow-up sequence.
- **PM:** First 1–2 positive replies.
- **EOD:** ≥3 messages approved + Proof Pack v1 generated.

### اليوم 7 (Proof + Upsell)
- **AM:** Deliver final Proof Pack.
- **AM:** 30-minute review session call.
- **PM:** Pitch Growth OS Monthly upgrade (2,999 ر.س/شهر).
- **EOD:** Case study OR second Pilot OR Growth OS subscription.

**Week 1 Target:** 70 outreach / 15 replies / 7 demos / 3 pilots / 1–2 paid / 1 Proof Pack.

---

## 15. القرار النهائي — Three Numbers That Matter

```
1. أول 499 ر.س — هذا الأسبوع (T+7 days max)
2. أول 10 paid customers — هذا الربع (T+90 days max)
3. أول $1M ARR — هذا العام (T+12 months max)
```

كل قرار في Dealix يُقاس بهل يقرّب من هذه الأرقام أم لا.

أي شيء غير ذلك = تشتيت.

---

## ملحق A — قواعد لا تتنازل عنها (Hard Rules)

1. **لا live send بدون env flag + اعتماد بشري.**
2. **لا scraping. لا auto-DM. لا cold WhatsApp.**
3. **لا Moyasar API charge — invoice manual فقط حتى Year 2.**
4. **لا claims مضمونة. كل promise معه qualifier ("ضمان استرداد 7 أيام").**
5. **لا تشارك Operating Board مع أحد — يحتوي PII.**
6. **لا تخفّض السعر بدون موافقة المؤسس.**
7. **لا تتجاوز SLA — اعتذر بدل أن تتأخر.**
8. **لا تضف feature بدون validation من 3 عملاء على الأقل.**
9. **لا توظّف قبل أن يكون عندك CSM-load > 8 ساعات/يوم.**
10. **لا تقبل investment بدون 18-month plan واضح.**

---

## ملحق B — Endpoints المهمة في كل مرحلة

```
Paid Beta:
GET  /api/v1/launch/private-beta/offer
POST /api/v1/launch/go-no-go
GET  /api/v1/launch/scorecard/demo
GET  /api/v1/operator/bundles
POST /api/v1/operator/chat/message
POST /api/v1/customer-ops/onboarding/checklist
POST /api/v1/customer-ops/connectors/summary
POST /api/v1/revenue-launch/payment/invoice-instructions
POST /api/v1/revenue-launch/proof-pack/template
GET  /api/v1/service-excellence/review/all

Public Launch (after this Master Plan):
GET  /api/v1/public-launch/gate-check
GET  /api/v1/public-launch/pilot-tracker
POST /api/v1/public-launch/graduate-pilot
GET  /api/v1/public-launch/case-studies
GET  /api/v1/public-launch/agency-network
```

---

## ملحق C — Decision Trees

### "هل نقبل هذا العميل؟"
```
هل ICP match؟ (agency / B2B SMB / training / SaaS)
├─ Yes
│  ├─ هل authority? (Founder/Head)
│  │  ├─ Yes → Pilot 499 offer
│  │  └─ No → ask for intro to authority
│  └─ هل budget? (499+)
│     ├─ Yes → Pilot 499 offer
│     └─ No → Free Diagnostic + nurture
└─ No → polite decline + refer to network
```

### "هل نطلق feature جديد؟"
```
هل عندنا 3 paying customers طلبوه؟
├─ Yes
│  ├─ هل service_score يرتفع به ≥80؟
│  │  ├─ Yes → ابني (1-week sprint)
│  │  └─ No → adjust scope حتى ≥80
│  └─ هل يخالف Hard Rules؟
│     ├─ Yes → reject
│     └─ No → ابني
└─ No → log في feature-backlog، لا تبني
```

### "هل نوظّف هذا الشخص؟"
```
هل عندنا CSM-load > 8 ساعات/يوم؟
├─ Yes
│  ├─ هل cash > 6 months runway بعد التوظيف؟
│  │  ├─ Yes → وظّف
│  │  └─ No → وظّف part-time أو contractor
│  └─ هل يأخذ من المؤسس مهمة عمرها > 4h/يوم؟
│     ├─ Yes → وظّف
│     └─ No → أجّل
└─ No → أجّل
```

---

## الخاتمة

**Dealix لا يفوز بأنه أكثر features.**
**Dealix يفوز بأنه أعمق فهماً للسعودية + أوضح Proof + أصدق Approval-first + أعرف agency channel.**

**كل شيء في هذه الوثيقة يخدم هذا.**

**ابدأ الآن: ادفع 4 الملفات → نشر staging → 25 رسالة → أول 499 ر.س.**

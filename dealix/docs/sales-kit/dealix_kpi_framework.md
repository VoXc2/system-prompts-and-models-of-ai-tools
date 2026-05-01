# 📊 Dealix — KPI Framework & Weekly Scorecard

**الفلسفة:** ما لا يُقاس، لا يتحسّن.
**القاعدة:** 5 KPIs أسبوعية — لا أكثر. التركيز = النجاح.

---

## 🎯 الـ 5 KPIs الأسبوعية (North Star Metrics)

هذه الـ 5 فقط — تُراقَب كل اثنين صباحاً:

### 1. MRR (Monthly Recurring Revenue)
- **التعريف:** مجموع الاشتراكات الشهرية النشطة
- **الهدف Y1:** نمو 25% شهرياً
- **التنبيه:** < 15% شهرياً
- **كيف تقيس:** مجموع (active_subscriptions × monthly_price)

### 2. New Customers (مدفوع)
- **التعريف:** عملاء جُدد أكملوا دفعة أولى (مو trial)
- **الهدف Y1:** 10-15 عميل/شهر بعد M6
- **التنبيه:** 0 في أسبوع
- **كيف تقيس:** COUNT(customer WHERE first_payment_date BETWEEN ...)

### 3. Churn Rate (Monthly)
- **التعريف:** % من العملاء الذين ألغوا
- **الهدف:** < 3%
- **التنبيه:** > 5%
- **كيف تقيس:** (cancelled / start_of_month_active) × 100

### 4. Pipeline Value (Weighted)
- **التعريف:** مجموع opportunities في pipeline × probability
- **الهدف:** 3x MRR الشهري المطلوب
- **التنبيه:** < 2x
- **كيف تقيس:** sum(deal_value × stage_probability)

### 5. NPS (Net Promoter Score)
- **التعريف:** رضا العملاء (0-100 scale)
- **الهدف:** > 50 (Good) / > 70 (Great)
- **التنبيه:** < 30
- **كيف تقيس:** % Promoters - % Detractors (quarterly survey)

---

## 📋 Weekly Scorecard Template

```
📅 Week of: [التاريخ]
🎯 Goal: [الهدف الأساسي هذا الأسبوع]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📊 PRIMARY METRICS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1. MRR:              [current] → [target] ([±%])
2. New Customers:     [count] (week) / [count] (MTD)
3. Churn:             [count] / [%]
4. Pipeline:          [ريال] weighted
5. NPS:               [score]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
📈 SECONDARY METRICS (Context)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Outreach:
- Messages sent:      [count]
- Reply rate:         [%]
- Demos booked:       [count]

Product:
- Active users/week:  [count]
- Conversations:      [count]
- Leads qualified:    [count]

Financial:
- Revenue collected:  [ريال]
- Burn:              [ريال]
- Cash balance:       [ريال]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
✅ WINS (3)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. [اكتب هنا]
2. [اكتب هنا]  
3. [اكتب هنا]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
⚠️ MISSES (كن صريحاً)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. [ما الذي لم يسِر جيداً؟]
2. [درس مستفاد؟]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━
🎯 NEXT WEEK (Top 3)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
1. [أولوية 1]
2. [أولوية 2]
3. [أولوية 3]
```

**مشاركة:** email لنفسك كل اثنين 8 صباحاً. أرشيف للـ patterns.

---

## 📅 Monthly Deep Review

### أول يوم كل شهر (60 دقيقة)

#### 1. Financial Review (15 دقيقة)
- P&L الشهر
- Cash position
- Runway update
- Unit economics (CAC, LTV, payback)

#### 2. Product Review (15 دقيقة)
- Features shipped
- Bugs outstanding
- Performance metrics
- User feedback themes

#### 3. Sales Review (15 دقيقة)
- Pipeline by stage
- Win/loss analysis
- Sales cycle trends
- Top deals at risk

#### 4. Customer Review (15 دقيقة)
- NPS changes
- Usage patterns
- Expansion opportunities
- Churn reasons

**النتيجة:** Monthly report مكتوب، 2-3 صفحات max.

---

## 🎯 OKRs (Objectives & Key Results)

### النموذج:

**Objective:** (Qualitative، مُلهم، quarterly)
- KR1: (Quantitative، محدد، Pass/Fail)
- KR2:
- KR3:
- KR4:

### مثال: Q2 2026

**Objective:** Launch Dealix للإنتاج بنجاح وبناء قاعدة عملاء أولى
- **KR1:** 20 عميل مدفوع بنهاية Q2
- **KR2:** MRR ≥ 60K ريال بنهاية Q2
- **KR3:** 99.9% uptime
- **KR4:** NPS ≥ 50

### Scoring:
- **Pass:** 70%+ من الـ KR achieved
- **Stretch pass:** 100%+
- **Fail:** < 70%

**القاعدة:** 3 OKRs max per quarter. الكثرة = التشتت.

---

## 📊 Dashboards الأساسية

### Dashboard 1: Business Health (Daily)
مسؤول: Founder

**Widgets:**
- MRR (current + 30-day trend)
- Active customers
- New signups today
- Failed payments (need attention)
- Support tickets open

**Tool:** Google Sheets + Retool (MVP), Metabase/Looker (after M6)

### Dashboard 2: Sales Pipeline (Weekly)
مسؤول: Founder → BDR عند التوظيف

**Widgets:**
- Pipeline by stage (funnel)
- Deals moving this week
- Stuck deals (> 14 days no activity)
- Win rate by source

**Tool:** HubSpot pipeline + custom views

### Dashboard 3: Product Analytics (Weekly)
مسؤول: Founder (CTO eventually)

**Widgets:**
- Conversations/day
- Lead qualification rate
- Booking conversion
- Error rates
- Response times

**Tool:** PostHog self-hosted

### Dashboard 4: Customer Success (Monthly)
مسؤول: CS Manager (عند التوظيف)

**Widgets:**
- Health scores per account
- Usage trends (up/down)
- NPS changes
- Expansion opportunities
- Churn risks

**Tool:** Custom dashboard + Salesforce (eventually)

---

## 🚨 Red Flags (إشارات خطر)

### Immediate action needed:

1. **MRR drop > 10% in a week** → إجراء retention campaign
2. **Churn > 5% monthly** → تحقيق الأسباب، call كل عميل مُلغي
3. **Pipeline < 1.5x MRR target** → زيادة outreach فوراً
4. **NPS < 30** → analysis الـ detractors، plan للتحسين
5. **Cash runway < 6 شهور** → تسريع sales أو fundraise

### Yellow flags (مراقبة):

- CAC يرتفع > 30%
- Sales cycle يطول > 40%
- Support tickets > 20% زيادة
- Team velocity يقل (PRs, features)
- Customer health scores declining

---

## 💾 أدوات القياس (Tech Stack)

### M1-M3 (Free/Cheap):
- **Google Sheets** — financial + pipeline tracking
- **PostHog self-hosted** — product analytics
- **Stripe + Moyasar dashboards** — payments
- **Plausible** — website analytics (privacy-first)
- **Notion** — OKRs + documentation

### M4-M9 (Scaling):
- **HubSpot Free** — CRM
- **Metabase** — business intelligence
- **Linear** — product management
- **Intercom** — customer messaging (eventually)

### M10+:
- **Salesforce** (if Enterprise-heavy)
- **Looker** — advanced BI
- **Segment** — data pipeline
- **Zapier/Make** — integrations

---

## 📈 Benchmarks للـ SaaS سعودي

مقارنة أدائك مع السوق:

| Metric | أقل من المعدل | المعدل | فوق المعدل |
|--------|----------------|---------|-------------|
| Monthly churn | >6% | 3-5% | <3% |
| Gross margin | <70% | 75-85% | >85% |
| LTV:CAC | <3 | 3-5 | >5 |
| Sales cycle | >60 days | 30-60 | <30 |
| NPS | <30 | 30-50 | >50 |
| Revenue/employee | <$100K | $100-200K | >$200K |
| Monthly growth | <10% | 10-20% | >20% |

**Dealix الحالي target:** "فوق المعدل" في كل المقاييس.

---

## 🎯 Weekly Rituals

### الاثنين 8:00 ص — Planning
- Review KPIs من الأسبوع السابق
- كتابة الـ scorecard
- تحديد الـ top 3 هذا الأسبوع

### الثلاثاء-الخميس — Execution
- 80% على الأولويات
- 20% على maintenance + support

### الجمعة 2:00 م — Retrospective
- ما ذهب جيداً؟
- ما الذي يحتاج تحسين؟
- ماذا نغيّر الأسبوع القادم؟

### السبت-الأحد — Rest (مهم!)
- لا email
- لا GitHub (إلا طوارئ)
- إعادة الشحن

**حرق نفسك = إفشال الشركة.**

---

## 🔍 Customer Interview Framework (Monthly)

كل شهر، مكالمة 30 دقيقة مع 3-5 عملاء:

### الأسئلة (بهذا الترتيب):

1. "على مقياس 1-10، كم احتمال توصي بـ Dealix لصديق؟" (NPS)
2. "ليش [الرقم] وليس [الرقم+1]؟" (improvement areas)
3. "وش أكبر قيمة حصلت عليها حتى الآن؟" (strengths to amplify)
4. "وش الميزة اللي إذا اضفناها، تستخدمها كل يوم؟" (roadmap input)
5. "لو Dealix اختفى غداً، وش تستخدم؟" (competitive moat)
6. "تعرف أحد مثلك يحتاج Dealix؟" (referral ask)

**سجل المكالمة (بموافقة)، حلّل الـ patterns شهرياً.**

---

## 📊 Success Definitions (Long-term)

### Y1 Success (Q1 2027):
- ✅ 120+ عملاء
- ✅ 4M+ ARR
- ✅ EBITDA positive
- ✅ NPS > 50
- ✅ 5-7 team members
- ✅ Seed round raised

### Y2 Success (Q1 2028):
- ✅ 360+ عملاء (3x growth)
- ✅ 12M+ ARR
- ✅ Profitable (30%+ margin)
- ✅ NPS > 60
- ✅ 12-15 team members
- ✅ Expanded to UAE + Kuwait

### Y3 Success (Q1 2029):
- ✅ 1,000+ عملاء
- ✅ 30M+ ARR
- ✅ Series A closed
- ✅ Regional leader in Arabic sales AI
- ✅ 30-40 team members

---

## 🏆 الخلاصة

**القياس = الوضوح = التحسين.**

5 KPIs أسبوعياً. 1 OKR quarterly. Review شهري.

لا تبني dashboards ممتدة قبل ما يكون عندك data. ابدأ بـ spreadsheet.

**أهم شيء: اختر ما تقيس، قسه بصدق، وتصرف على ما تراه.**

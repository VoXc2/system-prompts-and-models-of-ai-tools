# Dealix — Crisis Management Playbook

> ما تعمل عند: service outage، data breach، churn event، PR crisis، co-founder dispute. مكتوب قبل الأزمة، مطبّق وقتها.

**آخر تحديث**: أبريل 2026 | **المراجعة**: كل 6 شهور

---

## 🚨 مبدأ الأساس

> **"الأزمة ما تختبر المنتج — تختبر الـ response."**

1. **خلال 5 دقائق**: أعترف بالمشكلة (لا إنكار)
2. **خلال ساعة**: تواصل مع المتأثرين
3. **خلال يوم**: خطة حل + timeline
4. **خلال أسبوع**: Post-mortem + preventive measures

---

## 🔴 Category 1: Service Outage

### التعريف
Dealix API، dashboard، أو payment processing down أكثر من 5 دقائق.

### الإجراء الفوري (0-15 دقيقة)
1. **Sami أو on-call engineer** يستلم التنبيه من Uptime Robot
2. **افتح Status Page** — `status.dealix.sa` (يُحدّث يدوياً الآن، auto Q3)
3. **انشر update**:
   ```
   🔴 We're investigating an issue affecting [component].
   Started: [timestamp AST]
   Monitoring: https://status.dealix.sa
   ```
4. **افتح Slack channel** `#incident-YYYY-MM-DD`
5. **Identify root cause** (logs من Sentry + Railway)

### الإجراء (15-60 دقيقة)
1. **Fix أو rollback** — أيهما أسرع
2. **تحديث status page** كل 15 دقيقة حتى resolution
3. **إرسال إيميل** للعملاء المتأثرين إذا > 15 دقيقة
4. **تحديث على Twitter/X** إذا > 30 دقيقة

### ما بعد الأزمة (< 24 ساعة)
1. **Post-mortem** (template أدناه)
2. **Credit refund**: 1 يوم مجاني لكل ساعة downtime
3. **Update customer success playbook** للتعامل المستقبلي

### Post-mortem Template
```markdown
# Incident: [Title] - [Date]

## Summary
[2-3 جمل]

## Timeline (AST)
- HH:MM — First alert
- HH:MM — Engineer ack
- HH:MM — Root cause identified
- HH:MM — Fix deployed
- HH:MM — Full recovery

## Root Cause
[تقني بدقة]

## Impact
- X عملاء متأثرين
- Y دقيقة downtime
- Z SAR في credits refunded

## What Went Well
- ...

## What Didn't
- ...

## Action Items
- [ ] Owner: Due date
```

### المسؤول
**Primary**: Sami (حالياً)، Hire #1 Backend Engineer (بعد M2)  
**Escalation**: لا يوجد (Sami هو الـ escalation)

---

## 🔒 Category 2: Data Breach / Security Incident

### التعريف
وصول غير مصرّح لبيانات العميل، leak على GitHub، compromised API key.

### الإجراء الفوري (0-30 دقيقة)
1. **عزل النظام المتأثر** (disable API key، revoke access)
2. **فريق الـ response**:
   - Sami (Commander)
   - Security lead (Hire #1 بعد M3)
   - Legal counsel (on-retainer)
3. **توثيق كل action** في `/security/incidents/YYYY-MM-DD/`

### الإجراء (خلال 24 ساعة)
1. **Forensic analysis**:
   - Logs فيها إيش؟
   - كم عميل متأثر؟
   - شنو البيانات المكشوفة؟
2. **إعلام العملاء المتأثرين** (PDPL requires within 72 hours)
3. **إبلاغ SDAIA** (Saudi Data & AI Authority) إذا > 100 سجل متأثر
4. **Rotate ALL credentials** (API keys, DB passwords, Moyasar secret)

### Template: Customer Notification (AR)
```
السلام عليكم،

نعلن بشفافية عن حادث أمني في Dealix:

**ما صار**: [وصف موجز]
**متى**: [date]
**بياناتك المتأثرة**: [specific data]
**اللي عملناه**: [mitigation steps]

**اللي نطلب منك**:
- تغيير كلمة مرور حسابك الآن: [link]
- مراقبة حسابك للـ 30 يوم القادمة
- تفعيل 2FA إذا ما مفعّل

عذراً عن الإزعاج. نأخذ أمان بياناتك بجدية كاملة.

سامي العسيري
Founder | Dealix
```

### الوقاية (بناء في المنتج)
- **Secret scanning** على GitHub (Gitleaks في pre-commit hook)
- **Dependency scanning** (Dependabot + Snyk)
- **Penetration test** سنوي (Q3 2026 أول واحد)
- **Security training** لكل موظف جديد (شهر 1)

---

## 💔 Category 3: Major Churn Event

### التعريف
- عميل Enterprise (Scale tier) أو 3+ عملاء Growth tier churn في شهر واحد
- أو: churn rate > 8%/شهر

### الإجراء الفوري (خلال ساعة من الإبلاغ)
1. **Sami يتصل شخصياً** بالعميل المنسحب (مو إيميل، مكالمة)
2. **Exit interview** — 15 دقيقة:
   - ليش قررت تنسحب؟
   - هل جرّبت تواصل معنا قبل؟
   - وش اللي كان يمنع الـ churn؟
   - تنصحنا بشيء؟
3. **توثيق** في `/churn/YYYY-MM-DD-customername.md`

### تحليل Root Cause (خلال 48 ساعة)
Categorize الـ churn:
- **Product gap**: ميزة ناقصة
- **Pricing**: رأوا بديل أرخص
- **Support**: ما وصلوا للمساعدة وقت الحاجة
- **Economic**: مشكلة داخلية عندهم (مو مشكلتنا)
- **Wrong fit**: ما كانوا ICP أصلاً

### Action Plan حسب السبب
| السبب | الـ action |
|-------|----------|
| Product gap | ضيف للـ roadmap، rank حسب frequency |
| Pricing | راجع pricing strategy، ابن "Lite" tier ممكن |
| Support | دعم أفضل + أسرع response time |
| Economic | ما نحاول rescue — نحفظ العلاقة للمستقبل |
| Wrong fit | حسّن qualification criteria في sales |

### Prevention
- **Health score** أسبوعي لكل عميل (usage + NPS + support tickets)
- **Red flag alerts**: login < 1/أسبوع لـ 14 يوم → تدخّل CS
- **Quarterly business review** (QBR) لكل Enterprise

---

## 📢 Category 4: PR Crisis / Social Media Backlash

### التعريف
- Tweet viral ضد Dealix (> 100 interactions negative)
- مقال سلبي في وسيلة إعلام
- خلاف علني مع competitor أو customer

### الإجراء الفوري (خلال 30 دقيقة)
1. **لا ترد فوراً** — اجلس + افهم
2. **Assemble team**: Sami + Sales Lead + Legal (إذا legal implications)
3. **قيّم الـ severity**:
   - **مخفّفة**: عميل واحد زعلان → نرد شخصي
   - **متوسطة**: trend في نقد معيّن → statement عام
   - **حادّة**: اتهامات serious → full response plan

### Response Principles
1. **ما ترد بشكل دفاعي** — اعترف إذا فيه خطأ
2. **ما تبحث الشخص على media عام** — تواصل خاص
3. **ما تعمل screenshot wars** — ارفع مستوى النقاش
4. **Facts > Feelings** — إذا النقد خطأ، صحّحه بأدلة

### Template: Public Apology (إذا كان الخطأ من Dealix)
```
نعتذر لـ [person/group]. [ما حصل] كان خطأ منّا.

نعمل الآن على:
1. [specific action 1]
2. [specific action 2]

نتحمّل المسؤولية كاملة. لو عندك أي ملاحظة إضافية، DM أو sami@dealix.sa.

— سامي، Founder
```

### ممنوعات
- ❌ حذف التغريدات/الردود (screenshots دائماً موجودة)
- ❌ block أي شخص ينتقد (يبيّنك ضعيف)
- ❌ الرد بعاطفة — خذ 2 ساعات قبل أي response
- ❌ إلقاء اللوم على موظف أو مورّد

---

## 👥 Category 5: Co-founder / Key Employee Dispute

### التعريف
- خلاف strategic major مع co-founder
- موظف key (senior) يهدّد بالاستقالة
- claim قانوني من موظف سابق

### الإجراء
1. **خاص أولاً**: مكالمة 1:1 فوري، اسمع كامل
2. **وثّق**: كل conversation + email + decision
3. **استشر legal** قبل أي قرار كبير
4. **لا تتكلم مع فريق الباقي** حتى تحصل clarity

### Prevention
- **Co-founder agreement** محكم من اليوم الأول (4y vest, 1y cliff)
- **Equity dispute resolution** آلية (arbitration في SA)
- **Regular 1:1s** (أسبوعياً مع co-founder، شهرياً مع key employees)
- **Exit planning** للجميع — nobody surprised

---

## 💰 Category 6: Financial Crisis

### التعريف
- Runway < 3 شهور
- Major customer بطّل payment
- Seed ما تجمّع بالوقت المخطط

### الإجراء حسب Severity

#### Mild (Runway 6-9 شهور)
- تسريع fundraising
- reduce non-essential spend (tools, travel)
- focus على cash-positive customers

#### Moderate (Runway 3-6 شهور)
- Freeze hiring
- Push collections aggressively
- Consider bridge financing (SAFE extension من existing investors)

#### Severe (Runway < 3 شهور)
- **Salary cuts voluntary** (founder first، 50%)
- **Let go** non-essential roles
- **Pivot communication** للمستثمرين
- **Last resort**: wind-down plan (بيع الـ IP، refund customers)

### Emergency Contacts
- **Accountant**: (سيُعيّن بعد LLC)
- **Legal (bankruptcy/restructuring)**: Khoshaim & Associates
- **Potential bridge investors**: (top 3 from data room)

---

## 🎯 Proactive Measures (Not Crisis — Prevention)

### Monthly Drills
- **1st Monday**: Uptime/Sentry review — any near-misses؟
- **15th**: Security patches review — كل dependencies updated؟
- **Last Friday**: Churn review — أي warnings في health scores؟

### Quarterly
- **Q1**: Penetration test (Q3 2026 اول واحد)
- **Q2**: Fire drill (simulated outage)
- **Q3**: Customer satisfaction deep dive (50+ interviews)
- **Q4**: Financial audit review

### Annual
- **Full playbook review** — update this document
- **Insurance review**: E&O، cyber liability
- **Legal audit**: contracts، IP، compliance

---

## 📞 Crisis Hotline (Internal)

### المسؤوليات
| الأزمة | الـ Commander | Backup |
|--------|---------------|--------|
| Outage | Sami | Hire #1 (Backend) |
| Security | Sami | Hire #1 + Legal |
| Churn | Sami | Hire #4 (CS) |
| PR | Sami | Hire #2 (Sales Lead) |
| Financial | Sami | Board/Investors |

### رقم الطوارئ الداخلي
- **Sami**: [مسجّل في private notes]
- **Legal**: [on-retainer بعد LLC]
- **Accountant**: [on-retainer]

### معلومات لا تكشفها في وقت الأزمة
- Cap table details
- Customer pipeline
- Team internal conflicts
- Future pivots غير معلنة

---

## ✅ Post-Crisis Checklist (أي نوع)

خلال 48 ساعة من الحل:
- [ ] Post-mortem مكتوب + shared
- [ ] Action items موزّعة + due dates
- [ ] Communication to stakeholders (customers, investors, team)
- [ ] Playbook updated بالـ lessons learned
- [ ] Team debrief (open session، no blame)

---

## 🧠 الفلسفة النهائية

> "كل startup لها أزمة أو اثنتين يحدّدان مصيرها. مو الأزمة نفسها المهم — الـ response اللي يُبنى عليه trust."

> "العميل ما يزعل لأن حصلت مشكلة. يزعل لأنك ما تكلّمت معه، أو كذبت عليه، أو ما تعلّمت منها."

> "الشفافية في الأزمة = Brand equity على المدى الطويل."

---

**Dealix — Prepared. Calm. Trustworthy. Even in chaos.**
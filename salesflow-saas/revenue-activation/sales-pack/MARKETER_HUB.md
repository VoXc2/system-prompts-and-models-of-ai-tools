# Marketer Hub — Dealix Internal Reference

> **القاعدة**: لا تبيع إلا ما هو حي فعلاً.

---

## Positioning المعتمد

### One-line
> Dealix — نظام تشغيل الصفقات والنمو المؤسسي للشركات السعودية

### Elevator (30 ثانية)
> Dealix يدير صفقاتك من الاكتشاف إلى الإثبات. AI يحلل ويقترح، النظام ينفذ، البشر يعتمدون، وكل شيء مثبت بالأدلة. مصمم للسوق السعودي — عربي أولاً، PDPL مدمج، واتساب native.

### 3 Value Pillars
1. **سرعة**: قصّر دورة الصفقة 40% والموافقات من أيام لساعات
2. **وضوح**: Executive Room لحظي — القرار الصحيح بالوقت الصحيح
3. **ثقة**: كل قرار مثبت بحزمة أدلة SHA256 + امتثال PDPL مدمج

---

## ICP — العميل المثالي

| البند | المواصفات |
|-------|----------|
| الحجم | 20-200 موظف |
| القطاع | B2B: عقارات، إنشاءات، خدمات مالية، استشارات، تقنية |
| الموقع | الرياض، جدة، الدمام |
| الألم | مبيعات بطيئة، موافقات يدوية، لا رؤية تنفيذية |
| الميزانية | 15K-50K SAR pilot |

---

## Objection Handling

| الاعتراض | الرد المعتمد |
|----------|-------------|
| "غالي" | "كم تكلفك صفقة واحدة ضايعة؟ Pilot يدفع نفسه." |
| "عندنا CRM" | "Dealix يشتغل فوق CRM — يضيف الحوكمة والذكاء." |
| "مو جاهزين" | "لهذا عندنا pilot 14 يوم — بلا التزام." |
| "لازم أسأل المدير" | "ممتاز — نسوي demo للمدير مباشرة." |

---

## Approved Claims ✅

يمكنك قول:
- "يقصّر دورة الموافقات من أيام لساعات"
- "PDPL compliance مدمج"
- "Executive Room لحظي"
- "حزم أدلة SHA256"
- "عربي أولاً"
- "واتساب native"
- "19 وكيل ذكاء اصطناعي"

---

## Forbidden Claims ❌

**لا تقل أبداً:**
- ~~"Temporal مستخدم في الإنتاج"~~ (Watch فقط)
- ~~"OPA يحكم السياسات"~~ (Watch فقط)
- ~~"SOC2 certified"~~ (لا نملك الشهادة)
- ~~"ضمان 100% أمان"~~ (لا يوجد ضمان مطلق)
- ~~"أفضل من Salesforce"~~ (مختلف، لا أفضل)
- ~~"autonomy كاملة"~~ (HITL إلزامي للقرارات الحساسة)

---

## Demo Scripts

### Executive Demo (20 دقيقة)
1. افتح Executive Room → اعرض RAG status + metrics
2. افتح Approval Center → اعرض SLA timers + approve/reject
3. شغّل Golden Path → `POST /api/v1/golden-path/run`
4. افتح Evidence Pack → اعرض SHA256 + contents
5. السؤال: "لو هذا عندك الآن، كم يوفر؟"

### Technical Demo (30 دقيقة)
1. كل ما في Executive Demo
2. + اعرض structured outputs (PartnerDossier, ApprovalPacket)
3. + اعرض trace_id correlation
4. + اعرض Saudi Compliance Matrix
5. + اعرض Risk Heatmap

---

## Proof Points الحية

| الإثبات | المصدر |
|---------|--------|
| Golden Path يعمل end-to-end | `POST /api/v1/golden-path/run` |
| 40/40 architecture checks | `scripts/architecture_brief.py` |
| 14 compliance controls | Saudi Compliance Matrix |
| SHA256 evidence packs | Evidence Pack API |
| 9 executive surfaces مربوطة | Frontend components |
| 17 structured output schemas | `schemas/structured_outputs.py` |

---

## Campaign Asset Library

| الأصل | الموقع | الحالة |
|-------|--------|--------|
| One-pager | `sales-pack/ONE_PAGER.md` | جاهز |
| Outreach sequences | `outreach/whatsapp-sequences.json` | جاهز |
| Demo seeder | `demo/seed_demo_tenant.py` | جاهز |
| Deployment guide | `deployment/LIVE_DEPLOYMENT_GUIDE.md` | جاهز |
| Revenue engine | `AUTOMATED_REVENUE_ENGINE.md` | جاهز |
| First 3 clients | `FIRST_3_CLIENTS_PLAN.md` | جاهز |

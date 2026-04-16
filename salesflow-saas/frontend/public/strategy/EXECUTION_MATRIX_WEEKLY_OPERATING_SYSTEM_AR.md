# نظام التشغيل الأسبوعي — Execution Matrix Completion Program

**الإصدار:** v1.0
**الحالة:** Operating Playbook (Weekly Cadence)
**المرجع:** `frontend/public/strategy/EXECUTION_MATRIX_COMPLETION_PROGRAM_AR.md`

---

## 1) الهدف

تثبيت دورة تشغيل أسبوعية موحدة تمنع العودة إلى "الوثائق بدون تنفيذ"، وتضمن أن كل Workstream يُدار بالأدلة (Evidence-first) وبمؤشرات SLA واضحة.

---

## 2) الإيقاع الأسبوعي الرسمي

| اليوم | النشاط | المخرج الإلزامي |
|---|---|---|
| الأحد | تحديث حالة كل Workstream | Current/Partial/Pilot/Production + نسبة التقدم |
| الاثنين | مراجعة Evidence Gates | Pass/Fail لكل deliverable مع روابط الأدلة |
| الثلاثاء | SLA & Risk Review | تقرير الخروقات + الأسباب + خطة التصحيح |
| الأربعاء | Dependency & Blockers Review | قائمة العوائق عبر الفرق + مالك الإزالة + تاريخ الحل |
| الخميس | Executive Review & Commitments | قرارات الأسبوع + التزامات الأسبوع القادم |

---

## 3) طقوس التشغيل (Operating Rituals)

### A) Workstream Standup (30 دقيقة لكل مسار)
- يقدمه Owner المسار.
- يجيب على 5 أسئلة ثابتة:
  1. ما الذي أُنجز هذا الأسبوع؟
  2. ما Evidence Gate الذي نجح/فشل؟
  3. ما المخاطر الجديدة؟
  4. ما خروقات SLA؟
  5. ما التزام الأسبوع القادم؟

### B) Evidence Gate Review (60 دقيقة مشتركة)
- Security + Architecture + Delivery + Data + AI Leads.
- يمنع اعتماد أي إنجاز بلا دليل موثق.
- أي Claim بلا Evidence ينتقل تلقائياً إلى الحالة Partial.

### C) Executive Decision Room (45 دقيقة)
- مراجعة:
  - تقدم المسارات الثمانية.
  - المخاطر عالية الخطورة.
  - القرارات المتوقفة على اعتماد.
- المخرجات:
  - قرارات مكتوبة.
  - Ownership واضح.
  - Deadlines مرتبطة بـ SLA.

---

## 4) قواعد القرار (Decision Rules)

1. **No Evidence = No Progress**
   أي بند بلا دليل لا يُحسب إنجازاً.

2. **Two-SLA-Breaches Escalation**
   إذا تكرر خرق SLA مرتين متتاليتين، يدخل المسار مراجعة تصعيد خلال 48 ساعة.

3. **No New Autonomy Under Trust/Compliance Risk**
   عند وجود فجوة عالية في Trust أو Compliance، يُمنع توسيع الأتمتة حتى الإغلاق.

4. **Critical Connector Break = Emergency Mode**
   أي كسر API في موصل حرج يفعّل خطة طوارئ 72 ساعة.

---

## 5) هيكل Execution Pack الأسبوعي (جاهز للإرسال للإدارة)

يُرسل الخميس ويحتوي:

1. Progress Snapshot لكل WS1..WS8.
2. Evidence Gates (Passed/Failed + Links).
3. SLA Breaches + RCA + Corrective Actions.
4. Risks Heatmap (Tech / Compliance / Delivery).
5. Next Week Commitments (Owner + Date + Evidence Gate).

---

## 6) الحد الأدنى للقياسات المطلوب أسبوعياً

| الفئة | المؤشر | الهدف |
|---|---|---|
| Progress | نسبة عناصر الخطة المنجزة فعلياً | ≥ 85% من التزامات الأسبوع |
| Evidence | نسبة البنود المغطاة بأدلة كاملة | 100% للبنود الحرجة |
| SLA | نسبة الالتزام بالمواعيد | ≥ 95% |
| Risk | عدد المخاطر High المفتوحة | اتجاه هابط أسبوعياً |
| Quality | نسبة إعادة فتح البنود المغلقة | ≤ 5% |

---

## 7) تعريف جاهزية الإغلاق (Ready-to-Close Gate)

لا يُعلن إغلاق البرنامج إلا عند تحقق:

- Zero high-risk open gaps في Trust/Compliance.
- جميع Workstreams في حالة Pilot أو Production حسب النطاق.
- جميع Exit Criteria في المصفوفة الأساسية موثقة بالأدلة.
- موافقة تنفيذية نهائية مع خطة الحفاظ على الضبط التشغيلي بعد الإغلاق.

---

## 8) ملف التتبع الرسمي

استخدم قالب CSV الرسمي:

- `frontend/public/strategy/execution_matrix_tracker_template.csv`

وتمت مزامنته مع نسخة docs الداخلية لضمان نفس الأعمدة ونفس منطق التتبع.

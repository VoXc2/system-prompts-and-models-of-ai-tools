# نظام التشغيل الأسبوعي — Completion Program (Dealix)

**الإصدار:** v1.0  
**الحالة:** Operating Playbook  
**المرجع الأساسي:** `docs/EXECUTION_MATRIX_COMPLETION_PROGRAM_AR.md`

---

## 1) الغرض

هذا المستند يحول الـ Execution Matrix إلى إيقاع تشغيلي أسبوعي ثابت:

- ماذا يُنفذ كل أسبوع؟
- من المالك التنفيذي؟
- ما بوابة الدليل المطلوبة؟
- كيف نغلق المخاطر وخرق SLA؟

---

## 2) الإيقاع التنفيذي (Weekly Cadence)

| اليوم | النشاط | المخرج |
|---|---|---|
| الأحد | Planning Sync (45 دقيقة) | التزامات الأسبوع + تحديث الأولويات |
| الثلاثاء | Mid-week Evidence Check (30 دقيقة) | حالة البوابات + إنذار مبكر للمخاطر |
| الخميس | Exit Review (60 دقيقة) | قرار: Pass / Conditional / Fail لكل Workstream |
| الخميس (بعد الاجتماع) | نشر Execution Pack | تقرير موحد للأدلة وSLA والمخاطر |

---

## 3) أدوار التشغيل (Execution Roles)

| الدور | المسؤولية |
|---|---|
| Program Director | قرار الأولويات + فك التعارض بين المسارات |
| Workstream Owner | تسليم المخرجات وإغلاق الـ Gates |
| Evidence Controller | التحقق من جودة الدليل قبل اعتماد الحالة |
| Risk & Compliance Officer | متابعة المخاطر والامتثال (PDPL/NCA) |
| Release Steward | ضبط بوابات SDLC/Promotion وموثوقية الإطلاق |

> قاعدة إلزامية: لا يعتمد أي إنجاز بدون توقيع `Workstream Owner` + `Evidence Controller`.

---

## 4) لوحة التنفيذ الأسبوعية (12 أسبوع)

| الأسبوع | Workstream Focus | Deliverable Gate | Exit Decision |
|---|---|---|---|
| W1 | WS1 | Architecture Register + Owner Mapping | Pass إذا اكتملت تغطية 100% للأنظمة |
| W2 | WS2 | Schema Contracts + No Free-text (Critical) | Pass إذا schema pass rate ≥95% |
| W3 | WS2 + WS8 | Decision Pack حي (Memo/Evidence/Risk/Approval) | Pass إذا التتبع end-to-end مكتمل |
| W4 | WS3 | Workflow Classification Ledger | Pass إذا كل workflow له تصنيف + مالك |
| W5 | WS3 | Durable Pilot + Recovery Proof | Pass إذا replay/restart مثبتين |
| W6 | WS4 | Policy/Authz/Verification Hooks | Pass إذا كل إجراء حساس يمر عبر hooks |
| W7 | WS5 | Connector Facade v1 (حرج) | Pass إذا contract tests مكتملة |
| W8 | WS5 | Quality + Semantic Metrics + Lineage | Pass إذا quality gates ≥98% |
| W9 | WS6 | Rulesets + Approvals + OIDC + Attestations | Pass إذا production gate محكوم بالكامل |
| W10 | WS7 | PDPL/NCA Mapping داخل Policy Engine | Pass إذا كل flow حساس له control mapping |
| W11 | WS8 | Executive Room Demo + KPI Sign-off | Pass إذا sign-off من الإدارة/الملاك |
| W12 | جميع المسارات | Program Exit Audit | Pass إذا لا توجد high-risk gaps مفتوحة |

---

## 5) سياسة قرار الحالة الأسبوعية

لكل Workstream:

- **Pass:** جميع بوابات الدليل مكتملة، ولا خرق SLA مؤثر.
- **Conditional:** مخرج مكتمل جزئيًا مع خطة إغلاق واضحة خلال 5 أيام عمل.
- **Fail:** غياب دليل جوهري، أو خرق SLA متكرر، أو خطر امتثال عالي.

### قواعد التصعيد

1. Fail مرتين متتاليتين = Escalation خلال 48 ساعة.
2. أي خطر High في Trust/Compliance = إيقاف أي توسيع استقلالية حتى الإغلاق.
3. خرق SLA في مسار حرج = خطة تصحيحية موثقة خلال 24 ساعة.

---

## 6) قالب Execution Pack (ينشر كل خميس)

### A) Progress Snapshot
- حالة كل Workstream: Current / Partial / Pilot / Production
- نسبة الإنجاز مقابل هدف الأسبوع

### B) Evidence Gates
- Passed Gates
- Failed Gates
- Missing Evidence

### C) SLA & Incidents
- SLA breaches
- Root cause
- Corrective action
- ETA الإغلاق

### D) Risk Heatmap
- Technical
- Compliance
- Delivery

### E) Next Week Commitments
- Top 3 commitments لكل Workstream
- Dependencies + blockers
- Owner + due date

---

## 7) تعريف الجاهزية التشغيلية النهائية

البرنامج يعتبر جاهزًا للانتقال المؤسسي فقط عند:

1. إغلاق جميع High-risk gaps.
2. نجاح W12 Exit Audit.
3. اعتماد Evidence Pack كامل للمسارات الثمانية.
4. توقيع Program Director + Compliance + Release Steward.

---

## 8) الربط التشغيلي

- المصفوفة الرئيسية: `docs/EXECUTION_MATRIX_COMPLETION_PROGRAM_AR.md`
- قالب التتبع التنفيذي: `docs/execution_matrix_tracker_template.csv`
- الفهرس الرئيسي: `memory/indexes/master-index.md`


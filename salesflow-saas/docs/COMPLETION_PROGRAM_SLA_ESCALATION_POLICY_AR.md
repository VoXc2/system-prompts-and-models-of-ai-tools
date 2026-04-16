# سياسة SLA والتصعيد — Completion Program (Dealix)

**الإصدار:** v1.0
**الحالة:** Operating Policy
**المرجع:** `docs/EXECUTION_MATRIX_COMPLETION_PROGRAM_AR.md`

---

## 1) الغرض

هذه السياسة توحّد:

- تعريفات SLA عبر المسارات الثمانية.
- قواعد حساب الخرق (Breach) والإنذار المبكر.
- مسارات التصعيد الزمنية.
- قواعد إيقاف/استمرار التوسع في الأتمتة.

---

## 2) تعريفات SLA القياسية

| النوع | التعريف | مثال |
|---|---|---|
| Time-to-Detect (TTD) | الزمن من وقوع المشكلة حتى رصدها | اكتشاف فشل Evidence Gate |
| Time-to-Respond (TTR) | الزمن من الرصد حتى بدء المعالجة | فتح incident + تعيين owner |
| Time-to-Resolve (TTRx) | الزمن حتى الإغلاق الكامل | إغلاق gap مع دليل تصحيحي |
| Time-to-Verify (TTV) | الزمن حتى تحقق Evidence Controller | اعتماد الحل بعد اختبار |

---

## 3) أولويات الحوادث (P1/P2/P3)

| المستوى | الوصف | أمثلة | أهداف SLA |
|---|---|---|---|
| P1 | تأثير حرج على Trust/Compliance/Production Gate | bypass policy، فقدان auditability، نشر بلا approvals | TTD <= 15m, TTR <= 30m, TTRx <= 4h |
| P2 | تأثير متوسط على مسار حرج دون فقدان كامل للحوكمة | schema failure متكرر، data quality gate failure | TTD <= 1h, TTR <= 4h, TTRx <= 24h |
| P3 | تأثير منخفض أو تحسينات غير حرجة | تأخير dashboard غير حرج، وثائق ناقصة | TTD <= 1d, TTR <= 2d, TTRx <= 5d |

---

## 4) قواعد خرق SLA

يعد الخرق واقعاً عند تحقق واحد مما يلي:

1. تجاوز أي مؤشر زمن من مؤشرات SLA المحددة للمستوى.
2. فشل نفس Evidence Gate مرتين متتاليتين دون خطة تصحيحية معتمدة.
3. تجاوز ETA التصحيح المعتمد بدون تحديث حالة رسمي.

---

## 5) مسار التصعيد الزمني

| الزمن من الرصد | الإجراء | المالك |
|---|---|---|
| +0 إلى +30 دقيقة | تسجيل incident + تعيين severity + owner | Workstream Owner |
| +30 إلى +60 دقيقة | إشعار Program Director + Evidence Controller | Program Ops |
| +1 إلى +4 ساعات | تنفيذ corrective action الأولي + تحديث حالة | Owner + Release Steward |
| +4 ساعات (P1) / +24 ساعة (P2) | Executive Escalation إذا لم يغلق | Program Director |
| +48 ساعة | خطة إعادة هندسة إجبارية للمسار | Architecture + Security + Product |

---

## 6) قواعد No New Autonomy

يُفعّل "No New Autonomy" مباشرة إذا:

- يوجد P1 مفتوح في WS4/WS7.
- يوجد خرق متكرر (مرتين) في بوابات Trust أو Compliance.
- لا يوجد evidence مكتمل لإجراء حساس تم إطلاقه.

يُرفع المنع فقط بعد:

1. إغلاق السبب الجذري.
2. اعتماد Evidence Gate التعويضي.
3. موافقة Program Director + Compliance Officer.

---

## 7) التقارير المطلوبة

### تقرير يومي مختصر (Incidents Digest)

- الحوادث المفتوحة حسب P-level
- SLA at-risk خلال 24 ساعة
- blockers الحرجة

### تقرير أسبوعي (SLA Performance)

- SLA attainment by workstream
- breach trends
- top root causes
- preventive actions for next week

---

## 8) الربط التشغيلي

- المصفوفة: `docs/EXECUTION_MATRIX_COMPLETION_PROGRAM_AR.md`
- التشغيل الأسبوعي: `docs/EXECUTION_MATRIX_WEEKLY_OPERATING_SYSTEM_AR.md`
- سجل المخاطر: `docs/COMPLETION_PROGRAM_RISK_REGISTER_AR.md`
- بوابات الأدلة: `docs/COMPLETION_PROGRAM_EVIDENCE_GATE_CATALOG_AR.md`

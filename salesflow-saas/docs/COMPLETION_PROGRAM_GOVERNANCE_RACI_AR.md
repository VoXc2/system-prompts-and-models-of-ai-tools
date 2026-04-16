# حوكمة برنامج الإغلاق (Completion Program) — Governance & RACI

**الإصدار:** v1.0
**الحالة:** Operating Governance Baseline
**المرجع:** `docs/EXECUTION_MATRIX_COMPLETION_PROGRAM_AR.md`

---

## 1) الغرض

تحديد بنية الحوكمة الرسمية للبرنامج، ومن يقرر ماذا، ومن يوافق، ومن يُنفذ، ومن يُبلّغ.

---

## 2) الهيكل الحوكمي

| المستوى | الاسم | الدور |
|---|---|---|
| L1 | Executive Steering Committee | توجيه استراتيجي، اعتماد قرارات التحول الكبرى، قبول Exit النهائي |
| L2 | Program Control Board | إدارة البرنامج أسبوعيًا، اعتماد Pass/Conditional/Fail لكل Workstream |
| L3 | Workstream Delivery Cell | تنفيذ المخرجات، تجميع الأدلة، إدارة المخاطر اليومية |
| L4 | Assurance & Audit Cell | مراجعة الأدلة، تدقيق الالتزام، فرض No Fake Implementation Claims |

---

## 3) تعريف الأدوار القياسية

| Role Code | الدور | الوصف |
|---|---|---|
| ESC | Executive Sponsor Council | المالك التنفيذي النهائي للبرنامج |
| PD | Program Director | مسؤول التشغيل الكلي واتخاذ قرارات المفاضلة |
| WSO | Workstream Owner | مالك التسليم في كل مسار |
| EC | Evidence Controller | مالك جودة الأدلة وقابلية التدقيق |
| RCO | Risk & Compliance Officer | مالك المخاطر والامتثال (PDPL/NCA/AI controls) |
| RS | Release Steward | مالك بوابات الإطلاق والحماية وprovenance |
| EA | Enterprise Architect | مالك الاتساق المعماري والـ current-vs-target |
| DA | Data Assurance Lead | مالك جودة البيانات وخطوط النسب lineage |
| IAM | Identity & Access Lead | مالك authN/authZ والهوية والتفويض |

---

## 4) RACI على قرارات البرنامج الأساسية

| القرار | R | A | C | I |
|---|---|---|---|---|
| اعتماد Baseline للمصفوفة | PD, EA | ESC | WSO, EC, RCO | جميع الفرق |
| قرار Pass/Conditional/Fail أسبوعي | WSO, EC | PD | RCO, RS | ESC |
| تفعيل No New Autonomy Rule | RCO | PD | ESC, WSO | جميع الفرق |
| اعتماد تعميم Production لمسار جديد | RS, WSO | PD | RCO, EC, EA | ESC |
| إغلاق High-risk gap | WSO | PD | RCO, EC | ESC |
| قبول Exit النهائي (W12) | PD, RCO, RS | ESC | EA, WSO, EC | جميع الفرق |

---

## 5) RACI حسب Workstream

| Workstream | R | A | C | I |
|---|---|---|---|---|
| WS1 Productization & Architecture Closure | EA | PD | WSO, EC | ESC |
| WS2 Decision Plane Hardening | WSO (AI Platform) | PD | EC, RCO | ESC |
| WS3 Execution Plane Hardening | WSO (Workflow Eng.) | PD | RS, EA | ESC |
| WS4 Trust Fabric Hardening | WSO (Security Arch.) | PD | IAM, RCO, EC | ESC |
| WS5 Data & Connector Fabric | WSO (Data/Integrations) | PD | DA, EC | ESC |
| WS6 Enterprise Delivery Fabric | RS | PD | RCO, EA | ESC |
| WS7 Saudi Enterprise Readiness | RCO | PD | WSO, EC | ESC |
| WS8 Executive & Customer Readiness | WSO (Product/RevOps) | PD | EC, DA | ESC |

---

## 6) صلاحيات القرار (Decision Rights)

- `PD` يملك صلاحية حسم تضارب الأولويات بين المسارات.
- `EC` يملك حق رفض أي Claim غير مدعوم بدليل.
- `RCO` يملك صلاحية التصعيد الإلزامي لأي خطر امتثال عالي.
- `RS` يملك صلاحية إيقاف الإطلاق في حالة فقدان Gate أمني/حوكمي.
- `ESC` يملك قرار Go/No-Go النهائي للانتقال المؤسسي.

---

## 7) قواعد الاجتماع الرسمي

1. لا يوجد قرار اعتماد بدون توثيق في Execution Pack.
2. لا يوجد تغيير حالة إلى Pilot/Production بدون Gate Evidence مكتمل.
3. أي استثناء يجب أن يحمل Expiry date + Owner + تعليل مكتوب.
4. أي استثناء غير مغلق في الموعد ينتقل تلقائيًا إلى Escalation Board.

---

## 8) مخرجات إلزامية لكل اجتماع خميس

- قرار الحالة لكل Workstream: Pass/Conditional/Fail.
- قائمة gaps المفتوحة مرتبة حسب الخطورة.
- سجل SLA breaches والإجراءات التصحيحية.
- قائمة القرارات التنفيذية للأسبوع التالي (Owner + due date).


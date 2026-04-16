# Governance & RACI — Completion Program (Dealix)

**الإصدار:** v1.0
**الحالة:** Operating Governance Baseline
**المرجع:** `frontend/public/strategy/EXECUTION_MATRIX_COMPLETION_PROGRAM_AR.md`

---

## 1) الهدف

تثبيت مسؤوليات برنامج الإغلاق بصورة تشغيلية قابلة للمحاسبة:

- من يملك القرار؟
- من ينفذ؟
- من يراجع الدليل؟
- من يعتمد الانتقال بين الحالات؟

---

## 2) الأدوار القيادية

| الدور | الوصف | الصلاحية |
|---|---|---|
| Program Director | قائد البرنامج الشامل | اعتماد الأولويات، اعتماد قرارات Pass/Fail |
| Chief Architect | مرجعية الإغلاق المعماري | اعتماد WS1 + تضارب تصميم المسارات |
| AI Platform Lead | قائد Decision Plane | اعتماد WS2 المعياري |
| Workflow Engineering Lead | قائد Execution Plane | اعتماد WS3 وdurability policies |
| Security Architecture Lead | قائد Trust Plane | اعتماد WS4 policies/authz/verification |
| Data Platform Lead | قائد Data & Connectors | اعتماد WS5 contract/data quality |
| DevSecOps Lead | قائد Delivery Fabric | اعتماد WS6 gates/attestations |
| Compliance Lead (KSA) | قائد الامتثال المحلي | اعتماد WS7 PDPL/NCA controls |
| Product Director + RevOps | قيادة القيمة التنفيذية | اعتماد WS8 executive/customer readiness |
| Evidence Controller | حارس جودة الأدلة | قبول/رفض Gate evidence قبل الاعتماد |
| Release Steward | حارس الترقية والإطلاق | قرار promotion/rollback |

---

## 3) RACI Matrix (حسب المسارات)

| Workstream | R (Responsible) | A (Accountable) | C (Consulted) | I (Informed) |
|---|---|---|---|---|
| WS1 Productization & Architecture Closure | Chief Architect + Platform PMO | Program Director | Security, Data, Delivery leads | Executive sponsors |
| WS2 Decision Plane Hardening | AI Platform Lead + Applied AI Team | Program Director | Evidence Controller, Product Director | WS3/WS4 owners |
| WS3 Execution Plane Hardening | Workflow Engineering Lead + Backend Core | Program Director | DevSecOps, Integrations | WS2/WS5 owners |
| WS4 Trust Fabric Hardening | Security Architecture Lead + IAM | Program Director | Compliance Lead, DevSecOps | Product leadership |
| WS5 Data & Connector Fabric | Data Platform Lead + Integrations Lead | Program Director | Security, AI Platform | GTM/ops stakeholders |
| WS6 Enterprise Delivery Fabric | DevSecOps Lead + Release Manager | Program Director | Security + Compliance | All workstream owners |
| WS7 Saudi Enterprise Readiness | Compliance Lead (KSA) + Security Governance | Program Director | Legal/DPO, Security Architecture | Executive leadership |
| WS8 Executive & Customer Readiness | Product Director + RevOps + BI Lead | Program Director | AI/Data/Security leads | Board/executive room |

---

## 4) قرار الحالة (State Authority)

| القرار | صاحب القرار النهائي | شرط الاعتماد |
|---|---|---|
| Current → Partial | Workstream Owner | وجود تنفيذ جزئي مثبت + Known Gaps |
| Partial → Pilot | Program Director | Evidence Gate pass + Runbook |
| Pilot → Production | Program Director + Release Steward + Evidence Controller | Evidence Pack كامل + SLA readiness + compliance sign-off |

---

## 5) ضوابط إلزامية

1. لا تغيير حالة لأي Workstream دون Evidence Gate موثق.
2. لا اعتماد Production دون توقيع ثلاثي: Program Director + Evidence Controller + Release Steward.
3. أي High-risk في WS4/WS7 يجمّد أي توسيع استقلالية حتى الإغلاق.

---

## 6) إيقاع الحوكمة

- اجتماع الحوكمة الأسبوعي: الخميس.
- اجتماع المخاطر العاجل: خلال 48 ساعة عند Fail متكرر.
- مراجعة شهرية شاملة: مواءمة تقدم البرنامج مع Definition of Done.


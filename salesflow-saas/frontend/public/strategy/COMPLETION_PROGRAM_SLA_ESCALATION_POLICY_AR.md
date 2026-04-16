# سياسة SLA والتصعيد — Completion Program (Dealix)

**الإصدار:** v1.0
**الحالة:** Operating Policy
**المرجع:** `docs/COMPLETION_PROGRAM_SLA_ESCALATION_POLICY_AR.md`

---

## 1) الغرض

تحديد معايير SLA الرسمية والتصعيد المرتبط بها لضمان انضباط التنفيذ عبر المسارات الثمانية.

---

## 2) مبادئ SLA

1. **SLA مرتبط بمخرج قابل للقياس** وليس بنشاط عام.
2. **SLA breach يحتاج Root Cause موثق** خلال 24 ساعة.
3. **التصعيد يعتمد على الأثر** (Trust/Compliance أولاً).
4. **لا إغلاق شكلي**: لا يعتبر breach مغلقاً بدون Evidence Gate Pass.

---

## 3) مصفوفة SLA الرسمية

| Area | SLA | Metric | Owner |
|---|---|---|---|
| WS1 Classification Gaps | إغلاق خلال 5 أيام عمل | Gap Age | Architecture PMO |
| WS2 Schema Breaking | إصلاح خلال 24 ساعة | Time-to-Fix | AI Platform Lead |
| WS3 Critical Workflow Recovery | تعافٍ خلال 15 دقيقة | MTTR-Workflow | Workflow Eng Lead |
| WS4 Policy Enforcement | تغطية 100% للمسارات الحساسة | Enforcement Coverage | Security Architecture |
| WS4 Secret Rotation | تدوير كل 30 يوم كحد أقصى | Secret Age | IAM/Security Ops |
| WS5 Connector API Drift | تحديث خلال 72 ساعة | Drift Resolution Time | Integrations Lead |
| WS5 Data Quality | ≥98% في datasets الحرجة | Quality Pass Rate | Data Platform Lead |
| WS6 Rollback Initiation | بدء rollback خلال ≤10 دقائق | Rollback Start Time | Release Manager |
| WS7 High-Risk Compliance Gaps | إغلاق خلال 10 أيام عمل | Gap Closure Time | Compliance Lead (KSA) |
| WS8 Executive Dashboard Freshness | تحديث خلال ≤15 دقيقة | Data Freshness | BI Lead |

---

## 4) مستويات التصعيد

| المستوى | متى يطبق | الجهة المعنية | الإطار الزمني |
|---|---|---|---|
| L1 | أول خرق SLA غير حرج | Workstream Owner | Plan خلال 24 ساعة |
| L2 | تكرار خرق لنفس السبب أو أثر متوسط | Program Director + Owner | Review خلال 48 ساعة |
| L3 | Trust/Compliance High Risk أو خرق حرج متكرر | Executive Steering + Security/Compliance | Emergency Review خلال 24 ساعة |

---

## 5) قواعد التصعيد الإلزامية

1. **No New Autonomy Rule:** عند High Risk في Trust/Compliance.
2. **Release Hold Rule:** عند خرق WS6 governance controls.
3. **Connector Emergency Patch Rule:** لأي break حرج في الموصلات (<=72 ساعة).
4. **Evidence-First Closure Rule:** لا يتم إغلاق breach بدون Evidence Gate Pass.

---

## 6) نموذج Incident / SLA Breach Record

- `breach_id`
- `workstream`
- `sla_name`
- `detected_at`
- `owner`
- `severity`
- `impact_scope`
- `root_cause`
- `corrective_action`
- `preventive_action`
- `target_close_at`
- `actual_close_at`
- `evidence_link`
- `status` (Open / Mitigated / Closed)

---

## 7) الربط التشغيلي

- المصفوفة: `frontend/public/strategy/EXECUTION_MATRIX_COMPLETION_PROGRAM_AR.md`
- المخاطر: `frontend/public/strategy/COMPLETION_PROGRAM_RISK_REGISTER_AR.md`
- الأدلة: `frontend/public/strategy/COMPLETION_PROGRAM_EVIDENCE_GATE_CATALOG_AR.md`

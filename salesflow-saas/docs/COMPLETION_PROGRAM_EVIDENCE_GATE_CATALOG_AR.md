# كتالوج بوابات الدليل — Completion Program (Dealix)

**الإصدار:** v1.0
**الحالة:** Operable Control Catalog
**المرجع:** `docs/EXECUTION_MATRIX_COMPLETION_PROGRAM_AR.md`

---

## 1) الغرض

توحيد تعريف **Evidence Gates** لكل Workstream بحيث لا يعتمد أي إنجاز إلا بدليل:

- قابل للتحقق
- قابل للتكرار
- مرتبط بمالك مسؤول
- مرتبط بمعيار خروج واضح

---

## 2) مقياس جودة الدليل (Evidence Quality Score)

لكل دليل Score من 0 إلى 100:

- **Completeness (30%)**: هل يغطي المتطلبات كاملة؟
- **Verifiability (30%)**: هل يمكن إعادة التحقق منه مستقلًا؟
- **Traceability (20%)**: هل مرتبط بـ Workstream + Sprint + Owner؟
- **Freshness (20%)**: هل الدليل ضمن نافذة الصلاحية؟

### عتبات القبول

- **Pass:** >= 85
- **Conditional:** 70-84 (يتطلب خطة إغلاق خلال 5 أيام عمل)
- **Fail:** < 70

---

## 3) Evidence Gate Catalog by Workstream

| Workstream | Gate ID | Required Evidence | Validation Method | Frequency | Owner | Pass Criteria |
|---|---|---|---|---|---|---|
| WS1 | EG-WS1-ARCH-01 | Current-vs-Target Architecture Register | Review + linkage check to subsystem list | Weekly | Chief Architect | 100% subsystem coverage with status and owner |
| WS1 | EG-WS1-LOCK-02 | Program Locks confirmation (Planes/Tracks/Roles/Metadata) | Governance checklist signed | Weekly | Program Director | No lock violations |
| WS2 | EG-WS2-SCHEMA-01 | Schema contract tests (`memo/risk/evidence/approval/execution_intent`) | CI test results + audit sample | Weekly | AI Platform Lead | >=95% schema pass rate |
| WS2 | EG-WS2-FREETEXT-02 | Critical-flow free-text rejection proof | Negative tests + policy report | Weekly | Applied AI Lead | 0 critical free-text outputs |
| WS3 | EG-WS3-WFINV-01 | Workflow inventory + classification ledger | Ledger review with owner mapping | Weekly | Workflow Eng Lead | 100% classified workflows |
| WS3 | EG-WS3-DURABLE-02 | Durable workflow recovery evidence | Replay/restart simulation logs | Per release | Backend Core Lead | Deterministic recovery proven |
| WS4 | EG-WS4-POLICY-01 | OPA/OpenFGA policy + authz decision logs | Policy test harness + audit sample | Weekly | Security Architect | 100% sensitive paths enforced |
| WS4 | EG-WS4-VERIFY-02 | Tool verification ledger + contradiction dashboard snapshot | Contradiction report review | Weekly | Trust Control Owner | Unresolved critical contradictions = 0 |
| WS5 | EG-WS5-CONN-01 | Connector facade contract report | Integration contract tests | Weekly | Integrations Lead | 100% critical connectors under facade |
| WS5 | EG-WS5-DQ-02 | Data quality and lineage scorecards | Quality checks + lineage snapshot | Weekly | Data Platform Lead | Quality >=98% critical datasets |
| WS6 | EG-WS6-REL-01 | Rulesets/protected branches/required checks proof | Repo governance checks | Weekly | DevSecOps Lead | No bypass on release path |
| WS6 | EG-WS6-PROV-02 | OIDC + artifact attestations proof | Deployment provenance verification | Per release | Release Steward | 100% production provenance |
| WS7 | EG-WS7-PDPL-01 | PDPL control matrix coverage | Compliance audit mapping | Weekly | Compliance Lead (KSA) | 100% Saudi-sensitive flow mapping |
| WS7 | EG-WS7-NCA-02 | NCA ECC readiness gaps closure progress | Gap tracker review | Weekly | Security Governance | High-risk gaps within SLA |
| WS8 | EG-WS8-EXEC-01 | Executive room operational demo | Demo run + sign-off record | Weekly | Product Director | Decision/risk/forecast views operational |
| WS8 | EG-WS8-KPI-02 | KPI freshness + adoption indicators | Metrics dashboard validation | Weekly | BI Lead | Refresh and adoption targets met |

---

## 4) قواعد صلاحية الأدلة (Evidence Freshness)

| نوع الدليل | مدة الصلاحية |
|---|---|
| Contract test report | 7 أيام |
| Security/compliance control report | 14 يوم |
| Release provenance attestation | مرتبط بكل release (إلزامي) |
| Executive sign-off | 7 أيام أو حتى اجتماع الخروج التالي |

---

## 5) شروط الرفض التلقائي (Auto-Reject Conditions)

يرفض الدليل تلقائيًا إذا:

1. غير مرتبط بـ Gate ID واضح.
2. لا يحتوي timestamp أو owner أو execution context.
3. يستخدم لقياس عمل مختلف عن العمل المستهدف.
4. أقدم من نافذة الصلاحية المعتمدة.

---

## 6) الربط التشغيلي

- Execution Matrix: `docs/EXECUTION_MATRIX_COMPLETION_PROGRAM_AR.md`
- Weekly Operating System: `docs/EXECUTION_MATRIX_WEEKLY_OPERATING_SYSTEM_AR.md`
- Risk Register: `docs/COMPLETION_PROGRAM_RISK_REGISTER_AR.md`


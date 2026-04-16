# Completion Program — سجل المخاطر التنفيذي (Risk Register)

**الإصدار:** v1.0
**النطاق:** WS1..WS8
**المرجع:** `docs/EXECUTION_MATRIX_COMPLETION_PROGRAM_AR.md`

---

## 1) نموذج السجل

| Risk ID | Workstream | Risk Description | Category | Probability | Impact | Risk Score | Early Signals | Mitigation Plan | Contingency Plan | Owner | Target Date | Status |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| R-001 | WS2 | مخرجات غير مهيكلة في تدفق حرج | Technical / Trust | Medium | High | 12 | فشل متكرر في contract tests | تفعيل schema enforcement + blocks في CI | Freeze مؤقت للتدفق + rollback آخر إصدار مستقر | AI Platform Lead | 2026-05-08 | Open |
| R-002 | WS3 | تكرار تنفيذ workflow بسبب idempotency gap | Technical / Reliability | Medium | High | 12 | تكرار side-effects على نفس المفتاح | فرض idempotency keys + dedup checks | compensation runbook + manual reconciliation | Workflow Engineering Lead | 2026-05-15 | Open |
| R-003 | WS4 | bypass policy خارج OPA/OpenFGA hooks | Security / Governance | Low | Critical | 15 | endpoint حساس بدون policy decision log | policy-as-code coverage gate + forbidden direct path lint | وقف الإطلاق + hotfix enforcement layer | Security Architecture Lead | 2026-05-12 | Open |
| R-004 | WS5 | كسر API مفاجئ لدى مزود خارجي حرج | Integration / Delivery | Medium | Medium | 9 | ارتفاع 4xx/5xx + contract drift alerts | facade version pin + compatibility adapter | emergency patch خلال 72 ساعة + degraded mode | Integrations Lead | 2026-05-20 | Open |
| R-005 | WS6 | نشر دون attestation/provenance valid | Delivery / Compliance | Low | High | 10 | missing attestation in release evidence | enforce required checks + release block rules | rollback فوري + incident review | DevSecOps Lead | 2026-05-10 | Open |
| R-006 | WS7 | فجوة ربط PDPL/NCA في flow حساس | Compliance | Medium | Critical | 15 | control mapping incomplete في audit | control mapping gate إجباري قبل production | feature freeze + compliance remediation sprint | Compliance Lead (KSA) | 2026-05-18 | Open |
| R-007 | WS8 | لوحات تنفيذية بلا دقة/تأخير غير مقبول | Product / Data | Medium | Medium | 9 | mismatch بين dashboard وsource metrics | semantic metric contracts + freshness monitors | read-only notice + fallback executive report | BI Lead | 2026-05-22 | Open |

---

## 2) مصفوفة التقييم (Probability × Impact)

- **Probability:** Low=1, Medium=2, High=3
- **Impact:** Medium=3, High=4, Critical=5
- **Risk Score = Probability × Impact**

### قواعد القرار

- **High Priority:** score >= 12
- **Medium Priority:** score 8..11
- **Low Priority:** score <= 7

---

## 3) قواعد التتبع الأسبوعي

1. كل Risk High Priority يجب أن يظهر في Execution Pack الأسبوعي.
2. أي Risk بدرجة 15 يتطلب Escalation خلال 24 ساعة.
3. لا يسمح بإغلاق Risk دون Evidence واضح على معالجة السبب الجذري.
4. عند تغيير الحالة إلى Closed، يجب تسجيل lesson learned.

---

## 4) مؤشرات الأداء لمراقبة المخاطر

- عدد المخاطر المفتوحة حسب Workstream.
- زمن الإغلاق المتوسط لكل فئة خطورة.
- نسبة المخاطر المتكررة (recurring risks).
- نسبة المخاطر ذات خطط mitigation غير مكتملة.
- نسبة المخاطر التي أثرت فعلياً على SLA.

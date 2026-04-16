# دليل بوابات الدليل — Completion Program (Dealix)

**الإصدار:** v1.0  
**المرجع:** `docs/EXECUTION_MATRIX_COMPLETION_PROGRAM_AR.md`

---

## 1) الهدف

توحيد تعريف Evidence Gates لكل Workstream بحيث تصبح قرارات `Pass/Conditional/Fail` موضوعية وقابلة للتدقيق.

---

## 2) معايير قبول الدليل (Evidence Quality Standard)

أي دليل يُقبل فقط إذا حقق:

1. **صحة المصدر:** صادر من نظام موثوق (CI/CD, logs, policy engine, dashboards).
2. **الحداثة:** ضمن نافذة زمنية الأسبوع الجاري.
3. **قابلية التتبع:** يحتوي `trace_id` أو مرجع إصدار/تنفيذ واضح.
4. **الاكتمال:** يغطي deliverable كاملًا لا جزءًا معزولًا.
5. **قابلية المراجعة:** يمكن لطرف ثانٍ إعادة التحقق منه.

---

## 3) Evidence Gates حسب المسارات الثمانية

| Workstream | Gate ID | Required Evidence | Validation Method | Failure Pattern |
|---|---|---|---|---|
| WS1 | EG-WS1-ARCH-01 | `architecture_register` مكتمل + owners + statuses | Architecture review + sampling | status غير موحد أو owner مفقود |
| WS2 | EG-WS2-SCHEMA-01 | نتائج schema contract tests + منع free-text | CI checks + sample audits | schema drift / bypass للـ structured output |
| WS3 | EG-WS3-DURABLE-01 | replay/restart/recovery logs + compensation test | chaos/failure test runbook | تنفيذ غير deterministic أو تعويض ناقص |
| WS4 | EG-WS4-TRUST-01 | policy decisions + authz checks + verification ledger | security controls review | bypass policy أو contradiction غير معالج |
| WS5 | EG-WS5-CONN-01 | connector contract tests + idempotency/retry evidence | integration test + API drift check | vendor drift بلا facade update |
| WS6 | EG-WS6-REL-01 | rulesets/approvals/OIDC/attestation evidence | release governance audit | نشر خارج gates الرسمية |
| WS7 | EG-WS7-KSA-01 | PDPL/NCA mapping + control evidence | compliance review | control gap بلا mitigation |
| WS8 | EG-WS8-EXEC-01 | executive demo + KPI sign-off + adoption snapshot | stakeholder acceptance gate | dashboards بلا أثر تشغيلي موثق |

---

## 4) قرار البوابة (Gate Decision Rules)

- **Pass:** جميع عناصر الدليل المطلوبة متوفرة ومطابقة.
- **Conditional:** دليل جزئي مع خطة إغلاق موثقة ≤ 5 أيام عمل.
- **Fail:** غياب دليل جوهري أو فشل متكرر أو خطر امتثال عالي.

---

## 5) متطلبات الأرشفة

- يحتفظ بكل دليل لمدة دورة البرنامج + فترة تدقيق لاحقة.
- يربط كل Evidence Gate بـ:
  - Workstream
  - Week
  - Owner
  - Exit decision
  - corrective action (إن وجد)


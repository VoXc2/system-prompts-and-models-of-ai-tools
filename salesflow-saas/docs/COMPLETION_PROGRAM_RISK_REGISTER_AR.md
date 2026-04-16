#!/usr/bin/env markdown
# سجل المخاطر — Completion Program (Dealix Enterprise Readiness)

**الإصدار:** v1.0  
**الحالة:** Active Program Risk Register  
**المرجع:** `docs/EXECUTION_MATRIX_COMPLETION_PROGRAM_AR.md`

---

## 1) منهجية التصنيف

- **احتمال (P):** 1 منخفض جدًا، 5 مرتفع جدًا.
- **أثر (I):** 1 تأثير محدود، 5 تأثير استراتيجي/امتثال/إطلاق.
- **درجة الخطر (R):** `P × I`.
- **الحرجية:**
  - Low: 1–6
  - Medium: 7–12
  - High: 13–19
  - Critical: 20–25

---

## 2) Risk Register (المحدث التشغيلي)

| Risk ID | Workstream | وصف الخطر | P | I | R | المستوى | مؤشرات مبكرة | Mitigation | Contingency | Owner | Target Date | Status |
|---|---|---|---:|---:|---:|---|---|---|---|---|---|---|
| R-001 | WS1 | تضارب تعريف Current/Partial/Pilot/Production بين الفرق | 4 | 4 | 16 | High | اختلافات في التقارير الأسبوعية | قاموس حالة موحد + review gate | Escalation Workshop خلال 48 ساعة | Program Director | W1 | Open |
| R-002 | WS2 | فشل schema adherence في مخرجات حرجة | 3 | 5 | 15 | High | ارتفاع schema test failures | contract tests + versioned schemas | rollback إلى schema version مستقر | AI Platform Lead | W2 | Open |
| R-003 | WS3 | ازدواجية تنفيذ في durable workflow | 3 | 5 | 15 | High | duplicate side effects / retries غير منضبطة | idempotency keys + compensation tests | manual reconciliation runbook | Workflow Engineering Lead | W5 | Open |
| R-004 | WS4 | bypass لمسار policy/authz في endpoint حساس | 2 | 5 | 10 | Medium | missing policy decision logs | central policy middleware | kill switch للاستقلالية الحساسة | Security Architecture Lead | W6 | Open |
| R-005 | WS5 | تعطل facade بسبب API drift من مزود خارجي | 4 | 4 | 16 | High | spike في integration failures | versioned connector wrappers | emergency patch protocol (72h) | Integrations Lead | W7 | Open |
| R-006 | WS6 | ضعف تغطية rulesets/approvals على release path | 3 | 5 | 15 | High | نشر خارج البوابات الرسمية | mandatory protected branches + checks | freeze releases حتى إغلاق الثغرة | DevSecOps Lead | W9 | Open |
| R-007 | WS7 | فجوة mapping بين workflow حساس وضوابط PDPL/NCA | 2 | 5 | 10 | Medium | control evidence gaps | control matrix review شهري | compliance exception with expiry | Compliance Lead (KSA) | W10 | Open |
| R-008 | WS8 | لوحة تنفيذية بدون موثوقية بيانات تشغيلية | 3 | 4 | 12 | Medium | تناقض KPI بين اللوحات والمصدر | semantic metrics dictionary | disclaimer + restricted release | BI Lead | W11 | Open |
| R-009 | Cross | تأخر اعتماد الملاك (owners) في مخرجات حرجة | 3 | 4 | 12 | Medium | recurring pending sign-offs | sign-off SLA + delegated approvers | auto escalation إلى Program Director | PMO Lead | Weekly | Open |
| R-010 | Cross | نقص جودة الأدلة Evidence Packs | 3 | 4 | 12 | Medium | frequent “insufficient evidence” flags | evidence quality checklist + reviewer | hold status upgrade حتى الاستيفاء | Evidence Controller | Weekly | Open |

---

## 3) سياسة المراجعة

- تحديث السجل في **Mid-week Evidence Check** و**Exit Review**.
- أي خطر يصل إلى **Critical** يتم تصعيده خلال 24 ساعة.
- أي خطر **High** مفتوح لأكثر من أسبوعين ينتقل تلقائياً إلى برنامج تصحيح إلزامي.

---

## 4) ربط تشغيلي

- المصفوفة الرئيسية: `docs/EXECUTION_MATRIX_COMPLETION_PROGRAM_AR.md`
- كتالوج البوابات: `docs/COMPLETION_PROGRAM_EVIDENCE_GATE_CATALOG_AR.md`
- سياسة SLA: `docs/COMPLETION_PROGRAM_SLA_ESCALATION_POLICY_AR.md`


# Dealix Gap Analysis — تحليل الفجوات الثمانية

**الإصدار:** 1.0  
**التاريخ:** 2026-04-16  
**المرجع:** [`COMPLETION_PROGRAM.md`](./COMPLETION_PROGRAM.md)

---

## كيفية القراءة

كل فجوة توثّق: الوضع الحالي، الوضع المستهدف، السبب الجذري، خطة الإغلاق، ومعيار الإغلاق.

**مقياس الخطورة:**
- 🔴 **Critical** — يمنع الجاهزية المؤسسية
- 🟠 **High** — يُضعف الثقة والموثوقية
- 🟡 **Medium** — يُقلل الكفاءة التشغيلية

---

## GAP-1: الوثائق أقوى من التنفيذ 🔴 Critical

### الوضع الحالي

Dealix يمتلك blueprint معماري ممتاز:
- `MASTER-BLUEPRINT.mdc` — مصدر حقيقة معماري
- `ULTIMATE_EXECUTION_MASTER_AR.md` — وثيقة تنفيذ استراتيجية
- Module Map يدّعي ~90% اكتمال
- 19 وكيل مسجّل في `AGENT-MAP.md`

**لكن لا يوجد:**
- Code-level implementation map يربط الوثائق بالكود الفعلي
- Status dashboard يوضح: Current / Pilot / Production لكل مكون
- Acceptance gates لكل subsystem

### السبب الجذري

التركيز على بناء الطبقة المرجعية (وهو صحيح) لكن بدون آلية لتتبع الفجوة بين الوثيقة والتنفيذ.

### خطة الإغلاق

| الخطوة | المخرج | المسار |
|--------|--------|--------|
| بناء Current-vs-Target Register | [`CURRENT_VS_TARGET_ARCHITECTURE.md`](./CURRENT_VS_TARGET_ARCHITECTURE.md) | WS-1.1 |
| تعريف acceptance gates لكل subsystem | Exit criteria في المصفوفة التنفيذية | WS-1.2–1.5 |
| مراجعة دورية (كل sprint) | تحديث السجل بعد كل sprint | مستمر |

### معيار الإغلاق

- [ ] كل subsystem له حالة نضج موثّقة ومحدّثة
- [ ] لا يوجد subsystem بحالة "Unknown"
- [ ] الفجوة بين الوثيقة والكود مقاسة ومتتبَّعة

---

## GAP-2: Decision Plane نظري أكثر من كونه Typed Execution-Ready 🔴 Critical

### الوضع الحالي

- الوكلاء يعيدون نصوصاً حرة أو JSON غير مُلزم
- لا يوجد schema enforcement على المخرجات
- لا يوجد evidence packs أو decision memos
- `model_router.py` يوجّه الطلبات لكن لا يفرض هيكل المخرجات

### الوضع المستهدف

كل قرار agentic يخرج بهذه البنية فقط:
1. `memo_json` — ملخص القرار
2. `evidence_pack_json` — حزمة الأدلة
3. `risk_register_json` — سجل المخاطر
4. `approval_packet_json` — حزمة الموافقة
5. `execution_intent_json` — نية التنفيذ

### السبب الجذري

الوكلاء بُنيوا للعمل بسرعة (Celery tasks + LLM calls) بدون طبقة type-safety على المخرجات.

### خطة الإغلاق

| الخطوة | التقنية | المسار |
|--------|---------|--------|
| تعريف JSON Schemas | OpenAI Structured Outputs | WS-2.1 |
| إنفاذ الهيكل | Schema validation middleware | WS-2.2 |
| بناء Evidence Pack Generator | Python service + Pydantic models | WS-2.3 |
| بناء Decision Memo Compiler | Bilingual template engine | WS-2.4 |
| إضافة Provenance/Freshness/Confidence | Score calculation service | WS-2.5 |

### معيار الإغلاق

- [ ] صفر free-text operational outputs للتدفقات الحرجة
- [ ] كل evidence pack يمر بـ schema validation
- [ ] كل decision memo يُعرض بالعربية والإنجليزية بشكل صحيح

---

## GAP-3: Execution Durability 🔴 Critical

### الوضع الحالي

- Business commitments موزعة بين Celery tasks وخدمات agents
- لا يوجد durable workflow runtime
- إذا أُعيد تشغيل worker، تُفقد العمليات الجارية
- لا يوجد compensation logic للفشل

### الوضع المستهدف

- كل workflow > 15 دقيقة أو يعبر > نظامين أو يحتاج compensation → Temporal
- Celery يبقى فقط لـ short-lived tasks (<5 دقائق، نظام واحد)
- كل workflow حرج يتحمل إعادة التشغيل بدون فقدان حالة

### السبب الجذري

Celery مصمم لـ task queues لا لـ durable workflows. استخدامه لعمليات طويلة خطر مؤسسي.

### خطة الإغلاق

| الخطوة | المخرج | المسار |
|--------|--------|--------|
| جرد وتصنيف كل workflow | Workflow Inventory | WS-3.1 |
| إعداد Temporal | Infrastructure + Docker Compose | WS-3.2 |
| Pilot: Partner Approval Flow | أول workflow durable حي | WS-3.3 |
| Compensation policies | Saga patterns per workflow | WS-3.4 |
| Idempotency keys | Replay-safe endpoints | WS-3.5 |

### معيار الإغلاق

- [ ] Pilot workflow يتحمل worker restart بدون فقدان حالة
- [ ] Compensation يعمل عند فشل خطوة
- [ ] Idempotency keys تمنع التنفيذ المكرر

---

## GAP-4: Policy & Auth ليست Single Source of Truth 🟠 High

### الوضع الحالي

- Policy logic مبعثر في:
  - `security_gate.py` — بوابة أمان
  - `escalation.py` — تصعيد
  - Agent prompts — تعليمات سياسية داخل النصوص
  - Scattered conditionals — شروط متفرقة في الخدمات
- Authorization عبر JWT claims فقط
- لا يوجد relationship-based authorization

### الوضع المستهدف

| المكون | المسؤولية |
|--------|----------|
| OPA | Policy decisions — كل قرار سياسة |
| OpenFGA | Authorization graph — التفويض الدقيق |
| App code | Enforcement hooks only — نقاط إنفاذ فقط |

### السبب الجذري

الأمان بُني تدريجياً مع نمو النظام. لا يوجد policy-as-code discipline.

### خطة الإغلاق

| الخطوة | المخرج | المسار |
|--------|--------|--------|
| جرد كل سياسات الكود | Policy Inventory | WS-4.1 |
| كتابة Rego policies | OPA Policy Packs | WS-4.2 |
| تصميم authorization model | OpenFGA Model | WS-4.3 |
| ربط الخدمات بـ OPA/OpenFGA | Integration | WS-4.2–4.3 |

### معيار الإغلاق

- [ ] لا policy logic في application code (enforcement hooks فقط)
- [ ] كل سؤال "هل يحق لـ X فعل Y؟" يُجاب من OpenFGA
- [ ] كل سؤال "هل يجوز فعل X في سياق Z؟" يُجاب من OPA

---

## GAP-5: Tool Verification لم يصل إلى Mandatory Evidence 🟠 High

### الوضع الحالي

- `tool_verification.py` و `tool_receipts.py` موجودتان
- لكن الإنفاذ ليس شاملاً — بعض الأدوات تعمل بدون تحقق
- لا يوجد contradiction detection تلقائي

### الوضع المستهدف

كل tool/action يُنتج:

| الحقل | الوصف |
|-------|-------|
| `intended_action` | ما أراد الوكيل فعله |
| `claimed_action` | ما ادّعى الوكيل أنه فعله |
| `actual_execution` | ما حدث فعلاً |
| `side_effects` | التأثيرات الجانبية |
| `contradiction_status` | هل هناك تناقض؟ |

### السبب الجذري

الخطر الأكبر: hallucinated operations — الوكيل يدّعي تنفيذ عملية لم تحدث. متسق مع OWASP GenAI: excessive agency + insecure output handling.

### خطة الإغلاق

| الخطوة | المخرج | المسار |
|--------|--------|--------|
| توسيع tool_verification لكل الأدوات | Universal verification | WS-4.6 |
| إضافة contradiction detection | Auto-detection logic | WS-4.6 |
| بناء Contradiction Dashboard | Frontend view | WS-4.7 |

### معيار الإغلاق

- [ ] 100% من tool calls تمر عبر verification
- [ ] Contradictions تُكتشف تلقائياً وتُعرض في dashboard
- [ ] Zero hallucinated operations في الإنتاج

---

## GAP-6: Enterprise Connectors لم تُغلَّف 🟡 Medium

### الوضع الحالي

- الوكلاء يتصلون مباشرة بـ:
  - WhatsApp Cloud API (`whatsapp_service.py`)
  - Email providers (`email_service.py`)
  - Salesforce (`salesforce_agentforce.py`)
  - Stripe (`stripe_service.py`)
- لا يوجد abstraction layer موحّد
- لا versioning على API calls
- لا retry/idempotency policies موحّدة

### الوضع المستهدف

```
Agent → Connector Facade (versioned) → Vendor API
           ↓
    retry + timeout + idempotency + audit log
```

### السبب الجذري

Vendor APIs تتغير. HubSpot أعلن date-based API versioning في 2026. بدون wrappers versioned، كل تغيير API يكسر النظام.

### خطة الإغلاق

| الخطوة | المخرج | المسار |
|--------|--------|--------|
| تعريف Connector Facade ABC | Interface standard | WS-5.1 |
| تغليف WhatsApp | `WhatsAppConnector` | WS-5.2 |
| تغليف Email | `EmailConnector` | WS-5.3 |
| تغليف Salesforce | `SalesforceConnector` | WS-5.4 |

### معيار الإغلاق

- [ ] كل vendor API يُستدعى فقط عبر connector facade
- [ ] كل connector له version tag
- [ ] كل connector له retry + timeout + idempotency policy

---

## GAP-7: Observability/Evals لم تصبح Gate 🟠 High

### الوضع الحالي

- `observability.py` موجود لكن لا يستخدم OpenTelemetry
- لا `trace_id` أو `correlation_id` على الطلبات
- لا offline eval datasets للوكلاء
- لا online trace review
- لا red-team testing على أسطح الوكلاء/الأدوات
- لا regression review per release

### الوضع المستهدف

| المكون | الوصف |
|--------|-------|
| OTel traces/metrics/logs | Vendor-neutral telemetry |
| trace_id/correlation_id | على كل طلب من الدخول إلى الخروج |
| Offline eval datasets | مجموعات بيانات تقييم محفوظة |
| Online trace review | مراجعة traces في الإنتاج |
| Red-team | اختبار اختراق لأسطح الوكلاء |
| Regression review | مراجعة تراجعية لكل إصدار |

### السبب الجذري

Observability بُني كأداة تصحيح أخطاء، لا كبوابة جودة.

### خطة الإغلاق

| الخطوة | المخرج | المسار |
|--------|--------|--------|
| تكامل OTel | Traces + metrics + logs | WS-6.3, WS-1.1 |
| إضافة correlation IDs | Middleware + propagation | WS-6.3 |
| بناء eval datasets | Per-agent test sets | WS-2.2 |
| Red-team plan | Per-release security review | WS-7.6 |

### معيار الإغلاق

- [ ] كل طلب يحمل `trace_id` من الدخول إلى الخروج
- [ ] كل وكيل له ≥10 test cases في eval dataset
- [ ] كل إصدار يمر بـ regression review

---

## GAP-8: Saudi Enterprise Posture Needs Operationalization 🔴 Critical

### الوضع الحالي

- `pdpl-checklist.md` موجودة لكن كقائمة تحقق ثابتة
- `zatca_compliance.py` موجود لكن بدون اختبار شامل
- لا يوجد:
  - PDPL control matrix مربوطة بالكود
  - NCA ECC readiness matrix
  - AI governance controls mapped to NIST AI RMF
  - Data residency flags في policy engine

### الوضع المستهدف

| المكون | المعيار |
|--------|---------|
| PDPL Control Matrix | كل حقل PII مصنّف + قاعدة معالجة |
| NCA ECC Readiness | كل control من ECC 2-2024 مُقيَّم |
| AI Governance | ملف حوكمة per agent type (NIST AI RMF) |
| OWASP LLM | قائمة تحقق per release |
| Data Residency | أعلام إنفاذ في policy engine |

### السبب الجذري

التحول من PDPL checklist (وثيقة) إلى PDPL enforcement (كود) لم يحدث.

### خطة الإغلاق

| الخطوة | المخرج | المسار |
|--------|--------|--------|
| PDPL Data Classification | Matrix per data field | WS-7.1 |
| Processing Register | Per PDPL Art. 29 | WS-7.2 |
| Data Residency Flags | Policy engine integration | WS-7.3 |
| NCA ECC Gaps | Assessment + remediation plan | WS-7.4 |
| AI Governance Profile | NIST AI RMF mapping | WS-7.5 |
| OWASP LLM Checklist | Per-release gate | WS-7.6 |

### معيار الإغلاق

- [ ] كل حقل PII مصنّف ومربوط بقاعدة معالجة
- [ ] NCA ECC assessment مكتمل مع خطة remediation
- [ ] OWASP LLM checklist مدمج في release process
- [ ] Data residency enforced في policy engine

---

## ملخص الفجوات حسب الخطورة

| الخطورة | العدد | الفجوات |
|---------|-------|---------|
| 🔴 Critical | 4 | GAP-1 (Docs > Execution), GAP-2 (Decision Plane), GAP-3 (Execution Durability), GAP-8 (Saudi Posture) |
| 🟠 High | 3 | GAP-4 (Policy/Auth), GAP-5 (Tool Verification), GAP-7 (Observability) |
| 🟡 Medium | 1 | GAP-6 (Connectors) |

---

## أولوية الإغلاق

```
Sprint 1:  GAP-1 (Architecture Register → يُمكّن كل شيء آخر)
Sprint 2:  GAP-4 (Policy Inventory → أساس Trust Fabric)
Sprint 3:  GAP-2 (Decision Schemas → أساس Decision Plane)
Sprint 4:  GAP-3 (Temporal Pilot → أساس Execution Plane)
Sprint 5:  GAP-5 (Tool Verification → إنفاذ الثقة)
Sprint 6:  GAP-7 (Observability → بوابة الجودة)
Sprint 7:  GAP-6 (Connectors → استقرار التكاملات)
Sprint 8:  GAP-8 (Saudi Posture → جاهزية السوق)
```

---

*كل فجوة لها deliverables مربوطة بالمصفوفة التنفيذية. لا يُغلق أي فجوة بدون evidence gate.*

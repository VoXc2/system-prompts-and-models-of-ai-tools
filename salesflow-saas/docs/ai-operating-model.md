# AI Operating Model — Dealix Revenue & Operations OS

> **الحالة:** معتمد | **الإصدار:** 1.0 | **التاريخ:** 2026-04-16
>
> يحدد هذا الملف كيف يعمل الذكاء الاصطناعي في Dealix — من اتخاذ القرار إلى التنفيذ إلى الحوكمة.

---

## 1. المبدأ الأساسي

> **الذكاء الاصطناعي يقترح، والنظام ينفذ، والإنسان يوافق عند الحاجة.**

لا يوجد agent يعمل بشكل مستقل تماماً. كل قرار AI يمر عبر مسار محدد:

```
AI Agent (Decision Plane)
    │
    ▼
Structured Output (JSON schema)
    │
    ▼
Policy Gate (Class A/B/C check)
    │
    ├── Class A → Auto-execute via workflow
    ├── Class B → Route to approval → Execute on approval
    └── Class C → Block + alert
```

---

## 2. سجل الوكلاء (Agent Registry)

### 2.1 الوكلاء الـ 19

| # | الوكيل | الدور | المدخلات | المخرجات | الحالة |
|---|--------|------|----------|----------|--------|
| 1 | Lead Qualification | تصنيف وتقييم العملاء المحتملين | Lead data, behavior signals | Score 0-100, qualification label | Implemented |
| 2 | Affiliate Recruitment Evaluator | تقييم طلبات الشراكة | Application data | Accept/reject + score | Implemented |
| 3 | Onboarding Coach | توجيه الشركاء الجدد | Partner profile | Onboarding plan + checklist | Implemented |
| 4 | Outreach Writer | كتابة رسائل مخصصة | Lead profile, channel | Message draft | Implemented |
| 5 | Arabic WhatsApp Agent | محادثات واتساب بالعربية | Message, context | Response + intent | Implemented |
| 6 | English Conversation Agent | محادثات إنجليزية | Message, context | Response + intent | Implemented |
| 7 | Voice Call Agent | تحليل المكالمات | Call transcript | Summary + action items | Implemented |
| 8 | Meeting Booking Agent | جدولة الاجتماعات | Lead data, availability | Booking confirmation | Implemented |
| 9 | Sector Strategist | استراتيجية القطاع | Industry data, trends | Strategy recommendations | Implemented |
| 10 | Objection Handler | معالجة الاعتراضات | Objection text, context | Counter-argument | Implemented |
| 11 | Proposal Drafter | صياغة العروض | Deal data, requirements | Proposal document | Implemented |
| 12 | QA Reviewer | مراجعة الجودة | Agent output | Quality score + issues | Implemented |
| 13 | Compliance Reviewer | مراجعة الامتثال | Message/action | Compliance verdict | Implemented |
| 14 | Knowledge Retrieval Agent | استرجاع المعرفة | Query, context | Relevant articles + RAG | Implemented |
| 15 | Revenue Attribution Agent | إسناد الإيرادات | Deal, touchpoints | Attribution model | Implemented |
| 16 | Fraud Reviewer | كشف الاحتيال | Transaction data | Risk score + verdict | Implemented |
| 17 | Guarantee Reviewer | مراجعة الضمانات | Claim data | Approve/reject + reason | Implemented |
| 18 | Management Summary Agent | ملخصات تنفيذية | Period data | Executive summary | Implemented |
| 19 | Customer Integration Concierge | دليل التكامل | Customer setup data | Integration plan + steps | Implemented |

### 2.2 بنية التنسيق

```
                    ┌─────────────────┐
                    │  Hermes Router   │
                    │  (Intent→Agent)  │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              ▼              ▼              ▼
         ┌─────────┐  ┌─────────┐  ┌─────────┐
         │ Agent A  │  │ Agent B  │  │ Agent C  │
         └────┬────┘  └────┬────┘  └────┬────┘
              │            │            │
              ▼            ▼            ▼
         ┌─────────────────────────────────┐
         │       Manus Orchestrator         │
         │  (Parallel execution, max 8)     │
         │  (Sub-agents: max depth 2)       │
         └──────────────┬──────────────────┘
                        │
                        ▼
         ┌─────────────────────────────────┐
         │     Policy Gate + Approval       │
         └─────────────────────────────────┘
```

---

## 3. سلسلة مزودي LLM

| الأولوية | المزود | النموذج | الاستخدام |
|----------|--------|---------|----------|
| 1 (أساسي) | Groq | llama-3.1-70b | تصنيف سريع، Arabic NLP |
| 2 | Claude | Opus 4.6 | نسخ مبيعات، تحليل معقد |
| 3 | Gemini | — | بحث، تحليل |
| 4 | DeepSeek | — | كود، تحليل تقني |
| 5 (احتياطي) | OpenAI | GPT-4o-mini | احتياطي عام |

**قواعد التوجيه:**
- المهام عالية الجودة (proposals, strategies) → Claude / GPT-4o
- المهام السريعة (classification, routing) → Groq
- الـ Embeddings → text-embedding-3-small (OpenAI)
- محلي (اختياري) → Ollama qwen2.5:7b

---

## 4. الذاكرة والسياق

### 4.1 طبقات الذاكرة

| الطبقة | التقنية | النطاق | الغرض |
|--------|---------|--------|-------|
| Short-term | In-context (prompt) | جلسة واحدة | سياق المحادثة الحالية |
| Working | Mem0 | per agent/deal/customer | سياق عبر الجلسات |
| Long-term | PostgreSQL + pgvector | per tenant | معرفة مستمرة + RAG |
| Tiered | Letta | per tenant | استرجاع تدريجي متعدد المستويات |

### 4.2 حوكمة الذاكرة

- **Tenant isolation**: كل ذاكرة مقيدة بـ tenant_id
- **Freshness**: metadata تحمل last_updated + confidence score
- **Eviction**: 12-month TTL على consent-related memories
- **Privacy**: `<private>...</private>` tags تمنع الفهرسة

---

## 5. حلقة التحسين الذاتي

```
┌─────────┐    ┌─────────┐    ┌──────────┐    ┌────────┐    ┌────────┐    ┌───────────┐
│ Observe  │───▶│ Analyze  │───▶│Hypothesize│───▶│ Shadow  │───▶│ Canary  │───▶│Meta-Learn │
│(signals) │    │(diagnose)│    │(generate) │    │ (test)  │    │(deploy) │    │ (evolve)  │
└─────────┘    └─────────┘    └──────────┘    └────────┘    └────────┘    └───────────┘
```

**المصادر:**
- App analytics (conversion rates, response times)
- LLM traces (token usage, error rates)
- OpenClaw outcomes (approval rates, rejection reasons)
- Agent performance (quality scores, escalation rates)

**القيود:**
- تجارب خلف feature flags فقط
- Canary على tenants محددة أولاً
- كل تحسين يسجل before/after
- لا تعديل على إنتاج بدون validation

---

## 6. الحوكمة والامتثال

### 6.1 فئات الأفعال

| الفئة | أمثلة | القاعدة |
|-------|--------|--------|
| **Class A** (تلقائي) | read_status, classify, summarize, research, generate_draft, plan | تنفيذ تلقائي |
| **Class B** (موافقة) | send_whatsapp, send_email, create_charge, sync_salesforce, send_contract | يحتاج موافقة بشرية |
| **Class C** (ممنوع) | exfiltrate_secrets, delete_data_without_audit, bypass_auth | ممنوع دائماً |

### 6.2 مسار الموافقة

```
Agent Output → Policy Check → Approval Required?
                                    │
                          ┌─────────┼─────────┐
                          │ No      │ Yes     │
                          ▼         ▼         │
                     Execute    Create         │
                                ApprovalRequest │
                                    │          │
                                    ▼          │
                               Route to        │
                               Approver        │
                                    │          │
                              ┌─────┼─────┐    │
                              │ Approve   │    │
                              ▼     │ Reject   │
                          Execute   ▼     │    │
                                Log + Alert    │
                                               │
                          SLA: 24h timeout ────┘
```

### 6.3 Canary Tenants

- `OPENCLAW_CANARY_TENANTS` تحدد الـ tenants التجريبية
- الـ canary tenants تحصل على auto-execute لأفعال Class B محددة
- باقي الـ tenants تتطلب موافقة صريحة
- يُستخدم للتجارب قبل التعميم

---

## 7. المقاييس والمراقبة

| المقياس | الهدف | طريقة القياس |
|---------|-------|-------------|
| Agent accuracy | >90% | QA reviewer scores |
| Response latency | <3s | P95 from LLM traces |
| Escalation rate | <15% | Escalation events / total |
| Approval SLA | <24h | Approval request age |
| LLM cost per tenant | Budget-bound | Token usage * price |
| Consent compliance | 100% | PDPL audit checks |

---

## 8. الروابط

- المرجع الأعلى: [`MASTER_OPERATING_PROMPT.md`](../MASTER_OPERATING_PROMPT.md)
- المخطط المعماري: [`MASTER-BLUEPRINT.mdc`](../MASTER-BLUEPRINT.mdc)
- خريطة الوكلاء التفصيلية: [`AGENT-MAP.md`](AGENT-MAP.md)
- نسيج الثقة: [`governance/trust-fabric.md`](governance/trust-fabric.md)
- الطبقات: [`governance/planes-and-runtime.md`](governance/planes-and-runtime.md)

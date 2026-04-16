# MASTER OPERATING PROMPT — Dealix Revenue & Operations OS

> **الحالة:** معتمد | **الإصدار:** 1.0 | **التاريخ:** 2026-04-16
>
> هذا الملف هو الدستور التشغيلي للمنصة. أي agent أو workflow أو مُشغّل بشري يعمل ضمن Dealix يلتزم بما هنا.

---

## 1. الهوية

Dealix هو **نظام تشغيل إيرادات وعمليات مؤسسي** (Revenue & Operations OS) مصمم للسوق السعودي أولاً، ثم الخليجي والعالمي. ليس chatbot، ليس dashboard، بل **فريق رقمي كامل** يعمل 24/7 — من الاستكشاف إلى التأهيل إلى العرض إلى الإغلاق إلى ما بعد البيع.

**الشعار التشغيلي:**
> Agentic by design, governed by policy, proven by evidence.

---

## 2. المبادئ غير القابلة للتفاوض

| # | المبدأ | المعنى التشغيلي |
|---|--------|----------------|
| 1 | **القيمة أولاً** | كل feature مرتبط بنتيجة قابلة للقياس — revenue lift, cost reduction, compliance adherence |
| 2 | **الامتثال بالتصميم** | الموافقات، سجل المراجعة، تقليل البيانات — ليست إضافة لاحقة بل جزء من البنية |
| 3 | **التطور الذاتي** | حلقة تحسين ذاتي: رصد → تحليل → فرضية → تجربة ظل → canary → تعلم وصفي |
| 4 | **التعقيد مخفي، البساطة ظاهرة** | تنسيق غني داخلياً؛ UX بسيط (chat + dashboards) |
| 5 | **كل شيء قابل للقياس** | ROI تنفيذي، تكلفة LLM لكل tenant، SLOs |
| 6 | **عدم ثقة بين المستأجرين** | عزل صارم؛ الأفعال الحساسة خلف hooks/approvals |

---

## 3. الفصل بين Decision Plane و Execution Plane

هذا أهم قاعدة معمارية في المنصة:

```
┌─────────────────────────────────────────────────────────┐
│                    DECISION PLANE                        │
│  AI Agents, LLM reasoning, scoring, recommendations     │
│  ─── يقترح، يحلل، يصنف ───                              │
│  لا يلتزم خارجياً أبداً                                  │
└──────────────────────┬──────────────────────────────────┘
                       │ structured output
                       ▼
┌─────────────────────────────────────────────────────────┐
│                   EXECUTION PLANE                        │
│  Deterministic workflows, API calls, DB writes           │
│  ─── ينفذ فقط ما تمت الموافقة عليه ───                  │
│  هو الوحيد الذي يلتزم خارجياً                            │
└─────────────────────────────────────────────────────────┘
```

**القواعد:**
1. **Agent لا يلتزم خارجياً** — لا يرسل WhatsApp، لا ينشئ عقداً، لا يحول مالاً مباشرة
2. **Workflow حتمي فقط هو الذي يلتزم** — عبر facades محددة
3. **كل فعل حساس يحمل:** Approval / Reversibility / Sensitivity metadata
4. **كل output حرج يجب أن يكون structured** — JSON schema, not free text
5. **كل connector يمر عبر facade** — لا اتصال مباشر بخدمة خارجية
6. **لا policy logic داخل prompt** إذا كان موضعها الصحيح policy engine

---

## 4. الطبقات الخمس (5 Planes)

| الطبقة | المسؤولية | الحالة |
|--------|-----------|--------|
| **Decision Plane** | تفكير AI، تصنيف، توصيات، تحليل | Implemented (agents + LLM routing) |
| **Execution Plane** | Workflows حتمية، API calls، DB writes | Implemented (FastAPI + Celery) |
| **Trust Plane** | سياسات، موافقات، تحقق أدوات، أدلة، تدقيق | Partial (PDPL consent + audit logs) |
| **Data Plane** | CRM grounding، memory، vector search، metrics | Implemented (PostgreSQL + pgvector + Mem0) |
| **Operating Plane** | CI/CD، مراقبة، نشر، صحة النظام | Partial (GitHub Actions + health checks) |

→ التفصيل الكامل: [`docs/governance/planes-and-runtime.md`](docs/governance/planes-and-runtime.md)

---

## 5. المسارات الستة (6 Tracks)

| المسار | النطاق | المالك |
|--------|--------|--------|
| **Revenue OS** | Leads → Deals → Close → Upsell | Sales team |
| **Partnership OS** | Scout → Qualify → Engage → Manage | BD team |
| **CorpDev / M&A OS** | Target → Evaluate → Negotiate → Integrate | Founder |
| **Expansion OS** | New markets → Localize → Launch → Scale | Growth team |
| **PMI / PMO OS** | Integrate → Track → Optimize → Report | Ops team |
| **Executive / Governance OS** | Decide → Approve → Monitor → Steer | Executive team |

→ التفصيل الكامل: [`docs/dealix-six-tracks.md`](docs/dealix-six-tracks.md)

---

## 6. بوابات الأمان (Safety Gates)

كل فعل في المنصة مصنف حسب ثلاثة محاور:

### 6.1 فئات السياسة

| الفئة | الأفعال | القاعدة |
|-------|---------|--------|
| **Class A** — تلقائي | قراءة كود، توليد اختبارات، تحديث docs، تحليل | مسموح بدون موافقة |
| **Class B** — يحتاج موافقة | هجرات DB، رسائل عملاء، تغييرات دفع، نشر إنتاج، PDPL | يحتاج approval + audit trail |
| **Class C** — ممنوع | تسريب أسرار، تجاوز حماية فروع، حذف صامت، وصول بين tenants | ممنوع مطلقاً |

### 6.2 خصائص كل فعل حساس

```yaml
action:
  name: "send_whatsapp_message"
  sensitivity: high          # low | medium | high | critical
  reversibility: none        # full | partial | none
  approval_required: true
  approval_sla: "2h"
  audit_required: true
  evidence_pack: true
  pdpl_consent_check: true
```

### 6.3 قاعدة الالتزام الخارجي

> **لا يجوز لأي agent أن يلتزم خارجياً مباشرة.**
> الالتزام يتم فقط عبر workflow حتمي يمر عبر:
> 1. Policy gate (يفحص الصلاحيات)
> 2. Approval routing (يوجه للموافق المناسب)
> 3. Facade execution (ينفذ عبر واجهة محددة)
> 4. Evidence logging (يسجل الدليل)

---

## 7. حلقة التحسين الذاتي

```
Observation → Analysis → Hypothesis → Shadow Experiment → Canary Deploy → Meta-Learning
     ↑                                                                          │
     └──────────────────── Feedback Loop ──────────────────────────────────────┘
```

**القيود:**
- التجارب خلف feature flags فقط
- لا تعديل على prompts إنتاج بدون canary
- كل تحسين يسجل before/after metrics
- Meta-learning يغذي strategy، لا يغير policy مباشرة

---

## 8. المقاييس المستهدفة

| المحور | الهدف | الأساس |
|--------|-------|--------|
| نمو الإيرادات | 3-5× سنوياً | خط أساس العميل |
| كفاءة المبيعات | 70-80% تقليل عمل يدوي | Pipeline time audit |
| دورة البيع | ~40% أقصر | Close cycle baseline |
| تكلفة الاستحواذ | ~31% أقل | CAC baseline |
| الامتثال | PDPL-aligned, SOC2-ready | Regulatory requirements |

---

## 9. قواعد الجودة

1. **لا يُدّعى أن شيئاً "في الإنتاج" بدون evidence code/config حقيقي**
2. **كل مكون يصنف:** Implemented | Partial | Planned | Pilot
3. **لا عبارات فضفاضة** مثل "when added" أو "future integration" بدون تصنيف واضح
4. **لا خلط** بين "core رسمي" و "strong optional" و "pilot فقط"
5. **كل وثيقة تتحقق بـ** `python scripts/architecture_brief.py`
6. **كل مسار يبدأ من جذر الريبو** — لا افتراضات مسار قديمة

---

## 10. خريطة الوثائق

```
MASTER_OPERATING_PROMPT.md          ← أنت هنا (الدستور)
├── docs/ai-operating-model.md       ← نموذج تشغيل AI
├── docs/dealix-six-tracks.md        ← المسارات الستة
├── docs/governance/
│   ├── planes-and-runtime.md        ← الطبقات والتشغيل
│   ├── execution-fabric.md          ← نسيج التنفيذ
│   ├── trust-fabric.md              ← نسيج الثقة
│   ├── saudi-compliance-and-ai-governance.md ← امتثال سعودي
│   └── technology-radar-tier1.md    ← رادار التقنية
├── docs/execution-matrix-90d-tier1.md ← مصفوفة 90 يوم
├── docs/adr/
│   └── 0001-tier1-execution-policy-spikes.md ← ADR بوابات
├── MASTER-BLUEPRINT.mdc             ← المخطط المعماري
├── docs/ARCHITECTURE.md             ← البنية التقنية
├── docs/AGENT-MAP.md                ← خريطة الوكلاء
├── docs/DATA-MODEL.md               ← نموذج البيانات
└── docs/enterprise-closure-master-checklist.md ← قائمة الإغلاق
```

---

## 11. قاعدة التشغيل اليومية

قبل أي عمل جديد:
```bash
python scripts/architecture_brief.py   # spine check
```

يتحقق من:
- جميع مسارات `docs/governance/` موجودة
- أوامر `.claude/commands/` سليمة
- لا توجد path assumptions قديمة
- الاتساق بين الوثائق

---

*هذا الملف هو المرجع الأعلى. أي تعارض مع وثيقة أخرى يُحل لصالح هذا الدستور.*

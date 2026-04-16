# Dealix — المخطط السيادي المؤسسي الكامل (Sovereign Enterprise Growth OS)

> وثيقة تشغيل سيادي: تحويل Dealix من منصة CRM ذكية إلى نظام سيادة نمو مؤسسي يدير القرار والتنفيذ والحوكمة عبر المبيعات والشراكات والتوسع وCorpDev وPMI.

---

## 1) الرؤية النهائية

الهدف ليس "أفضل CRM ذكي"، بل:

**Dealix Sovereign Enterprise Growth OS**

نظام موحد يدير:
- المبيعات (Revenue OS)
- الشراكات (Partnership OS)
- التطوير المؤسسي والاستحواذات (M&A / CorpDev OS)
- التوسع الجغرافي والقطاعي (Expansion OS)
- ما بعد الاندماج وإدارة البرامج (PMI / PMO OS)
- القيادة التنفيذية ومجلس الإدارة (Executive / Board OS)

قاعدة التشغيل:
**الذكاء الاصطناعي يستكشف ويحلل ويقترح، الأنظمة تنفذ، والبشر يعتمدون القرارات الحرجة.**

---

## 2) الفجوة الحقيقية الآن

أنتم تجاوزتم مرحلة الفكرة: توجد طبقة مرجعية قوية (prompt دستوري، governance library، execution matrices، architecture pack، cadence تشغيلي أسبوعي).

**الفجوة الحالية ليست نقص الأفكار؛ بل إغلاق تشغيلي كامل داخل المنتج نفسه** بحيث تصبح الحوكمة والاعتماد والتنفيذ جزءًا أصيلًا من كل مسار عمل.

---

## 3) معمارية السيادة: 5 Planes

## 3.1 Decision Plane (طبقة القرار)
المهام:
- signal detection
- triage
- scenario analysis
- memo generation
- forecasting
- recommendation
- next best action
- evidence pack assembly

المتطلبات التقنية:
- Responses API (stateful interactions)
- Structured Outputs (schema-bound decisions)
- function calling / MCP
- agents tracing + guardrails
- LangGraph للحلقات المعتمدة على الحالة وinterrupts للـ HITL

المعيار:
كل recommendation يجب أن يكون typed + evidence-backed + policy-aware + freshness-aware.

## 3.2 Execution Plane (طبقة التنفيذ)
أي مسار يمتد، يعبر عدة أنظمة، أو يخلق التزامًا خارجيًا يجب أن يكون durable.

القاعدة:
- **LangGraph**: cognition + HITL + short/medium orchestration
- **Temporal**: durable business commitments (approvals, DD rooms, signatures, launches, PMI)

المعيار:
كل business commitment يجب أن يكون durable + resumable + idempotent + compensatable + observable.

## 3.3 Trust Plane (طبقة الثقة)
المكونات الإلزامية:
- policy engine
- approval routing
- fine-grained authorization
- secrets governance
- tool verification ledger
- evidence packs
- contradiction detection
- auditability
- AI governance controls

التوصية المرجعية:
- OPA للسياسات
- OpenFGA للتفويض الدقيق
- Vault للأسرار والدوران والاعتمادات القصيرة العمر
- Keycloak للهوية وSSO والـ brokering

## 3.4 Data Plane (طبقة البيانات)
تصميم منضبط:
- Postgres كمصدر تشغيلي للحقيقة
- pgvector للذاكرة الدلالية قرب بيانات العمليات
- Airbyte للربط ingestion/connectors
- Unstructured لاستخراج المستندات
- Great Expectations لجودة البيانات
- CloudEvents + JSON Schema + AsyncAPI لعقود البيانات والأحداث
- OpenTelemetry للإشارات الثلاث traces/metrics/logs

## 3.5 Operating Plane (طبقة التشغيل المؤسسي)
متطلبات SDLC/GitHub:
- rulesets + protected branches
- CODEOWNERS
- required status checks
- environments + deployment protection rules
- OIDC federation بدل long-lived secrets
- artifact attestations / provenance
- external audit log streaming

---

## 4) الشكل الكامل للمنتج (Surfaces إلزامية)

هذه ليست إضافات اختيارية؛ بل واجهات تشغيل سيادي يجب أن تكون حية:

- Executive Room
- Approval Center
- Evidence Pack Viewer
- Partner Room
- DD Room
- Risk Board
- Policy Violations Board
- Actual vs Forecast Dashboard
- Revenue Funnel Control Center
- Partnership Scorecards
- M&A Pipeline Board
- Expansion Launch Console
- PMI 30/60/90 Engine
- Tool Verification Ledger
- Connector Health Board
- Release Gate Dashboard
- Saudi Compliance Matrix
- Model Routing Dashboard

---

## 5) Business Tracks (6 Tracks إلزامية)

## 5.1 Revenue OS
capture, enrichment, qualification, scoring, routing, outreach, meeting orchestration, proposal generation, pricing/discount governance, contract handoff, onboarding handoff, renewal/upsell/cross-sell.

## 5.2 Partnership OS
partner scouting, strategic fit scoring, channel economics, alliance structure recommendation, term sheet drafts, approval/legal routing, partner activation, partner scorecards, contribution margin tracking.

## 5.3 M&A / CorpDev OS
target sourcing/screening, DD orchestration, DD room controls, valuation ranges, synergy modeling, investment committee memos, board packs, offer strategy, sign/close readiness.

## 5.4 Expansion OS
market scanning, prioritization, compliance readiness, localization, pricing/channel planning, launch readiness, stop-loss logic, post-launch actual vs forecast.

## 5.5 PMI / PMO OS
Day-1 readiness, 30/60/90 plans, dependency tracking, owner assignment, escalation engine, synergy realization, risk registers, weekly executive review.

## 5.6 Executive / Board OS
board-ready memos, evidence packs, approval center, risk heatmaps, actual vs forecast, next best action, policy violations, integrated portfolio view.

---

## 6) نموذج الأتمتة: ماذا يُؤتمت وما الذي يحتاج اعتمادًا

## 6.1 يُؤتمت بالكامل
intake, enrichment, scoring, memo drafting, evidence aggregation, workflow kickoff, reminders, task assignment, SLA tracking, dashboard refresh, variance detection, anomaly alerts, extraction, connector syncs, quality checks, telemetry collection.

## 6.2 يُؤتمت مع اعتماد إلزامي
term sheet sending, signature requests, strategic partner activation, market launch, M&A offers, off-policy discounts, high-sensitivity data sharing, production promotion, capital commitments.

قاعدة الحوكمة:
كل إجراء غير قابل للعكس أو عالي الحساسية يمر عبر HITL interrupts.

---

## 7) السيادة على السوق السعودي (Arabic-first + Saudi-ready)

العربية ليست طبقة تجميل؛ هي طبقة تفوق سوقي وتشغيلي.

العربية يجب أن تكون أصلية في:
- classification
- memo generation
- board packs
- approval reasons
- notifications
- partner summaries
- retrieval/search
- executive UI
- terminology normalization

الالتزام المحلي:
- PDPL mapping واضح لكل مسار حساس
- مواءمة ضوابط الأمن السيبراني الوطنية
- إطار عملي لإدارة مخاطر AI (NIST AI RMF)
- معالجة مخاطر LLM التنفيذية (مثل prompt injection وoutput handling)

---

## 8) Connector Strategy: لا ربط مباشر للوكلاء مع كل Vendor

ابنوا **Connector Facade** لكل تكامل، ويحتوي كل connector على:
- contract
- version
- retry policy
- timeout policy
- idempotency key
- approval policy
- audit mapping
- telemetry mapping
- rollback/compensation notes

الهدف:
منع هشاشة التكاملات عند تغييرات API وتخفيف N×M بين الوكلاء والخدمات.

---

## 9) Program Locks (إقفال البرنامج رسميًا داخل النظام)

تثبيت بنية إلزامية داخل المنتج:
- 5 planes
- 6 business tracks
- 3 agent roles
- 3 action classes
- 3 approval classes (حد أدنى)
- 4 reversibility classes
- sensitivity model
- provenance/freshness/confidence trio

### تعريفات تشغيلية موصى بها
- Action classes: `observe` / `recommend` / `commit`
- Approval classes: `A0 auto` / `A1 manager` / `A2 executive-board`
- Reversibility classes: `R0 reversible` / `R1 bounded` / `R2 costly` / `R3 irreversible`

---

## 10) Sovereign Routing Fabric (سياسة توجيه النماذج)

تحويل model pool الحالي إلى policy-based routing:
- coding lane
- executive reasoning lane
- throughput drafting lane
- fallback lane

مقاييس إلزامية لكل lane:
- latency
- schema adherence
- contradiction rate
- Arabic quality
- cost per successful task

---

## 11) Evidence-Native Operations

لا يكفي إخراج memo فقط؛ كل قرار كبير يجب أن يتضمن:
- sources
- assumptions
- freshness stamp
- financial model version
- policy notes
- alternatives
- rollback / compensation
- approval class
- reversibility class

المعيار:
أي قرار بلا evidence pack مكتمل لا يُعد قرارًا قابلًا للتنفيذ.

---

## 12) Contradiction Engine (أولوية سيادية)

بناء dashboard يلتقط:
- intended action
- claimed action
- actual tool call
- observed side effects
- contradiction status

الغاية:
إغلاق فجوة "الوكيل قال إنه نفّذ" عبر التحقق من التنفيذ الفعلي.

---

## 13) Definition of Done (جاهزية سيادية نهائية)

لا يعتبر Dealix جاهزًا مؤسسيًا حتى تتحقق الشروط التالية:

- كل قرار business-critical هو structured + evidence-backed + schema-bound.
- كل long-running commitment هو durable + resumable + crash-tolerant.
- كل action حساس يحمل metadata: approval + reversibility + sensitivity.
- كل connector versioned ويملك retry/idempotency/audit mapping.
- كل release يطبق rulesets + environments + OIDC + provenance.
- كل surface يدعم OTel + correlation IDs.
- كل deployment مؤسسي يمر security review وred-team لسطوح LLM/tool execution.
- كل workflow حساس في السعودية لديه mapping واضح على PDPL وضوابط الحوكمة.

---

## 14) خارطة إغلاق تشغيلي (90 يومًا)

## المرحلة A (0–30 يوم)
- إطلاق Approval Center + Evidence Pack Viewer + Release Gate Dashboard
- تفعيل Program Locks وحقول metadata الإلزامية على الإجراءات الحساسة
- ربط OTel correlation IDs عبر Decision/Execution/Trust planes

## المرحلة B (31–60 يوم)
- إدخال Connector Facade للإضافات الحرجة وربط health board
- إطلاق Contradiction Engine v1
- تفعيل policy-based model routing مع قياسات lane الأساسية

## المرحلة C (61–90 يوم)
- DD Room + Partner Room + Policy Violations Board
- ربط workflow durability لمسارات الالتزامات طويلة المدى
- إصدار Saudi Compliance Matrix وربطه بالموافقات والتدقيق

---

## 15) مؤشرات السيادة (KPIs)

| المحور | KPI أساسي | الهدف |
|--------|-----------|-------|
| القرار | نسبة القرارات schema-bound | >= 95% |
| التنفيذ | نسبة commitments القابلة للاستئناف | >= 99% |
| الثقة | نسبة الإجراءات الحساسة المعتمدة قبل التنفيذ | 100% |
| التناقض | contradiction rate | انخفاض ربع سنوي مستمر |
| البيانات | data quality pass rate | >= 98% |
| السوق | جودة العربية في المخرجات التنفيذية | قياس دوري + تحسن مستمر |

---

## 16) التمركز الاستراتيجي النهائي

النسخة المهيمنة من Dealix ليست "AI CRM مطوّر"، بل منصة:
- decision-native
- execution-durable
- trust-enforced
- data-governed
- Arabic-first
- Saudi-ready
- board-usable
- enterprise-saleable

---

## 17) خطوات فورية هذا الأسبوع

1. اعتماد وثيقة Program Locks رسميًا وإضافتها لمعيار القبول في المسارات الحساسة.
2. تعريف action/approval/reversibility classes داخل نماذج القرار والتنفيذ.
3. إطلاق backlog إجباري للـ 18 surfaces (مع ترتيب P0/P1/P2).
4. إنشاء scoreboard موحد: schema adherence + contradiction rate + Arabic quality + cost/task.
5. تثبيت Definition of Done السيادي كـ release gate على مستوى المنتج.

---

*آخر تحديث: وثيقة حية — تراجع أسبوعيًا تشغيليًا وربع سنويًا استراتيجيًا.*

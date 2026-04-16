# Dealix Sovereign Enterprise Growth OS

> مرجع سيادي حي يربط الرؤية، الطبقات، المسارات، الأسطح، الضوابط، وتعريف الجاهزية النهائية داخل المنتج نفسه.

---

## 1) التعريف الصحيح للمنتج

لا يجب أن يتموضع Dealix كـ "أفضل CRM ذكي" فقط.

التموضع الصحيح هو:

**Dealix Sovereign Enterprise Growth OS**

منصة سيادية تدير على قاعدة تشغيل واحدة:
- المبيعات
- الشراكات
- Corporate Development / M&A
- التوسع
- PMI / PMO
- التنفيذ التنفيذي والحوكمة والاعتماد

القاعدة التشغيلية:

> **AI يستكشف ويحلل ويقترح، الأنظمة تنفذ، والبشر يعتمدون القرارات الحرجة.**

---

## 2) أطروحة السيادة

النسخة المهيمنة لا تأتي من زيادة عدد الوكلاء فقط.

بل تأتي من جعل Dealix:
- **decision-native**
- **execution-durable**
- **trust-enforced**
- **data-governed**
- **Arabic-first**
- **Saudi-ready**
- **board-usable**
- **enterprise-saleable**

المشكلة الحقيقية بعد وجود طبقة prompt / governance / execution matrices / architecture pack ليست "نقص أفكار"، بل:

**نقص الإغلاق التشغيلي الكامل داخل المنتج نفسه.**

---

## 3) البنية الكبرى: 5 planes

### 3.1 Decision Plane

وظيفته:
- signal detection
- triage
- scenario analysis
- memo generation
- forecasting
- recommendation
- next best action
- evidence pack assembly

مبادئه:
- Structured outputs
- schema-bound decisions
- provenance + freshness + confidence
- HITL عند المسارات الحساسة

طبقات التنفيذ المقترحة:
- Responses API
- Structured Outputs
- function calling / MCP
- LangGraph للـ stateful loops والـ interrupts

النتيجة المطلوبة:

**كل recommendation business-critical يجب أن يكون typed + evidence-backed + policy-aware + approval-aware.**

### 3.2 Execution Plane

يستوعب كل فعل:
- يمتد أكثر من دقائق
- يمر عبر أكثر من نظام
- يحتاج retry / timeout / compensation
- يخلق التزامًا خارجيًا
- يحتاج approval / resume later

القاعدة:
- **LangGraph = cognition + HITL + short/medium orchestration**
- **Temporal = durable business commitments**

النتيجة المطلوبة:

**كل business commitment يجب أن يكون durable + resumable + idempotent + observable + compensatable.**

### 3.3 Trust Plane

يفصل بين "منصة جميلة" و"منصة شركات".

يضم:
- policy engine
- approval routing
- fine-grained authorization
- secrets governance
- tool verification ledger
- evidence packs
- contradiction detection
- auditability
- AI governance controls

الهدف المرجعي:
- OPA للسياسات
- OpenFGA للتفويض
- Vault للأسرار
- Keycloak للهوية وSSO

النتيجة المطلوبة:

**كل فعل حساس يجب أن يكون authorized + policy-evaluated + audited + verified against actual execution.**

### 3.4 Data Plane

طبقة بيانات منضبطة، لا فوضى تكاملات.

المكوّنات المرجعية:
- Postgres = source of truth
- pgvector = semantic memory near ops data
- Airbyte = ingestion/connectors
- Unstructured = document extraction
- Great Expectations = data quality
- CloudEvents + JSON Schema + AsyncAPI = contracts
- OpenTelemetry = traces + metrics + logs

النتيجة المطلوبة:

**كل surface وكل workflow يجب أن يكون traceable ويعتمد عقود بيانات واضحة.**

### 3.5 Operating Plane

طبقة SDLC والإطلاقات والإثباتات.

تضم:
- rulesets
- protected branches
- CODEOWNERS
- required status checks
- environments
- deployment protection rules
- OIDC federation
- artifact attestations
- external audit log streaming

النتيجة المطلوبة:

**كل release مؤسسي يجب أن يحمل provenance واضحًا وبوابات نشر قابلة للتدقيق.**

---

## 4) المنتج الكامل: 6 business tracks

### 4.1 Revenue OS

يدير:
- capture
- enrichment
- qualification
- scoring
- routing
- outreach
- meeting orchestration
- proposal generation
- pricing / discount governance
- contract handoff
- onboarding handoff
- renewal / upsell / cross-sell

### 4.2 Partnership OS

يدير:
- partner scouting
- strategic fit scoring
- channel economics
- alliance structure recommendation
- term sheet drafts
- approval and legal routing
- partner activation
- partner scorecards
- contribution margin tracking

### 4.3 M&A / CorpDev OS

يدير:
- target sourcing
- target screening
- DD orchestration
- DD room access control
- valuation range
- synergy modeling
- investment committee memos
- board packs
- offer strategy
- signing / close readiness

### 4.4 Expansion OS

يدير:
- market scanning
- prioritization
- compliance readiness
- localization
- pricing / channel plan
- launch readiness
- stop-loss logic
- post-launch actual vs forecast

### 4.5 PMI / PMO OS

يدير:
- Day-1 readiness
- 30/60/90 integration plans
- dependency tracking
- owner assignment
- escalation engine
- synergy realization tracking
- risk registers
- weekly executive review

### 4.6 Executive / Board OS

يعرض:
- board-ready memos
- evidence packs
- approval center
- risk heatmaps
- actual vs forecast
- next best action
- policy violations
- partner / M&A / expansion pipeline

---

## 5) Program locks

يجب قفل ما يلي رسميًا داخل النظام:
- 5 planes
- 6 business tracks
- 3 agent roles على الأقل
- 3 action classes
- 3 approval classes على الأقل
- 4 reversibility classes
- sensitivity model
- provenance / freshness / confidence trio

### 5.1 Action classes
- **Advisory**: تحليل وتوصية فقط
- **Assistive**: تحضير drafts وتشغيل workflow دون التزام خارجي مباشر
- **Committing**: فعل ينشئ التزامًا خارجيًا أو مادياً

### 5.2 Approval classes
- **Operational**: مدير أو مالك مسار
- **Sensitive**: بيانات حساسة / إطلاق / مشاركة / خصومات خارج السياسة
- **Board / Committee**: M&A / التزامات رأسمالية / قرارات غير قابلة للعكس

### 5.3 Reversibility classes
- Reversible
- Time-bound reversible
- Hard-to-reverse
- Irreversible

### 5.4 Metadata trio
- provenance
- freshness
- confidence

---

## 6) ما يُؤتمت وما لا يُؤتمت وحده

### يُؤتمت بالكامل
- intake
- enrichment
- scoring
- memo drafting
- evidence aggregation
- workflow kickoff
- reminders
- task assignment
- SLA tracking
- dashboard refresh
- variance detection
- anomaly alerts
- document extraction
- connector syncs
- quality checks
- telemetry collection

### يُؤتمت مع اعتماد إلزامي
- term sheet sending
- signature request
- strategic partner activation
- market launch
- M&A offer
- discount خارج السياسة
- high-sensitivity data sharing
- production promotion
- capital commitments

---

## 7) Sovereign routing fabric

يجب تحويل model pool إلى **policy-based routing**:

- coding lane
- executive reasoning lane
- throughput drafting lane
- fallback lane

ويُقاس لكل lane:
- latency
- schema adherence
- contradiction rate
- Arabic quality
- cost per successful task

---

## 8) Evidence-native operations

كل قرار كبير لا يخرج معه memo فقط، بل:
- sources
- assumptions
- freshness
- financial model version
- policy notes
- alternatives
- rollback / compensation
- approval class
- reversibility class

بدون هذه العناصر، يبقى القرار غير board-ready.

---

## 9) Contradiction engine

يجب أن توجد طبقة أو لوحة تلتقط:
- intended action
- claimed action
- actual tool call
- side effects
- contradiction status

بدون هذا، ستبقى فجوة agentic أساسية:

**"الوكيل قال إنه فعل."**

---

## 10) Connector facade discipline

لا يُسمح للوكلاء بالارتباط المباشر بكل vendor.

كل connector يجب أن يحمل:
- contract
- version
- retry policy
- timeout policy
- idempotency key
- approval policy
- audit mapping
- telemetry mapping
- rollback / compensation notes

هذا مهم لأن APIs تتغير، ولأن المنتج يحتاج استقرارًا مؤسسيًا لا direct bindings هشّة.

---

## 11) الأسطح الحيّة الإلزامية داخل المنتج

هذه القائمة إلزامية للنسخة المهيمنة:
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

إذا غاب واحد من هذه، فهناك جزء ناقص من النسخة الكاملة.

---

## 12) السعودية والعربية: جزء من التفوق وليس إضافة

التفوق المحلي لا يتحقق بترجمة الواجهة فقط.

العربية يجب أن تدخل في:
- classification
- memo generation
- board packs
- approval reasons
- notifications
- partner summaries
- search / retrieval
- executive UI
- terminology normalization

والجاهزية السعودية يجب أن تظهر بوضوح في:
- PDPL mapping
- NCA / ECC alignment
- AI governance controls
- channel governance
- data handling boundaries

---

## 13) ربط هذه الرؤية بالمستودع الحالي

مرتكزات موجودة الآن ويمكن البناء عليها:
- `backend/app/api/v1/strategy_summary.py`
- `frontend/src/app/strategy/strategy-page-client.tsx`
- `frontend/src/lib/strategy-summary.ts`
- `backend/app/services/tool_verification.py`
- `backend/app/services/security_gate.py`
- `backend/app/services/hermes_orchestrator.py`
- `backend/app/services/execution_router.py`
- `backend/app/services/model_router.py`
- `backend/app/services/go_live_matrix.py`
- `memory/architecture/module-map.md`

المطلوب التالي ليس البدء من الصفر، بل:
- تحويل الرؤية إلى **contract** حي
- ربطها بالـ surfaces الموجودة والقادمة
- إغلاق الفجوة بين docs وproduct

---

## 14) تعريف الجاهزية النهائية

لا يعتبر Dealix جاهزًا بصدق لخدمة الشركات إلا إذا صار:

- كل قرار business-critical structured + evidence-backed + schema-bound.
- كل long-running commitment durable + resumable + crash-tolerant.
- كل action حساس يحمل approval / reversibility / sensitivity metadata.
- كل connector versioned وله retry / idempotency / audit mapping.
- كل release له rulesets + environments + OIDC + provenance.
- كل surface traceable عبر OTel + correlation IDs.
- كل deployment مؤسسي له security review وred-team لسطوح LLM/tool execution.
- كل workflow حساس في السعودية له mapping واضح على PDPL / NCA / AI governance.

---

## 15) الخلاصة التنفيذية

النقلة المطلوبة ليست:
- المزيد من الوكلاء
- المزيد من الصفحات التسويقية
- المزيد من المذكرات

بل:
- تثبيت planes
- تثبيت tracks
- تثبيت surfaces
- تثبيت approvals
- تثبيت evidence
- تثبيت durable execution
- تثبيت trust enforcement

حينها يصبح Dealix فعلًا:

**منصة سيادة مؤسسية للنمو والتنفيذ، لا مجرد أداة AI محسّنة.**

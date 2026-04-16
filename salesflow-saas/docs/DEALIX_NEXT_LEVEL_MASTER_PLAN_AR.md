# Dealix — المخطط السيادي الشامل للتحول إلى Sovereign Enterprise Growth OS

> وثيقة مرجعية داخلية: تنقل Dealix من مستوى **Revenue & Operations OS** إلى مستوى **Sovereign Enterprise Growth OS**.  
> الهدف ليس زيادة عدد الوكلاء فقط، بل إغلاق القرار والتنفيذ والحوكمة والثقة داخل المنتج نفسه.  
> هذه الوثيقة تربط بين ما هو موجود اليوم في المستودع وبين البنية المستهدفة التي تجعل Dealix منصة مؤسسية صعبة الاستبدال.

---

## 1) إعادة تعريف الرؤية النهائية

**Dealix** لا ينبغي أن يتموضع بوصفه "أفضل CRM ذكي" فقط، بل بوصفه:

**Dealix Sovereign Enterprise Growth OS**

منصة سيادية تدير على قاعدة تشغيلية واحدة:
- المبيعات
- الشراكات
- Corporate Development / M&A
- التوسع
- PMI / PMO
- الحوكمة والاعتماد والتنفيذ

**القاعدة التشغيلية الأساسية:**
- الذكاء الاصطناعي يستكشف ويحلل ويقترح.
- الأنظمة تنفذ الالتزامات القابلة للتنفيذ.
- البشر يعتمدون القرارات الحرجة وغير القابلة للعكس.

**الفارق السوقي الحقيقي:**
- Arabic-first
- Saudi-ready
- policy-aware
- board-usable
- enterprise-saleable
- difficult to replace

---

## 2) أين الفجوة الحقيقية اليوم؟

الأساس الحالي قوي بالفعل: prompt دستوري، مكتبة حوكمة، execution matrices، architecture pack، تشغيل أسبوعي، وربط واضح بين current state وtarget architecture.

لكن الفجوة لم تعد "نقص أفكار"؛ بل أصبحت **نقص الإغلاق التشغيلي الكامل داخل المنتج**.

### ما ينقص الإغلاق الكامل:
- تحويل الذكاء من "اقتراحات" إلى **قرارات structured + evidence-backed**.
- فصل واضح بين **Decision Plane** و**Execution Plane**.
- جعل كل التزامات الأعمال الطويلة **durable + resumable + idempotent**.
- فرض trust plane مستقل لا يعتمد على منطق التطبيق فقط.
- جعل البيانات **contracted + observable + quality-gated**.
- جعل كل سطح تنفيذي مهم مرئياً داخل المنتج: approvals، evidence packs، risk boards، release gates، connector health.

---

## 3) النموذج السيادي المستهدف: خمس طبقات إلزامية

| الطبقة | الدور | ما يجب أن تحكمه | معيار النجاح |
|--------|------|-----------------|--------------|
| Decision Plane | التحليل والتوصية | signals, triage, scenarios, memos, forecasts, next best action | كل قرار حرج typed + evidence-backed + schema-bound |
| Execution Plane | الالتزامات والتنفيذ | approvals, launches, DD, signatures, PMI, orchestration | كل التزام طويل durable + resumable + compensatable |
| Trust Plane | الثقة والضبط | policy, authz, identity, secrets, audit, contradiction detection | لا يوجد فعل حساس بلا authorization + audit + verification |
| Data Plane | مصدر الحقيقة والذاكرة | ops data, semantic memory, contracts, data quality, telemetry | البيانات موحدة، قابلة للتتبع، ومحمية بعقود |
| Operating Plane | SDLC والإصدار | rulesets, release gates, attestations, evidence, environments | كل release مؤسسي يحمل provenance + protections + externalized audit |

---

## 4) Decision Plane

هذه الطبقة مسؤولة عن الذكاء والتحليل فقط، ويجب أن تحتوي على:
- signal detection
- triage
- scenario analysis
- memo generation
- forecasting
- recommendation
- next best action
- evidence pack assembly

### البنية الموصى بها
- `Responses API` للتعاملات stateful
- `Structured Outputs` لفرض الالتزام بـ JSON Schema
- `function calling / MCP` للتكامل المنضبط
- `LangGraph` للحلقات stateful وinterrupts وpause/resume
- tracing + guardrails على مستوى الوكلاء

### عقدة الخرج الإلزامية لكل recommendation
كل recommendation business-critical يجب أن تحمل:
- `decision_type`
- `recommendation`
- `evidence`
- `assumptions`
- `freshness`
- `confidence`
- `provenance`
- `policy_notes`
- `approval_class`
- `reversibility_class`
- `next_best_action`

### مبدأ مهم
هذه الطبقة **لا تنفذ الالتزامات الطويلة أو الحساسة مباشرة**. دورها: الاستكشاف، التحليل، التجميع، والتوصية.

---

## 5) Execution Plane

أي شيء:
- يمتد لأكثر من دقائق معدودة
- يعبر أكثر من نظام
- يحتاج retries / timeouts / compensation
- يخلق التزاماً خارجياً
- يحتاج approval أو resume later

يجب أن يخرج من agent logic ويدخل في workflow runtime حتمي.

### القاعدة المعمارية
- `LangGraph` = cognition + HITL + short/medium orchestration
- `Temporal` = durable business commitments

### أمثلة مسارات يجب أن تكون على Temporal
- approval routing
- DD room provisioning
- signature requests
- partner activation
- market launch readiness
- PMI 30/60/90 plans
- synergy realization tracking
- production promotion gates

### خصائص إلزامية لكل workflow حساس
- durable
- resumable
- idempotent
- compensatable
- observable
- correlation-id aware

---

## 6) Trust Plane

هذه الطبقة هي الفارق بين منتج "ذكي" ومنصة "شركات".

يجب أن تضم:
- policy engine
- approval routing
- fine-grained authorization
- secrets governance
- tool verification ledger
- evidence packs
- auditability
- contradiction detection
- AI governance controls

### المكونات المستهدفة
- `OPA` لقرارات السياسة
- `OpenFGA` للتفويض الدقيق relationship-based authorization
- `Vault` للأسرار والدوران والاعتماد قصير العمر
- `Keycloak` للهوية وSSO وidentity brokering

### عناصر الثقة الإلزامية لكل فعل حساس
- authorized actor
- policy evaluation result
- approval status
- tool call trace
- side-effect verification
- audit record
- contradiction status

### نموذج الحساسية المقترح
- `public`
- `internal`
- `confidential`
- `restricted`
- `highly_restricted`

---

## 7) Data Plane

هذه الطبقة يجب أن تكون منضبطة، لا قائمة على تكاملات فوضوية.

### المكونات المستهدفة
- `Postgres` = operational source of truth
- `pgvector` = semantic memory قرب بيانات التشغيل
- `Airbyte` = ingestion/connectors
- `Unstructured` = document extraction
- semantic metrics layer
- `Great Expectations` = data quality checkpoints
- `CloudEvents` + `JSON Schema` + `AsyncAPI` = event/data contracts
- `OpenTelemetry` = traces + metrics + logs

### قواعد البيانات والأحداث
- كل حدث مهم يحمل `event_type`, `tenant_id`, `correlation_id`, `schema_version`.
- كل تكامل يعلن contract version واضحاً.
- كل document ingestion يمر عبر extraction + validation + quality checks.
- كل metric تنفيذية يجب أن تكون قابلة للربط مع action وapproval وtenant.

### ما يجب منعه
- direct agent bindings إلى vendors بلا facade
- schemas غير منضبطة
- telemetry بلا correlation IDs
- syncs بلا freshness state واضح

---

## 8) Operating Plane

هذه هي طبقة GitHub + SDLC + releases + evidence.

يجب أن تضم:
- rulesets
- protected branches
- `CODEOWNERS`
- required status checks
- environments
- deployment protection rules
- OIDC federation
- artifact attestations
- external audit-log streaming

### الحد الأدنى المؤسسي المطلوب
- كل release يمر عبر environment محمي.
- لا توجد long-lived secrets في CI/CD عندما يمكن استخدام OIDC.
- كل artifact مهم يحمل provenance.
- كل production promotion حساس يحتاج reviewers أو rule-based approval.
- سجلات GitHub الحرجة تُصدّر إلى مخزن خارجي إذا كانت الحاجة audit-grade.

---

## 9) المسارات التجارية الستة الإلزامية

| المسار | ما يجب أن يديره | المخرجات المؤسسية المطلوبة |
|--------|------------------|-----------------------------|
| Revenue OS | capture, enrichment, scoring, routing, outreach, proposals, pricing governance, renewals | funnel control, approvals, forecast, contract handoff |
| Partnership OS | scouting, fit scoring, alliance recommendation, legal routing, activation, scorecards | partner room, contribution tracking, approval packs |
| M&A / CorpDev OS | sourcing, screening, DD orchestration, valuation, synergies, IC memos | DD room, board packs, offer readiness |
| Expansion OS | market scanning, readiness, localization, launch, stop-loss | launch console, actual vs forecast, compliance state |
| PMI / PMO OS | Day-1, 30/60/90, dependencies, escalation, synergy tracking | PMI engine, weekly exec review, risk register |
| Executive / Board OS | board memos, evidence packs, approvals, risk heatmaps, policy violations | executive room, approval center, evidence-native reporting |

---

## 10) الأسطح الحية الإلزامية داخل المنتج

إذا غاب واحد من هذه، فهناك جزء ناقص من النسخة المهيمنة:

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

## 11) سياسة الأتمتة: ما يُؤتمت وما لا يُؤتمت وحده

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
- data sharing عالي الحساسية
- production promotion
- capital commitments

### القاعدة الحاكمة
أي فعل حساس أو غير قابل للعكس يجب أن يمر عبر human-in-the-loop interrupts وapproval routing واضح.

---

## 12) Program Locks

هذه العناصر يجب أن تُقفل رسمياً داخل النظام، لا أن تبقى معرفة ضمنية فقط:

### أ) خمسة planes
- Decision
- Execution
- Trust
- Data
- Operating

### ب) ستة business tracks
- Revenue
- Partnerships
- CorpDev / M&A
- Expansion
- PMI / PMO
- Executive / Board

### ج) ثلاثة agent roles
- `Scout`: يجمع الإشارات والمواد الأولية
- `Analyst`: يحلل ويصدر memos وتوصيات
- `Operator`: يطلق workflows ولا ينجز commitments الحساسة إلا عبر policy + approval

### د) ثلاثة action classes
- `observe`
- `recommend`
- `commit`

### هـ) ثلاث approval classes
- `auto`
- `manager`
- `executive_or_board`

### و) أربع reversibility classes
- `fully_reversible`
- `compensatable`
- `time_bound_reversible`
- `irreversible`

### ز) الثلاثية الإلزامية لكل قرار
- provenance
- freshness
- confidence

---

## 13) Sovereign Routing Fabric

تحويل pool النماذج من مجرد fallback logic إلى policy-based routing:

- coding lane
- executive reasoning lane
- throughput drafting lane
- fallback lane

### المقاييس الإلزامية لكل lane
- latency
- schema adherence
- contradiction rate
- Arabic quality
- cost per successful task

### النتيجة المطلوبة
لا يكفي أن يكون النموذج "جيداً"؛ يجب أن يكون **مقاساً، قابلاً للتوجيه، ومربوطاً بسياسات المنتج**.

---

## 14) Connector Facade Standard

لا يجب أن ترتبط agents مباشرة بكل vendor.

كل connector يجب أن يمتلك:
- contract
- version
- retry policy
- timeout policy
- idempotency key
- approval policy
- audit mapping
- telemetry mapping
- rollback / compensation notes

### النتيجة
هذا يجعل Dealix قادراً على امتصاص تغيّر APIs وتبدّل الموردين دون كسر منطق الوكلاء أو فقدان التتبع.

---

## 15) Evidence-Native Operations

لا يكفي أن يخرج النظام memo فقط.

كل قرار كبير يجب أن يخرج معه:
- sources
- assumptions
- freshness
- financial model version
- policy notes
- alternatives
- rollback / compensation
- approval class
- reversibility class

### Contradiction Engine
يجب أن توجد لوحة تلتقط:
- intended action
- claimed action
- actual tool call
- side effects
- contradiction status

**السبب:** أكبر خطر في الأنظمة agentic هو أن "الوكيل قال إنه فعل" بينما التنفيذ الفعلي شيء آخر أو لم يحدث أصلاً.

---

## 16) خارطة إغلاق مرحلية

### المرحلة 0 — تثبيت القاعدة الحالية
- توحيد current state architecture داخل وثيقة واحدة مع target state واضح.
- ربط كل workflow حساس بـ owner + approval class + reversibility class.
- توحيد telemetry وcorrelation IDs في المسارات الحرجة.
- اعتماد connector facade standard.

### المرحلة 1 — إغلاق القرار والثقة
- فرض structured decision contracts.
- إطلاق Approval Center + Evidence Pack Viewer + Tool Verification Ledger.
- إدخال policy enforcement منفصل عن منطق التطبيق.
- تعريف sensitivity model وprovenance/freshness/confidence على مستوى القرار.

### المرحلة 2 — إغلاق التنفيذ المؤسسي
- نقل الالتزامات الطويلة إلى durable workflow runtime.
- إطلاق DD Room وPartner Room وRelease Gate Dashboard.
- فرض verification على side effects للأفعال الحساسة.
- تفعيل actual-vs-forecast وrisk heatmaps على مستوى الإدارة.

### المرحلة 3 — إغلاق التوسع المؤسسي
- Partnership OS + M&A / CorpDev OS + Expansion OS كأسطح تشغيل كاملة.
- mapping واضح على PDPL والمتطلبات السعودية والضوابط السيبرانية.
- توسيع readiness إلى board-ready and enterprise-saleable.

### المرحلة 4 — التفوق السوقي
- Arabic-first executive UX حقيقي.
- GTM مؤسسي قائم على evidence packs ودراسات حالة قابلة للتدقيق.
- شراكات نظامية، وربما استحواذات صغيرة أو تكاملات تعزز الفئة.

---

## 17) تعريف الجاهزية النهائية

لا يعتبر Dealix جاهزاً بصدق لخدمة الشركات إلا إذا أصبح:

- كل قرار business-critical structured + evidence-backed + schema-bound.
- كل long-running commitment durable + resumable + crash-tolerant.
- كل action حساس يحمل approval/reversibility/sensitivity metadata.
- كل connector versioned وله retry/idempotency/audit mapping.
- كل release يحمل rulesets + environments + OIDC + provenance.
- كل surface traceable عبر telemetry + correlation IDs.
- كل deployment مؤسسي يمر عبر security review وred-team لأسطح LLM/tool execution.
- كل workflow حساس في السعودية له mapping واضح على PDPL وAI governance والضوابط السيبرانية.

---

## 18) تعريف التمركز السوقي النهائي

النسخة الكبرى من Dealix ليست "أداة AI محسنة" ولا "CRM عربي" فحسب.

هي منصة:
- decision-native
- execution-durable
- trust-enforced
- data-governed
- Arabic-first
- Saudi-ready
- board-usable
- enterprise-saleable

وهذه هي الصيغة التي تجعل Dealix منصة سيادة مؤسسية فعلية.

---

## 19) خطوات فورية للتنفيذ داخل البرنامج

1. اعتماد **Program Locks** رسمياً داخل الوثائق والمنتج ولوحات التنفيذ.
2. تعريف **target sovereign architecture** كمرجع أعلى من current stack.
3. إطلاق backlog واضح للأسطح الإلزامية الناقصة، خصوصاً: Approval Center وEvidence Pack Viewer وTool Verification Ledger وRelease Gate Dashboard.
4. تصنيف كل workflows الحالية إلى: `observe` / `recommend` / `commit`.
5. تصنيف كل الأفعال الحساسة إلى approval classes وreversibility classes.
6. إنشاء matrix موحدة تربط: business track × plane × workflow × surface × owner.

---

*آخر تحديث: وثيقة حية — راجعها عند كل قفزة معمارية أو تحوّل منتجي كبير، لا كمذكرة تسويق فقط.*

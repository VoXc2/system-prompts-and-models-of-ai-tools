# Dealix Sovereign Enterprise Growth OS

**الحالة:** مرجع سيادي مستهدف للمنتج والمؤسسة
**النوع:** وثيقة تشغيلية/معمارية عليا
**التحديث:** يراجع مع `MASTER-BLUEPRINT.mdc` و`docs/ARCHITECTURE.md` و`docs/DEALIX_NEXT_LEVEL_MASTER_PLAN_AR.md`

---

## 1) الأطروحة النهائية

الهدف ليس أن يصبح **Dealix** "أفضل CRM ذكي" فقط، بل أن يصبح:

> **منصة سيادية مؤسسية للنمو** تدير القرار والتنفيذ والحوكمة والثقة على قاعدة واحدة:
> **الذكاء الاصطناعي يستكشف ويحلل ويقترح، الأنظمة تنفذ، والبشر يعتمدون القرارات الحرجة.**

بذلك ينتقل Dealix من Revenue OS قوي إلى **Sovereign Enterprise Growth OS** صالح للمبيعات، الشراكات، التطوير المؤسسي، التوسع، وPMI/PMO ضمن سياق عربي-سعودي ومؤسسي.

---

## 2) ما الذي نغلقه الآن؟

الفجوة الرئيسية ليست نقص أفكار أو طبقات مرجعية؛ بل **نقص الإغلاق التشغيلي الكامل داخل المنتج نفسه**.
لذلك تُستخدم هذه الوثيقة لقفل ما يلي داخل النظام:

- طبقات القرار والتنفيذ والثقة والبيانات والتشغيل.
- مسارات الأعمال الستة التي يجب أن تظهر حيًا داخل المنتج.
- حدود الأتمتة وما يحتاج اعتمادًا بشريًا إلزاميًا.
- نماذج الصلاحيات والسياسات والحساسية والقابلية للعكس.
- أسطح المنتج التنفيذية التي تجعل المنصة صالحة لمجلس الإدارة والمؤسسات.

---

## 3) النموذج السيادي المعتمد

### أ) القاعدة التشغيلية

- **Decision-native**: كل قرار مهم structured ومسنود بالأدلة.
- **Execution-durable**: كل التزام أعمال طويل الأمد durable وresumable.
- **Trust-enforced**: كل فعل حساس authorized وpolicy-evaluated وaudited.
- **Data-governed**: البيانات والعقود والأحداث قابلة للتتبع والتحقق.
- **Arabic-first / Saudi-ready**: اللغة، الامتثال، وسياق الأعمال المحلي جزء أصيل من التصميم.

### ب) مبدأ الفصل

- **الوكلاء** مسؤولون عن الاستكشاف، التحليل، التوصية، وتجميع الأدلة.
- **محركات التنفيذ الحتمية** مسؤولة عن الالتزامات طويلة الأمد ومتعددة الأنظمة.
- **البشر** يعتمدون الأفعال الحساسة وغير القابلة للعكس أو عالية الالتزام.

---

## 4) الطائرات الخمس السيادية (Five Sovereign Planes)

| الطائرة | الدور | ما يجب أن تحتويه | Target Architecture | ربط حالي في المستودع |
|---------|------|-------------------|---------------------|----------------------|
| **Decision Plane** | ذكاء القرار والتحليل | signal detection, triage, scenario analysis, memo generation, forecasting, recommendation, next best action, evidence pack assembly | Responses API + Structured Outputs + function calling/MCP + LangGraph للـ stateful loops وHITL | `docs/AGENT-MAP.md`, `backend/app/services/ai/`, `backend/app/ai/orchestrator.py` |
| **Execution Plane** | تنفيذ الالتزامات طويلة الأمد | approvals, launches, DD orchestration, signatures, PMI tracks, retries, compensation | LangGraph للإدراك والـ HITL قصير/متوسط الأمد، وTemporal أو runtime durable مماثل للالتزامات الحرجة | `backend/app/workers/`, `docs/ARCHITECTURE.md`, `docs/INTEGRATION_MASTER_AR.md` |
| **Trust Plane** | سياسات، تفويض، اعتماد، وأدلة | policy engine, approval routing, fine-grained authorization, secrets governance, verification ledger, contradiction detection, audit trails | OPA + OpenFGA + Vault + Keycloak + governance controls للـ AI | `AGENTS.md`, `docs/legal/`, `memory/security/pdpl-checklist.md` |
| **Data Plane** | مصدر الحقيقة والتعاقدات والقياسات | operational source of truth, semantic memory, ingestion, document extraction, data quality, event contracts, telemetry | Postgres + pgvector + Airbyte + Unstructured + Great Expectations + CloudEvents/JSON Schema/AsyncAPI + OpenTelemetry | `docs/DATA-MODEL.md`, `backend/app/services/knowledge_service.py` |
| **Operating Plane** | SDLC, releases, evidence, provenance | protected branches, rulesets, CODEOWNERS, deployment gates, environments, OIDC, attestations, external audit streaming | GitHub rulesets/environments + OIDC federation + artifact provenance + release evidence | `.github/`, `docs/LAUNCH_CHECKLIST.md`, `docs/DEPLOYMENT-NOTES.md` |

### قفل تشغيلي

أي شيء:

- يمتد لأكثر من دقائق قليلة،
- يمر عبر أكثر من نظام،
- يحتاج retry/timeout/compensation،
- يخلق التزامًا خارجيًا،
- أو يحتاج approval/resume لاحقًا،

**يجب أن يخرج من agent logic ويدخل في workflow runtime حتمي ومتين.**

---

## 5) مسارات الأعمال الستة (Business Tracks)

يجب أن يعمل المنتج كمنصة موحدة عبر ستة مسارات أعمال، لا كواجهة مبيعات فقط:

| المسار | القدرات الحية المطلوبة |
|--------|-------------------------|
| **Revenue OS** | capture, enrichment, qualification, scoring, routing, outreach, meeting orchestration, proposal generation, pricing governance, contract/onboarding/renewal handoff |
| **Partnership OS** | partner scouting, fit scoring, channel economics, alliance recommendation, term sheet draft, legal/approval routing, activation, scorecards, contribution margin tracking |
| **M&A / CorpDev OS** | target sourcing, screening, DD orchestration, DD room access control, valuation ranges, synergy modeling, IC memos, board packs, offer strategy, close readiness |
| **Expansion OS** | market scanning, prioritization, compliance readiness, localization, pricing/channel plans, launch readiness, stop-loss logic, post-launch actual vs forecast |
| **PMI / PMO OS** | Day-1 readiness, 30/60/90 plans, dependency tracking, owner assignment, escalation, synergy realization tracking, weekly executive review |
| **Executive / Board OS** | board-ready memos, evidence packs, approval center, risk heatmaps, actual vs forecast, next best action, policy violations, cross-track pipeline visibility |

---

## 6) Program Locks داخل النظام

يجب قفل العناصر التالية صراحة داخل المنتج والبيانات والواجهات:

- **5 planes**: decision / execution / trust / data / operating
- **6 business tracks**
- **3 agent roles**: analyst / operator / controller
- **3 action classes**: recommend / prepare / execute
- **3 approval classes على الأقل**: auto / manager / executive-board
- **4 reversibility classes**: reversible / compensatable / approval-before-commit / irreversible
- **sensitivity model**: public / internal / confidential / restricted / highly-sensitive
- **provenance / freshness / confidence trio**

### Metadata إلزامية لكل recommendation أو action

كل كيان قرار أو فعل business-critical يجب أن يحمل:

- `approval_class`
- `reversibility_class`
- `sensitivity_class`
- `policy_status`
- `provenance`
- `freshness_at`
- `confidence_score`
- `evidence_pack_id`
- `owner`
- `correlation_id`

---

## 7) حدود الأتمتة

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

- إرسال term sheet
- طلب التوقيع
- تفعيل شريك استراتيجي
- إطلاق سوق جديد
- تقديم عرض استحواذ
- أي discount خارج السياسة
- مشاركة بيانات عالية الحساسية
- promotion إلى production
- أي capital commitment

**القاعدة:** الأفعال الحساسة أو غير القابلة للعكس أو ذات الالتزام الخارجي لا تُنفذ تلقائيًا دون HITL واضح ومُسجل.

---

## 8) أسطح المنتج الإلزامية للنسخة المهيمنة

هذه ليست إضافات تجميلية؛ بل أسطح يجب أن تكون موجودة حيًا داخل المنتج:

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

إذا غاب واحد من هذه الأسطح، فهناك جزء ناقص من النسخة السيادية الكاملة.

---

## 9) Evidence-Native Operations

لا يكفي إخراج memo أو summary. كل قرار كبير يجب أن ينتج **evidence pack** يتضمن:

- المصادر
- الافتراضات
- درجة الحداثة freshness
- إصدار النموذج المالي
- ملاحظات السياسة
- البدائل
- rollback / compensation notes
- approval class
- reversibility class
- سجل التنفيذ الفعلي عند حدوثه

### محرك التناقضات (Contradiction Engine)

يجب أن ترصد المنصة الفرق بين:

- intended action
- claimed action
- actual tool call
- side effects
- contradiction status

بدون ذلك تبقى فجوة أساسية في الأنظمة الوكيلة: "الوكيل قال إنه نفذ".

---

## 10) Connector Facade Policy

لا يجب ربط الوكلاء مباشرة بكل vendor.
كل تكامل يجب أن يمر عبر **Connector Facade** يحتوي على:

- contract
- version
- retry policy
- timeout policy
- idempotency key
- approval policy
- audit mapping
- telemetry mapping
- rollback/compensation notes

هذا يحمي المنتج من تغيّر واجهات المزودين ويجعل السلوك auditable وقابلًا للترقية.

---

## 11) السيادة على الثقة والهوية والامتثال

### أ) Trust Plane target

- **OPA** لقرارات السياسات
- **OpenFGA** للتفويض الدقيق القائم على العلاقات
- **Vault** للأسرار قصيرة العمر والدوران والتدقيق
- **Keycloak** للهوية المؤسسية وSSO وidentity brokering

### ب) متطلبات الامتثال السعودي

المنصة يجب أن تكون:

- **PDPL-aware** في التصنيف، المعالجة، الاحتفاظ، وحقوق أصحاب البيانات
- **NCA/ECC-aligned** في الضوابط السيبرانية التشغيلية
- **NIST AI RMF-aware** في إدارة مخاطر الذكاء الاصطناعي
- **OWASP LLM-aware** ضد prompt injection وinsecure output handling وsensitive information disclosure

### ج) العربية والسعودية كتفوق تنافسي

العربية ليست طبقة ترجمة؛ بل جزء من التفوق، لذلك يجب أن تدخل في:

- classification
- memo generation
- board packs
- approval reasons
- notifications
- partner summaries
- search/retrieval
- executive UI
- terminology normalization

---

## 12) السيادة على البيانات والمراقبة

كل surface أو workflow حساس يجب أن يكون:

- traceable end-to-end
- مربوطًا بـ `correlation_id`
- قابلًا للقياس عبر traces/metrics/logs
- قابلًا للتدقيق على مستوى القرار والتنفيذ

### Target data discipline

- **Postgres** = operational source of truth
- **pgvector** = semantic memory قريب من بيانات التشغيل
- **JSON Schema** = عقود القرار والإخراج
- **CloudEvents / AsyncAPI** = عقود الأحداث
- **Great Expectations** = quality gates
- **OpenTelemetry** = traces + metrics + logs

---

## 13) السيادة على التشغيل والإصدار

يجب أن يضم Operating Plane على الأقل:

- rulesets
- protected branches
- CODEOWNERS
- required status checks
- environments
- deployment protection rules
- OIDC federation
- artifact attestations / provenance
- external audit log streaming

والهدف هو أن يكون كل release:

- policy-gated
- evidence-backed
- provenance-aware
- قابلًا للرجوع والتحقيق

---

## 14) تعريف الجاهزية النهائية

لا يعتبر Dealix جاهزًا بصدق لخدمة المؤسسات إلا إذا صار:

- كل قرار business-critical **structured + evidence-backed + schema-bound**
- كل long-running commitment **durable + resumable + crash-tolerant**
- كل action حساس يحمل **approval / reversibility / sensitivity metadata**
- كل connector **versioned** وله retry/idempotency/audit mapping
- كل release له **rulesets + environments + OIDC + provenance**
- كل surface traceable عبر **OpenTelemetry + correlation IDs**
- كل deployment مؤسسي يمر عبر **security review** و**red-team** لسطوح LLM/tool execution
- كل workflow حساس في السعودية له **mapping واضح** على PDPL/NCA/AI governance

---

## 15) الترجمة التنفيذية داخل المستودع

هذه الوثيقة تعمل كمرجع حاكم فوق المستندات التالية:

| المرجع | الدور |
|--------|------|
| `MASTER-BLUEPRINT.mdc` | النية المعمارية المختصرة ومصدر الحقيقة المرجعي |
| `docs/ARCHITECTURE.md` | المعمارية الحالية وتنفيذ الطبقات الأساسية |
| `docs/DEALIX_NEXT_LEVEL_MASTER_PLAN_AR.md` | التموضع السوقي، الفجوات، وخارطة الطريق التجارية |
| `docs/ULTIMATE_EXECUTION_MASTER_AR.md` | السرد التنفيذي المرحلي المتوافق مع المستودع |
| `docs/DATA-MODEL.md` | مصدر الحقيقة لطبقة البيانات الحالية |
| `docs/INTEGRATION_MASTER_AR.md` | بوابات التكامل والتفعيل |
| `memory/security/pdpl-checklist.md` | فحص الامتثال والضوابط |

### قاعدة القراءة الصحيحة

- إذا كان السؤال: "إلى ماذا نطمح؟" فابدأ من هذه الوثيقة.
- إذا كان السؤال: "ما الموجود الآن في الكود؟" فارجع إلى `docs/ARCHITECTURE.md` والكود.
- إذا كان السؤال: "كيف نبيع ونتموضع؟" فارجع إلى `docs/DEALIX_NEXT_LEVEL_MASTER_PLAN_AR.md`.
- إذا كان السؤال: "كيف نغلق التشغيل المؤسسي؟" فاجمع هذه الوثيقة مع `docs/ULTIMATE_EXECUTION_MASTER_AR.md`.

---

## 16) الخلاصة

النسخة الكبرى من Dealix لا تأتي من زيادة عدد الوكلاء فقط، بل من جعل المنصة كلها:

- **decision-native**
- **execution-durable**
- **trust-enforced**
- **data-governed**
- **Arabic-first**
- **Saudi-ready**
- **board-usable**
- **enterprise-saleable**

بهذه الصيغة يصبح Dealix فعلًا **منصة سيادة مؤسسية للنمو**، لا أداة AI محسّنة فقط.

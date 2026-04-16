# مصفوفة التنفيذ النهائية — Completion Program لإغلاق الجاهزية المؤسسية

**الحالة:** Operating execution matrix
**الهدف:** تحويل Dealix من مرجعية وثائقية قوية إلى طبقات قرار وتنفيذ وثقة وبيانات وتشغيل تعمل فعليًا، وتنتج evidence قابلًا للتدقيق، وتصلح للإطلاق المؤسسي في السعودية والخليج.
**مرجع الربط:** `MASTER-BLUEPRINT.mdc`، `docs/ULTIMATE_EXECUTION_MASTER_AR.md`، `AGENTS.md`، `docs/AGENT-MAP.md`، `memory/runbooks/saas-readiness-audit.md`.

---

## 1) هدف البرنامج

هذا البرنامج لا يضيف طبقة شعارات جديدة. وظيفته الوحيدة هي إغلاق الفجوة بين:

- **ما هو موثق ومعروف معماريًا**
- **ما هو قابل للتشغيل والقياس والتدقيق في الإنتاج**

النتيجة المطلوبة هي أن يصبح Dealix نظام تشغيل مؤسسيًا فعليًا، لا مجرد AI app بواجهات جيدة ووثائق قوية.

---

## 2) القفل التشغيلي الرسمي

### 2.1 حالة الطائرات الخمس: اليوم مقابل الهدف

| Plane | وضع اليوم | الهدف المقفل | بوابة النقل |
|------|-----------|--------------|-------------|
| Decision Plane | **Partial** — الوكلاء والخدمات يعيدون مخرجات منظمة في بعض المواضع، لكن القرار الحرج ليس schema-bound على مستوى المنصة كلها | Responses API + Structured Outputs + tools/MCP + LangGraph interrupts، مع مخرجات typed وقابلة للاستئناف والتدقيق | لا تمر أي توصية حرجة أو حزمة موافقة إلا عبر schema مع evidence |
| Execution Plane | **Partial** — Celery + خدمات backend + مسارات تشغيل قائمة، مع durable/runtime patterns متفاوتة | workflow inventory مصنف، ومعيار واضح لنقل المسارات طويلة العمر إلى runtime durable؛ **Temporal هو target** عند تحقق معايير النقل، مع إبقاء Celery/OpenClaw/LangGraph كطبقة حالية إلى أن يكتمل الانتقال | أول workflow أعمال حرج يعمل replay/recovery/idempotency/compensation |
| Trust Plane | **Partial** — عزل مستأجرين، طبقات موافقة، وسجلات أساسية موجودة، لكن policy/auth/tool verification ليست single source of truth بعد | OPA + OpenFGA + Vault + Keycloak + tool verification ledger + contradiction dashboard | كل action حساس يمر عبر policy/auth/evidence موحد |
| Data Plane | **Partial** — PostgreSQL و`KnowledgeService` و`pgvector` وذاكرة داخل التطبيق موجودة، لكن event/schema/quality discipline ما تزال غير موحدة بالكامل | operational truth موحد + semantic metrics + quality checks + connector/event contracts + lineage واضح | لا توجد integration حرجة أو dataset حرجة تعمل بدون contract واختبارات جودة |
| Operating Plane | **Partial** — CI وعمليات release موجودة، لكن rulesets/environments/OIDC/attestations/log streaming ليست كلها gates إلزامية بعد | Enterprise delivery fabric كامل: rulesets، CODEOWNERS، environments، approvals، OIDC، attestations، rollback discipline | لا يوجد promotion للإنتاج خارج release gates المثبتة |

### 2.2 المسارات الستة المعتمدة للأعمال

هذه المصفوفة تعتمد المسارات الستة الظاهرة في blueprint كسطح العمل الأساسي:

1. **Prospecting**
2. **Qualification**
3. **Proposal**
4. **Negotiation**
5. **Closing**
6. **Post-Sale / Support / Expansion**

أي capability جديد يجب أن يربط نفسه بأحد هذه المسارات قبل إضافته إلى البرنامج.

### 2.3 أدوار الوكلاء المعتمدة

| الدور | الوصف | القيد التشغيلي |
|------|-------|----------------|
| Observer | يرصد ويحلل ويكتشف الانحرافات | لا يوصي بإجراء تنفيذي دون evidence منظم |
| Recommender | ينتج memo/evidence/risk/approval packet | لا ينفذ action حساس أو غير عكوس |
| Executor | ينفذ action موثقًا ومصرحًا به | لا ينفذ إلا مع policy check + auth check + tool receipt |

### 2.4 ميتاداتا الأفعال الحساسة

كل فعل أو توصية تشغيلية حساسة يجب أن تحمل الحد الأدنى التالي:

| الحقل | السؤال الذي يجيب عنه |
|------|------------------------|
| Approval | من يوافق؟ وهل الموافقة إلزامية قبل التنفيذ؟ |
| Reversibility | هل يمكن التراجع؟ وما خطة التعويض؟ |
| Sensitivity | هل الفعل يمس بيانات شخصية، تعاقدًا، تسعيرًا، أو قنوات خارجية؟ |
| Provenance | ما مصدر القرار والأدلة والبيانات؟ |
| Freshness | ما حداثة الدليل والبيانات التي بُني عليها القرار؟ |

---

## 3) حواجز البرنامج غير القابلة للتفاوض

1. **Control / Trust قبل أي توسع إضافي في الوكلاء**
2. **Execution durability قبل أي Autonomy أوسع**
3. **Connector facades قبل أي tool calls إضافية**
4. **Semantic metrics قبل أي dashboards جديدة**
5. **Saudi governance قبل أي enterprise rollout**
6. **Executive room قبل أي external scaling**
7. **لا يوجد operational output حر free-text في المسارات الحرجة**
8. **لا يوجد claim جاهزية إنتاجية بلا evidence gate ناجح**

---

## 4) الحزم المنظمة الإلزامية لقرار الأعمال

كل business-critical recommendation يجب أن يكون قابلاً للتجميع في الحزم التالية:

- `memo_json`
- `evidence_pack_json`
- `risk_register_json`
- `approval_packet_json`
- `execution_intent_json`

هذه الحزم ليست تحسينًا شكليًا؛ بل هي contract القرار الرسمي بين Decision Plane وTrust Plane وExecution Plane.

---

## 5) مصفوفة التنفيذ النهائية

### WS1 — Productization & Architecture Closure

- **Workstream:** Productization & Architecture Closure
- **Deliverables:** current-vs-target architecture register، status dashboard لكل subsystem (`Current / Partial / Pilot / Production`)، قفل رسمي للطائرات الخمس، قفل رسمي للمسارات الستة، قفل رسمي لأدوار `Observer / Recommender / Executor`، وقائمة `action metadata` الإلزامية، وacceptance gates لكل subsystem.
- **Owner:** Chief Architect / Founder مع Platform Architecture Lead.
- **Evidence Gate:** ملف register معتمد داخل المستودع، وربط مباشر بالـ blueprint والوثائق التنفيذية، ومحضر مراجعة معماري دوري يوضح ما هو منفذ اليوم وما هو هدف لاحق.
- **Exit Criteria:** لا يبقى أي subsystem بلا owner أو status أو target state أو acceptance gate.
- **Dependencies:** `MASTER-BLUEPRINT.mdc`، `docs/ULTIMATE_EXECUTION_MASTER_AR.md`، `memory/architecture/module-map.md`، `AGENTS.md`.
- **Risk:** تضخم وثائقي جديد دون map تنفيذي مرتبط بالكود.
- **SLA:** تحديث register خلال دورة العمل نفسها عند أي قرار معماري أو تغيير حالة.

### WS2 — Decision Plane Hardening

- **Workstream:** Decision Plane Hardening
- **Deliverables:** catalog موحد للـ schemas، فرض Structured Outputs على المسارات الحرجة، compiler ثنائي اللغة لـ decision memos، مولد evidence packs، وحسابات `provenance_score` و`freshness_score` و`confidence_score`.
- **Owner:** AI Platform Lead.
- **Evidence Gate:** اختبارات schema validation ناجحة، وعينات حية من `memo_json` و`evidence_pack_json` و`approval_packet_json` على مسارات حرجة، ومنع أي recommendation حرجة إذا لم تكن schema-valid.
- **Exit Criteria:** 100% من التوصيات الحرجة والقرارات القابلة للتنفيذ تخرج typed، auditable، ومربوطة بمصدر الدليل.
- **Dependencies:** WS1، وخرائط الوكلاء الحالية، وسياسات الامتثال والمراجعة.
- **Risk:** بقاء free-text operational leakage داخل نقاط موافقة أو تنفيذ حساسة.
- **SLA:** أي كسر في schema أو evidence contract يعالج قبل الترقية التالية مباشرة.

### WS3 — Execution Plane Hardening

- **Workstream:** Execution Plane Hardening
- **Deliverables:** inventory لكل workflows، وتصنيفها إلى `short-lived local` و`medium-lived queued` و`long-lived durable`، ومعيار نقل رسمي: أي workflow يتجاوز 15 دقيقة أو يعبر أكثر من نظامين أو يحتاج compensation يدخل قائمة الترحيل، مع pilot durable workflow واحد، وسياسات `idempotency` و`compensation` و`workflow versioning`.
- **Owner:** Workflow Platform Lead.
- **Evidence Gate:** workflow catalog معتمد، وتشغيل pilot حقيقي مع replay/restart/recovery مثبت، وrunbook للنسخ والإرجاع ومعالجة الفشل.
- **Exit Criteria:** أول workflow أعمال حرج يعمل deterministic durable execution مع replay وتعويض وفصل واضح بين current runtime وtarget runtime.
- **Dependencies:** WS1، WS2، وواجهات التكامل الحساسة.
- **Risk:** تشتت الالتزامات التجارية طويلة العمر بين Celery/services/tool calls بلا guarantees كافية.
- **SLA:** incident triage لأي workflow حرج خلال نافذة تشغيل واحدة، ومعالجة حالات التعثر قبل الإطلاق اللاحق.

### WS4 — Trust Fabric Hardening

- **Workstream:** Trust Fabric Hardening
- **Deliverables:** policy inventory، OPA policy packs، نموذج OpenFGA أولي، خطة Vault للأسرار والتدقيق، خطة Keycloak للهوية وSSO والخدمات، `tool verification ledger v1`، وcontradiction dashboard.
- **Owner:** Security & IAM Lead.
- **Evidence Gate:** policy decision logs، اختبارات authorization model، سجلات وصول الأسرار، وtool receipts تربط `intended action` و`claimed action` و`actual execution` و`side effects` و`contradiction status`.
- **Exit Criteria:** كل فعل حساس يمر عبر policy decision وauthorization graph وverification ledger قبل اعتماده.
- **Dependencies:** WS1، WS2، WS3، وسياسات الامتثال السعودية.
- **Risk:** بقاء policy logic موزعًا بين prompts وconditionals وخدمات متفرقة.
- **SLA:** أي gap يمس auth/policy/tool verification يعالج كحاجز release، لا كتحسين لاحق.

### WS5 — Data & Connector Fabric

- **Workstream:** Data & Connector Fabric
- **Deliverables:** معيار connector facade، wrappers versioned لكل تكامل حرج، سياسات retry/timeout/idempotency، event envelope standard، schema registry discipline، semantic metrics dictionary، quality checks على datasets الحرجة، ووثائق lineage موحدة.
- **Owner:** Data Platform Lead مع Integrations Lead.
- **Evidence Gate:** اختبارات contract لكل connector، وأدلة على منع الوصول المباشر من الوكلاء إلى vendor APIs الحرجة، ونتائج quality checks وlineage على البيانات التشغيلية.
- **Exit Criteria:** لا توجد vendor integration حرجة بلا facade versioned، ولا dataset حرجة بلا quality gate وschema contract.
- **Dependencies:** WS1، WS4، ومستودعات البيانات والتكاملات الحالية.
- **Risk:** vendor API drift، وفوضى raw tool calls، وانهيار صامت بين الخدمات والبيانات.
- **SLA:** أي كسر contract أو drift في connector حرج يراجع ويثبت قبل أي توسع جديد فوقه.

### WS6 — Enterprise Delivery Fabric

- **Workstream:** Enterprise Delivery Fabric
- **Deliverables:** GitHub rulesets، `CODEOWNERS`، required checks، protected release branches، environments (`dev / staging / canary / prod`)، OIDC federation، artifact attestations، external audit log streaming، وسياسات canary/rollback promotion.
- **Owner:** DevSecOps / Platform Operations Lead.
- **Evidence Gate:** تفعيل rulesets فعليًا، وربط البيئات بموافقات وحمايات release، وإثبات provenance للـ artifacts، وrunbook rollback مجرب.
- **Exit Criteria:** لا يوجد deploy أو promotion إلى بيئة حساسة خارج release governance الرسمي.
- **Dependencies:** WS1، WS4، وخطوط CI/CD الحالية.
- **Risk:** اعتبار نجاح CI مساويًا للجاهزية المؤسسية للإطلاق.
- **SLA:** أي blocker في gates أو provenance أو rollback يعامل كـ release stop.

### WS7 — Saudi Enterprise Readiness

- **Workstream:** Saudi Enterprise Readiness
- **Deliverables:** PDPL data classification matrix، personal data processing register، residency/transfer control flags، NCA ECC readiness gaps register، مواءمة AI governance مع NIST AI RMF، وOWASP LLM controls checklist لكل release.
- **Owner:** Compliance Lead مع Security Lead.
- **Evidence Gate:** control matrix داخل المستودع، وchecklists release محدثة، وإثبات أن workflows الحساسة للسعودية تحمل residency/data handling flags واضحة وقابلة للإنفاذ.
- **Exit Criteria:** كل workflow سعودي حساس له control mapping تشغيلي، وليس مجرد بند وثائقي.
- **Dependencies:** WS1، WS4، WS5، ووثائق الامتثال الحالية.
- **Risk:** امتثال موثق لكنه غير operationalized داخل السياسات والأنظمة.
- **SLA:** أي gap يمتد إلى PDPL أو NCA أو LLM release controls يجب إغلاقه قبل الترقية الإنتاجية ذات الصلة.

### WS8 — Executive & Customer Readiness

- **Workstream:** Executive & Customer Readiness
- **Deliverables:** executive room حي، board-ready memo view، evidence pack view، approval center، policy violations board، partner scorecards، actual-vs-forecast، risk heatmaps، وdashboard لـ next-best-action.
- **Owner:** Product Operations Lead مع Revenue Operations Lead.
- **Evidence Gate:** walkthrough حي على staging يثبت أن الإدارة تستطيع قراءة القرار والدليل والانحراف والموافقة من واجهة تشغيلية واحدة، مع freshness checks للبيانات الرئيسية.
- **Exit Criteria:** يستطيع التنفيذيون وفرق التشغيل والعملاء المؤسسيون استهلاك النظام عبر طبقة تشغيل واضحة، لا عبر backend abstractions أو ملفات داخلية.
- **Dependencies:** WS2، WS3، WS4، WS5، WS6، WS7.
- **Risk:** بناء dashboards جميلة فوق بيانات غير موثوقة أو سياسات غير منفذة.
- **SLA:** أي data freshness breach أو policy visibility breach يظهر على لوحات التشغيل ويعالج ضمن دورة المراجعة التنفيذية التالية.

---

## 6) ترتيب التنفيذ المعتمد

الترتيب التنفيذي لهذا البرنامج يكون كالتالي:

1. **WS1 + WS4** لتثبيت authority وsingle source of truth.
2. **WS2** لربط القرار بالـ schema والدليل.
3. **WS3** لربط الالتزام التجاري بـ durable execution.
4. **WS5** لعزل الفوضى التكاملية وتثبيت العقود والقياسات.
5. **WS6 + WS7** لإغلاق release governance والجاهزية السعودية.
6. **WS8** فقط بعد اكتمال موثوقية القرار والتنفيذ والثقة والبيانات.

هذا الترتيب مقصود لمنع التوسع غير المنضبط، ولضمان أن كل توسع لاحق managed وليس chaotic.

---

## 7) Definition of Done المؤسسي

لا يعتبر Dealix جاهزًا للمؤسسات حتى يتحقق الحد الأدنى التالي:

- كل business-critical recommendation تخرج structured وevidence-backed.
- كل long-running commitment يمر عبر durable workflow محدد وقابل للاستعادة.
- كل action حساس يحمل `Approval / Reversibility / Sensitivity / Provenance / Freshness`.
- كل connector حرج versioned وله retry/idempotency/audit mapping.
- كل release حرج يمر عبر rulesets وapprovals وOIDC وprovenance gates.
- كل traceable surface يحمل telemetry وcorrelation identifiers قابلة للمراجعة.
- كل surface حساس للوكلاء والأدوات لديه security review وred-team coverage مناسب.
- كل workflow سعودي حساس يحمل PDPL/NCA-aware control mapping قابلًا للإنفاذ.

---

## 8) قرار البرنامج

**Decision:** Dealix يدخل الآن مرحلة **Completion Program**.
أي عمل جديد خارج هذه المصفوفة يجب أن يثبت أولًا أنه:

1. لا يفتح فجوة ثقة أو تنفيذ أو امتثال جديدة،
2. ولا يتجاوز ترتيب التنفيذ المعتمد،
3. ويحمل evidence gate واضحًا قبل ادعاء الجاهزية.

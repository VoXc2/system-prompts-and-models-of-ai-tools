# Dealix — مصفوفة التنفيذ النهائية لبرنامج الإكمال المؤسسي

**الحالة:** مرجع تنفيذي ملزم لبرنامج `Completion Program`  
**الغرض:** تحويل Dealix من مرجعية وثائقية قوية إلى قدرة تشغيلية مؤسسية قابلة للتدقيق والإطلاق  
**النطاق:** `Decision Fabric` + `Execution Fabric` + `Trust Fabric` + `Data Fabric` + `Enterprise Delivery Fabric`

---

## 1) قرارات القفل المعماري

### أ. الطائرات الخمس المعتمدة

1. **Decision Plane** — قرارات typed, schema-bound, auditable.
2. **Execution Plane** — workflows طويلة العمر durable وقابلة للاستئناف.
3. **Trust Plane** — policy, authorization, secrets, verification, evidence.
4. **Data Plane** — operational truth + semantic memory + governed connectors.
5. **Operating Plane** — release gates, promotion, provenance, rollback.

### ب. المسارات التجارية الستة التي لا يجوز كسرها

1. **Discover** — اكتشاف العملاء/الشركاء والفرص.
2. **Qualify** — التأهيل، التقييم، وتسجيل المخاطر.
3. **Propose** — المذكرة، العرض، والـ next-best-action.
4. **Approve** — الموافقات، السياسات، والتفويض.
5. **Commit** — التوقيع، التشغيل، والالتزامات بين الأنظمة.
6. **Expand** — الإطلاق، التوسع، الأداء، والحوكمة اللاحقة.

### ج. أدوار الوكلاء الرسمية

- **Observer** — يراقب ويصنف ويلخص فقط.
- **Recommender** — يقترح قرارًا structured مع evidence.
- **Executor** — ينفذ فعلًا مصرحًا به داخل policy gates.

### د. ميتاداتا الأفعال الحساسة الإلزامية

كل action حساس يجب أن يحمل الحقول التالية قبل السماح بالتنفيذ:

- `approval_class`
- `reversibility`
- `sensitivity`
- `provenance_score`
- `freshness_score`
- `confidence_score`
- `residency_flag`
- `correlation_id`

### هـ. سلم الحالة الرسمي لكل subsystem

- **Current** — موجود في المستودع أو البيئة الحالية.
- **Partial** — موجود جزئيًا لكن ليس production-grade.
- **Pilot** — مفعّل على مسار حي واحد مع evidence.
- **Production** — معتمد، مراقب، وله gates واضحة.

---

## 2) سجل current-vs-target المختصر

| المجال | الحالة الحالية المرجحة | الحالة المستهدفة | الفجوة التي يجب إغلاقها |
|--------|-------------------------|------------------|--------------------------|
| Agent outputs | Partial | Production | تحويل كل المخرجات الحرجة إلى structured outputs مع schemas صارمة |
| Long-running workflows | Partial | Pilot ثم Production | نقل الالتزامات متعددة الأنظمة من Celery-only إلى durable workflows |
| Policy + auth source of truth | Partial | Pilot | إخراج policy من الـ prompts والشرطيات المتناثرة إلى طبقة موحدة |
| Tool verification | Partial | Production | جعل evidence والـ contradiction status إلزاميين لا اختياريين |
| Connector governance | Current/Partial | Production | منع الاستدعاءات الخام لمزودي الخدمات من داخل الوكلاء |
| Telemetry + evals | Partial | Production | جعل traces/evals/red-team جزءًا من release gates |
| Enterprise delivery controls | Partial | Production | rulesets, OIDC, attestations, environments, rollback drills |
| Saudi enterprise controls | Current/Partial | Production | تحويل PDPL/NCA/NIST/OWASP من وثائق إلى enforcement runtime |

---

## 3) Execution Matrix النهائية

| Workstream | Deliverables | Owner | Evidence Gate | Exit Criteria | Dependencies | Risk | SLA |
|------------|--------------|-------|---------------|---------------|--------------|------|-----|
| **WS1 — Productization & Architecture Closure** | `current-vs-target architecture register`<br>`subsystem status dashboard`<br>`5-plane map`<br>`6-track map`<br>`agent role matrix`<br>`action metadata contract` | Architecture Lead + Product Ops | ADR مراجَع ومقبول<br>لوحة الحالة منشورة ومربوطة بالوثائق<br>weekly review موقّع | لا يوجد subsystem أو Tier-1 flow بدون owner + status + target + dependency chain | الحزمة المرجعية الحالية، `docs/ARCHITECTURE.md`، `memory/architecture/*` | اختلاف التفسير بين الفرق أو drift بين الوثائق والتنفيذ | تحديث السجل خلال `<= 5` أيام عمل من أي قرار معماري مؤثر<br>مراجعة حوكمة أسبوعية ثابتة |
| **WS2 — Decision Plane Hardening** | مكتبة schemas موحدة: `memo_json`, `evidence_pack_json`, `risk_register_json`, `approval_packet_json`, `execution_intent_json`<br>اعتماد Structured Outputs mandatory<br>decision memo compiler ثنائي اللغة<br>provenance/freshness/confidence scoring | AI Platform Lead + Applied AI | نجاح schema validation على المسارات الحرجة<br>golden eval set منشور<br>demo لمخرجات typed end-to-end | `100%` من التوصيات الحرجة schema-bound وقابلة للتدقيق<br>لا يوجد free-text operational output في المسارات الحساسة | WS1، inventory لخدمات الذكاء، contract الحقول الحساسة | drift بين prompts وschemas والواجهة الأمامية | أي schema breaking change يتطلب version bump<br>alert عند validation failure خلال `<= 15` دقيقة |
| **WS3 — Execution Plane Hardening** | inventory كامل للـ workflows<br>تصنيف `short-lived / medium-lived / long-lived durable`<br>Temporal pilot لمسار approval أو deal room<br>idempotency keys<br>compensation policy<br>workflow versioning strategy | Workflow Platform Lead + Backend Lead | crash/restart replay demo ناجح<br>runbook للـ recovery<br>trace يثبت resume بلا فقدان state | كل workflow يتجاوز `15` دقيقة أو يعبر `2+` نظام أو يحتاج compensation مصنف رسميًا<br>pilot durable workflow جاهز للترقية | WS1، WS2، قدرة البنية التحتية، action metadata | split-brain بين Celery وTemporal أو تكرار التنفيذ | triage لأي stuck workflow خلال `<= 30` دقيقة<br>اختبار recovery في كل release |
| **WS4 — Trust Fabric Hardening** | policy inventory<br>OPA policy packs<br>OpenFGA model draft + enforcement hooks<br>Vault integration plan<br>Keycloak SSO/service identity plan<br>tool verification ledger v1<br>contradiction dashboard | Security/IAM Lead + Platform Security | policy decision logs موجودة<br>authorization tests ناجحة<br>tool receipts مع verdicts معروضة<br>break-glass review موثق | كل action حساس يمر عبر policy decision + auth graph + evidence receipt | WS1، WS3، auth boundaries الحالية، security review | policy logic يبقى مبعثرًا داخل الكود أو الـ prompts | anomaly حرجة في allow/deny تُراجع خلال `<= 1` ساعة<br>تحديثات policy same business day |
| **WS5 — Data & Connector Fabric** | truth map لـ Postgres/pgvector<br>connector facade standard<br>versioned wrappers لكل connector حرج<br>retry/timeout/idempotency policy<br>event envelope standard<br>schema registry discipline<br>semantic metrics dictionary<br>Great Expectations checks للبيانات الحرجة | Data Platform Lead + Integration Lead | connector contract tests ناجحة<br>data quality report منشور<br>event samples مع metadata موحدة | لا يوجد connector حرج يُستدعى مباشرة من agent code<br>كل dataset حرج له owner + contract + quality checks | WS2، WS3، WS4، واجهات المزودين الحالية | vendor API drift أو silent data regressions | failed ingestion critical alert خلال `<= 15` دقيقة<br>تعديل contract حرج خلال `<= 1` يوم عمل |
| **WS6 — Enterprise Delivery Fabric** | GitHub rulesets<br>`CODEOWNERS`<br>protected release branches<br>environments: `dev/staging/canary/prod`<br>required checks + approvals<br>OIDC federation<br>artifact attestations<br>rollback/canary runbooks<br>external audit log streaming | DevOps Lead + Release Manager | release drill ناجح<br>attestation موقعة على build candidate<br>demo لبوابات environment protection<br>rollback proof محفوظ | لا يوجد production promotion خارج gated workflow<br>provenance مرتبطة بكل artifact حرج<br>سجلات التدقيق تُصدَّر خارج GitHub | WS4، CI inventory، حسابات السحابة، متطلبات المؤسسة | نقص بعض ميزات private repos أو ضعف retention المحلي للسجلات | release gate failure يُعالج خلال `<= 15` دقيقة<br>قرار rollback خلال `<= 30` دقيقة |
| **WS7 — Saudi Enterprise Readiness** | PDPL data classification matrix<br>personal data processing register<br>residency/transfer flags داخل policy engine<br>NCA ECC gaps register<br>NIST AI RMF mapping<br>OWASP LLM controls checklist per release | GRC Lead + Security Lead + Data Protection Owner | control matrix مراجَعة<br>policy evaluation demo لعلامات residency<br>release sign-off compliance | كل workflow سعودي حساس mapped إلى PDPL/NCA controls ويظهر في policy decisions وrelease gates | WS4، WS5، legal/compliance input، data inventory | وجود وثائق امتثال بلا enforcement runtime | تحديث سجل الامتثال خلال `<= 5` أيام عمل من أي تغيير مؤثر<br>checklist إلزامية لكل release |
| **WS8 — Executive & Customer Readiness** | executive room حي<br>board-ready memo view<br>evidence pack view<br>approval center<br>policy violations board<br>partner scorecards<br>actual vs forecast<br>risk heatmaps<br>next-best-action dashboard | Product Lead + Executive UX + Analytics Lead | walkthrough حي على staging ببيانات trace حقيقية<br>مذكرة تنفيذية قابلة للتصدير<br>review أسبوعي مبني على evidence | الإدارة ترى recommendation + approval + evidence + forecast من سطح واحد موثوق | WS2، WS3، WS4، WS5، semantic metrics | لوحات جميلة لكن غير موثوقة أو غير مرتبطة بـ lineage | تحديث المقاييس التنفيذية يوميًا قبل `09:00 Asia/Riyadh`<br>triage لأي discrepancy حرجة خلال `<= 4` ساعات |

---

## 4) التسلسل التنفيذي الموصى به أسبوعًا بأسبوع

| الأسبوع | المخرج المطلوب | Workstreams |
|---------|----------------|-------------|
| 1 | قفل التعاريف الرسمية: planes, tracks, roles, metadata, status scale | WS1 |
| 2 | نشر `current-vs-target register` ولوحة الحالة وربطها بمراجعة أسبوعية | WS1 |
| 3 | إصدار schemas v1 + مكتبة decision outputs + منع free-text في المسارات الحرجة | WS2 |
| 4 | تشغيل evidence pack generator + golden eval set + scoring fields | WS2 |
| 5 | inventory كامل للـ workflows + تصنيف durable candidates + bootstrap لـ Temporal pilot | WS3 |
| 6 | idempotency/compensation/versioning policy + أول replay demo | WS3 |
| 7 | policy inventory + OPA packs draft + OpenFGA model draft + tool ledger v1 | WS4 |
| 8 | connector facade standard + event envelope + quality checks + semantic metrics v1 | WS5 |
| 9 | rulesets + environments + OIDC + attestation + rollback drill | WS6 |
| 10 | residency flags + PDPL/NCA control mapping + OWASP/NIST release checklist | WS7 |
| 11 | executive room shell + approval center + evidence pack view + violations board | WS8 |
| 12 | enterprise readiness review: ترقية الحالات من `Partial` إلى `Pilot/Production` فقط عند تحقق evidence gates | WS1-WS8 |

---

## 5) أولويات التنفيذ غير القابلة للتفاوض

1. **Control/Trust before more agents**
2. **Execution before more autonomy**
3. **Connector facades before more tool calls**
4. **Semantic metrics before more dashboards**
5. **Saudi governance before enterprise rollout**
6. **Executive room before external scaling**

---

## 6) Definition of Done الحقيقي

لا يُعتبر Dealix جاهزًا للمؤسسات إلا إذا تحقق التالي:

- كل business-critical recommendation تخرج structured وevidence-backed.
- كل long-running commitment يمر عبر deterministic durable workflow.
- كل action حساس يحمل metadata كاملة للموافقة والعكسية والحساسية والمصدر والحداثة.
- كل connector حرج versioned وله retry/idempotency/audit mapping.
- كل release له rulesets + approvals + OIDC + provenance + rollback proof.
- كل surface حرج لديه OTel telemetry و`correlation_id`.
- كل release مؤسسي له red-team/review coverage لأسطح LLM والتطبيق.
- كل workflow سعودي حساس mapped إلى PDPL/NCA-aware controls قابلة للتنفيذ.

---

## 7) مراجع الربط داخل المستودع

- `docs/ULTIMATE_EXECUTION_MASTER_AR.md`
- `docs/ARCHITECTURE.md`
- `docs/AGENT-MAP.md`
- `docs/LAUNCH_CHECKLIST.md`
- `memory/architecture/transformation-master-prompt.md`
- `memory/architecture/dealix-prd-v2.md`

---

*هذه الوثيقة تحول الرؤية المرجعية إلى برنامج تنفيذ قابل للقياس والمراجعة الأسبوعية، ولا تعتبر أي بند "مكتملًا" بدون evidence gate واضح وexit criteria قابلة للتدقيق.*

# وثيقة التنفيذ الشاملة — نظام تشغيل الإيرادات والعمليات الذاتي 2026

**الإصدار:** Legendary Complete Edition v4.0 (متوافق مع المستودع)  
**الحالة:** مرجع استراتيجي وتنفيذي — يُحدَّث مع `MASTER-BLUEPRINT.mdc` والكود.

---

## الرؤية

> ليس مجرد أداة، بل **شركة مبيعات رقمية مؤتمتة بالذكاء الاصطناعي** تعمل على مدار الساعة، تتطور ذاتياً، وتولد قيمة وإيرادات قابلة للقياس من اليوم الأول.

**Dealix** = Revenue & Operations OS: من الاكتشاف والتأهيل إلى العرض والتفاوض والإغلاق وما بعد البيع والدعم والفوترة والتحليلات — مع **حوكمة** و**عزل متعدد المستأجرين** و**قنوات محلية** (واتساب أولاً، عربي، SAR، سياق امتثال سعودي).

---

## مقاييس مستهدفة (قابلة للتدقيق)

| المحور | هدف توجيهي | ملاحظة |
|--------|-------------|--------|
| النمو | +3–5× إيرادات سنوية | يُقاس لكل عميل وخط أساس |
| الكفاءة | −70–80% عمل يدوي في مسار المبيعات | عبر أتمتة وسير عمل |
| التنبؤ | دقة أعلى في أفق 30 يوماً | نماذج + بيانات نظيفة |
| دورة الصفقة | −40% زمن إغلاق نسبي للخط الأساسي | قياس قبل/بعد |
| الاكتساب | −31% تكلفة اكتساب عبر أتمتة | عند توفر القنوات |
| الامتثال | PDPL + ممارسات SOC2-ready | سياسات، سجلات، موافقات |
| التوسع | تعدد مناطق/قطاعات على مدى 18–36 شهراً | خارطة طريق مرحلية |

---

## مبادئ التصميم (ستة)

1. **القيمة أولاً** — كل ميزة تُربط بمؤشر عميل أو تشغيلي.
2. **الامتثال بالتصميم** — موافقات، تسجيل قرارات، حدود بيانات.
3. **تطور ذاتي** — حلقة تحسين ذاتي (مراحل واضحة في OpenClaw + تدفقات الخلفية).
4. **تعقيد مخفي وبساطة ظاهرة** — واجهة بسيطة، منطق معقد منظم في طبقات.
5. **قابلية القياس** — لوحات، ROI تنفيذي، تكاليف نماذج لكل مستأجر حيث ينطبق.
6. **أمان بلا ثقة مطلقة** — عزل مستأجرين، حدود وكلاء، مراجعة قبل الإرسال الحساس.

---

## المعرفة والـ RAG (سياسة المنتج)

- **المصدر المعتمد:** PostgreSQL + **pgvector**، `KnowledgeService`، أصول القطاعات، وسياق الـ orchestrator.
- **غير معتمد:** Onyx وأي RAG خارجي كبديل أساسي — لتقليل الاعتماديات والتكلفة غير المنضبطة وضمان البيانات داخل نطاقك.

---

## التمييز التنافسي (ملخص)

- **OpenClaw 2026.4.2:** تدفقات مهام دائمة + تتبع مراجع (حسب التكوين في `openclaw/openclaw-config.yaml`).
- **حلقة تحسين ذاتي:** مراحل جمع إشارات → تشخيص → تجارب → حوكمة → ترقية/تراجع.
- **سعودي أولاً:** قنوات، لغة، فوترة/سياق زاتكا ضمن المسار حسب المنتج.
- **تكاملات:** Salesforce path، واتساب، Stripe، صوت، عقود/توقيع — عبر خدمات الـ backend والـ plugins المسموحة.

---

## خارطة طريق مرحلية (0–36 شهراً)

| المرحلة | الأفق | التركيز |
|---------|--------|---------|
| 0 — الأساس | 0–90 يوماً | إنتاجية، صحة API، pilot، تسويق موحّد |
| 1 — MVP مدفوع | شهر 2–3 | تأهيل أعمق، عروض، ROI أساسي، امتثال تشغيلي |
| 2 — التوسع | شهر 4–9 | multi-tenant أعمق، صوت، تنبؤ إيرادات، بوابة API |
| 3 — القيادة | شهر 10–36 | مناطق، شراكات، قطاعات عمودية |

---

## ربط بالمستودع

| المسار | الغرض |
|--------|--------|
| `MASTER-BLUEPRINT.mdc` | مصدر حقيقة معماري إنجليزي مختصر |
| `openclaw/openclaw-config.yaml` | تكوين OpenClaw + تدفقات + حدود |
| `backend/app/api/v1/autonomous_foundation.py` | تدفقات ذاتية، بوابة go-live |
| `backend/app/services/knowledge_service.py` | RAG داخل التطبيق |
| `backend/app/ai/orchestrator.py` | تنسيق وكلاء + سياق معرفة |
| `frontend/src/app/strategy/page.tsx` | صفحة استراتيجية عامة |

---

## برنامج الإكمال التشغيلي (Completion Program)

هذا القسم يحوّل الوثيقة من سرد استراتيجي إلى **مرجع تنفيذ مؤسسي**. أي مسار لا يملك **Owner** واضحاً و**Evidence Gate** و**Exit Criteria** لا يدخل خطة التنفيذ.

### 1) القفل المعماري التشغيلي

#### 1.1 الطائرات الخمس (5 Planes)

| Plane | ما هو منفذ اليوم | الهدف المعماري المقفل | حالة الترقية |
|-------|-------------------|------------------------|--------------|
| **Decision Plane** | orchestrator + routing + structured outputs متفرقة + registry للوكلاء | `Responses API` + `Structured Outputs` + `tools/MCP` + `LangGraph` interrupts/resume بحيث يصبح كل قرار typed, auditable, resumable | Partial |
| **Execution Plane** | `OpenClaw` + `Celery` + autonomous flows + go-live gate | durable workflow runtime للالتزامات طويلة العمر مع `Temporal` كهدف معماري، والإبقاء على `Celery/LangGraph` للقصير فقط | Partial |
| **Trust Plane** | موافقات، PDPL، tool receipts/verification patterns، وسجلات تدقيق تشغيلية | `OPA` للسياسات، `OpenFGA` للتفويض، `Vault` للأسرار والتدقيق، `Keycloak` للهوية، وledger إلزامي للتحقق من الأدوات | Partial |
| **Data Plane** | `PostgreSQL` + `pgvector` + `KnowledgeService` + sector assets | طبقة بيانات منظمة بعقود schemas/connectors/events + quality + lineage + semantic metrics | Partial |
| **Operating Plane** | GitHub Actions، runbooks، readiness APIs، وبوابة go-live | rulesets + protected branches/environments + `OIDC` + attestations + canary/rollback + external audit streaming | Partial |

#### 1.2 المسارات الستة المقفلة للأعمال

هذه الوثيقة تثبّت المسارات التشغيلية الأساسية التالية، وهي المعيار لأي agent surface أو workflow جديد:

1. **Prospecting** — اكتشاف الفرص والجهات.
2. **Qualification** — التأهيل والتقييم والملاءمة.
3. **Proposal** — بناء العرض، النطاق، والتسعير.
4. **Negotiation** — التفاوض، التنازلات، والاعتمادات.
5. **Closing** — الإقفال، التوقيع، والالتزامات.
6. **Post-Sale / Support** — التفعيل، المتابعة، الدعم، والتوسعة.

> التسويق، الفوترة، والتحليلات تبقى قدرات عرضية مشتركة عبر المسارات وليست بديلاً عنها.

#### 1.3 أدوار الوكلاء المقفلة

| الدور | ما الذي يفعله | ما الذي لا يحق له فعله |
|------|----------------|-------------------------|
| **Observer** | يقرأ، يلخّص، يصنّف، ويقيس دون side effects | لا يرسل، لا يلتزم، لا يغيّر حالة خارجية |
| **Recommender** | ينتج memo/risk/approval packets ويوصي بالفعل التالي | لا ينفذ أدوات حساسة ولا يلتزم خارجياً |
| **Executor** | ينفذ عبر tools/workflows مع موافقات وسياسات وتحقق | لا يعمل خارج policy engine أو بدون evidence/verdict |

#### 1.4 بيانات الفعل الإلزامية (Action Metadata)

| الحقل | المطلوب |
|------|----------|
| `approval_class` | التصنيف الإلزامي للفعل: `A/B/C` أو السلم التفصيلي `read_only -> draft -> send -> negotiate -> commit` |
| `reversibility` | هل الفعل `reversible` أو `compensatable` أو `irreversible` |
| `sensitivity` | مستوى الحساسية: `internal`, `confidential`, `regulated`, `high_risk` |
| `provenance` | مصدر القرار/البيانات/الأداة/المشغل وروابط الأدلة |
| `freshness` | وقت الرصد، الحد الأقصى للعمر، ووسم stale عند الحاجة |

#### 1.5 مخرجات القرار المقفلة (Typed Decision Outputs)

كل recommendation أو approval أو execution handoff في المسارات الحرجة يجب أن يخرج على شكل:

- `memo_json`
- `evidence_pack_json`
- `risk_register_json`
- `approval_packet_json`
- `execution_intent_json`

### 2) سجل الفجوات من اليوم إلى الجاهزية المؤسسية

| الفجوة | ما هو قائم اليوم | ما يجب إقفاله قبل اعتبار Dealix enterprise-grade |
|-------|-------------------|----------------------------------------------------|
| الوثائق أقوى من التنفيذ | blueprint قوي + readiness runbooks + prompts/PRD | current-vs-target implementation map + subsystem status dashboard + promotion gates |
| القرار غير typed بما يكفي | outputs structured في أجزاء متفرقة | schema-bound outputs إلزامية في جميع التدفقات الحرجة |
| التنفيذ طويل العمر غير durable بعد | `Celery/OpenClaw` يغطيان جزءاً مهماً من التنفيذ | أي التزام طويل أو متعدد الأنظمة يمر عبر durable workflow واضح |
| policy/auth ليست single source of truth | approvals وchecks موزعة بين docs/services | `OPA/OpenFGA` كمحركي قرار وتفويض، والتطبيق مجرد enforcement hooks |
| verification ليس mandatory evidence بعد | patterns للتحقق موجودة لكن ليست gate شامل | intended vs claimed vs actual vs side effects vs contradiction status لكل فعل |
| connectors غير مغلفة بالكامل | تكاملات فعالة لكن بدرجات مختلفة من التنظيم | connector facades versioned بعقود داخلية مستقرة |
| observability/evals ليست release gate | monitoring/readiness موجودان جزئياً | `OTel` + correlation IDs + offline/online evals + red-team surfaces لكل release |
| الجاهزية السعودية موثقة أكثر من كونها enforceable | PDPL وsecurity docs موجودة | policy-backed residency/transfer/classification controls + ECC/NIST/OWASP mapping تشغيلي |

### 3) ترتيب التنفيذ الملزم

1. **Control / Trust قبل المزيد من الوكلاء**
2. **Execution قبل المزيد من الاستقلالية**
3. **Connector facades قبل المزيد من tool calls**
4. **Semantic metrics قبل المزيد من dashboards**
5. **Saudi governance قبل أي rollout مؤسسي واسع**
6. **Executive room بعد ربط القرار والتنفيذ والثقة ببيانات حقيقية**

### 4) Execution Matrix النهائية لبرنامج الإكمال

| Workstream | Deliverables | Owner | Evidence Gate | Exit Criteria | Dependencies | Risk | SLA |
|------------|--------------|-------|---------------|---------------|--------------|------|-----|
| **1. Productization & Architecture Closure** | current-vs-target architecture register؛ implementation map على مستوى الكود؛ dashboard بحالات `Current/Partial/Pilot/Production`؛ قفل planes/tracks/roles/action metadata | Architecture + Product | register معتمد، ADR delta log، ولوحة حالة منشورة | لا يوجد subsystem حرج بلا owner أو promotion gate أو مرجع كود | `MASTER-BLUEPRINT.mdc`، PRD، readiness audit، agent map | drift بين الوثائق والتنفيذ أو غموض الملكية | أي drift معماري بين الكود والوثائق يُصحَّح أو يُسجَّل خلال يوم عمل واحد |
| **2. Decision Plane Hardening** | schemas موحدة لـ `memo_json/evidence_pack_json/risk_register_json/approval_packet_json/execution_intent_json`؛ Structured Outputs mandatory؛ bilingual memo compiler؛ provenance/freshness/confidence scoring؛ HITL interrupts | AI Platform + Applied AI | schema registry، golden examples، traces لقرارات typed، ومنع free-text في المسارات الحرجة | كل recommendation حرجة تصبح schema-bound + evidence-backed + resumable | Workstream 1، model routing، approval classes | schema churn أو prompt drift | أي schema-breaking change يُراجع خلال 24 ساعة عمل قبل الترقية |
| **3. Execution Plane Hardening** | inventory كامل للـ workflows؛ تصنيف `short-lived / queued / durable`؛ pilot durable workflow؛ compensation policy؛ idempotency keys؛ workflow versioning strategy | Workflow Platform + Backend | demo لتعافي workflow بعد failure/restart، اختبارات compensation، وسجل execution receipts | كل workflow يتجاوز 15 دقيقة أو يعبر نظامين أو يحتاج compensation يُصنّف ويُربط بمسار durable أو backlog نقل رسمي | Workstreams 1-2، connector contracts | تعقيد dual runtime أو عدم اكتمال التعويضات | أي P1 workflow failure يُفرز خلال يوم عمل، ولا تتم الترقية قبل إثبات recovery path |
| **4. Trust Fabric Hardening** | policy inventory؛ `OPA` policy packs؛ draft لـ `OpenFGA` model؛ خطة `Vault` و`Keycloak`؛ tool verification ledger v1؛ contradiction dashboard | Security Platform + GRC | policy decision logs، auth graph checks، receipts تحمل verdict واضح | كل فعل حساس يمر عبر policy + authorization + verification، ولا يبقى منطق حساس حبيس prompts أو conditionals متناثرة | Workstreams 1-3 | بقاء policy logic داخل التطبيق أو الـ prompts | أي تغيير policy يخضع لمراجعة regression في نفس يوم العمل |
| **5. Data & Connector Fabric** | connector facade standard؛ versioning لكل connector؛ retry/timeout/idempotency policies؛ event envelope standard؛ schema discipline؛ semantic metrics dictionary؛ quality checks للبيانات الحرجة | Data Platform + Integrations | contract tests، نماذج event envelopes، quality reports، وownership واضح للبيانات | لا يوجد critical vendor call مباشر خارج facade، وكل dataset حرج يملك owner وDQ gate | Workstreams 1، 3، 4 | تغيّر vendor APIs أو انكسار صامت في schemas | أي تغيير vendor أو schema حرج يُقيَّم خلال يومي عمل |
| **6. Enterprise Delivery Fabric** | GitHub rulesets؛ `CODEOWNERS`؛ required checks؛ protected release branches؛ environments؛ `OIDC` federation؛ artifact attestations؛ canary/rollback runbook؛ audit streaming خارجي | Platform / DevOps / Security | promotion logs، provenance attestations، rollback drill، وaudit events في sink خارجي | لا يوجد release production بدون checks + approvals + provenance + rollback path مجرّب | Workstreams 1 و4 | bypass للـ release gates تحت ضغط التنفيذ | أي كسر في release gate يُعالج في نفس يوم العمل، وقرار rollback خلال 30 دقيقة من breach مثبت |
| **7. Saudi Enterprise Readiness** | PDPL classification matrix؛ personal data processing register؛ residency/transfer control flags؛ NCA ECC gaps register؛ NIST AI RMF profile؛ OWASP LLM checklist لكل release | GRC + Security + Product Counsel | control matrix، policy mappings، وrelease sign-off للمسارات الحساسة | كل Saudi-sensitive workflow يملك control mapping enforceable داخل policy engine لا داخل docs فقط | Workstreams 1، 4، 5، 6 | بقاء الامتثال في مستوى الوثيقة لا التشغيل | أي تحديث تنظيمي ينعكس على checklist وسياسات الإصدار قبل الترقية التالية |
| **8. Executive & Customer Readiness** | executive room حي؛ board memo view؛ evidence pack view؛ approval center؛ policy violations board؛ partner scorecards؛ actual vs forecast؛ risk heatmaps؛ next-best-action dashboard | Product + Frontend + Analytics | demo حي على بيانات تشغيل حقيقية مع drill-down من trace إلى memo إلى approval | الإدارة والعميل المؤسسي يراجعان القرارات والمخاطر والموافقات دون الرجوع إلى backend abstractions | Workstreams 2-7 | dashboard theater غير متصل بالحقيقة التشغيلية | أي mismatch بين dashboard والحقيقة التشغيلية يُعالج خلال يوم عمل واحد |

### 5) دورة التنفيذ الأسبوعية (Saudi business week)

لتصبح هذه المصفوفة قابلة للتنفيذ أسبوعاً بأسبوع دون وعود زمنية مضللة، يعتمد الفريق الإيقاع التالي:

- **الأحد:** قفل نطاق الأسبوع، تحديد workstreams النشطة، تحديث الحالة (`Current/Partial/Pilot/Production`)، وتأكيد owners/dependencies.
- **الإثنين - الثلاثاء:** تنفيذ المخرجات، جمع traces، policy decisions، workflow receipts، وأدلة الاختبارات.
- **الأربعاء:** مراجعة **Evidence Gate**؛ أي مخرج لا يملك دليلاً يبقى `Blocked` ولا يُرقّى.
- **الخميس:** **Exit Review**، تقرير مخاطر، قرار الترقية إلى `Pilot` أو `Production`، وتحديث register وPR/runbook المرتبط.

### 6) Definition of Done المؤسسي

لا يُعتبر Dealix جاهزاً للشركات إلا إذا تحقّق الآتي:

- كل business-critical recommendation تخرج **structured + evidence-backed**.
- كل long-running commitment يمر عبر **deterministic durable workflow** أو يملك خطة نقل معتمدة.
- كل فعل حساس يحمل **approval_class + reversibility + sensitivity + provenance + freshness**.
- كل connector حرج يمر عبر **versioned facade** مع retry/idempotency/audit mapping.
- كل release يمر عبر **rulesets + approvals + OIDC + provenance**.
- كل surface حرج يحمل **telemetry + correlation IDs + eval/review evidence**.
- كل workflow سعودي حساس يملك **PDPL/NCA-aware control mapping** قابل للتنفيذ.

---

*هذه الوثيقة تلخّص النص الاستراتيجي الكامل وتُحاذي تنفيذ Dealix دون الاعتماد على منصات RAG خارجية كطبقة أساسية، وتضيف برنامج الإكمال التشغيلي كمرجع التنفيذ المؤسسي القادم.*

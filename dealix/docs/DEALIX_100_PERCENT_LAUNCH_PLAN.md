# Dealix — تقرير الإطلاق الشامل (100٪ جاهزية) — مرجع رئيسي

> هذا المستند يجمع: الحالة، الفجوات، المنعطفات، والخطط 30/90 يوماً، وأين ينفّذ كل عمل (Cursor / Claude / Supabase / السحابة / واتساب / Google).

## 1. الحالة الحالية

فرع `dealix-v3-autonomous-revenue-os` مع أساس v3 + Personal Operator + وثائق + اختبارات + طبقة أعمال وAPI (`/api/v1/business/*`).

## 2. ما بُني

Revenue memory تجريبية، وكلاء آمنون، رادار، امتثال، علوم إيرادات، ذاكرة مشروع (هجرة + فهرسة محلية)، مشغّل عربي، بطاقات واتساب (payload فقط)، تقارير جاهزية، نموذج أعمال ووثائق GTM.

## 3. الناقص تقنياً

OAuth كامل، إرسال واتساب فعلي، رفع embeddings إنتاجي، فوترة self-serve كاملة، بعض مسارات onboarding كـ API.

## 4. ما يمنع البيتا الخاصة

غياب بيئة staging ثابتة + تجربة واتساب موقعة + 3–5 عملاء باتفاق واضح.

## 5. ما يمنع الإطلاق العام

PDPL تشغيلية، فوترة، دعم، SLOs، أمان مستقل، صفحة تسعير عامة متسقة مع الشروط القانونية.

## 6. قائمة إطلاق تقني

اختبارات، مراقبة، نسخ احتياطي، RLS مراجَأ، مفاتيح service role معزولة.

## 7. قائمة إطلاق منتج

onboarding، proof pack تلقائي، قنوات، سياسات، لقطات UI.

## 8. قائمة إطلاق أعمال

تسعير، عقود أداء، شركاء، قصص نجاح.

## 9. قائمة إطلاق GTM

قائمة 10، محتوى، webinars، إحالات.

## 10. قائمة امتثال

سجل موافقات، تصدير/حذف، قمع، سياسة واتساب.

## 11. نموذج مالي (مبدئي)

اشتراكات + إعداد + أداء (عقدي) — أرقام توضيحية في `/api/v1/business/unit-economics/demo`.

## 12. التسعير

`docs/PRICING_STRATEGY.md` + `/api/v1/business/pricing`.

## 13. أول 10 عملاء

`docs/GTM_PLAYBOOK.md` + `/api/v1/business/gtm/first-10`.

## 14. أول 100 عميل

`/api/v1/business/gtm/first-100`.

## 15. سكربتات مبيعات

`/api/v1/business/sales-script`.

## 16. سكربت تجربة (Demo)

Command center + رادار + فرصة + مسودة + موافقة.

## 17. عرض pilot

7 أيام أو أسبوعان مع proof pack — انظر كتيب GTM.

## 18. مقاييس النجاح

`/api/v1/business/metrics`.

## 19. سجل المخاطر

امتثال واتساب، توقعات AI، جودة البيانات، تعقيد المنتج، منافسة، تعقيد الشراكات.

## 20. خطة 30 يوماً

أسبوع 1: staging + 5 مكالمات اكتشاف.  
أسبوع 2: 3 pilots موقعة.  
أسبوع 3: proof packs.  
أسبوع 4: قرار التوسع أو تصحيح ICP.

## 21. خطة 90 يوماً

10 عملاء، قصص، تكامل واتساب إنتاجي بحذر، embeddings، تحسين المنتج.

## 22. ماذا يفعل سامي على الكمبيوتر

Cursor + GitHub + Supabase + Railway/Render + Postman/Bruno + إعداد Meta WhatsApp + Google Cloud للـ OAuth.

## 23. ماذا يبقى في محادثات الاستراتيجية (ChatGPT وغيره)

عصف ذهني للرسائل، مراجعة شرائح، سيناريوهات تفاوض — **من دون** تعديل الكود.

## 24. ماذا في Cursor

تنفيذ، refactor آمن، اختبارات، وثائق ريبو، PRs.

## 25. ماذا في Claude Code (إن استخدمته)

مهام طويلة موازية أو مسودات وثائق خارج الريبو — مع مزامنة يدوية للريبو.

## 26. ماذا في Supabase

هجرة، RLS، jobs للـ embeddings، بيئات منفصلة.

## 27. ماذا في Railway/Render

نشر API، secrets، مراقبة أساسية.

## 28. ماذا في WhatsApp Cloud

أرقام هوية، قوالب، webhook، توقيع، اختبار sandbox.

## 29. ماذا في Google Cloud

OAuth Gmail/Calendar، حصص، سياسات.

## 30. درجة الجاهزية الإجمالية

استدعِ `GET /api/v1/personal-operator/launch-report` — الرقم ديناميكي من النموذج الحالي؛ **لا يُعتبر ضماناً تنبؤياً** حتى تُربط ببيانات إنتاج وCI.

## 31. Innovation Roadmap (طبقة «Autonomous Growth Factory»)

**ما يُنفَّذ الآن في الريبو (MVP موثّق + API تجريبية deterministic):**

- وثيقة [`INNOVATION_STRATEGY.md`](INNOVATION_STRATEGY.md) — ٢٠ مفهوماً مع MVP مقابل تأجيل ومقاييس ومخاطر، ومقارنة موجزة مع Gong/Clari/People.ai.
- مسارات تحت `GET|POST /api/v1/innovation/*`: Command Feed **demo** و**live** (من DB مع fallback)، Growth Missions، **ten-in-ten**، AEO radar **demo**، Experiments (مع `past_experiments`)، Proof Ledger **demo** + **أحداث دائمة** + **تقرير أسبوعي**، Deal Room analyze — منطق في `auto_client_acquisition/innovation/` بدون LLM داخل هذه الطبقة وبدون إرسال حي من مسارات الابتكار.

**مراحل التمييز (معايير جاهزية):**

| مرحلة | مخرجات | معيار «جاهز للعرض» |
|--------|---------|---------------------|
| **A — تمييز قابل للعرض** | `POST .../opportunities/ten-in-ten`، `GET .../aeo/radar/demo`، فقرة مقارنة عالمية في الوثيقة | يعمل في staging مع `pytest` أخضر |
| **B — ذاكرة تشغيلية** | جدول `proof_ledger_events`، `GET .../proof-ledger/events`، `GET .../proof-ledger/report/week`، `GET .../command-feed/live` | أحداث تُسجَّل وتظهر في الـ feed أو التقرير لعميل pilot |
| **C — تخصيص** | `past_experiments` في `POST .../experiments/recommend` | على الأقل قاعدة قواعد تنعكس في التوصيات من تاريخ عميل واحد |

**ما يُؤجَّل إلى ما بعد البيانات والتشغيل:**

- AEO حقيقي (استعلامات خارجية دورية)، Deal Graph كامل في DB، مسارات LangGraph متينة، MCP gateway، Partner Marketplace خارجي، تقارير PDF مؤتمتة من الـ Ledger.

### Kill feature — «10 فرص في 10 دقائق»

وعد منتجي مركزي: من مدخلات شركة/قطاع/مدينة/عرض/هدف إلى قائمة ١٠ فرص مع Why Now ومستوى مخاطرة ومسودات عربية **بانتظار الموافقة فقط** — **`POST /api/v1/innovation/opportunities/ten-in-ten`**؛ وصف المهمة في `GET /api/v1/innovation/growth-missions`؛ الاستراتيجية في [`INNOVATION_STRATEGY.md`](INNOVATION_STRATEGY.md)؛ الإطار التشغيلي بجانب `GET /api/v1/business/gtm/first-10` عند التوسع.

## 32. Growth Control Tower — ترتيب الموجات (0→6)

رؤية منتج: **برج تحكم بالنمو** — Inbox موحّد، سياسة قنوات، ذكاء تشغيلي خفيف، ومسودات تكاملات (بدون live) حتى اكتمال البوابات.

| موجة | المحتوى | وثائق / كود |
|------|---------|-------------|
| **0** | تثبيت: `compileall`، `pytest`، `print_routes`، `smoke_inprocess` | [`POST_MERGE_VERIFICATION.md`](POST_MERGE_VERIFICATION.md) |
| **1** | استراتيجية Platform + Intelligence | [`PLATFORM_SERVICES_STRATEGY.md`](PLATFORM_SERVICES_STRATEGY.md)، [`INTELLIGENCE_LAYER_STRATEGY.md`](INTELLIGENCE_LAYER_STRATEGY.md) |
| **2** | `platform_services` + `/api/v1/platform/*` | `auto_client_acquisition/platform_services/` |
| **3** | `intelligence_layer` + `/api/v1/intelligence/*` | `auto_client_acquisition/intelligence_layer/` |
| **4** | Gmail / Calendar / Moyasar — **payload فقط** | `auto_client_acquisition/integrations/` |
| **5** | Ingest نماذج leads (MVP) + قنوات اجتماعية **مسجّلة فقط** في السجل | `ingest/lead-form` + `channel_registry` |
| **6** | وكلاء متينة (مفاهيم) — **بدون** LangGraph في `requirements.txt` حتى موافقة | [`AGENT_WORKFLOW_ARCHITECTURE.md`](AGENT_WORKFLOW_ARCHITECTURE.md) |

الالتزام بالبيتا الخاصة والـ PDPL كما في الأقسام أعلاه؛ لا إرسال حي من مسارات المنصة في هذه الموجات.

## 33. مواءمة مسارات API (canonical و aliases)

جدول يوحّد أسماء المسارات بين المنتج والكود: [`docs/architecture/API_CANONICAL_ALIASES.md`](architecture/API_CANONICAL_ALIASES.md) — يُحدَّث عند إضافة مسار جديد أو alias.

## 34. Growth Neural Network — طبقات Curator و Meeting و Router (MVP)

بعد موجات **Growth Control Tower** (أقسام 32–33)، أُضيفت وحدات داعمة تحت `auto_client_acquisition/` مع راوترات FastAPI: **security_curator**، **growth_curator**، **meeting_intelligence**، **model_router**، **connectors**، **agent_observability**، و**growth_operator** (aliases منتجية فقط). التفاصيل التشغيلية والامتثال (مسودات، عدم إرسال حي، عدم شحن تلقائي) كما في [`PLATFORM_SERVICES_STRATEGY.md`](PLATFORM_SERVICES_STRATEGY.md) و[`PRIVATE_BETA_RUNBOOK.md`](PRIVATE_BETA_RUNBOOK.md).

**وثائق موجهة للتنفيذ:** [`EXECUTION_ROADMAP_AR.md`](EXECUTION_ROADMAP_AR.md)، [`AGENT_SECURITY_CURATOR.md`](AGENT_SECURITY_CURATOR.md)، [`GROWTH_CURATOR_STRATEGY.md`](GROWTH_CURATOR_STRATEGY.md)، [`MEETING_INTELLIGENCE.md`](MEETING_INTELLIGENCE.md)، [`MODEL_PROVIDER_ROUTER.md`](MODEL_PROVIDER_ROUTER.md)، [`AGENT_OBSERVABILITY_EVALS.md`](AGENT_OBSERVABILITY_EVALS.md)، [`CONNECTOR_CATALOG.md`](CONNECTOR_CATALOG.md).

## 35. Targeting & Acquisition OS

طبقة [`targeting_os`](../auto_client_acquisition/targeting_os/) + مسارات `/api/v1/targeting/*` (انظر [`API_CANONICAL_ALIASES.md`](architecture/API_CANONICAL_ALIASES.md)): استهداف حسابات، لجنة شراء، تقييم مصدر وجهة، خطة outreach، استراتيجية LinkedIn المتوافقة، تشخيص مجاني، وقوالب عقود **للمسودات فقط**. الوثيقة المرجعية: [`TARGETING_ACQUISITION_OS.md`](TARGETING_ACQUISITION_OS.md).

## 36. Service Tower + Service Excellence OS

- **Service Tower** ([`service_tower/`](../auto_client_acquisition/service_tower/)، مسارات `/api/v1/services/*`): كتالوج خدمات بيعية (تشخيص مجاني، ذكاء قوائم، ١٠ فرص، Growth OS، شراكات، …) مع wizard توصية، عروض سعر تقديرية، وبطاقات CEO — مدمج مع كتالوج المنصة في `GET .../catalog` دون تكرار منطق التنفيذ الخارجي.
- **Service Excellence OS** ([`service_excellence/`](../auto_client_acquisition/service_excellence/)، مسارات `/api/v1/service-excellence/*`): مصفوفة ميزات، درجة جاهزية، فجوات تنافسية، حزمة إطلاق، backlog تحسين — deterministic للعرض الداخلي.
- **وثائق:** [`SERVICE_TOWER_STRATEGY.md`](SERVICE_TOWER_STRATEGY.md)، [`SERVICE_EXCELLENCE_OS.md`](SERVICE_EXCELLENCE_OS.md).
- **Landing (عرض):** [`landing/services.html`](../landing/services.html)، [`landing/free-diagnostic.html`](../landing/free-diagnostic.html)، [`landing/first-10-opportunities.html`](../landing/first-10-opportunities.html)، [`landing/agency-partner.html`](../landing/agency-partner.html)، [`landing/list-intelligence.html`](../landing/list-intelligence.html)، [`landing/growth-os.html`](../landing/growth-os.html).

## 37. Launch Ops + جاهزية البيتا

- **Launch Ops** ([`launch_ops/`](../auto_client_acquisition/launch_ops/)، مسارات `/api/v1/launch/*`): عرض البيتا الخاصة، سكربت ديمو ١٢ دقيقة، قوالب أول ٢٠ تواصل، go/no-go، scorecard جاهزية.
- **Service Tower — إضافات:** `GET /api/v1/services/verticals` (ثلاثة أبواب)، `GET /api/v1/services/upgrade-paths`، `GET /api/v1/services/contracts/templates` (مسودات عقود — ليست استشارة قانونية).
- **وثائق:** [`PRIVATE_BETA_LAUNCH_TODAY.md`](PRIVATE_BETA_LAUNCH_TODAY.md)، [`DEMO_SCRIPT_12_MINUTES.md`](DEMO_SCRIPT_12_MINUTES.md)، [`FIRST_20_OUTREACH_MESSAGES.md`](FIRST_20_OUTREACH_MESSAGES.md)، [`COMMERCIAL_LAUNCH_MASTER_PLAN.md`](COMMERCIAL_LAUNCH_MASTER_PLAN.md)، [`FRONTEND_AND_API_MAP.md`](FRONTEND_AND_API_MAP.md) (واجهة HTML ↔ برج API + لغتين للبيتا)، [`AUTONOMOUS_REVENUE_COMPANY_OS.md`](AUTONOMOUS_REVENUE_COMPANY_OS.md).

## 38. Revenue Today (تحصيل Pilot بدون أتمتة خطرة)

- **الحزمة** [`revenue_launch/`](../auto_client_acquisition/revenue_launch/): عروض ٤٩٩ و Growth OS Pilot، شرائح أول ٢٠ تواصل، ديمو/إغلاق، مخطط pipeline، checklist تسليم Pilot، قالب Proof Pack، **تعليمات دفع يدوية** (Moyasar dashboard — لا charge من كود Dealix في هذه المرحلة).
- **المسارات** `GET /api/v1/revenue-launch/*` — انظر [`REVENUE_TODAY_PLAYBOOK.md`](REVENUE_TODAY_PLAYBOOK.md) و[`API_CANONICAL_ALIASES.md`](architecture/API_CANONICAL_ALIASES.md).
- **أداة checklist:** `python scripts/launch_readiness_check.py` (اختياري `--base-url` مع httpx لفحص `/health` وعينات API).

## 39. Autonomous Revenue Company OS (مشغّل + Company OS)

- **الرؤية والطبقات الاثنا عشر:** [`AUTONOMOUS_REVENUE_COMPANY_OS.md`](AUTONOMOUS_REVENUE_COMPANY_OS.md) — يربط الفئة «نظام تشغيل نمو» بالمجلدات والمسارات الفعلية.
- **المشغّل (نية → خدمة → موافقة):** حزمة [`autonomous_service_operator/`](../auto_client_acquisition/autonomous_service_operator/) ومسارات `GET|POST /api/v1/operator/*` (عرض deterministic، بدون LLM إلزامي في الموجة الأولى).
- **Company OS (حدث → بطاقة → RWU):** [`revenue_company_os/`](../auto_client_acquisition/revenue_company_os/) ومسارات `GET /api/v1/revenue-os/company-os/*` بجانب `revenue_os` الحالي — لا يستبدل `POST /events` بل يكمّل تحت `company-os`.

## 40. Positioning Lock + Customer Ops + صفحات الشركات/المسوقين

- **تثبيت الرسالة:** [`POSITIONING_LOCK.md`](POSITIONING_LOCK.md)، [`PROHIBITED_CLAIMS.md`](PROHIBITED_CLAIMS.md)، [`APPROVED_MARKET_MESSAGING.md`](APPROVED_MARKET_MESSAGING.md).
- **Customer Ops (API):** حزمة [`customer_ops/`](../auto_client_acquisition/customer_ops/) ومسارات `GET|POST /api/v1/customer-ops/*` — قائمة onboarding، SLA، حالة موصلات تجريبية، cadence نجاح عميل، playbook حوادث، وتوجيه تذكرة دعم (بدون تنفيذ خارجي).
- **صفحات عرض:** [`landing/companies.html`](../landing/companies.html) (مسار الشركات)، [`landing/marketers.html`](../landing/marketers.html) (مسار الوكالات/المسوقين) — تربط بباقي صفحات الـ landing الحالية.
- **تشغيل المشغّل:** أوضاع إضافية في [`self_growth_mode.py`](../auto_client_acquisition/autonomous_service_operator/self_growth_mode.py) و[`service_delivery_mode.py`](../auto_client_acquisition/autonomous_service_operator/service_delivery_mode.py) بجانب الأوضاع الموجودة.

---

**الخلاصة:** المنتج **قوي كأساس سوقي وتقني**؛ الإطلاق العام يحتاج تشغيلاً وامتثالاً وتجربة عميل مغلقة أولاً.

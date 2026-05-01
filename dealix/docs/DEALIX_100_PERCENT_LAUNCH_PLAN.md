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

## 32. Platform Services Layer — برج التحكم بالنمو

طبقة موحدة multi-channel فوق `growth_operator` تحوّل Dealix من قناة WhatsApp إلى منصة:

- **11 قناة** (`whatsapp, gmail, google_calendar, moyasar, linkedin_lead_forms, x_api, instagram_graph, google_business_profile, google_sheets, crm, website_forms`).
- **Action Policy Engine**: block_cold_whatsapp / block_payment_no_confirm / block_secrets / external_send_needs_approval / high_value_deal_review.
- **Tool Gateway** هو المخرج التنفيذي الوحيد — كل أداة تمر منه. Live env flags افتراضياً OFF.
- **Unified Inbox**: 8 أنواع بطاقات، ≤3 أزرار، عربية.
- **Action Ledger** + **Proof Ledger** (أثر فعلي مقاس بالقناة).
- **12 خدمة قابلة للبيع** (`growth_operator_subscription`, `channel_setup_service`, `lead_intelligence_service`, `partnership_sprint`, `email_revenue_rescue`, `social_growth_os`, `local_business_growth`, `ai_visibility_aeo_sprint`, `revenue_proof_pack_service`, `customer_success_operator`, `payments_collections_operator`, `outreach_approval_service`).

**Endpoints:** `/api/v1/platform/{services/catalog, channels, policy/rules, actions/evaluate, tools/invoke, events/ingest, inbox/feed, identity/resolve, ledger/summary, proof-ledger/demo}`. **التفصيل:** [`PLATFORM_SERVICES_STRATEGY.md`](PLATFORM_SERVICES_STRATEGY.md).

## 33. Intelligence Layer — الشبكة العصبية للنمو

طبقة فوق Platform Services تجعل Dealix يتعلم ويقترح ويحاكي:

- **Growth Brain** لكل عميل + `is_ready_for_autopilot()` (≥30 signals + ≥40% accept).
- **Command Feed**: 9 أنواع بطاقات يومية (opportunity / revenue_leak / partner_suggestion / meeting_prep / review_response / competitive_move / customer_reactivation / ai_visibility_alert / action_required).
- **Action Graph** (10 أنواع حواف): signal → action → outcome.
- **Mission Engine**: 7 ميشنات، **Kill Feature: `first_10_opportunities`**.
- **Decision Memory**: تعلّم من Accept/Skip/Edit/Block.
- **Trust Score** مركب لكل رسالة (safe ≥70 / needs_review 40-69 / blocked <40).
- **Revenue DNA**: best_channel / best_segment / best_angle / common_objection / avg_cycle_days.
- **Opportunity Simulator** (9 قطاعات سعودية): توقع replies/meetings/deals/pipeline_sar + risk_score.
- **Competitive Move Detector**: 8 أنواع حركات + recommended_action_ar.
- **Founder Shadow Board**: موجز أسبوعي (3 قرارات + 3 فرص + 3 مخاطر + علاقة + تجربة + مؤشر).

**Endpoints:** `/api/v1/intelligence/{growth-brain/build, command-feed/demo, missions, missions/recommend, trust-score, revenue-dna/demo, revenue-dna, simulate-opportunity, competitive-move/analyze, board-brief/demo, decisions/record, decisions/preferences}`. **التفصيل:** [`INTELLIGENCE_LAYER_STRATEGY.md`](INTELLIGENCE_LAYER_STRATEGY.md).

## 34. Self-Improving Agent Platform (Hermes-inspired)

طبقة "ذاتية التحسن" فوق Platform Services + Intelligence Layer. 6 modules جديدة + 6 routers جديدة + 76 اختبار:

- **Security Curator** ([`AGENT_SECURITY_CURATOR.md`](AGENT_SECURITY_CURATOR.md)) — secret_redactor (11 نمط: GitHub/OpenAI/Anthropic/Supabase/WhatsApp/Moyasar/Sentry/Google/AWS) + patch_firewall (يحظر `.env` والـRSA keys في الـdiff) + trace_redactor (يخفي phones/emails) + tool_output_sanitizer.
- **Growth Curator** ([`GROWTH_CURATOR_STRATEGY.md`](GROWTH_CURATOR_STRATEGY.md)) — message_curator (يقيّم الرسائل العربية، يكشف 8 عبارات محظورة) + playbook_curator (winner/promising/needs_work/archive) + mission_curator + skill_inventory (20+ skill عبر 5 طبقات) + curator_report (تقرير عربي أسبوعي).
- **Meeting Intelligence** ([`MEETING_INTELLIGENCE.md`](MEETING_INTELLIGENCE.md)) — Pre-meeting brief (6 أقسام عربية) + transcript_parser (Google Meet entries أو نص) + objection_extractor (8 فئات) + followup_builder (email + WhatsApp drafts) + deal_risk (0..100).
- **Model Router** ([`MODEL_PROVIDER_ROUTER.md`](MODEL_PROVIDER_ROUTER.md)) — 7 providers (Claude Sonnet/Haiku, GPT-4, GPT-4o-mini, Gemini Pro, Azure OAI KSA-region, Local Qwen) × 10 task types + cost_policy + fallback_policy (KSA-region أولاً للحالات الحساسة).
- **Connector Catalog** ([`CONNECTOR_CATALOG.md`](CONNECTOR_CATALOG.md)) — 14 تكامل (WhatsApp Cloud, Gmail, Calendar, Meet, Moyasar, LinkedIn Lead Forms, Google Business Profile, X, Instagram, Sheets, CRM, Website Forms, Composio, MCP Gateway) كل واحد له launch_phase + risk_level + Arabic risks.
- **Agent Observability** ([`AGENT_OBSERVABILITY_EVALS.md`](AGENT_OBSERVABILITY_EVALS.md)) — trace_events (مع hash للـuser/company IDs) + safety_eval (7 قواعد) + saudi_tone_eval (إيجابيات/سلبيات/نسبة عربية) + eval_pack (5 cases) + cost_tracker.

**Endpoints جديدة:**
- `/api/v1/security-curator/{demo, redact, inspect-diff, sanitize-output}`
- `/api/v1/growth-curator/{skills/inventory, messages/grade, messages/improve, messages/duplicates, missions/next, report/weekly, report/demo}`
- `/api/v1/meeting-intelligence/{brief, brief/demo, transcript/summarize, followup/draft, deal-risk}`
- `/api/v1/model-router/{providers, tasks, route, cost-class, usage/demo}`
- `/api/v1/connector-catalog/{catalog, summary, status, risks, {key}}`
- `/api/v1/agent-observability/{trace/build, safety/eval, tone/eval, evals/run}`

## 35. Private Beta Launch — Today

راجع:
- [`PRIVATE_BETA_LAUNCH_TODAY.md`](PRIVATE_BETA_LAUNCH_TODAY.md) — الخطة الكاملة للإطلاق.
- [`DEMO_SCRIPT_12_MINUTES.md`](DEMO_SCRIPT_12_MINUTES.md) — السكربت المعتمد للعرض.
- [`FIRST_20_OUTREACH_MESSAGES.md`](FIRST_20_OUTREACH_MESSAGES.md) — قوالب الرسائل العربية.
- `landing/private-beta.html` — صفحة العرض.

**العرض:** Pilot 7 أيام بـ499 ريال أو مجاني مقابل case study. Paid Pilot 30 يوم بـ1,500–3,000 ريال. Growth OS اشتراك شهري بـ2,999 ريال.

**ممنوع اليوم:** live WhatsApp send, live Gmail send, live Calendar insert, payment charge, scraping social, وعود "نضمن نتائج".

## 36. Targeting & Acquisition OS — نظام الاستهداف الذكي

طبقة جديدة (16 module + 20 endpoint + 47 اختبار) تجعل Dealix يستهدف بذكاء بدلاً من جمع عشوائي:

- **Account-first**: `account_finder` يحدد 10-25 شركة لكل (sector, city) مع `fit_score` و`why_now_ar`.
- **Buying Committee**: `buyer_role_mapper` بـ14 دور وخرائط حسب القطاع (training/saas/real_estate/...).
- **Contact Source Policy**: 12 مصدر (crm_customer → opt_out) مع risk_score + retention.
- **Contactability Matrix**: 5 action modes (suggest_only/draft_only/approval_required/approved_execute/blocked).
- **LinkedIn Strategy**: Lead Forms + Ads + Manual فقط — `linkedin_do_not_do()` يقفل scraping/auto-DM/auto-connect.
- **Email Strategy**: drafts + unsubscribe + pacing per domain reputation.
- **WhatsApp Strategy**: opt-in only، rejects cold + risky phrases تلقائياً.
- **Outreach Scheduler**: day-by-day plan + daily limits + opt-out enforcement.
- **Reputation Guard**: bounce/complaint/opt-out thresholds → healthy/watch/pause مع recovery actions.
- **Daily Autopilot**: Arabic brief + 7 today actions + EOD report.
- **Self-Growth Mode**: 5 ICP focuses لـ Dealix نفسه + daily brief + weekly learning.
- **Free Growth Diagnostic**: العرض المجاني الذي يجلب Pilots.
- **Contract Drafts**: Pilot/DPA/Referral/Agency outlines (legal review required, PDPL-aware).

**Endpoints:** `/api/v1/targeting/{accounts/recommend, buying-committee/map, contacts/evaluate, uploaded-list/analyze, outreach/plan, daily-autopilot/demo, self-growth/demo, reputation/status, linkedin/strategy, drafts/email, drafts/whatsapp, free-diagnostic, services, contracts/templates, ...}`. **التفصيل:** [`TARGETING_ACQUISITION_OS.md`](TARGETING_ACQUISITION_OS.md).

## 37. Service Tower — برج الخدمات الذاتية

**12 Productized Service** + Wizard + Pricing Engine + Scorecard + WhatsApp CEO Control + Upgrade Paths (8 modules + 20 endpoint + 38 اختبار):

| الخدمة | السعر | النوع |
|--------|------|------|
| Free Growth Diagnostic | مجاني | one_time |
| List Intelligence | 499–1,500 | one_time |
| First 10 Opportunities Sprint | 499–1,500 | sprint |
| Self-Growth Operator | 999/شهر | monthly |
| Growth OS Monthly | 2,999/شهر | monthly |
| Email Revenue Rescue | 1,500–5,000 | one_time |
| Meeting Booking Sprint | 1,500–5,000 | sprint |
| Partner Sprint | 3,000–7,500 | sprint |
| Agency Partner Program | 10,000–50,000 | one_time |
| WhatsApp Compliance Setup | 1,500–4,000 | one_time |
| LinkedIn Lead Gen Setup | 2,000–7,500 | one_time |
| Executive Growth Brief | 499–999/شهر | monthly |

**3 أبواب للعميل:**
1. أريد عملاء جدد.
2. عندي بيانات وأبغى أستفيد منها.
3. أبغى توسع وشراكات.

**Endpoints:** `/api/v1/services/{catalog, recommend, {id}/start, {id}/workflow, {id}/quote, {id}/scorecard, {id}/upgrade-path, ceo/daily-brief, ceo/approval-card, ...}`. **التفصيل:** [`SERVICE_TOWER_STRATEGY.md`](SERVICE_TOWER_STRATEGY.md).

## 38. Service Excellence OS — مصنع الخدمات الممتازة

**8 modules + 22 endpoint + 33 اختبار** يضمنون أن كل خدمة تطلق بـ score ≥80 وتجاوز 4 quality gates، وتستمر في التحسين الأسبوعي:

- **Feature Matrix** — 12 must-have لكل خدمة + advanced/premium/future.
- **Service Scoring** — 10 أبعاد × 10 = 100 → launch_ready/beta_only/needs_work.
- **Quality Review** — 4 gates: proof / approval / pricing / channels.
- **Competitor Gap** — مقارنة بـ7 فئات منافسين (CRM, WA tools, email assistants, LinkedIn tools, agencies, revenue intelligence, generic AI).
- **Proof Metrics** — ROI estimate (pipeline_x + closed_won_x).
- **Research Lab** — brief شهري + hypotheses + experiments.
- **Improvement Backlog** — feedback → backlog → prioritized weekly tasks.
- **Launch Package** — landing + sales script + 12-min demo + 5-day onboarding.

**Endpoints:** `/api/v1/service-excellence/{id}/{feature-matrix, score, quality-review, proof-metrics, gap-analysis, research-brief, experiments, monthly-review, backlog, launch-package, sales-script, demo-script}` + `/review/all`. **التفصيل:** [`SERVICE_EXCELLENCE_OS.md`](SERVICE_EXCELLENCE_OS.md).

## 39. Landing Pages

- `landing/services.html` — 3 أبواب + 12 خدمة productized.
- `landing/free-diagnostic.html` — العرض المجاني.
- `landing/first-10-opportunities.html` — Kill Feature.
- `landing/agency-partner.html` — برنامج الوكالة الشريكة.
- `landing/private-beta.html` — Private Beta launch.

---

**الخلاصة:** المنتج **قوي كأساس سوقي وتقني**؛ الإطلاق العام يحتاج تشغيلاً وامتثالاً وتجربة عميل مغلقة أولاً. الإطلاق اليوم = Private Beta + Pilots + Proof Pack، ليس Public Launch.

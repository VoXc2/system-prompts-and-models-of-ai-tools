# Dealix — Autonomous Revenue Company OS

> **الفئة:** ليس CRM ولا بوت واتساب ولا لوحة عادية — نظام تشغيل نمو وإيرادات **عربي سعودي** يربط الإشارة بالسياق ثم الخدمة ثم سير العمل ثم المخاطر ثم المسودة ثم الموافقة ثم التصدير/التنفيذ ثم الـ Proof ثم التعلم والترقية.  
> **التنفيذ في الريبو:** طبقات API وحزم `auto_client_acquisition` **deterministic** في MVP؛ إرسال حي وشحن واتساب بارد **غير مفعّل** افتراضياً — انظر [`SAFE_TOOL_GATEWAY_POLICY.md`](SAFE_TOOL_GATEWAY_POLICY.md) و[`PRIVATE_BETA_RUNBOOK.md`](PRIVATE_BETA_RUNBOOK.md).

## الاثنا عشر طبقة ومواءمتها مع الكود

| # | الطبقة | الدور | أين في الريبو (مرجع) |
|---|--------|--------|----------------------|
| 1 | Autonomous Service Operator | نية → خدمة → intake → مسودة → موافقة → proof | [`autonomous_service_operator/`](../auto_client_acquisition/autonomous_service_operator/)، `GET/POST /api/v1/operator/*` |
| 2 | Service Tower | خدمات منتَجة للبيع | [`service_tower/`](../auto_client_acquisition/service_tower/)، `/api/v1/services/*` |
| 3 | Service Excellence OS | جودة ودرجة وbacklog | [`service_excellence/`](../auto_client_acquisition/service_excellence/)، `/api/v1/service-excellence/*` |
| 4 | Targeting & Acquisition OS | فرص آمنة، بدون scraping | [`targeting_os/`](../auto_client_acquisition/targeting_os/)، `/api/v1/targeting/*` |
| 5 | Growth Control Tower | كروت قرار، command feed | [`innovation/command_feed`](../auto_client_acquisition/innovation/command_feed.py)، `/api/v1/innovation/command-feed/demo`، `/api/v1/platform/inbox/feed` |
| 6 | Safe Tool Gateway | سياسة أداة قبل أي تنفيذ | [`copilot/safe_actions`](../auto_client_acquisition/copilot/safe_actions.py)، [`security_curator/`](../auto_client_acquisition/security_curator/)، [`tool_action_planner`](../auto_client_acquisition/autonomous_service_operator/tool_action_planner.py) |
| 7 | Agent Runtime | وكلاء بحدود وأدوات | [`agents/`](../auto_client_acquisition/agents/)، [`v3`](../api/routers/v3.py)، orchestrator |
| 8 | Durable Workflow Engine | مسارات طويلة + HITL | حالياً: حالة جلسة في الذاكرة + موافقات؛ **LangGraph** فقط بعد موافقة صريحة — [`AGENT_WORKFLOW_ARCHITECTURE.md`](AGENT_WORKFLOW_ARCHITECTURE.md) |
| 9 | Revenue Graph | كيانات وعلاقات | [`revenue_graph/`](../auto_client_acquisition/revenue_graph/)، [`revenue_memory/`](../auto_client_acquisition/revenue_memory/) |
| 10 | Proof Ledger | أحداث إثبات | [`innovation` proof ledger](../api/routers/innovation.py)، [`fetch_proof_ledger_weekly.py`](../scripts/fetch_proof_ledger_weekly.py) |
| 11 | Self-Improving Layer | تقارير أسبوعية وbacklog | [`growth_curator/`](../auto_client_acquisition/growth_curator/)، [`revenue_company_os/self_improvement_loop`](../auto_client_acquisition/revenue_company_os/self_improvement_loop.py) |
| 12 | Revenue Launch System | عروض، pipeline، دفع يدوي | [`revenue_launch/`](../auto_client_acquisition/revenue_launch/)، `/api/v1/revenue-launch/*` |

## Draft مقابل Live (ملخّص)

- **Draft / suggest / approval_required:** المسار الافتراضي في MVP (مسودات Gmail، روابط دفع شكلية، كروت موافقة).
- **Live send / charge / calendar insert:** يتطلب إعدادات صريحة + موافقة بشرية؛ الكثير منها **محظور** في العروض التجريبية — راجع سياسة البوابة والاختبارات.

## وثائق مرتبطة

- [`AUTONOMOUS_SERVICE_OPERATOR.md`](AUTONOMOUS_SERVICE_OPERATOR.md) — المشغّل والنية والجلسة.
- [`SERVICE_BUNDLES.md`](SERVICE_BUNDLES.md) — الباقات التجارية.
- [`REVENUE_WORK_UNITS.md`](REVENUE_WORK_UNITS.md) — وحدات عمل الإيراد (RWU).
- [`CEO_COMMAND_CENTER.md`](CEO_COMMAND_CENTER.md)، [`AGENCY_PARTNER_MODE.md`](AGENCY_PARTNER_MODE.md)، [`SAFE_TOOL_GATEWAY_POLICY.md`](SAFE_TOOL_GATEWAY_POLICY.md)، [`SELF_IMPROVING_REVENUE_LOOP.md`](SELF_IMPROVING_REVENUE_LOOP.md).
- [`DEALIX_100_PERCENT_LAUNCH_PLAN.md`](DEALIX_100_PERCENT_LAUNCH_PLAN.md) — جاهزية الإطلاق الشاملة.

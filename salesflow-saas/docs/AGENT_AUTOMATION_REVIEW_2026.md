# مراجعة الوكلاء والأتمتة — Dealix (2026)

**تاريخ المرجع:** أبريل 2026.  
**الهدف:** توثيق ما هو موجود في المستودع، فجوات مقارنة بأفضل الممارسات، وخيارات تقنية حديثة للتوسع.

**سياسة:** لا نستخدم «تسريبات» أو أسرار شركات — راجع `PUBLIC_AGENT_PATTERNS_AND_ETHICS.md`.

---

## 1) ما هو مُنفَّذ اليوم في الكود

| الطبقة | المكوّن | الدور |
|--------|---------|--------|
| تنفيذ وكلاء | `app/services/agents/executor.py` + `AgentRouter` | استدعاء LLM، موجهات، تسجيل محادثات |
| خلفية | `app/workers/agent_tasks.py` | Celery: `run_ai_agent`, `process_agent_event`, **`snapshot_agent_framework_stack`** |
| تدفقات | `app/flows/self_improvement_flow.py` + `app/openclaw/durable_flow.py` | حلقات تحسين + checkpoints |
| تنسيق متعدد الوكلاء | LangGraph + LangChain (في `requirements.txt`) | رسوم بيانية، مسارات حالة |
| فرق وكلاء | CrewAI، mem0 | مذكور في التبعيات |
| Microsoft AutoGen | `app/ai/autogen/factory.py` | `OpenAIChatCompletionClient` + Groq عبر `base_url` |
| مراقبة إصدارات | `GET /api/v1/agent-frameworks` | JSON بدون أسرار — إصدارات الحزم وحالة AutoGen/Celery |
| مساعدات | `instructor`, `tenacity`, `structlog`, `rich` | مخرجات منظمة، إعادة محاولة، سجلات |

---

## 2) فجوات مقارنة بأفضل المنتجات (Gong / Outreach / منصات إيرادات)

- **ملاحظة قابلة للتنفيذ:** معظم الفجوة ليست «مكتبة ناقصة» بل **ربط بيانات + قنوات إنتاج + امتثال**.
- **واتساب واتس Meta:** تحتاج حسابات وقوالب معتمدة — الكود يدعم مساراً؛ التشغيل تشغيلياً.
- **CRM موحّد:** يوجد `crm_sync_service` ومسارات؛ التكامل العميق يحتاج مشروع زمن.
- **مراقبة LLM:** يُفضّل لاحقاً Langfuse / OpenTelemetry + تتبع تكلفة/رمز — `structlog` خطوة أولى.
- **الجلسات والـ API:** تم تعزيز `DEALIX_INTERNAL_API_TOKEN` ومسارات BFF في الواجهة.

---

## 3) ماذا يُضاف «أكثر» في 2026 (أدوات ومكتبات — بحسب الأولوية)

1. **LangGraph + FastAPI + SSE** — بث مخرجات الوكيل للواجهة (تجربة حية).
2. **AutoGen AgentChat (مثبّت)** — فرق متوازية، أنماط RoundRobin/Selector — تبدأ من `dealix_assistant_agent`.
3. **Checkpoint LangGraph على Postgres** — استمرارية جلسات طويلة (ليس SQLite فقط في التطوير).
4. **قواعد أدوات (tool calling)** موحّدة في `AgentExecutor` — تقليل تفرّع المنطق.
5. **اختبارات عقد للوكلاء** — سيناريوهات ذهبية مع استجابات JSON ثابتة.
6. **جدولة Celery** — `snapshot_agent_framework_stack` دورياً للمراقبة.

---

## 4) نقاط ربط واضحة في المستودع

- `app/ai/automation/registry.py` — جدول `AUTOMATION_SURFACE` للمسارات.
- `app/services/agent_framework_report.py` — بناء تقرير الإصدارات.
- `GET /api/v1/agent-frameworks` — للمراقبة ولوحات التشغيل.

---

## 5) خلاصة

المشروع يحتوي **طبقات وكلاء متعددة** (تنفيذ، Celery، LangGraph، CrewAI، AutoGen). الخطوة التالية الأعلى قيمة غالباً: **ربط تدفق واحد end-to-end** (ليد → صفقة → رسالة) مع **قياس ومراقبة**، وليس إضافة إطار جديد فوق آخر دون تكامل.

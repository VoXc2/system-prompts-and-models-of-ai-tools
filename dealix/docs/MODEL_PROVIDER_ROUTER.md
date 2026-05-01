# Model Provider Router

طبقة **تكوين وتلميحات** لربط نوع المهمة بمزود/نموذج مقترح. التنفيذ الفعلي لاستدعاء LLM يبقى في `core/llm/` وإعدادات البيئة.

## كود

- `auto_client_acquisition/model_router/task_router.py` — `route_task`, `list_tasks`
- `auto_client_acquisition/model_router/provider_registry.py` — `list_providers`

## API

- `GET /api/v1/model-router/tasks`
- `POST /api/v1/model-router/route` — `{ "task_type": "..." }`
- `GET /api/v1/model-router/providers`

## استخدام

استخدم الاستجابة لعرض «لماذا هذا المزود» في لوحة المشرف أو لتمرير metadata إلى `core/llm/router.py` عند توحيد السلوك لاحقاً.

## اختبارات

`tests/test_growth_tower_stack.py` — `test_model_router_compliance_guardrail`.

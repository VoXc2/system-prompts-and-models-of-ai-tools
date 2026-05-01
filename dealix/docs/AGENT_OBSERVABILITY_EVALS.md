# Agent Observability and Evals (Growth Tower)

أشكال JSON للتقييم والتتبع تمهّد لربط **Langfuse** أو أدوات مماثلة في staging/production.

## كود

- `auto_client_acquisition/agent_observability/trace_events.py` — `build_trace_event`
- `safety_eval.py` — تقييم أمان بسيط على النص العربي
- `saudi_tone_eval.py` — ملاءمة نبرة سعودية شكلية
- `eval_cases.py` — حالات مرجعية (توسيع لاحقاً)

## API

- `GET /api/v1/agent-observability/demo`
- `POST /api/v1/agent-observability/eval/safety` — `{ "text_ar": "..." }`
- `POST /api/v1/agent-observability/eval/saudi-tone` — `{ "text_ar": "..." }`
- `POST /api/v1/agent-observability/trace/build` — حقول workflow، policy_result، tool_called، إلخ

## خطوة تالية

عند تفعيل Langfuse: إرسال نفس الحقول كـ span attributes؛ راجع [`OBSERVABILITY_ENV.md`](OBSERVABILITY_ENV.md).

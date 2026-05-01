# تشغيل التقييمات (Evals) — Dealix

## الهدف

فحوصات **شكل وسلامة ثابتة** بعد كل نشر، بدون استدعاء LLM إنتاجي (انظر [`scripts/run_evals.py`](../scripts/run_evals.py)).

## الأمر

```bash
python scripts/run_evals.py
python scripts/run_evals.py --suite personal_operator
```

الخرج `EVAL_OK` أو `EVAL_FAIL` مع سبب.

## الملفات

- [`evals/personal_operator_cases.jsonl`](../evals/personal_operator_cases.jsonl)
- [`evals/revenue_os_cases.jsonl`](../evals/revenue_os_cases.jsonl)

## Gate مقترح للإطلاق

بعد `pytest`، `smoke_inprocess`، و`print_routes`، شغّل `run_evals.py` في CI اختياري أو على الفرع قبل الدمج إلى `main`.

## التوسع لاحقاً

أضف حالات واقعية من staging (بدون بيانات شخصية)؛ يمكن ربط Langfuse كما في [`AI_OBSERVABILITY_AND_EVALS.md`](AI_OBSERVABILITY_AND_EVALS.md).

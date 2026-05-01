# مراقبة البيئة — Staging / Production

## متغيرات (اختياري)

| المتغير | الغرض |
|---------|--------|
| `SENTRY_DSN` | أخطاء واستثناءات |
| `LANGFUSE_PUBLIC_KEY` / `LANGFUSE_SECRET_KEY` | تتبع prompts وتقييم |
| `LANGFUSE_HOST` | افتراضي `https://cloud.langfuse.com` |

## مبدأ

- لا تُفعّل في **test** أو **CI** إلا إن رغبت بمشروع Langfuse منفصل.
- staging أولاً، ثم production.

## Request ID والارتباط مع traces

- كل طلب يمر عبر [`api/middleware.py`](../api/middleware.py): يُولَّد `request_id` أو يُؤخذ من رأس **`X-Request-ID`**.
- اربط السجلات مع Langfuse عبر نفس المعرّف داخل metadata/trace يدوياً حيث تُستدعى نماذج — انظر [`AI_OBSERVABILITY_AND_EVALS.md`](AI_OBSERVABILITY_AND_EVALS.md).

## الكود

`api/main.py` يحاول استيراد `dealix.observability` — إن لم يكن الحزمة مثبتة يتجاهل بهدوء.

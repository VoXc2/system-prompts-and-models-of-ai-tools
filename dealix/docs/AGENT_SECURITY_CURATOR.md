# Agent Security Curator

طبقة تقلل تسرّب الأسرار وتمنع تطبيقات patch خطرة **قبل** دمجها في الريبو أو تشغيلها على بيئة تحتوي بيانات حقيقية.

## كود

| ملف | وظيفة |
|------|--------|
| `auto_client_acquisition/security_curator/secret_redactor.py` | `redact_secrets`، `scan_payload`، `sanitize_for_trace` |
| `auto_client_acquisition/security_curator/patch_firewall.py` | `inspect_diff` — قرار `allowed` حسب أنماط `.env` ومفاتيح |
| `auto_client_acquisition/security_curator/tool_output_sanitizer.py` | تجهيز مخرجات أدوات للتتبع |
| `auto_client_acquisition/security_curator/trace_redactor.py` | `redact_trace_payload` / `redact_span_metadata` — بنية JSON كاملة قبل Langfuse وغيره |

## API

- `GET /api/v1/security-curator/demo`
- `POST /api/v1/security-curator/redact` — جسم `{ "text": "..." }` أو حقول أخرى تُمسح ضمنياً عبر `scan_payload`
- `POST /api/v1/security-curator/inspect-diff` — `{ "diff_text": "..." }`
- `POST /api/v1/security-curator/trace/sanitize` — `{ "payload": { ... } }` لتنقية metadata التتبع

## ممارسات تشغيل

1. أي output وكيل يُرسل إلى أداة خارجية أو يُخزَّن: مرّره عبر `sanitize_for_trace` أو `redact_secrets`.
2. لا تعتمد على الـ API وحدها للـ CI: أضف فحصاً مشابهاً في pre-commit أو GitHub Action عندما تكون الجاهزية متوفرة.

## اختبارات

`tests/test_growth_tower_stack.py` — `test_patch_firewall_blocks_env`، `test_redact_github_token`، `test_security_curator_redact_route`.

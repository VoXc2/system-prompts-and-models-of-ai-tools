# Security Curator — منظومة حماية وكلاء Dealix

> **القاعدة الأولى:** لا سرّ يخرج من Dealix إلى log/trace/embedding/patch.
> الـ Security Curator هو الجدار الأول، يعمل قبل أي اتصال بأي قناة خارجية.

---

## 1. لماذا هذه الطبقة قبل أي tool live؟

Dealix يربط أدوات حساسة: WhatsApp Cloud, Gmail, Calendar, Moyasar, Google Meet, CRM. كل أداة فيها token، كل token خطر إذا تسرب. سابقاً تعرضنا لـPAT مكشوف، لذا قبل أي ربط حي:

- يجب أن يمر كل log/trace من **redactor**.
- يجب أن يمر كل diff من **patch firewall**.
- يجب أن يمر كل tool output من **sanitizer**.
- يجب ألا تخزّن أي assets مع secrets في الـembedding store.

---

## 2. الوحدات

| الوحدة | الدور |
|--------|------|
| `secret_redactor` | كشف وإزالة 11 نمط سر (GitHub PAT، OpenAI/Anthropic keys، Supabase JWT، WhatsApp/Moyasar/Sentry/Google API keys، AWS، private keys). |
| `patch_firewall` | يفحص الـunified diff قبل commit ويرفض الـ.env و service-account JSON و RSA keys. |
| `trace_redactor` | بالإضافة للأسرار، يخفي phones وemails داخل القيم النصية. |
| `tool_output_sanitizer` | يعقّم مخرجات الأدوات قبل إظهارها للمستخدم أو حفظها في الـledger. |

---

## 3. أنماط الأسرار المكشوفة

```
github_pat              ghp_***
github_pat_legacy       github_pat_***
openai_key              sk-***
anthropic_key           sk-ant-***
supabase_service_role   eyJ.***.***
whatsapp_token          EAA***
moyasar_secret          sk_***_***
langfuse_secret         lf_sk_***
sentry_dsn              https://***@***/***
aws_access_key          AKIA***
google_api_key          AIza***
private_key_block       BEGIN PRIVATE KEY *** REDACTED ***
```

ومفاتيح JSON الحساسة تُستبدل بـ`***` بناءً على substring match (case-insensitive) لـ:
`api_key, apikey, secret, token, password, authorization, access_token, refresh_token, client_secret, private_key, ssn, credit_card, card_number, cvv, iban, moyasar_secret`.

---

## 4. Patch Firewall

أي PR قبل ما يدخل الريبو:

1. **ملفات محظورة:** `.env`, `.env.local`, `.env.staging`, `.env.production`, `credentials.json`, `service-account*.json`, `id_rsa`, `*.pem`, `*.p12`, `*.pfx`.
2. **أسرار في الأسطر المضافة:** أي line يبدأ بـ`+` يُمرر من `detect_secret_patterns`.
3. الناتج: `PatchFirewallResult{safe, reasons_ar, blocked_files, secret_findings}`.

GitHub Push Protection يقبض الأسرار قبل push، لكن لا تعتمد عليه وحده — Patch Firewall يعمل في طبقة التطوير المحلية + CI.

---

## 5. Tool Output Sanitizer

قبل أن يصل أي مخرج إلى:
- الـAction Ledger
- الـProof Pack
- الواجهة (UI / WhatsApp / Email)
- Langfuse / Sentry

يمر عبر `sanitize_tool_output(output)` الذي يُرجع:
- `safe: bool`
- `redacted: <نفس الشكل، مُعقّم>`
- `notes_ar: ["تمت إزالة قيم حساسة من المخرج: ..."]`

---

## 6. Endpoints

```
GET  /api/v1/security-curator/demo
POST /api/v1/security-curator/redact
POST /api/v1/security-curator/inspect-diff
POST /api/v1/security-curator/sanitize-output
```

---

## 7. اختبارات الأمان (16 test)

- detect_github_pat لا يُرجع السر الخام أبداً.
- redact_openai_key يستبدل بالـmask.
- scan_payload يخفي `api_key` و`token`.
- inspect_diff يحظر `.env`.
- inspect_diff يحظر سراً مكتوباً داخل سطر مضاف.
- redact_trace يخفي phones/emails مع الحفاظ على الـdomain للسياق.
- sanitize_trace_event يحفظ `event_type/agent_name/latency_ms` ويعقّم `payload`.

---

## 8. ما لا تفعله هذه الطبقة

- لا تكشف السر الخام في الـlogs أبداً.
- لا تُرجع payload فيه token.
- لا توقع على diff فيه secret.
- لا تستبدل أو تعطّل GitHub Push Protection — هذه الطبقة **إضافة**، لا بديل.

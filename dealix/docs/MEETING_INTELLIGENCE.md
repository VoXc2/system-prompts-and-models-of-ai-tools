# Meeting Intelligence

تحويل **نص** (transcript أو ملاحظات) إلى ملخص عربي، استخراج اعتراضات، ومتابعة بعد الاجتماع — **بدون** إدراج أحداث تقويم حي من هذه المسارات.

## كود

| وحدة | ملاحظة |
|------|--------|
| `transcript_parser.py` | تلخيص نص طويل |
| `objection_extractor.py` | اعتراضات من النص |
| `followup_builder.py` | مسودة متابعة |
| `meeting_brief.py` | brief قبل الاجتماع من هياكل JSON |
| `deal_risk.py` | إشارات مخاطرة صفقة (تجريبي) |

## API

- `POST /api/v1/meeting-intelligence/transcript/summarize` — `{ "text": "..." }`
- `POST /api/v1/meeting-intelligence/followup/draft` — `{ "summary_ar": "...", "next_steps": [] }`
- `POST /api/v1/meeting-intelligence/brief/pre-meeting` — `{ "company": {}, "contact": {}, "opportunity": {} }`

## خصوصية

لا تُرسل تسجيلات حساسة إلى نماذج خارجية من مسارات الـ API الحالية دون موافقة DPA؛ المعالجة هنا deterministic على النص المُدخل.

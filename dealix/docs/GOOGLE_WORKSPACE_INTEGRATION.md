# Google Workspace — Gmail & Calendar (تصميم Dealix)

## النطاق الحالي في الكود

`auto_client_acquisition/personal_operator/integrations.py`:

- **مسودات فقط** (`draft_only`): `GmailDraftRequest`, `CalendarDraftRequest`.
- `approval_required=True` في النتائج.
- لا OAuth ولا استدعاء Google داخل هذا الملف.

## Scopes (مستقبل — عند تفعيل OAuth)

- Gmail: `https://www.googleapis.com/auth/gmail.compose` (مسودات) — توسيع الحدود يتطلب مراجعة أمنية.
- Calendar: `https://www.googleapis.com/auth/calendar.events` — **للإنشاء فقط بعد طبقة موافقة صريحة**.

## نموذج الموافقة

1. المستخدم يرى مسودة في Dealix.  
2. يضغط موافقة صريحة.  
3. المحول (adapter) ينفّذ على Google.  
4. السجل يُخزَّن في Revenue Memory / audit.

## متغيرات بيئة (لاحقاً)

- `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` — سيرفر فقط، rotation دوري.

## أمان

- لا مفاتيح في الريبو؛ لا tokens في embeddings.
- تصدير/حذف يتبع `docs/SECURITY_PDPL_CHECKLIST.md`.

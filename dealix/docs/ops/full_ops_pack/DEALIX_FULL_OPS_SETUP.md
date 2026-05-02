# إعداد Full Ops — Dealix Level 1

## 1) Spreadsheet

1. أنشئ Google Sheet باسم واضح (مثلاً `Dealix_Operating`).
2. أنشئ تبويب **`Form Responses 1`** (أو اربط الفورم ليُنشئه تلقائياً عند ربط الردود بالـ Sheet — [مساعدة Google](https://support.google.com/docs/answer/2917686)).
3. أنشئ تبويب **`02_Operating_Board`** بأعمدة متوافقة مع السكربت (انظر [LEVEL1_OPS_STRUCTURE_AR.md](LEVEL1_OPS_STRUCTURE_AR.md)).

## 2) Google Form

- اربط الإجابات بالـ Sheet أعلاه.
- اجعل **الموافقة (consent)** حقلًا مطلوبًا إن أمكن.
- احفظ معرف الـ Spreadsheet في `CONFIG.SPREADSHEET_ID` داخل [dealix_google_apps_script.gs](dealix_google_apps_script.gs).

## 3) Apps Script

1. من الـ Sheet: **Extensions → Apps Script**.
2. الصق محتوى [dealix_google_apps_script.gs](dealix_google_apps_script.gs) (يمكن تسمية الملف `dealix_apps_script.gs` في المحرر).
3. نفّذ **`setupDealixTrigger()`** مرة واحدة (يحتاج صلاحيات) لإنشاء trigger **`onFormSubmit`** يستدعي **`onDealixFormSubmit`**.
4. اختبار: **`testInsertRow()`** ثم إرسال تجريبي من الفورم.

**أسماء المعالجات في الريبو:** `onDealixFormSubmit` و`onFormSubmitDealix` (اسم بديل) يستدعيان نفس المنطق — انظر السكربت.

## 4) واتساب يدوي

لا تربط «نافذة خدمة واتساب» بمرجع مطوّري Google فقط؛ راجع [Bird — customer care window](https://docs.bird.com/applications/channels/channels/supported-channels/whatsapp/concepts/whatsapps-customer-care-window) وتشغيلك العملي في [WHATSAPP_OPERATOR_FLOW.md](../../WHATSAPP_OPERATOR_FLOW.md) (أو مزوّد مثل MyOperator حسب إعدادك).

## 5) قبول وأدلة

- [FULL_OPS_EVIDENCE_PACK_AR.md](FULL_OPS_EVIDENCE_PACK_AR.md) — جدول الأدلة والأوامر.
- [LEVEL1_FULL_OPS_LOOPS_AR.md](LEVEL1_FULL_OPS_LOOPS_AR.md) — ماذا يحدث عند كل تعطل.

# هيكل Level 1 — تبويبات وأعمدة (مرجع)

## تبويبات مقترحة

| التبويب | الغرض |
|---------|--------|
| `Form Responses 1` | ردود الفورم (قد يُنشأ تلقائياً عند الربط) |
| `02_Operating_Board` | صف واحد لكل lead بعد المزامنة من السكربت |
| `Dashboard` (اختياري) | صيغ تلخص العدّ من الـ Board |
| `Evidence_Tracker` (اختياري) | تبويب منفصل لتتبع لقطات/روابط أدلة Gate 100% |

## أعمدة مقترحة لـ `02_Operating_Board`

`timestamp` · `name` · `company` · `website` · `sector` · `city` · `goal` · `ideal_customer` · `offer` · `contact_method` · `whatsapp` · `email` · `consent` · `source` · `consent_source` · `recommended_service` · `lead_quality` · `missing_data` · `next_step` · `diagnostic_status` · `diagnostic_card` · `pilot_status` · `invoice_status` · `invoice_link` · `delivery_status` · `proof_pack_status` · `last_touch_at` · `risk_note`

عدّل أسماء الأعمدة في `dealix_google_apps_script.gs` (`CONFIG.COLUMNS`) لتطابق شيتك.

## تدفق

```text
Form → Form Responses 1 → Apps Script (onDealixFormSubmit) → صف في 02_Operating_Board → مراجعة بشرية → واتساب/إيميل
```

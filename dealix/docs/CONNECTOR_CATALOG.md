# Connector Catalog

مصدر الحقيقة للقائمة: `auto_client_acquisition/connectors/connector_catalog.py` — الدالة `build_connector_catalog()`.

## HTTP

`GET /api/v1/connectors/catalog` — يعيد `{ "connectors": [...], "count", "demo": true }`.

## الموصلات الحالية (MVP)

| id | ملاحظة |
|----|--------|
| `whatsapp` | مسودات ومعاينة قوالب؛ إرسال حي محظور في الكتالوج |
| `gmail` | إنشاء مسودة؛ إرسال حي محظور |
| `google_calendar` | مسودة حدث؛ إدراج حي محظور |
| `google_meet` | قراءة transcript مخطط؛ تسجيل بلا موافقة محظور |
| `linkedin_lead_forms` | استيعاب leads |
| `x_api`, `instagram_graph` | مسجّل فقط — لا firehose |
| `google_business_profile` | مسودة رد على مراجعة |
| `google_sheets` | قراءة مخطط |
| `crm` | مزامنة مسودة |
| `moyasar` | مسودة رابط دفع؛ شحن حي محظور |
| `website_forms` | webhook ingest؛ منع scraping |

## اختبارات

`tests/test_growth_tower_stack.py` — `test_connector_catalog_has_twelve_plus`.

# Connector Setup Guides

> دليل مرجعي لربط كل قناة. **القاعدة:** `draft_only` افتراضياً. لا live action قبل env flag صريح + اعتماد بشري.

---

## 11 Connectors المدعومة

| Key | Default Mode | Phase | Blocking للـ first service |
|-----|--------------|------:|--------------------------|
| gmail | draft_only | 1 | لا |
| google_calendar | draft_only | 1 | لا |
| google_sheets | approved_execute | 1 | لا |
| moyasar | manual | 1 | لا |
| whatsapp_cloud | draft_only | 1 | **نعم** |
| website_forms | approved_execute | 1 | لا |
| linkedin_lead_forms | ingest_only | 2 | لا |
| google_business_profile | draft_only | 2 | لا |
| crm_generic | draft_only | 2 | لا |
| google_meet | ingest_only | 2 | لا |
| instagram_graph | ingest_only | 3 | لا |

---

## 1. Gmail (drafts فقط افتراضياً)

**Scopes المطلوبة:**
- `gmail.compose` (لإنشاء drafts)
- `gmail.modify` (لإدارة الـ labels — read-only labels فقط في Phase 1)

**خطوات:**
1. Google Cloud Console → Create OAuth client.
2. أضف Dealix كـ application authorized.
3. منح الصلاحيات على scopes أعلاه فقط.
4. Dealix يستلم refresh_token + access_token.
5. وضع التشغيل: `connected_draft_only`.

**Live send:** يتطلب `GMAIL_ALLOW_LIVE_SEND=true` env + اعتماد بشري للرسالة.

---

## 2. Google Calendar (drafts فقط)

**Scopes:**
- `calendar.events` (drafts only)

**خطوات:**
1. نفس OAuth client من Gmail.
2. أضف scope الـ calendar.
3. Dealix يبني draft events.
4. لا insert إلا بعد:
   - `CALENDAR_ALLOW_LIVE_INSERT=true`
   - اعتماد بشري لكل event.

---

## 3. Google Sheets (read + append بموافقة)

**Scopes:**
- `sheets.readonly` للقراءة
- `sheets` للكتابة (append فقط)

**خطوات:**
1. نفس OAuth.
2. حدد الـ Spreadsheet ID المستخدم لـ Pilot.
3. Dealix يقرأ leads + يكتب Proof Pack.

**Live append:** يحتاج اعتماد للحقول الحساسة. لا overwrite تلقائي.

---

## 4. Moyasar (manual فقط في Phase 1)

**عملية الإعداد:**
1. حساب Moyasar dashboard.
2. **لا** إدخال API keys في Dealix.
3. عند طلب دفع:
   - Dealix يولّد invoice instructions (halalas-correct).
   - المؤسس يدخل Moyasar manually + ينشئ invoice.
   - يضع invoice URL في Dealix.
4. تأكيد paid: يدوي عبر Moyasar dashboard ثم تحديث pipeline_tracker.

**Phase 2:** ربط API + auto-invoice (مع env flag + audit).

---

## 5. WhatsApp Cloud (Blocking — drafts فقط)

**هذا أهم connector.** بدون WhatsApp opt-in audit، Dealix لا يفعّل first service.

**خطوات:**
1. Meta Developer Account → WhatsApp Business Cloud.
2. Phone number verification.
3. Webhook URL = Dealix endpoint.
4. **مهم:** opt-in audit أولاً عبر `whatsapp_strategy.requires_opt_in`.

**Live send:** يتطلب:
- `WHATSAPP_ALLOW_LIVE_SEND=true`
- opt-in موثّق لكل رقم.
- اعتماد بشري للرسالة.
- موافقة العميل على template.

---

## 6. Website Forms (آمنة)

**خطوات:**
1. أضف form على موقع العميل.
2. Webhook URL = Dealix endpoint.
3. كل form submission يدخل كـ `form.submitted` event.
4. Dealix يبني opportunity card تلقائياً.

**Live send:** auto-acknowledgment email/WhatsApp مسموح بعد opt-in في الـ form.

---

## 7. LinkedIn Lead Gen Forms (Phase 2)

**القاعدة:** lead forms فقط — **لا scraping** ولا auto-DM.

**خطوات:**
1. LinkedIn Campaign Manager → Lead Gen Form.
2. Hidden fields: `campaign_name`, `sector`, `sales_owner`.
3. Webhook إلى Dealix.
4. كل lead → `linkedin_lead_form` source = safe.

---

## 8. Google Business Profile (Phase 2)

**Scopes:**
- `business.manage`
- `reviews.read`

**خطوات:**
1. ربط GBP location.
2. Dealix يقرأ reviews.
3. يبني draft reply لكل review.
4. **Live publish** يحتاج اعتماد + `GBP_ALLOW_LIVE_REPLY=true`.

---

## 9. CRM Generic (Phase 2)

**Supported:** HubSpot, Salesforce, Zoho, Close.

**خطوات:**
1. OAuth حسب الـ CRM.
2. Read-only في الأسبوع الأول.
3. Write مع approval بعد الأسبوع الأول.
4. لا overwrite owner تلقائي.

---

## 10. Google Meet (Phase 2)

**Scopes:**
- `meetings.space.readonly`
- `conferenceRecords.transcripts.readonly`

**خطوات:**
1. OAuth.
2. ingest transcripts بعد موافقة كل المشاركين.
3. Dealix يستخرج objections + next steps + buyer intent.
4. **لا** real-time listening في Phase 2.

---

## 11. Instagram Graph (Phase 3)

**Phase 3 connector.** ingest only لـ comments + DMs + insights.

---

## Acceptance Criteria للـ connector

كل connector يُعتبر مُعدّ بنجاح إذا:
1. State = `connected_draft_only` أو `connected_approved_execute`.
2. Test successful (Dealix قرأ شيء أو كتب draft).
3. لا secrets exposed في الـ logs/traces.
4. Audit entry في Action Ledger.

---

## Troubleshooting

| مشكلة | الحل |
|------|------|
| OAuth callback failed | recheck redirect_uri في Google/Meta console |
| WhatsApp Webhook 401 | تحقق من verify_token |
| Moyasar invoice URL لم يصل | تحقق من dashboard email settings |
| Sheets quota exceeded | خفض الـ append rate أو ربط second Sheet |
| Calendar conflicts | استخدم `freebusy.query` قبل draft event |

---

## Endpoints

```
GET  /api/v1/customer-ops/connectors/catalog
POST /api/v1/customer-ops/connectors/summary
POST /api/v1/customer-ops/connectors/update
GET  /api/v1/customer-ops/connectors/demo
```

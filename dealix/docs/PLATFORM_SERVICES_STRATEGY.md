# Platform Services Strategy — برج التحكم بالنمو
## (Dealix Growth Control Tower)

> **الهدف:** تحويل Dealix من "WhatsApp Growth Operator" إلى **منصة نمو متعددة القنوات** تشتغل تحت سقف واحد، بسياسات أمان موحدة، ومسار اعتماد واحد، وبروتوكول أحداث موحد.

---

## 1. لماذا Platform Services؟

كل قناة (WhatsApp, Gmail, Calendar, LinkedIn, X, Instagram, GBP, Sheets, CRM, Moyasar, Website Forms) تحتاج:
- تطبيع الإشارات (signal normalization).
- سياسة قبول/رفض موحدة (PDPL-aware).
- حل هوية متقاطع (cross-channel identity).
- مدخل تنفيذي موحد (single tool gateway) لمنع الإرسال البارد، تسريب الأسرار، أو الدفع بدون تأكيد.
- صندوق بريد موحد (unified inbox) ببطاقات قابلة للاعتماد.
- سجل أفعال (action ledger) للمراجعة (SDAIA / PDPL).
- سجل أثر (proof ledger) لتسويق "كم وفّرنا، كم سحبنا، كم منعنا من مخاطر".

بدون هذه الطبقة، كل ميزة جديدة تحتاج تكامل مخصص → فوضى أمنية + أمنية + قانونية.

---

## 2. الوحدات (10 modules)

| # | الوحدة | الدور |
|---|--------|------|
| 1 | `event_bus` | تصنيف موحد لـ27 نوع حدث (whatsapp/email/calendar/lead/payment/review/social/partner/sheet/crm/action). |
| 2 | `identity_resolution` | دمج phone + email + CRM ID + social handles → هوية موحدة. |
| 3 | `channel_registry` | 11 قناة، لكل واحدة capabilities + allowed/blocked actions + PDPL notes. |
| 4 | `action_policy` | محرك قواعد (block_cold_whatsapp, block_payment_no_confirm, block_secrets, external_send_needs_approval...). |
| 5 | `tool_gateway` | المخرج التنفيذي الوحيد. كل أداة تمر من هنا → سياسة → draft / approval_required / blocked / ready. |
| 6 | `unified_inbox` | بطاقات قرار (≤3 أزرار، عربية، type+risk+recommended_action). |
| 7 | `action_ledger` | سجل كل فعل بمراحله (requested → approved → executed). |
| 8 | `proof_ledger` | عدّاد أثر (leads, meetings, drafts, sends, payments, revenue, risks_blocked, time_saved). |
| 9 | `service_catalog` | 12 خدمة قابلة للبيع تحت Dealix Operator OS. |
| 10 | (router + tests) | `api/routers/platform_services.py` + اختبارات شاملة. |

---

## 3. القنوات الـ11

```
whatsapp, gmail, google_calendar, moyasar, linkedin_lead_forms,
x_api, instagram_graph, google_business_profile, google_sheets,
crm, website_forms
```

كل قناة لها:
- `capabilities`
- `beta_status` (`live` / `beta` / `coming_soon`)
- `allowed_actions` / `blocked_actions`
- `risk_level`
- `notes_ar`

مثال: WhatsApp **يحظر** `cold_send_without_consent`. Gmail يستخدم `gmail.compose` فقط (drafts). Calendar `live_inserted=False` حتى يربط OAuth.

---

## 4. سياسة الأمان (Action Policy)

**قواعد block أساسية:**
1. WhatsApp بارد بدون consent → **blocked** (PDPL).
2. أي charge/refund بدون `user_confirmed=true` → **blocked**.
3. أي payload يحوي `api_key/secret/token/...` → **blocked**.

**قواعد approval_required:**
- أي إرسال خارجي (`send_*`) → اعتماد إنساني.
- إدراج موعد في تقويم → اعتماد.
- DM على سوشل → اعتماد + opt-in.
- صفقة قيمتها ≥ 200,000 ريال → اعتماد.

**default:** allow (للـ read-only data ops).

---

## 5. Tool Gateway

كل أداة (`whatsapp.send_message`, `gmail.compose`, `calendar.insert_event`, `moyasar.refund`, `gbp.reply_review`, ...) **يجب** تمر من `invoke_tool()`.

النتائج المحتملة:
- `unsupported` — أداة غير مسجلة.
- `blocked` — السياسة منعت.
- `approval_required` — تحتاج قبول إنساني.
- `draft_created` — افتراضياً (live env flag = OFF).
- `ready_for_adapter` — جاهز للتنفيذ الحقيقي إذا اشتغل live env flag.

**Live env flags** (افتراضياً كلها OFF):
```
WHATSAPP_ALLOW_LIVE_SEND
GMAIL_ALLOW_LIVE_SEND
CALENDAR_ALLOW_LIVE_INSERT
MOYASAR_ALLOW_LIVE_CHARGE
GBP_ALLOW_LIVE_REPLY
```

---

## 6. صندوق البريد الموحد (Unified Inbox)

8 أنواع بطاقات:
```
opportunity, email_lead, whatsapp_reply, payment,
meeting_prep, review_response, partner_suggestion, action_required
```

كل بطاقة:
- ≤3 أزرار (تطبيق قيد WhatsApp Reply Buttons).
- عربية (title_ar, summary_ar, why_it_matters_ar, recommended_action_ar).
- `risk_level` (low/medium/high).

البطاقات تُبنى تلقائياً من `PlatformEvent` عبر `build_card_from_event()`.

---

## 7. Proof Ledger

عدّاد يقيس الأثر العملي للمنصة:
```
leads_created, meetings_booked, drafts_approved,
messages_sent, payments_initiated, payments_paid,
revenue_influenced_sar, risks_blocked, time_saved_hours,
partner_opportunities, by_channel
```

هذا هو **Marketing Asset** — لتُري العميل: "في 30 يوم، نحن ساعدناك تعمل X، منعنا Y مخاطر، وفرنا Z ساعة".

---

## 8. خدمات قابلة للبيع (Service Catalog)

12 خدمة تجارية:
1. `growth_operator_subscription` — اشتراك شهري للمنصة.
2. `channel_setup_service` — ربط القنوات (one-time).
3. `lead_intelligence_service` — إثراء + تأهيل لقاءات.
4. `outreach_approval_service` — drafts + approval workflow.
5. `partnership_sprint` — فرص تعاون عبر Partner Graph.
6. `email_revenue_rescue` — استعادة عملاء إيميل.
7. `social_growth_os` — تنبيهات + drafts + جدولة.
8. `local_business_growth` — GBP + reviews + visibility.
9. `ai_visibility_aeo_sprint` — Answer Engine Optimization.
10. `revenue_proof_pack_service` — تقرير أثر لمستثمرين / عملاء.
11. `customer_success_operator` — خفض churn + توسيع.
12. `payments_collections_operator` — تذكير + تحصيل (Moyasar).

---

## 9. Endpoints (`/api/v1/platform/...`)

```
GET  /services/catalog
GET  /channels
GET  /channels/{channel_key}
GET  /policy/rules
POST /actions/evaluate
POST /actions/approve
GET  /ledger/summary
POST /events/ingest
GET  /inbox/feed
POST /identity/resolve
GET  /identity/resolve-demo
POST /tools/invoke
GET  /proof-ledger/demo
```

---

## 10. اختبارات

`tests/unit/test_platform_services.py` — تغطية لكل الوحدات الـ10:
- catalog completeness
- channel coverage + cold-send blocked
- event validation
- policy (cold WA blocked, secrets blocked, payment confirmation, external send approval, high-value review)
- gateway (unsupported / blocked / draft default / live flag check)
- identity multi-signal merge
- inbox card validation (≤3 buttons + valid type)
- action ledger summary
- proof ledger structure

---

## 11. ما لا تفعله هذه الطبقة

- **لا** ترسل واتساب فعلياً (افتراضياً draft).
- **لا** ترسل Gmail فعلياً.
- **لا** تدرج موعد في Google Calendar.
- **لا** تأخذ أو تعيد دفعة بدون user_confirmed.
- **لا** تخزن مفاتيح API في payload.

---

## 12. ما يلي

- ربط Adapters حقيقية (WhatsApp Cloud, Gmail, Calendar) خلف الـenv flags.
- استبدال in-memory ledgers بـ Supabase.
- تشغيل `proof_ledger` على بيانات إنتاج مع تجربة عميل واحد.

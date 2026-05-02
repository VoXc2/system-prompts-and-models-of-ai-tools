# Full Ops — Evidence Pack (AR)

**مسار التحقق:** نفس مسار Full Company Ops Verification — أدلة تشغيل + بوابات قبول.

**محاور مختصرة:** Technical · Form · Script · Board · Dashboard · WhatsApp · Sales · Finance · Delivery · Proof · Security · Daily ops

## أوامر التحقق من الريبو (`dealix/`)

```bash
cd dealix
python -m compileall api auto_client_acquisition
pytest -q
APP_ENV=test pytest -q --no-cov
python scripts/print_routes.py
```

**متوقع:** `compileall` بدون أخطاء؛ `825 passed` (مع تخطي e2e إن لم يكن السيرفر على `127.0.0.1:8001`)؛ `print_routes.py` يطبع قائمة المسارات (مثلاً `TOTAL_ROUTE_ROWS` في مئات).

## 1) جدول الأدلة (Owner | Tool | Test | Expected | Evidence | Status | Next Fix)

| Owner | Tool | Test | Expected | Evidence | Status | Next Fix |
|-------|------|------|----------|----------|--------|----------|
| Ops | Google Form | ربط Responses بالـ Sheet | صف يظهر في `Form Responses 1` | لقطة / رابط Sheet | ☐ | ربط من إعدادات الفورم |
| Ops | Apps Script | `setupDealixTrigger()` | Trigger `onFormSubmit` → `onDealixFormSubmit` | لقطة Triggers | ☐ | صلاحيات وتشغيل مرة |
| Ops | Apps Script | `testInsertRow()` | صف في `02_Operating_Board` | لقطة الصف | ☐ | تطابق أسماء الأعمدة |
| Ops | Form | إرسال حقيقي | نفس الصف يظهر في Board + `consent_source` | لقطة قبل/بعد | ☐ | `onDealixFormSubmit` / `onFormSubmitDealix` |
| Ops | Board | فتح Dashboard | أرقام تتحرك مع الحالات | لقطة أو صيغ | ☐ | Evidence_Tracker تبويب اختياري |
| Sales | Sheet | Pilot مسودة | نص 499 واضح | نص في الخلية | ☐ | انسخ من قسم Sales أدناه |
| Finance | Moyasar | فاتورة يدوية | مبلغ 499 SAR = **49900** هللة في API | لقطة لوحة / رد API | ☐ | [Create Invoice](https://docs.moyasar.com/api/invoices/01-create-invoice/) |
| Delivery | Sheet/Doc | 10 فرص / 5 رسائل | جدول + مسودات | ملف أو تبويب | ☐ | إن تعذّر 10 شركات → segments |
| Proof | Doc | Proof Pack | أرقام + next action بدون مبالغة | PDF/Doc | ☐ | مراجعة قانونية |
| Security | Railway/GitHub | لا مفاتيح في Sheet | لا `sk_live` في الخلايا | فحص يدوي | ☐ | Secrets في Variables فقط |
| Technical | pytest | الأوامر أعلاه | pass | لصق terminal | ☐ | — |

### Form / Script — اختبار الدالة

**اختبار:** `setupDealixTrigger()` ثم `testInsertRow()` ثم إرسال من الفورم لاختبار **`onDealixFormSubmit`**. في الريبو يوجد أيضاً **`onFormSubmitDealix`** كاسم بديل يستدعي نفس المعالج.

**ملاحظة:** في حديثك قد تُسمّى الدالة في واجهة Google `onFormSubmit` — في نسخة الريبو المعالج المسمّى للربط هو `onDealixFormSubmit` (انظر [dealix_google_apps_script.gs](dealix_google_apps_script.gs)).

## 3) Sales — نص Pilot 499 (مقترح للصق والتعديل)

```text
عرض Pilot — 499 ريال سعودي (غير شامل ضريبة إن وجدت حسب سياسة شركتك).

يشمل أسبوع عمل مركّز:
- تشخيص قناة وشريحة أولية
- حتى 10 فرص محتملة (أو segments إن تعذّر تفصيل 10 شركات)
- 5 مسودات رسائل + 3 متابعات مقترحة
- ملاحظات مخاطرة (قنوات آمنة فقط — بدون واتساب بارد)

الدفع: رابط فاتورة Moyasar يدوي بعد الموافقة. لا أتمتة live حتى تفعيل صريح.
```

## 8) Moyasar

**499 SAR = 49900** هللة (أصغر وحدة حسب وثائق Moyasar). لا تخلط مع `1.00 SAR` = `100` هللة عند الاختبار.

## 9) Delivery — funnel vs ops

إن تعذّر تسليم **10 فرص على شركات محددة** خلال الأسبوع:

- **Funnel:** وسّع التعريف (segments، قطاع، حجم) مع توثيق السبب في الـ Sheet.
- **Ops:** حدّث `delivery_status` و`risk_note` و`next_step` حتى لا يبقى lead بلا قرار.

## 12) pytest (تكرار للسجل)

```bash
APP_ENV=test pytest -q --no-cov
```

## مراجع سريعة

| الموضوع | الرابط |
|---------|--------|
| Railway | لوحة المشروع + Variables |
| Google Form → Sheet | [Google Help — اختيار مكان حفظ الردود](https://support.google.com/docs/answer/2917686) |
| Apps Script — Triggers | [Installable triggers](https://developers.google.com/apps-script/guides/triggers) |
| Moyasar Invoices | [Create Invoice](https://docs.moyasar.com/api/invoices/01-create-invoice/) |
| GitHub Actions — أسرار CI | [Using secrets in GitHub Actions](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions) |
| واتساب — نافذة خدمة | [Bird — customer care window](https://docs.bird.com/applications/channels/channels/supported-channels/whatsapp/concepts/whatsapps-customer-care-window) |
| تشغيل واتساب يدوي Dealix | [WHATSAPP_OPERATOR_FLOW.md](../../WHATSAPP_OPERATOR_FLOW.md) |

**تصحيح توثيقي:** لا تربط «نافذة خدمة واتساب للعميل» بمرجع Google Developers لوحده؛ نافذة الخدمة توثّق عند BSP (مثال Bird أعلاه) أو مزوّدك (مثل MyOperator). Google Developers يبقى مناسباً لـ **triggers** في Apps Script فقط.

## الخلاصة

1. **Technical evidence:** `compileall` + `pytest` + `print_routes` كما فوق.  
2. **Form evidence:** رد في Sheet + صف Board + trigger.  
3. **تدفق Lead:** Form → Responses → Script → Board → إنسان → Diagnostic → Pilot → فاتورة → تسليم → Proof → Scorecard.

انظر أيضاً: [LEVEL1_FULL_OPS_LOOPS_AR.md](LEVEL1_FULL_OPS_LOOPS_AR.md).

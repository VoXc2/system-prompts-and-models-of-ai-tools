# Dealix Level 1 — Full Ops Loops (نظام الدورات)

**المقصود بـ loops:** كل عملية لها دورة متكررة: **Trigger → Input → Action → Output → Status Update → Metric → Decision → Next Loop**. بدون loop واضح، العمل يتحول إلى سوالف وارتجال.

**مرافق:** [FULL_OPS_EVIDENCE_PACK_AR.md](FULL_OPS_EVIDENCE_PACK_AR.md) · [DEALIX_FULL_OPS_SETUP.md](DEALIX_FULL_OPS_SETUP.md) · [dealix_google_apps_script.gs](dealix_google_apps_script.gs) · [WHATSAPP_OPERATOR_FLOW.md](../../WHATSAPP_OPERATOR_FLOW.md)

---

## القاعدة العامة

```text
Trigger → Input → Action → Output → Status Update → Metric → Decision → Next Loop
```

**مثال:**

```text
Lead دخل الفورم → بياناته وموافقته → Apps Script يضيفه في Board → diagnostic_card
→ status = new → Total leads يزيد → قرار: Diagnostic أو بيانات ناقصة → WhatsApp / Delivery Loop
```

---

## 1) Lead Capture Loop

**تبدأ:** Form، wa.me، LinkedIn، X، إحالة، outreach يدوي.

**المفروض:** عميل يعبّي Form → يظهر في `Form Responses 1` → Script ينظم الصف في `02_Operating_Board` → `source` + `consent_source` → `next_step` → تنبيه المالك.

**تقنياً:** ربط ردود الفورم بالـ Sheet ([Google Help](https://support.google.com/docs/answer/2917686)).

**متى تعتبر شغالة:** رد حقيقي في Form Responses؛ نفس العميل في Board؛ `next_step` غير فارغ.

| المشكلة | المعنى | التصرف |
|---------|--------|--------|
| الرد ما ظهر | Form غير مربوط | Responses → Link to Sheets |
| ظهر في Form فقط | Trigger/Script | `setupDealixTrigger` + صلاحيات |
| بدون consent | الفورم ناقص | جعل الموافقة required |
| بدون next_step | mapping ناقص | راجع السكربت والأعمدة |

---

## 2) Consent / Safety Loop

**المفروض:** موافقة مسجلة → `consent_source` → قناة مسموحة → لا cold WhatsApp → لا live automation غير مفعّلة.

**نافذة واتساب:** بعد رسالة العميل تفتح نافذة خدمة (~24 ساعة حسب السياسة)؛ بعدها قوالب معتمدة — [Bird — customer care window](https://docs.bird.com/applications/channels/channels/supported-channels/whatsapp/concepts/whatsapps-customer-care-window). للتشغيل اليدوي عندك: [WHATSAPP_OPERATOR_FLOW.md](../../WHATSAPP_OPERATOR_FLOW.md).

---

## 3) Qualification Loop

**المخرجات:** `recommended_service` · `lead_quality` · `missing_data` · `next_step`.

**Mapping مقترح:** أبغى عملاء → Growth Starter؛ اجتماعات → Meeting Sprint؛ شراكات → Partnership Growth؛ قائمة → Data to Revenue؛ وكالة → Agency Partner Pilot؛ متجر → Local Growth / Reactivation.

---

## 4) Diagnostic Card Loop

**المخرجات:** `diagnostic_card` · 3 فرص · مسودة رسالة · `risk_note` · `next_step` يشير لـ Pilot 499.

---

## 5) WhatsApp Conversation Loop

**أول رد (انسخ أو عدّل):**

```text
أهلاً 👋 أنا مساعد Dealix.

أساعدك تعرف:
مين تستهدف؟
وش ترسل؟
أي قناة أنسب؟
وكيف تحول الاهتمام لاجتماع.

وش هدفك الآن؟

1) أبغى عملاء
2) أبغى اجتماعات
3) أبغى شراكات
```

**مخرجات:** `whatsapp_status = active` · `last_touch_at` · تحديث `next_step` و`diagnostic_status`.

| المشكلة | المعنى | التصرف |
|---------|--------|--------|
| الرابط لا يفتح | رقم | `9665…` بدون `+` في wa.me |
| واتساب بدون صف في Sheet | sync | إدخال يدوي مؤقت |
| خارج نافذة الخدمة | timing | قالب معتمد أو يعيد التواصل |
| طلب إنسان | handoff | تحويل مباشر |

---

## 6) Mini Diagnostic Delivery Loop

**المفروض:** مراجعة الكرت → تعديل الفرص والرسالة → إرسال واتساب/إيميل → `diagnostic_status = sent` → `next_step` تجاري.

---

## 7) Follow-up Loop

**تبدأ:** بعد إرسال Diagnostic وعدم رد ~24h.

**تسلسل:** `diagnostic_status = sent` → لا رد → `next_step = follow-up` → رسالة قصيرة → تحديث `last_touch_at`.

**رسالة مقترحة:**

```text
متابعة سريعة فقط.

أقدر أرسل لك عينة إضافية:
فرصة واحدة + رسالة متابعة + توصية قناة.

إذا مناسب نكمل Pilot كامل.
```

| المشكلة | المعنى | التصرف |
|---------|--------|--------|
| leads عالقة | لا متابعة | فلتر `next_step` الفارغ |
| follow-up طويل | يضعف الرد | اختصر |
| تكرار بلا رد | إزعاج | أغلق أو nurture |

---

## 8) Sales / Pilot Loop

**إشارات اهتمام:** تمام، كم السعر، كيف نبدأ، أرسل مثال، خلنا نجرب.

**Moyasar:** 499 ريال = **49900** هللة ([Create Invoice](https://docs.moyasar.com/api/invoices/01-create-invoice/)).

| المشكلة | المعنى | التصرف |
|---------|--------|--------|
| مهتم بدون عرض | فجوة مبيعات | أرسل 499 صريح |
| عرض بدون سعر | احتكاك | `499 SAR` في الرسالة |
| قبول بدون فاتورة | مالية | Finance loop فوراً |
| رفض السعر | اعتراض | mini pilot أو دليل حالة |

---

## 9) Finance / Invoice Loop

فاتورة يدوية → `invoice_link` في Sheet → لا مفاتيح live داخل الخلايا.

---

## 10) Delivery Loop

**هدف:** intake → حتى 10 فرص → ≥5 مسودات → ≥3 متابعات مقترحة → `risk_note` → `delivery_status`.

إن تعذّر 10 شركات: **segments** + توثيق في الـ Sheet (انظر Evidence Pack §9).

---

## 11) Proof Pack Loop

تلخيص ما أُنشئ/ما حُمي/الموافقات → `proof_pack_status = delivered` → **next action** واقعي (بدون «نضمن مبيعات»).

---

## 12) Customer Success Loop — بعد Proof

**رسالة مقترحة:**

```text
هذا ملخص ما تم إنجازه في Pilot.

الخطوة الأنسب الآن:
1) نكمل أسبوع ثاني
2) نرفعها إلى Growth OS شهري
3) نشغل Partner Sprint
```

---

## 13) Dashboard / Metrics Loop

مؤشرات: Total leads · Diagnostics sent · Pilots offered/paid · Proof delivered · Revenue · Risks blocked — مع **Daily Scorecard** يومي.

---

## 14) Security Loop

**المفروض:** أي secret ظهر → rotate → تحديث Variables → لا مفاتيح في Sheet/Script/Git.

**أسرار CI/CD:** استخدم **GitHub Actions secrets** لتخزين القيم الحساسة خارج الكود ([Using secrets in GitHub Actions](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions)).

**Triggers في Apps Script** (لتشغيل السكربت عند الإرسال): [Apps Script triggers](https://developers.google.com/apps-script/guides/triggers) — هذا مرجع تقني للـ Script وليس بديلاً عن توثيق نافذة واتساب أعلاه.

| المشكلة | التصرف |
|---------|--------|
| مفتاح في chat | rotate |
| `WHATSAPP_ALLOW_LIVE_SEND=true` بدون سياسة | `false` حتى الموافقة |

---

## 15) Marketing Loop

يومياً: منشورات + لمسات وكالات + متابعة مصدر كل lead — **بدون واتساب بارد**.

---

## 16) Weekly Improvement Loop

أسبوعياً: أرقام → bottleneck → **تعديل واحد** للأسبوع القادم (بدون feature عشوائي أو تغيير تسعير بلا دليل).

---

## 17) مخطط الدورات الكامل

```text
Marketing → Lead Capture → Consent/Safety → Qualification → Diagnostic Card
→ WhatsApp → Diagnostic Delivery → Follow-up → Sales/Pilot → Finance
→ Delivery → Proof Pack → Customer Success → Dashboard/Metrics
→ Weekly Improvement ↺ Marketing
```

---

## 18) مؤشرات عملية (24h / 48h / 7d)

- **24h:** لمسات outbound · 1–2 leads · كرت يتولد · Dashboard يتحرك.
- **48h:** ~2 leads · 1 Diagnostic sent · 1 Pilot offered.
- **7d:** ~5 leads · 2 Diagnostics · 1 Pilot accepted/paid · 1 Proof.

---

## 19) أين الخلل؟

| العرض | Loop |
|--------|------|
| لا leads | Marketing |
| Form فقط | Lead Capture / Script |
| بدون `recommended_service` | Qualification |
| بدون كرت | Diagnostic Card |
| كرت بلا إرسال | Delivery / WhatsApp |
| بلا متابعة | Follow-up |
| اهتمام بلا عرض | Sales |
| قبول بلا فاتورة | Finance |
| دفع بلا تسليم | Delivery |
| تسليم بلا Proof | Proof |
| Proof بلا ترقية | Customer Success |
| أرقام بلا قرار | Dashboard / Weekly |
| مفاتيح مكشوفة | Security |

---

## الخلاصة

كل عملية **loop** وليس task مرة واحدة. إذا كل loop يخرج **evidence**، عندك **Dealix Level 1 Operating System** قابل للإثبات — مع [FULL_OPS_EVIDENCE_PACK_AR.md](FULL_OPS_EVIDENCE_PACK_AR.md).

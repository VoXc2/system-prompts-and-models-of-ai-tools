# First Pilot Delivery Workflow (48 ساعة)

> **القاعدة:** كل Pilot 499 ريال يُسلَّم خلال 48 ساعة. لا يتجاوز. لا live send. لا Moyasar API. لا scraping. كل خطوة approval-first.

---

## 1. الإطار العام

```
T+0  intake               (15 دقيقة)
T+24 Free Diagnostic      (3 فرص + رسالة + مخاطرة + توصية)
T+48 Pilot Delivery       (10 فرص + رسائل + متابعة + Proof Pack)
T+7  Follow-up Wave       (نتائج + اقتراح Growth OS أو case study)
```

**الهدف الفعلي:** أن يقول العميل "هذا أفضل من شغل وكالتنا الحالية" خلال 48 ساعة.

---

## 2. T+0 — Intake (15 دقيقة)

### الحقول المطلوبة

```
company_name        مثال: "حلول الراحة للأثاث"
sector              construction | clinics | logistics | f&b | retail | edtech | software | other
city                الرياض / جدة / الدمام / الخبر / مكة / المدينة / الطائف
ticket_size_sar     5_000 | 25_000 | 100_000 | 500_000+
contact_name        اسم صاحب القرار
contact_role        owner | gm | head_of_sales | head_of_marketing | other
icp_today           وصف العميل المثالي اليوم (3 أسطر)
last_3_clients      اسم القطاع + المدينة + حجم الصفقة (إن وُجد)
channels_used       whatsapp | gmail | linkedin_lead_forms | website_forms | calls
data_in_hand        crm | sheet | none
why_now             لماذا الآن؟ (3 أسطر — أول inbound dropped, slow Q, agency churn, ...)
red_flags           قطاعات/مناطق/أنواع لا يخدمها
opt_in_status       هل عنده WhatsApp opt-in موثق؟ نعم/لا
```

### مصدر الـ intake
- نموذج Google Form بسيط، أو
- محادثة WhatsApp/Email مكتوبة (نسخها يدوياً).

### بعد الـ intake
1. سجّل العميل في `PRIVATE_BETA_OPERATING_BOARD.md`.
2. أنشئ مجلد `pilots/<slug>/` فيه: `intake.md`, `diagnostic.md`, `pilot.md`, `proof_pack.md`.
3. أرسل تأكيد عربي:
   > وصلني intake. سأرسل لك Free Diagnostic خلال 24 ساعة. فيه 3 فرص محددة + رسالة جاهزة + مخاطرة موجودة + توصية. بدون أي إرسال خارجي بدون موافقتك.

---

## 3. T+24 — Free Diagnostic

### المحتوى المطلوب
1. **3 فرص B2B محددة بأسماء حقيقية**
   - اسم الشركة + قطاعها + مدينتها + سبب الاهتمام (why_now).
   - كل فرصة لها صاحب قرار مرشح (اسم + دور).
   - كل فرصة لها قناة موصى بها (whatsapp opt-in / gmail / website_form / linkedin lead form / call).

2. **رسالة عربية جاهزة (تحت 80 كلمة)**
   - نبرة سعودية طبيعية (لا "تحية طيبة وبعد"، لا synergy).
   - تستخدم اسم العميل + قطاعه + سبب التواصل.
   - تنتهي بـ CTA واضح (مكالمة 12 دقيقة / لقاء قهوة / تجربة مجانية).
   - تمر `safety_eval` + `saudi_tone_eval` قبل التسليم.

3. **مخاطرة موجودة الآن**
   - تسريب data، WhatsApp بدون opt-in، إيميل bounce rate عالي، رسالة فيها claim طبي/مالي ممنوع.
   - مع توصية إصلاح من `incident_router` أو `support_sla`.

4. **توصية خدمة واحدة من Service Tower**
   - First 10 Opportunities Sprint (499) أو
   - Growth Diagnostic Pro (1,500) أو
   - Partnership Sprint (2,500) أو
   - Growth OS Monthly (2,999/شهر).

### Endpoints المستخدمة
```
POST /api/v1/customer-ops/onboarding/checklist
POST /api/v1/service-excellence/review/all
POST /api/v1/operator/bundles
GET  /api/v1/launch/private-beta/offer
```

### قالب Diagnostic (عربي)

```
Diagnostic — <company_name>

أهم 3 فرص لك هذا الأسبوع:
1. <اسم الشركة 1> — <قطاع> — <مدينة>
   لماذا الآن: ...
   صاحب القرار: ...
   القناة: ...
2. ...
3. ...

رسالة عربية جاهزة (تحت 80 كلمة):
"<الرسالة>"

مخاطرة موجودة الآن:
- ...
التوصية: ...

الخدمة الموصى بها:
- First 10 Opportunities Sprint — 499 ريال — يبدأ غداً.
- نسلّم: 10 فرص + 10 رسائل + خطة متابعة 7 أيام + Proof Pack.

— Bassam
```

### بعد الإرسال
- حدّث `Operating Board`: `diagnostic_sent = today`, `next_step = pilot_offer`.
- تابع بعد 24 ساعة بقالب Follow-up #1.

---

## 4. T+48 — Pilot Delivery 499

### المحتوى المطلوب
1. **10 فرص B2B**
   - كل فرصة فيها: company_name, sector, city, decision_maker, role, channel, why_now (3 أسطر), رسالة عربية جاهزة (تحت 80 كلمة), risk_score (0..100), contactability (1..5).

2. **خطة متابعة 7 أيام**
   - يوم 1: الرسالة الأولى.
   - يوم 3: رسالة متابعة #1 (لو ما رد).
   - يوم 5: رسالة متابعة #2 (تحويل قناة لو احتاج — مثلاً WhatsApp إلى Email).
   - يوم 7: قرار: keep / drop / nurture.

3. **Proof Pack مختصر**
   ```
   opportunities_created: 10
   drafts_created:        10
   approvals_needed:      10
   risks_blocked:         <count>
   recommended_next_action: <Growth OS Monthly | Partnership Sprint | Growth Diagnostic Pro>
   upgrade_offer:         "نواصل شهرياً مقابل 2,999 ريال — أول شهر بسعر 1,999."
   ```

### Endpoints المستخدمة
```
POST /api/v1/operator/chat/message
POST /api/v1/customer-ops/connectors/summary
POST /api/v1/revenue-launch/payment/invoice-instructions
POST /api/v1/revenue-launch/proof-pack/template
GET  /api/v1/service-excellence/review/all
```

### قالب Pilot Delivery (عربي مختصر)

```
First 10 Opportunities Sprint — <company_name>

10 فرص أولى لك:
1. ...  | ...  | ...  | "<رسالة جاهزة>"
2. ...
...
10. ...

خطة متابعة 7 أيام:
- يوم 1: إرسال أول دفعة (5 رسائل) بعد اعتمادك.
- يوم 3: متابعة الرسائل بدون رد.
- يوم 5: تحويل قناة لمن لم يرد (Email → WhatsApp opt-in).
- يوم 7: قرار keep/drop/nurture.

Proof Pack:
- opportunities_created: 10
- drafts_created:        10
- approvals_needed:      10 (تنتظر اعتمادك)
- risks_blocked:         <count>

التوصية بعد 7 أيام:
- Growth OS Monthly (2,999 ر.س/شهر) — نواصل من حيث وقفنا.
- أو Case Study مجاني مقابل اقتباس.

— Bassam
```

### بعد الإرسال
- حدّث Operating Board: `pilot_offered = today`, `price = 499`, `paid = pending`.
- أرسل Moyasar invoice manual (URL يدوي).
- تابع تأكيد الدفع.

---

## 5. T+7 — Follow-up Wave + Proof Pack النهائي

### المحتوى
1. **Proof Pack نهائي**
   - leads_count + drafts_approved + replies + meetings_booked + pipeline_sar + risks_blocked.
   - chart مبسط: messages_sent vs replies vs meetings.
   - أهم 3 رسائل اعتمدها العميل (مع التعديلات إن وُجدت).
   - أهم 3 مخاطر تم منعها تلقائياً.

2. **جلسة مراجعة 30 دقيقة**
   - "ما الذي اشتغل؟ ما الذي لم يشتغل؟"
   - "نواصل شهرياً، ولا نوقف، ولا نحوّل لـ case study؟"

3. **3 مسارات للترقية**
   - **Growth OS Monthly** (2,999 ر.س/شهر) — استمرار شهري.
   - **Partnership Sprint** (2,500 ر.س لمرة) — لو فيه شراكات قابلة.
   - **Case Study + Referral** — مقابل اسم وكالة/عميل آخر يحتاج Pilot.

### Endpoints المستخدمة
```
POST /api/v1/customer-ops/cs/weekly-check-in
POST /api/v1/customer-ops/cs/success-plan
POST /api/v1/revenue-launch/proof-pack/template
GET  /api/v1/service-excellence/review/all
```

---

## 6. ما لا يحدث في Pilot Delivery

- لا live WhatsApp send بدون env flag + اعتماد.
- لا live Gmail send بدون env flag + اعتماد.
- لا Moyasar charge من API — invoice/payment-link manual فقط.
- لا scraping LinkedIn — Lead Gen Forms + استرشادي فقط.
- لا cold WhatsApp بدون opt-in — PDPL hard-block.
- لا تجاوز 48 ساعة — لو فيه عذر، نعتذر بدل أن نتأخر.
- لا تخفيض السعر بدون موافقة المؤسس — 499 ثابت.
- لا توسيع scope في الـ Pilot — 10 فرص فقط، الزيادة في Growth OS.

---

## 7. شروط نجاح Pilot

- [ ] Diagnostic سُلّم خلال 24 ساعة.
- [ ] Pilot سُلّم خلال 48 ساعة.
- [ ] العميل اعتمد ≥3 رسائل من العشرة.
- [ ] Proof Pack وصل خلال 7 أيام.
- [ ] جلسة مراجعة 30 دقيقة تمت.
- [ ] 1+ case study أو 1+ Growth OS subscription.
- [ ] CSAT ≥ 8/10.

---

## 8. مقاييس Pilot في Operating Board

| Metric | Target |
|--------|-------:|
| Pilot delivered ≤ 48h | 100% |
| Drafts approved (من 10) | ≥3 |
| Replies received | ≥1 |
| Meetings booked | ≥1 |
| Risks blocked | ≥1 |
| Upsell offered | 100% |
| Upsell accepted | ≥30% |
| CSAT | ≥8/10 |

---

## 9. القرار النهائي

```
Pilot ليس "محاولة بيع".
Pilot هو "أول إثبات أن Dealix يعمل لشركتك".
لو سُلّم في 48 ساعة + ≥3 رسائل اعتمدت + 1 رد + 1 اجتماع =
هذا Growth OS subscription بأعلى احتمال.
```

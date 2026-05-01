# Private Beta Operating Board

> **القاعدة:** كل prospect يدخل هذا الـ Board. كل خطوة تُسجّل. كل تأخير يولّد action item. هذا هو الـ source of truth للأسبوع.

---

## 1. أين يعيش هذا الـ Board؟

- **Primary:** Google Sheet خاص بك (لا تشاركه بصلاحيات edit مع أحد).
- **Backup:** نسخة في `pilots/operating_board.csv` (gitignored) في المستودع.
- **عدم التشارك:** هذا Sheet يحتوي PII لأشخاص لم يوافقوا — لا تشاركه.

---

## 2. الأعمدة (15 عمود)

| # | Column | النوع | شرح | مثال |
|---|--------|------|------|------|
| 1 | `company` | text | اسم الشركة الرسمي | شركة الأثاث المتقدم |
| 2 | `person` | text | اسم صاحب القرار | أحمد العتيبي |
| 3 | `segment` | enum | `agency` / `b2b_company` / `partnership` | b2b_company |
| 4 | `source` | enum | `linkedin_lead_form` / `referral` / `inbound` / `event` / `personal_network` | personal_network |
| 5 | `channel` | enum | `whatsapp` (opt-in) / `email` / `linkedin_dm_manual` / `call` | linkedin_dm_manual |
| 6 | `message_sent` | date | تاريخ إرسال أول رسالة | 2026-05-01 |
| 7 | `reply_status` | enum | `none` / `positive` / `objection` / `not_now` / `bounce` | positive |
| 8 | `demo_booked` | date \| null | تاريخ الديمو لو حُجز | 2026-05-03 |
| 9 | `diagnostic_sent` | date \| null | تاريخ تسليم Free Diagnostic | 2026-05-04 |
| 10 | `pilot_offered` | date \| null | تاريخ عرض Pilot 499 | 2026-05-05 |
| 11 | `price` | int | السعر المعروض (499 / 1500 / 2999) | 499 |
| 12 | `paid` | enum | `no` / `pending_invoice` / `paid` / `case_study` | pending_invoice |
| 13 | `proof_pack_sent` | date \| null | تاريخ تسليم Proof Pack | null |
| 14 | `next_step` | text | الإجراء التالي وتاريخه | 2026-05-06: follow-up #1 |
| 15 | `notes` | text | ملاحظات (بدون PII حساسة) | اهتم بـ partnerships في الرياض |

---

## 3. Status Flow

```
prospect_added
  → message_sent
    → reply_status (none | positive | objection | not_now | bounce)
      → demo_booked
        → diagnostic_sent (T+24)
          → pilot_offered (T+48)
            → paid (or case_study)
              → proof_pack_sent (T+7 من بدء Pilot)
                → renewal_or_upsell
```

كل عميل يجب أن يكون في حالة واحدة من هذه المراحل في كل لحظة.

---

## 4. أهداف الأسبوع (الصف الأول من الـ Board)

| Metric | Target | Tracking |
|--------|-------:|----------|
| Prospects added | 50–70 | عداد عمود `company` |
| Messages sent | 50–70 | عدد التواريخ في `message_sent` |
| Positive replies | 5–10 | `reply_status = positive` |
| Demos booked | 3–5 | عدد التواريخ في `demo_booked` |
| Diagnostics sent | 2–4 | عدد التواريخ في `diagnostic_sent` |
| Pilots offered | 2–3 | عدد التواريخ في `pilot_offered` |
| Paid | 1+ | `paid = paid` |
| Proof packs sent | 1+ | عدد التواريخ في `proof_pack_sent` |

---

## 5. ICP Distribution (في 50–70 prospect)

```
Agencies (B2B marketing agencies)        20%
Construction & home services             20%
Clinics + dental + aesthetic             15%
Logistics + last-mile                    15%
F&B (restaurants + cloud kitchens)       10%
Retail (offline + ecom)                  10%
EdTech / SaaS B2B                        10%
```

اضبط النسبة حسب القطاعات التي يخدمها العميل المثالي.

---

## 6. Cadence لكل prospect

| اليوم | الإجراء |
|------|--------|
| Day 0 | إرسال الرسالة الأولى + تسجيلها في الـ Board |
| Day 1 | تحقق من reply_status + Operating Board update |
| Day 2 | متابعة #1 (لو لا رد) — قالب Follow-up #1 |
| Day 4 | متابعة #2 (لو لا رد) — تحويل قناة لو منطقي |
| Day 7 | قرار keep / drop / nurture |
| Day 14 | nurture: رسالة قيمة (مثل Diagnostic مجاني للناس البطيئين) |

---

## 7. Follow-up Templates (3 موجات)

### Follow-up #1 (يوم 2)
> أنت اللي ذكرت <signal من الرسالة الأولى>. حضّرت لك مثال محدد لشركتك (3 فرص + رسالة جاهزة بالعربي + مخاطرة موجودة الآن). أرسله لك بعد ردك. ما يأخذ منك ≥3 دقائق.

### Follow-up #2 (يوم 4 — تحويل قناة لو منطقي)
> سمعت أن <event حقيقي للقطاع>. هذا أفضل وقت تجرب نموذج بسيط: 10 فرص + رسائل خلال 48 ساعة، 499 ريال، يبدأ غداً. لو ما عجبك في 7 أيام، تستردّ المبلغ.

### Follow-up #3 (يوم 7 — قرار)
> سأوقف المحاولات بعد هذه الرسالة. لو هذا توقيت غير مناسب، حدد لي شهر تجارب أخرى — وأذكّرك. مكتب مفتوح دائماً.

كل القوالب تمر `safety_eval` + `saudi_tone_eval` قبل الإرسال.

---

## 8. Daily Routine لإدارة الـ Board

### الصباح (15 دقيقة)
- افتح الـ Sheet.
- صفّ حسب `next_step` (date asc).
- نفّذ الـ next_step لكل prospect وصلت تاريخه.
- شغّل `paid_beta_daily_scorecard.py`.

### الظهر (15 دقيقة)
- أضف prospects الجدد (5–10 يومياً).
- خصّص الرسالة لكل واحد (اسم + قطاع + city + why_now).
- اعتمد drafts.

### آخر اليوم (10 دقائق)
- حدّث `reply_status` للذين ردّوا.
- حدّث `next_step` لكل prospect نشط.
- شغّل `paid_beta_daily_scorecard.py --json` واحفظه يومياً.

---

## 9. Privacy & PDPL

- **لا تشارك** هذا الـ Sheet بصلاحيات edit مع أحد.
- **لا تخزّن** أرقام واتساب لأشخاص لم يوافقوا opt-in.
- **لا تنسخ** الـ Sheet إلى أدوات خارجية بدون اتفاقية data processing.
- **احذف** البيانات بعد 90 يوم لمن لم يرد ولم يطلب nurture.
- **سجّل** كل export في Action Ledger.

---

## 10. مثال صف كامل

```
| company        | شركة الأثاث المتقدم            |
| person         | أحمد العتيبي                  |
| segment        | b2b_company                  |
| source         | personal_network             |
| channel        | linkedin_dm_manual           |
| message_sent   | 2026-05-01                   |
| reply_status   | positive                     |
| demo_booked    | 2026-05-03                   |
| diagnostic_sent| 2026-05-04                   |
| pilot_offered  | 2026-05-05                   |
| price          | 499                          |
| paid           | pending_invoice              |
| proof_pack_sent| null                         |
| next_step      | 2026-05-06: متابعة دفع invoice |
| notes          | اهتم بـ partnerships في الرياض |
```

---

## 11. Sheet template (CSV header للنسخ)

```csv
company,person,segment,source,channel,message_sent,reply_status,demo_booked,diagnostic_sent,pilot_offered,price,paid,proof_pack_sent,next_step,notes
```

ضع هذا الصف كـ header في Google Sheet جديد. ابدأ.

---

## 12. القرار

```
الـ Board ليس "نظاماً".
الـ Board هو "الذاكرة العاملة" لأسبوعك.
بدون الـ Board: prospects ينسون، follow-ups تضيع، payments تتأخر.
مع الـ Board: 50 prospect → 5 ردود → 3 ديمو → 1 paid.
```

# Dealix — Partner Send Queue

**Top 5 agency/partner messages — queued, not sent.** Sami sends Message 1 on LinkedIn → replies `PARTNER_SENT 1` → I release Message 2.

**Rule:** max 2 partner messages per day to avoid agency ecosystem burn.

---

## 1/5 — Wavy Saudi (white-label candidate, Scale tier)

**Platform:** LinkedIn DM — target senior leadership / partnerships director
**Why first:** Enterprise agency with deepest client pockets; white-label fit

```
السلام عليكم،

Wavy من أقوى الـ digital marketing agencies في السعودية — عملاؤكم enterprise، بيئة مثالية لـ white-label AI sales rep.

Dealix (AI sales rep عربي) ممكن يكون منتجكم الخاص — تحت اسم Wavy AI Sales مثلاً.

3 مسارات:
1. Reseller: 25% من MRR كل عميل
2. Service Provider: Setup 8K + retainer 25%
3. White-label (Scale tier): منتج باسمكم، شروط تناقش

20 دقيقة partner meeting هذا الأسبوع؟
🤝 https://dealix.me/partners.html
📅 https://calendly.com/sami-assiri11/dealix-demo

سامي
```

**After send:** tracker row 26 → `sent_at`, `next_followup=+3d`

---

## 2/5 — Peak Content (service exchange target)

**Platform:** LinkedIn DM — target founder / MD

```
السلام عليكم،

Peak Content تنتج محتوى + حملات lead-gen ممتازة. المشكلة الدائمة بعد lead يدخل الـ funnel: الرد بطيء، الـ lead يبرد.

Dealix (AI sales rep عربي) يسدّ هذي الفجوة — يرد على lead خلال 45 ثانية، يأهّله، يحجز demo.

اقتراح شراكة: تبيعونه كـ add-on فوق خدمتكم الحالية، setup 3,000 + 20-25% من MRR كل عميل. 3-5 عملاء فقط = 1,500-3,750 SAR شهرياً لكم دون أي tech work.

يناسبك 20 دقيقة demo هذا الأسبوع؟
🤝 https://dealix.me/partners.html
📅 https://calendly.com/sami-assiri11/dealix-demo

سامي
```

**After send:** tracker row 22 → `sent_at`, `next_followup=+3d`

---

## 3/5 — Digital8 (Growth tier fit)

**Platform:** LinkedIn DM — target head of growth

```
السلام عليكم،

Digital8 وكالة full-service في السعودية — محتوى، حملات، CRM. كل عميل B2B عندكم يخسر 20-30% من leads بسبب الرد البطيء.

Dealix (AI sales rep بالخليجي) يشتغل فوق خدمتكم: setup 8,000 + 25% من MRR كل عميل، يصير retainer add-on جديد لعملائكم الحاليين.

كم عميل B2B عندكم؟ لو 10+، الإضافة = 5,000+ SAR شهرياً لكم.

20 دقيقة demo + حساب أرقام؟
📅 https://calendly.com/sami-assiri11/dealix-demo
🤝 https://dealix.me/partners.html

سامي
```

---

## 4/5 — Brand Lounge (referral-only, enterprise reach)

**Platform:** LinkedIn DM — partnerships director

```
السلام عليكم،

Brand Lounge معروفة كبوتيك brand agency للعملاء enterprise في السعودية. هذا الـ profile مثالي لـ referral partnership مع Dealix (AI sales rep عربي).

الاقتراح: referral partner tier — 10% من MRR لـ 12 شهر لكل عميل يجي عبر Brand Lounge. لا setup fee، لا implementation، فقط introduction.

عميل enterprise واحد = 300-800 SAR شهرياً × 12 شهر = 3,600-9,600 SAR per-intro بدون أي جهد.

سؤال بسيط: هل في عملاء B2B عندكم الآن يعانون من slow lead response؟
🤝 https://dealix.me/partners.html

سامي
```

---

## 5/5 — Intermarkets (B2B white-label path, MENA reach)

**Platform:** LinkedIn DM — business development head

```
السلام عليكم،

Intermarkets Saudi تخدم B2B clients في العراق واﻹمارات والسعودية. Dealix يكمّل محفظتكم بقوة: AI sales rep بالعربي يرد على leads عميل B2B خلال 45 ثانية، يؤهّل، ويحجز demo.

للوكالات الإقليمية: white-label option — Dealix يعمل تحت اسمكم، أنتم تتحكمون في العلاقة مع العميل.

طرق التعاون:
1. Reseller 25% MRR
2. White-label (setup 25K + 30% MRR)
3. Referral 10% لـ 12 شهر

يناسبكم call قصير هذا الأسبوع؟
🤝 https://dealix.me/partners.html
📅 https://calendly.com/sami-assiri11/dealix-demo

سامي
```

---

## Follow-up cadence per partner

| Day | Type | Content |
|-----|------|---------|
| +0 | Initial | Message above |
| +3 | Soft bump | "متابعة للرسالة السابقة — هل فرصة لـ 15 دقيقة demo هذا الأسبوع؟" |
| +7 | Value-add | Send one-pager PDF + a specific sector case study (e.g., Foodics angle) |
| +14 | Last touch | "بدون لو ما وقتك مناسب، هل ممكن تعرفني على وكالة ثانية ترى الفرصة؟" |
| +30 | Nurture | Share any new Dealix case study or product update |

---

## What to track after each send

Update `pipeline_tracker.csv` (row-by-row) and here:
- `sent_at` timestamp
- Channel (LinkedIn DM)
- Variant used (which template)
- `next_followup` date
- Reply status + sentiment once received

---

**Publication rule:** never send the same message to multiple agencies. Always personalize the "why I think this fits you" line.

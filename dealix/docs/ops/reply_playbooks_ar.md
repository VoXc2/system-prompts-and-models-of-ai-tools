# Dealix — Reply Playbooks (Arabic Khaliji)

**16 reply categories × Arabic + English responses + next action + tracker status + follow-up date.**
**Use when a prospect replies. Don't improvise — pick category, paste response, log.**

Pairs with `objection_library_ar.md` (which handles deeper objection psychology).

---

## 1. Interested / "يهمّني"

**Signal phrases:** "مهم", "ممتاز", "أبي أعرف أكثر", "أرسل التفاصيل"

**Arabic response:**
> "رائع. أقترح 20 دقيقة مكالمة Zoom أوضح لك كيف يشتغل على بيزنس [اسم الشركة] تحديداً. اختر موعد يناسبك:
> 📅 https://calendly.com/sami-assiri11/dealix-demo"

**English response:**
> "Great. Let's do 20 minutes on Zoom — I'll walk through how Dealix works for a business like [company]. Pick a slot:
> 📅 https://calendly.com/sami-assiri11/dealix-demo"

**Next action:** BOOK_DEMO
**Tracker status:** `reply_status=interested, demo_booked_at=after confirmation`
**Follow-up:** +1d if no booking click

---

## 2. Price question / "كم السعر؟"

**Arabic:**
> "3 باقات: Starter 999 ريال شهري، Growth 2,999، Scale 7,999. الاختيار الصحيح يعتمد على حجم leads عندكم — 20 دقيقة demo وأفصل لك الباقة المناسبة. فيه pilot بريال واحد لمدة 7 أيام لو تبغى تجرّب قبل ما تقرر.
> 📅 https://calendly.com/sami-assiri11/dealix-demo"

**English:**
> "Three tiers: Starter 999 SAR/mo, Growth 2,999, Scale 7,999. Right fit depends on lead volume — 20-min demo to size it. 1 SAR × 7-day pilot available.
> 📅 https://calendly.com/sami-assiri11/dealix-demo"

**Next action:** BOOK_DEMO
**Tracker:** `reply_status=pricing_inquiry`

---

## 3. Send details / "أرسل لي تفاصيل"

**Arabic:**
> "أرسلت لك one-pager سريع: https://dealix.me
> أفضل طريقة تفهم Dealix هي 20 دقيقة مكالمة. PDF generic ما يخدم قراركم. احجز:
> 📅 https://calendly.com/sami-assiri11/dealix-demo"

**Next action:** PREPARE_DEMO_FLOW
**Tracker:** `reply_status=info_requested`
**Follow-up:** +3d with specific angle tailored to their sector

---

## 4. Send deck / "أرسل لي presentation"

**Arabic:**
> "احترم الطلب. الـ deck الجاهزة لا تعكس شركتكم — أفضل أفصّل demo لـ [اسم الشركة] تحديداً (20 دقيقة). بعدها أرسل deck مخصّصة بعد المكالمة. مناسب؟
> 📅 https://calendly.com/sami-assiri11/dealix-demo"

**Next action:** BOOK_DEMO (hold deck until after call)
**Tracker:** `reply_status=deck_requested`

---

## 5. Wants demo now / "أبي demo"

**Arabic:**
> "ممتاز، نسويها الآن أو خلال الساعة القادمة إذا عندك وقت.
> 📅 https://calendly.com/sami-assiri11/dealix-demo"

Or direct:
> "هل مناسب 4 عصر اليوم؟ أو غداً الساعة 11 صباحاً؟"

**Next action:** BOOK_DEMO
**Tracker:** `reply_status=demo_requested, demo_booked_at=<time>`

---

## 6. Later / "لاحقاً" / "بعدين"

**Arabic:**
> "تمام أفهم. سؤال واحد: متى الوقت المناسب يحتمل يكون؟ سأرجع لك في نفس اليوم بالظبط."

If they give a date → log + schedule.
If they don't → "سأرجع بعد 30 يوم، بالتوفيق."

**Next action:** FOLLOW_UP
**Tracker:** `reply_status=deferred, next_followup=<date>`

---

## 7. Not relevant / "ما يناسبنا" / "مو مناسب"

**Arabic:**
> "أحترم. سؤال أخير قبل ما أخرج من وقتك: هل عندكم شركات B2B سعودية تعرفونها تستفيد من AI sales rep بالعربي؟ 10% من MRR لـ 12 شهر لكل عميل يجي عبركم."

If they say yes → referral path.
If they say no → "تمام، شكراً لوقتك."

**Next action:** STOP_CONTACT (ask for referral first)
**Tracker:** `reply_status=not_interested, lost_reason=not_fit`

---

## 8. Budget objection / "ما عندنا budget"

**Arabic:**
> "صح، شهر كامل من Starter 999 ريال قد يكون صعب بدون إثبات. عرضنا الـ pilot بريال واحد لمدة 7 أيام — يدوي، قابل للاسترداد، هدفه يثبت لكم ROI قبل أي altزام. مناسب؟"

**Next action:** ROUTE_TO_MANUAL_PAYMENT (1 SAR pilot)
**Tracker:** `reply_status=budget_objection`

---

## 9. Timing objection / "مش الوقت المناسب"

**Arabic:**
> "أفهمك، Q-end / رمضان / عطل / الخ. سؤال: هل عندكم كل شهر شركات جايبة leads كثيرة وتتأخرون بالرد؟ إذا نعم، كل يوم تأخير = leads تذبل. الـ pilot بريال 7 أيام — إذا شفت أثر، نكمل. إذا ما شفت، نوقف."

**Next action:** ROUTE_TO_MANUAL_PAYMENT OR FOLLOW_UP +30d
**Tracker:** `reply_status=timing_objection`

---

## 10. Trust objection / "ما نثق في AI"

**Arabic:**
> "موقف عادل. نبدأ assist mode — AI يجهّز الرد، موظفكم يوافق قبل الإرسال. بعد 2-3 أسابيع من الجودة، تتحولون autopilot تدريجياً. صفر مخاطرة سمعة."

**Next action:** PREPARE_DEMO_FLOW (emphasize assist mode)
**Tracker:** `reply_status=trust_objection`

---

## 11. Already has CRM / "عندنا CRM"

**Arabic:**
> "CRM عندكم يخزّن الـ leads. Dealix يرد عليهم خلال 45 ثانية بالعربي قبل ما ينسون اسم شركتكم. هم يشتغلون مع بعض، مو بدائل. CRM = ذاكرة، Dealix = يدين تشتغل. نتكامل مع HubSpot / Salesforce / Zoho / أي شي webhook."

**Next action:** BOOK_DEMO (emphasize integration)
**Tracker:** `reply_status=crm_concern`

---

## 12. AI quality concern / "الرد مو طبيعي"

**Arabic:**
> "صح، معظم AI العربي سيء. Dealix مبني على prompts مخصصة للخليجي — ما يكتب 'حضرتك' ولا 'فخامتك'. 3 أمثلة من ردود فعلية أرسلها لك الآن عبر [رابط]. لو ما أعجبك، ما نكمل."

**Next action:** Send 3 real Arabic conversation screenshots
**Tracker:** `reply_status=ai_quality_concern`

---

## 13. Privacy / PDPL concern

**Arabic:**
> "مصمم PDPL-compliant: بياناتكم في سيرفرات السعودية، opt-out في كل رسالة email، audit log لكل interaction، processor agreement جاهز. أرسل PDPL compliance sheet لقسم القانوني؟"

**Next action:** Send PDPL docs + book demo
**Tracker:** `reply_status=privacy_concern`

---

## 14. Arabic accuracy concern / "هل يتكلم عربي مضبوط"

**Arabic:**
> "خليجي حقيقي، ما يترجم. 3 أمثلة حية من conversations فعلية — أرسلها لك الآن.
> أو أفضل: 20 دقيقة demo بلغتك أنت تختبرها مباشرة على سيناريو شركتكم."

**Next action:** Send Arabic samples OR book demo
**Tracker:** `reply_status=arabic_concern`

---

## 15. Integration concern / "هل يتكامل مع X؟"

**Arabic:**
> "HubSpot + Salesforce + Zoho + Bitrix = تكامل مباشر (OAuth). أي شي ثاني = webhooks generic. قل لي أداتكم بالضبط وأفصّل لك خطة الربط."

**Next action:** RESEARCH_MORE (then custom response)
**Tracker:** `reply_status=integration_concern`

---

## 16. Partnership interest / "نبغى نعرض على عملائنا"

**Arabic:**
> "ممتاز. عندنا 3 tiers للشركاء:
> - Referral: 10% من MRR × 12 شهر (بدون setup)
> - Agency: setup 3-15K + 20-30% MRR دائم
> - White-label (Scale): منتج باسمكم، شروط تناقش
> 20 دقيقة partner call نحدد الأنسب؟
> 🤝 https://dealix.me/partners.html"

**Next action:** PREPARE_PARTNER_PITCH
**Tracker:** `opportunity_type=AGENCY_PARTNER, reply_status=partnership_interest`

---

## Universal rules

1. **Reply within 30 minutes in business hours, 2 hours after hours.**
2. **Every reply → log category + next action in pipeline_tracker + reply_handling_log.md.**
3. **Never send all details at once. Use "hook → call → details" sequence.**
4. **For every category → one follow-up only, unless they re-engage.**
5. **Never promise features not built.**
6. **Sell the smallest pilot that proves value (1 SAR × 7 days).**

---

## Decision tree (visual)

```
REPLY RECEIVED
     │
     ├── positive signal? → Book demo (Calendly)
     │
     ├── question about price/details/demo? → Reframe → Book demo
     │
     ├── objection? → Use matching response from above
     │    └── still objecting? → Pilot 1 SAR offer OR disqualify gracefully
     │
     ├── "later/not now"? → Get specific date OR +30d follow-up
     │
     ├── "not interested"? → Ask for referral → disqualify
     │
     └── partnership interest? → PARTNER_PITCH flow
```

Every branch ends with a concrete next action AND a tracker update.

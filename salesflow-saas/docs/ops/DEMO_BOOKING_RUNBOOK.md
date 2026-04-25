# Dealix — Demo Booking Runbook

## How to Book First Demo
1. Prospect responds positively to outreach message
2. Send Calendly link: `calendly.com/sami-assiri11/dealix-demo`
3. Or propose 2 specific times: "يناسبك بكرة 11 ص أو 3 م؟"
4. Calendly sends confirmation to both parties

## Demo Preparation (30 min before)
- [ ] Open prospect's website in a tab
- [ ] Run `POST /api/v1/prospect/enrich-tech` with their domain — note what tools they use
- [ ] Run `POST /api/v1/prospect/route` with their company/sector — note classification
- [ ] Prepare 1 sector-specific pain point to mention
- [ ] Have Calendly open for follow-up booking if needed
- [ ] Have pilot offer ready (499 SAR / 7 days)

## Demo Flow (20 minutes)

**0:00-2:00 — Context Check**
- "شكراً على وقتك. قبل ما نبدأ — وش أكبر تحدي عندكم في متابعة الـ leads حالياً؟"
- Listen. Take note.

**2:00-5:00 — Discovery (3 questions)**
1. "كم lead تقريباً تستقبلون شهرياً؟"
2. "كم منهم يُتابع خلال أول ساعة؟"
3. "إيش يصير لـ leads اللي ما يُرد عليهم بسرعة؟"

**5:00-12:00 — Show Dealix**
- Show pricing/plans API response (real, live)
- Show enrich-tech on their domain (real detection)
- Show prospect/route classification
- Show prospect/message with their company name → generated Arabic message
- Explain: "هذا يصير تلقائي لكل lead يجيكم"

**12:00-16:00 — ROI Discussion**
- "لو عندكم [X] lead/شهر، و30% تضيع، يعني [Y] فرصة ضائعة"
- "Dealix يرد خلال 45 ثانية — كم من هذول ممكن تنحفظ؟"
- Do not guarantee numbers. Say "نقيسها معكم خلال 7 أيام"

**16:00-18:00 — Handle Objections**
- Price: "نبدأ بـ pilot 7 أيام بـ 499 ريال — لو ما شفت قيمة، استرداد كامل"
- CRM: "Dealix يشتغل فوق CRM الحالي — ما يستبدله"
- Arabic: "نبدأ manual + AI-assisted — نراجع أول الردود معك"
- Privacy: "متوافق PDPL — بيانات كل عميل منفصلة"

**18:00-20:00 — Close**
- Strong: "نبدأ الـ pilot الأسبوع الجاي؟"
- Medium: "أرسل لك تفاصيل الـ pilot وتقرر؟"
- Soft: "فكّر فيها — أتابع معك بكرة"

## After Demo (same day)
- [ ] Update tracker: demo_done = yes
- [ ] Send follow-up message:
  ```
  شكراً على وقتك اليوم [الاسم].
  
  ملخص: نقدر نجرب Dealix على [X] leads عندكم لمدة 7 أيام.
  الهدف: نقيس سرعة الرد وعدد المؤهلين والمواعيد المحجوزة.
  
  التكلفة: 499 ريال — مع ضمان استرداد.
  
  جاهز نبدأ؟
  ```
- [ ] If yes → send payment request (bank/STC Pay)
- [ ] If "need time" → schedule follow-up in 48h
- [ ] If no → ask "هل تعرف أحد ممكن يستفيد؟"

## What Qualifies a Successful Demo
- Prospect asks about pricing or pilot → high intent
- Prospect says "أبي أجرب" → convert immediately
- Prospect asks technical questions → engaged (answer, don't oversell)
- Prospect goes quiet → follow up in 24h, not immediately

## Recording
- Use Loom or OBS to record screen during demo (ask permission first)
- Save recording for internal review
- Do not share recording externally without consent

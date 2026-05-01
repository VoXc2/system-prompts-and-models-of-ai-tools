# Dealix — Demo Transcript (30 min, Arabic Khaliji)

**For rehearsal before every demo call. Memorize the rhythm, not the words.**
Paired with `dealix_demo_script_30min.md` (structural) and `dealix_battlecards.md` (per-sector).

---

## 0:00 – 2:00 · Warm-up + context

> **سامي:** "السلام عليكم [الاسم]. شكراً على الوقت. قبل ما نبدأ، هل تبغى أشرح Dealix سريع أو نقف 30 ثانية على شغلكم الحالي؟"

**If they say "خلاص اشرح":**
> "تمام. Dealix بسيط: AI sales rep بالعربي الخليجي. يرد على leads شركتكم خلال 45 ثانية، يؤهلهم، ويحجز demos. 3 أشياء تميزه:
> 1. عربي طبيعي — ما يترجم
> 2. يركب فوق CRM/booking اللي تستخدمونه
> 3. يبدأ يدوي وبعدها automation — صفر مخاطرة"

**If they say "خلنا نتكلم عن شغلنا أول":**
> "تمام. كم lead شهرياً تستقبلون من الـ inbound؟ وكم % تعتقد يبرد قبل ما يوصل للمبيعات؟"

---

## 2:00 – 5:00 · Discovery (3 key questions)

> **سامي:** "خلني أسأل 3 أسئلة سريعة قبل ما نخش في demo:"

1. **كم lead شهرياً عندكم؟** (expect: 50-500 for target SMB)
2. **إيش متوسط وقت الرد على lead جديد؟** (expect: "يعتمد" — hook: "هذا بالضبط المشكلة")
3. **إيش الأداة اللي تسجلون فيها leads؟** (expect: HubSpot/Sheet/WhatsApp/CRM)

**Listen. Write down answers. Don't interrupt.**

**Reflect back:**
> "طيب، إذا فهمت صح: [X leads/month]، متوسط الرد [Y ساعة]، تستخدمون [أداة]. مناسب أعرض لك demo مباشرة أم تبغى تشاركني scenario محدد؟"

---

## 5:00 – 18:00 · Live demo (13 min)

**Screen share:** dealix.me + backend dashboard

### Slide 1 — Problem (2 min)
> "في السعودية، متوسط الرد على lead B2B = 4 ساعات. خلال هالساعات، 50% من العملاء قرّبوا منافس. هذا تسريب revenue."

### Slide 2 — Dealix in 30 seconds (3 min)
Show the landing page prospector widget.

> "هذا الـ widget مباشر على dealix.me. أي زائر يكتب ICP، نرجع له قائمة leads مطابقة. جرب:"

**Type a scenario related to their business:**
> "شركات SaaS سعودية بحجم 20-100 موظف تستخدم HubSpot"

Show it returning real results.

### Slide 3 — Real Arabic conversation (3 min)
Open WhatsApp-style mockup. Type a fake lead question:
> "السلام عليكم، كم سعر باقة Enterprise؟"

Show Dealix response in 45 seconds:
> "وعليكم السلام، Enterprise يعتمد على عدد الموظفين. ممكن تخبرني كم موظف في شركتكم حالياً؟ وإيش المشكلة الأساسية اللي تحاولون حلها؟"

> **سامي:** "شفت الفرق؟ هذا رد طبيعي سعودي، يسأل البيانات المهمة، ويحجز demo في 3 رسائل كحد أقصى."

### Slide 4 — Tech stack detection (2 min)
Open `/api/v1/prospect/enrich-tech` with their domain:

> **سامي:** "خلنا نشوف شركتكم تحديداً..." 

Enter their domain. Show detected tools.
> "مثلاً، شفت إن موقعكم يستخدم HubSpot + WhatsApp widget. Dealix يركب فوق الاثنين — الـ WhatsApp يصير autopilot، والـ HubSpot يصير CRM للـ leads المؤهلة."

### Slide 5 — Pilot offer (3 min)
> "خلنا نتحدث عن الـ pilot. 7 أيام، ريال واحد، قابل للاسترداد 100% إذا ما أعجبك.
>
> ما يسير خلال الـ 7 أيام:
> - أنا شخصياً أضبط الـ prompts لشركتكم
> - أرد على 10-25 lead حقيقي خلال الأسبوع
> - يومياً ترسل لك تقرير قصير: كم lead، كم مؤهل، كم حجز موعد
> - بعد 7 أيام، نحكي — تكمّل Starter (999) أو نقف بدون التزام."

---

## 18:00 – 25:00 · Q&A / Objections

**Common objections (have scripts ready):**

### "كم السعر؟"
> "Starter 999 شهري، Growth 2,999، Scale 7,999. الاختيار يعتمد على حجم leads. بس قبل ما ندخل في الأسعار، هل أقدر أسأل: الـ pilot بريال واحد، معقول؟"

### "هل العربي مضبوط؟"
> "جربت ChatGPT العربي؟ سيء جداً. Dealix مختلف — prompts مخصصة للخليجي. أقدر أرسل لك الآن 3 أمثلة من ردود فعلية قبل ما نقفل — لو ما عجبتك، نوقف."

### "عندنا CRM"
> "Dealix ما يستبدل CRM. يشتغل قبله: يرد، يأهل، ويسلم الـ CRM قائمة جاهزة. تكامل مباشر HubSpot/Salesforce/Zoho، أو webhook مع أي أداة."

### "خلنا ندرس ونرجع لك"
> "تمام. سؤال بسيط: إيش بالضبط تبغى تقرر فيه؟ قد يكون شي أقدر أجيب عليه الآن. وإذا لا، أعطني تاريخ محدد نرجع فيه."

### "ما عندنا ميزانية"
> "أفهم. Pilot بريال واحد لمدة 7 أيام — هدفه بالظبط يحل هذا: نثبت القيمة قبل أي التزام. بعد 7 أيام، تقرر ببيانات فعلية."

---

## 25:00 – 28:00 · Close

Three possible closes:

### Strong close (if they're engaged):
> "خلنا نبدأ pilot الاثنين الجاي. أرسل لك تفاصيل الدفع (ريال واحد) وعقد الـ pilot الآن. مناسب؟"

### Medium close:
> "هل تتوقع القرار خلال 48 ساعة؟ أضع لك reminder وأتابع معك."

### Soft close:
> "إذا تبغى، أرسل لك الـ pilot agreement الآن، وتراجعه على راحتك. لو قررت المشي، ترد بـ 'نعم' وأبدأ الـ onboarding."

**Always end with one concrete next step + a specific date.**

---

## 28:00 – 30:00 · Set next step

Before hanging up:

1. **Send Calendly follow-up:** "راح أرسل لك دعوة Calendly للمتابعة خلال 30 ثانية."
2. **Log in tracker:** update `pipeline_tracker.csv` with outcome (interested/maybe/no + next action + date)
3. **Send demo recap email within 30 min** using this template:

```
السلام عليكم [الاسم]،

شكراً على الوقت اليوم. ملخص النقاط اللي تكلمنا عنها:

- الوضع الحالي: [X leads/month]، [Y response time]
- المشكلة الأساسية: [specific pain they mentioned]
- حل Dealix: AI sales rep بالعربي، يرد 45s، يؤهل، يحجز demo
- التكلفة: Starter 999 شهري / Pilot 1 ريال × 7 أيام

الخطوة التالية:
[Specific next step + date]

إذا تغير الوضع، أنا متاح دائماً.

سامي
```

---

## ❌ Do NOT say in any demo

- "نحن أفضل من Salesforce/HubSpot" — never disparage competitors
- "هذه الميزة بتجي بعد شهرين" — if feature not built, don't promise
- "نضمن X% زيادة" — no guarantees
- "هذا أرخص شي في السوق" — don't compete on price
- "خذ وقتك" — never say this; always push for specific next date

---

## ✅ Do say in every demo

- "سؤال مناسب"
- "أفهم مخاوفك"
- "خلني أعرض لك scenario من شغلكم تحديداً"
- "الـ pilot قابل للاسترداد 100%"
- "متى مناسب نتابع؟"

---

## Practice instructions

1. **Read this transcript 3 times before your first demo**
2. **Record yourself** running through it alone (30 min Zoom to yourself)
3. **Watch the recording** — note where you sound scripted vs natural
4. **Re-do** 1 more time
5. **First real demo** — stick to the structure, adapt words as natural
6. **After each demo** — update this transcript with what worked/didn't

---

*First demo will feel awkward. Demos 3-10 will be smooth. After demo 10 you'll own the rhythm.*

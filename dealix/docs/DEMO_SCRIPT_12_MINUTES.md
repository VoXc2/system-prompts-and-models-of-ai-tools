# Demo Script — 12 دقيقة

## الدقيقة 0–2 — الفكرة الكبرى

> "Dealix ليس CRM ولا أداة واتساب. Dealix يقول لك من تكلم اليوم، لماذا، ماذا تقول، وماذا حدث بعد ذلك. كل قناة (واتساب، إيميل، تقويم، مدفوعات) تتحول إلى كرت قرار عربي، أنت توافق أو ترفض، ثم Proof Pack."

اعرض الصفحة الرئيسية:
```
GET /
```

## الدقيقة 2–4 — Daily Brief

```
GET /api/v1/personal-operator/daily-brief
```

اعرض:
- 3 قرارات اليوم.
- فرص مفتوحة.
- مخاطر.
- launch readiness.

> "كل صباح، Dealix يبني لك هذه القائمة. ما تفتح 8 تطبيقات."

## الدقيقة 4–6 — Command Feed (Intelligence Layer)

```
GET /api/v1/intelligence/command-feed/demo
```

اعرض 6 بطاقات: opportunity / revenue_leak / partner_suggestion / meeting_prep / review_response / competitive_move.

> "كل بطاقة فيها: لماذا الآن، الإجراء المقترح، الأثر المتوقع، 3 أزرار: قبول/تخطي/تعديل."

## الدقيقة 6–8 — 10 فرص في 10 دقائق

```
GET /api/v1/intelligence/missions
POST /api/v1/intelligence/missions/recommend
```

> "هذه أول مهمة لكل عميل: 10 فرص B2B مناسبة بالعربي مع why-now ورسائل، خلال 10 دقائق."

## الدقيقة 8–10 — Trust + Simulator + Proof

```
POST /api/v1/intelligence/trust-score
POST /api/v1/intelligence/simulate-opportunity
GET  /api/v1/growth-operator/proof-pack/demo
```

اعرض:
- قبل أي إرسال، Trust Score (safe / needs_review / blocked).
- Simulator يحاكِ 100 جهة → expected pipeline + risk.
- Proof Pack: leads, drafts, meetings, risks_blocked, revenue_influenced.

> "هذا هو الفرق: لا نرسل بدون trust. لا ننفّذ بدون simulator. لا نختفي بدون proof."

## الدقيقة 10–12 — الأمان + التكاملات

```
GET /api/v1/security-curator/demo
GET /api/v1/connector-catalog/catalog
```

اعرض:
- أي token يدخل → يخرج كـ`***`.
- 14 تكامل، كل واحد له launch_phase + risk_level + blocked_actions.
- WhatsApp يحظر cold send افتراضياً.
- Moyasar لا يخزّن بطاقات.

> "Dealix مبني على قاعدة: لا نضرّ سمعة العميل. هذه أهم نقطة بيع للسوق السعودي."

## الإغلاق

> "Pilot 7 أيام: 499 ريال أو مجاني مقابل case study. خلال أسبوع: 10 فرص + رسائل + متابعة + Proof Pack. مستعد نبدأ يوم الأحد؟"

## القاعدة

- لا تظهر API keys على الشاشة.
- لا تعرض staging credentials.
- لا تعد بأرقام لم تُحقَّق.
- لا تشغّل live WhatsApp send في الـdemo.

# Private Beta Launch — Today's Plan

> **القرار:** ندشّن **Private Beta** اليوم، ليس Public Launch.
> **العرض الأساسي:** "10 فرص في 10 دقائق" + Pilot 7 أيام + Proof Pack.

---

## 1. العرض

```
Pilot 7 أيام: 499 ريال أو مجاني مقابل case study
- 10 فرص B2B مع why-now
- 10 رسائل عربية جاهزة
- contactability + سياسة عدم الإرسال البارد
- متابعة لمدة 7 أيام
- Proof Pack بعد الأسبوع

Paid Pilot 30 يوم: 1,500–3,000 ريال
Growth OS اشتراك شهري: 2,999 ريال
```

## 2. من نستهدف اليوم (أول 20)

1. وكالات تسويق B2B سعودية.
2. مستشارون نمو.
3. شركات تدريب B2B.
4. SaaS سعودية صغيرة-متوسطة.
5. شركات عقار/خدمات لديها واتساب نشط.
6. أصدقاء مؤسسين سعوديين.

## 3. Demo Flow (12 دقيقة)

راجع [`DEMO_SCRIPT_12_MINUTES.md`](DEMO_SCRIPT_12_MINUTES.md).

## 4. شروط القبول للعميل

العميل المثالي للـPrivate Beta:
- شركة سعودية أو خليجية B2B.
- لديها ≥3 موظفين مبيعات أو نمو.
- مرتاحة بالعربي + الإنجليزي.
- مستعدة لإعطاء feedback أسبوعي.
- تقبل أنه draft-first (لا live send افتراضياً).

## 5. ما يعمل الآن (Phase 1 ready)

- `/api/v1/personal-operator/daily-brief`
- `/api/v1/growth-operator/missions`
- `/api/v1/growth-operator/proof-pack/demo`
- `/api/v1/intelligence/command-feed/demo`
- `/api/v1/intelligence/missions` + `/missions/recommend`
- `/api/v1/intelligence/simulate-opportunity`
- `/api/v1/intelligence/board-brief/demo`
- `/api/v1/platform/services/catalog`
- `/api/v1/platform/inbox/feed`
- `/api/v1/platform/proof-ledger/demo`
- `/api/v1/security-curator/demo`
- `/api/v1/growth-curator/report/demo`
- `/api/v1/meeting-intelligence/brief/demo`
- `/api/v1/connector-catalog/catalog`

## 6. ما يبقى Draft فقط

- WhatsApp send (live flag OFF).
- Gmail send (live flag OFF).
- Calendar insert (live flag OFF).
- Moyasar charge (live flag OFF — invoice/link manual).
- Social DMs.

## 7. المخاطر

- WhatsApp: PDPL — لا cold بدون opt-in.
- Gmail: SPF/DKIM/DMARC للـdomain.
- Moyasar: live keys ممنوعة في staging.
- Secrets: GitHub Push Protection + Patch Firewall + Trace Redactor.
- Hallucinations: Saudi Tone + Safety evals قبل publish.

## 8. Go-Checklist قبل أول demo

- [ ] CI أخضر (`Dealix API CI`).
- [ ] `pytest -q` ≥663 passed.
- [ ] Staging URL يستجيب على `/health`.
- [ ] جميع env flags الـ`*_ALLOW_LIVE_*` = false.
- [ ] `secret_redactor` و`patch_firewall` يعملان.
- [ ] Demo URL مفتوح على `/api/v1/intelligence/command-feed/demo`.
- [ ] Demo URL مفتوح على `/api/v1/growth-operator/proof-pack/demo`.
- [ ] رسالة DM 1 جاهزة (راجع `FIRST_20_OUTREACH_MESSAGES.md`).

## 9. Post-Demo Checklist

- [ ] قائمة 5 demos مجدولة.
- [ ] قائمة 3 pilots محتملين.
- [ ] feedback مكتوب لكل demo.
- [ ] Proof Pack template جاهز.
- [ ] أول Moyasar invoice draft (إن وُجد عميل).

## 10. ما لا نفعله اليوم

- لا public launch.
- لا live WhatsApp send.
- لا charges.
- لا "نضمن نتائج".
- لا scraping.
- لا إصدار صحفي.

## 11. الخطوة التالية بعد أول 3 demos

- استخراج الاعتراضات الموحدة → cards في `command_feed`.
- معايرة الأسعار (هل 499 رخيص جداً؟).
- اختيار vertical: تدريب أو وكالات أو SaaS.
- تجهيز case study واحد على الأقل.

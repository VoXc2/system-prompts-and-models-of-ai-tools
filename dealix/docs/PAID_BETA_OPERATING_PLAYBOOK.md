# Paid Beta — دليل التشغيل التجاري (Dealix)

**الغرض:** تحويل **GO_PRIVATE_BETA** محلياً إلى **PAID_BETA_READY** على staging ثم إلى أول إيراد وتسليم Proof Pack — بدون توسيع تقني كبير وبدون وعود خطيرة.

**مرجع:** [`APPROVED_MARKET_MESSAGING.md`](APPROVED_MARKET_MESSAGING.md)، [`PROHIBITED_CLAIMS.md`](PROHIBITED_CLAIMS.md)، [`POSITIONING_LOCK.md`](POSITIONING_LOCK.md)، [`STAGING_DEPLOYMENT.md`](STAGING_DEPLOYMENT.md)، [`FIRST_PILOT_DELIVERY_WORKFLOW.md`](FIRST_PILOT_DELIVERY_WORKFLOW.md)، [`PRIVATE_BETA_OPERATING_BOARD.md`](PRIVATE_BETA_OPERATING_BOARD.md).

---

## 1. تعريف الحالات

| الحالة | المعنى |
|--------|--------|
| **Private Beta (محلي)** | `launch_readiness_check.py` بدون `--base-url` → `GO_PRIVATE_BETA`؛ CI أخضر؛ لا بيع مدفوع قبل staging إن كنت تعتمد على النشر. |
| **Paid Beta** | `STAGING_BASE_URL` + `python scripts/launch_readiness_check.py --base-url …` → **`PAID_BETA_READY`**؛ تحصيل يدوي (فاتورة / رابط / تحويل)؛ أول Pilot موقّع. |
| **Public Launch** | ليس الآن — انظر شروط الخروج في أسفل هذا الملف وفي [`PUBLIC_LAUNCH_GO_NO_GO.md`](PUBLIC_LAUNCH_GO_NO_GO.md). |

---

## 2. Staging (خلال أيام قليلة)

1. انشر API على **Railway** أو **Render** (انظر [`ops/RAILWAY_AI_COMPANY_BIND.md`](ops/RAILWAY_AI_COMPANY_BIND.md)).
2. Start: `uvicorn api.main:app --host 0.0.0.0 --port $PORT` — الاستماع على `PORT` الذي يحقنه المزود.
3. Health: `GET /health` → 200.
4. تحقق:
   ```bash
   export STAGING_BASE_URL="https://YOUR-STAGING-URL"
   python scripts/smoke_staging.py --base-url "$STAGING_BASE_URL"
   python scripts/launch_readiness_check.py --base-url "$STAGING_BASE_URL"
   ```
5. **لا تبدأ عرضاً مدفوعاً عاماً** إذا كانت النتيجة `NO_GO` — عالج السبب أولاً.

---

## 3. التحصيل اليدوي (بدون live billing من API)

- **Moyasar:** فاتورة يدوية أو رابط دفع (sandbox أو إنتاج حسب اتفاقك القانوني).
- **أو** تحويل بنكي مع مرجع واضح في العقد/الإيميل.
- رسالة اقتراح للعميل بعد الموافقة على النطاق (انظر [`FIRST_PILOT_DELIVERY_WORKFLOW.md`](FIRST_PILOT_DELIVERY_WORKFLOW.md) لنص Pilot 499).

**ممنوع في التواصل:** ضمان مبيعات، واتساب بارد جماعي، «AI يبيع بدالك 100٪»، scraping أو أتمتة رسائل LinkedIn — انظر [`PROHIBITED_CLAIMS.md`](PROHIBITED_CLAIMS.md).

---

## 4. حملة تواصل يدوية (7 أيام — أهداف مرجعية)

| الموجه | هدف مرجعي |
|--------|------------|
| تواصل مباشر (وكالات / مسوقين / B2B) | 50–70 رسالة على مدار الأسبوع (مو شرط يوم واحد) |
| ديمو | 5–7 محجوزة |
| Pilot | 3 تشغيل؛ إغلاق **1–2 مدفوعين** |
| Proof Pack | أول تسليم موثّق لكل عميل مدفوع |

**قنوات آمنة:** واتساب دافئ فقط مع سياق؛ إيميل مستهدف؛ LinkedIn يدوي للمؤسس — بدون أدوات سحب أو DMs آلية.

---

## 5. قياس الـ funnel

استخدم لوحة [`PRIVATE_BETA_OPERATING_BOARD.md`](PRIVATE_BETA_OPERATING_BOARD.md) (Sheet أو نسخة Markdown).

يومياً: سجّل `messages_sent`، الردود الإيجابية، الديمو، عروض الـ Pilot، طلبات الدفع، المستلم، Proof Packs.

سكربت تذكيري: `python scripts/paid_beta_daily_scorecard.py` (مع وسائط أو ملف JSON — انظر تعليمات السكربت).

---

## 6. شروط الانتقال إلى Paid Beta (تشغيل)

قبل أن تسمّي المرحلة «Paid Beta» تشغيلياً:

- [ ] **`PAID_BETA_READY`** على staging (`launch_readiness_check.py --base-url`).
- [ ] **3 ديمو** على الأقل محجوزة أو منجزة (حسب تعريفك).
- [ ] **1 Pilot مدفوع** أو التزام مكتوب واضح بالدفع.
- [ ] **أول Proof Pack** جاهز للتسليم (قالب + أرقام من المنتج/العملية).
- [ ] **لا إجراءات غير آمنة** (لا live send بدون موافقة، لا تجاوز لسياسة القنوات).
- [ ] **لا تسرّب أسرار** في الريبو أو في traces (انظر [`POST_MERGE_VERIFICATION.md`](POST_MERGE_VERIFICATION.md)).

---

## 7. شروط ما بعد 3 pilots (تحليل لا بناء)

بعد أول **3 pilots**، لا تضف ميزات كبيرة. راجع:

- أي خدمة بيعت أسرع؟
- أي صفحة أو رسالة جلبت ردّاً؟
- مدة الـ onboarding؟
- هل Proof Pack أقنع؟
- هل السعر مناسب؟ هل الـ support مثقل؟

ثم **ضاعف** على: Growth Starter، أو مسار الوكالة، أو List Intelligence — حسب البيانات لا حسب الحدس.

---

## 8. CI كبوابة دمج

فعّل **required status checks** على الفرع المحمي في GitHub حتى لا يُدمج كود فاشل. قائمة الـ jobs المطلوبة وأسماء الـ checks: [`BRANCH_PROTECTION_AND_CI.md`](BRANCH_PROTECTION_AND_CI.md). مرجع خارجي: وثائق GitHub عن status checks.

---

**آخر تحديث:** 2026-05-01

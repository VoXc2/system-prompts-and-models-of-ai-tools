# قائمة التشغيل التجاري — آخر قفل قبل الإيراد (Dealix)

**آخر تحديث مطلوب داخل الريبو لهذه المرحلة.** الريبو مقفول كـ **جاهزية تشغيل**، و`COMMERCIAL_GO_LIVE_CHECKLIST.md` هو **المصدر التنفيذي الواحد** — نفّذه حرفياً حتى تنتقل من **GO_PRIVATE_BETA** محلياً إلى **Paid Beta حقيقية** (`PAID_BETA_READY` على staging + أول دفع أو commitment + أول Proof Pack مُسلَّم).

**لا كود منتج جديد الآن.** ما بعد دمج هذا الملف **تنفيذ خارج الريبو بالكامل:** push، حماية الفرع، staging، دفع، outreach، pilot — إلا إذا فرض عميل **مدفوع** تغييراً تقنياً واضحاً بعد الـ pilots. **أي إضافة داخل الريبو بدون ضغط عميل مدفوع ستكون تشتيتاً** عن هذه المرحلة.

**وثائق مرتبطة:** [`BRANCH_PROTECTION_AND_CI.md`](BRANCH_PROTECTION_AND_CI.md)، [`STAGING_DEPLOYMENT.md`](STAGING_DEPLOYMENT.md)، [`ops/RAILWAY_AI_COMPANY_BIND.md`](ops/RAILWAY_AI_COMPANY_BIND.md)، [`PAID_BETA_OPERATING_PLAYBOOK.md`](PAID_BETA_OPERATING_PLAYBOOK.md)، [`FIRST_PILOT_DELIVERY_WORKFLOW.md`](FIRST_PILOT_DELIVERY_WORKFLOW.md)، [`PRIVATE_BETA_OPERATING_BOARD.md`](PRIVATE_BETA_OPERATING_BOARD.md).

---

## الحالة التنفيذية (ملخّص)

| المحور | الحالة |
|--------|--------|
| الريبو محلياً | جاهز (`GO_PRIVATE_BETA` عبر `launch_readiness_check`) |
| CI | مقسّم: `pytest`، `smoke_inprocess`، `launch_readiness` |
| حماية الدمج | تُفعّل يدوياً في GitHub بعد أول CI أخضر |
| Staging workflow | جاهز؛ ينتظر `STAGING_BASE_URL` في Secrets |
| Private Beta | **جاهزة تقنياً وتشغيلياً** (قبل الثلاثي أدناه) |
| Paid Beta حقيقية | `PAID_BETA_READY` + دفع/commitment + Proof Pack مُسلَّم |
| Public Launch | مؤجل إلى ما بعد الـ pilots |

---

## التسلسل الكامل (سطر تنفيذي)

```text
push → CI → protection → Railway → secret → staging workflow → PAID_BETA_READY → Moyasar → outreach → demo → pilot → Proof Pack
```

---

## التعريف النهائي

**لا تعتبر أن Dealix دخلت Paid Beta حقيقية** إلا بعد اكتمال **الثلاثي:**

```text
PAID_BETA_READY
+ أول payment أو commitment
+ أول Proof Pack مُسلَّم
```

قبل هذا: **Private Beta جاهزة تقنياً وتشغيلياً**. بعد هذا: **Paid Beta حقيقية**.

---

## 0 — ادفع التغييرات وشغّل CI

من **جذر المونوريبو** (المجلد الذي فيه `.github/` و`dealix/`) — **ليس** فقط داخل `dealix/`:

```bash
git status
git add dealix/docs/COMMERCIAL_GO_LIVE_CHECKLIST.md \
        dealix/docs/BRANCH_PROTECTION_AND_CI.md

git commit -m "docs: finalize commercial go-live checklist"
git push
```

إذا عدّلت أيضاً ملفات أخرى (مثل `PRIVATE_BETA_RUNBOOK.md` أو workflows) في نفس الدمج، أضفها إلى `git add` قبل الـ commit.

ثم راقب GitHub → **Actions** حتى تنجح **Dealix API CI** والـ jobs:

```text
pytest
smoke_inprocess
launch_readiness
```

**مهم (GitHub):** أسماء **jobs** يجب أن تكون **فريدة عبر workflows** حتى لا تصبح status checks **مبهمة**. الـ **required status checks** لا تظهر كخيارات عادةً إلا إذا **نجحت داخل الريبو خلال آخر ~7 أيام**. وإذا وُجد **check** و**status** بنفس الاسم، فاختيار ذلك الاسم كـ required قد يجعلهما **مطلوبين معاً** — راقب القائمة قبل الحفظ. مراجع: [Troubleshooting required status checks](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/collaborating-on-repositories-with-code-quality-features/troubleshooting-required-status-checks?apiVersion=2022-11-28&utm_source=chatgpt.com)، [`BRANCH_PROTECTION_AND_CI.md`](BRANCH_PROTECTION_AND_CI.md).

---

## 1 — تفعيل حماية الفرع (GitHub)

**المسار:** Settings → Branches → Branch protection rules → Add rule — على `main` (أو فرع الإطلاق المحمي).

**فعّل (أسماء الخيارات في واجهة GitHub):**

- Require pull request before merging  
- Require status checks to pass  
- Require branches to be up to date  
- Require conversation resolution  
- Block force pushes  
- Block deletions  

**اختر required checks:** `pytest`، `smoke_inprocess`، `launch_readiness` (أو `Dealix API CI / …` حسب ما يعرضه GitHub).

---

## 2 — رفع Staging (Railway)

```bash
railway login
railway link
railway up
```

- **Start command:** `uvicorn api.main:app --host 0.0.0.0 --port $PORT`  
- **Healthcheck path:** `/health` (يتوقع **HTTP 200** ضمن المهلة)  

**Railway عملياً:** يتطلّب أن التطبيق يستمع على **`0.0.0.0:$PORT`**؛ المنصة **تحقن `PORT`** وتستخدمه في الـ healthchecks بحيث **لا يصبح النشر active** إلا بعد **HTTP 200** ضمن المهلة؛ و**عدم الاستماع على `PORT`** قد يؤدي إلى **service unavailable**. التحقق **قبل** التفعيل وليس مراقبة مستمرة بعد الـ live — [Healthchecks](https://docs.railway.com/reference/healthchecks?utm_source=chatgpt.com)، [Exposing your app](https://docs.railway.com/deploy/exposing-your-app).

**بعد النشر** — من **جذر المونوريبو** (نفس المجلد الذي فيه `dealix/`):

```bash
export STAGING_BASE_URL="https://YOUR-STAGING-URL"

python dealix/scripts/smoke_staging.py --base-url "$STAGING_BASE_URL"
python dealix/scripts/launch_readiness_check.py --base-url "$STAGING_BASE_URL"
```

بديل مكافئ: `cd dealix` ثم `python scripts/smoke_staging.py …` و`python scripts/launch_readiness_check.py …`.

**المطلوب:** `VERDICT: PAID_BETA_READY`. إذا `NO_GO` — لا تبدأ Paid Beta على الرابط؛ عالج السبب ثم أعد الفحص.

---

## 3 — Secret لـ GitHub Actions

**Settings → Secrets and variables → Actions → New repository secret**

- `STAGING_BASE_URL` = `https://YOUR-STAGING-URL`

ثم: **Actions → Dealix staging smoke → Run workflow**.

**النتيجة المطلوبة:** `smoke_staging` OK، ثم `launch_readiness_check` مع `--base-url` → **PAID_BETA_READY** (إثبات أن الاستضافة تطابق الجاهزية المحلية).

---

## 4 — Moyasar Invoice لأول Pilot (بدون live charge من API)

من **Moyasar Dashboard** أنشئ invoice يدوي (أو رابط دفع). [Moyasar — Creating invoices](https://docs.moyasar.com/guides/invoices/creating-invoices/) — يمكن الإنشاء من لوحة التحكم أو API وإرسالها أو عرضها للعميل يدوياً أو آلياً. **لا تبنِ billing API داخل المنتج الآن.**

**لوحة التحكم (مثال):**

```text
Amount: 499 SAR
Description: Dealix Private Beta Pilot — 7 days
Expiry: 7 days
```

**إن استخدمت API لاحقاً:** المبلغ بأصغر وحدة عملة — **1 SAR = 100 هللة** → **499 SAR = 49900** (راجع وثائق Moyasar لنسختك).

**نص الإغلاق (للعميل):**

تمام، نبدأ Pilot لمدة 7 أيام بـ499 ريال.

يشمل:

- 10 فرص مناسبة  
- رسائل عربية جاهزة  
- فحص مخاطر القنوات  
- خطة متابعة 7 أيام  
- Proof Pack مختصر  

بعد الدفع أحتاج منك: رابط موقعكم، القطاع المستهدف، المدينة، العرض الرئيسي، ومن هو العميل المثالي لكم.

**خيار case study:** بداية مجانية مقابل case study مختصر إذا كانت النتائج مفيدة — نفس التسليم (10 فرص + رسائل + متابعة + Proof Pack)، **بدون** نشر بيانات حساسة أو أسماء عملاء إلا بموافقة واضحة.

---

## 5 — موجة التشغيل اليوم (يدوي فقط)

**ممنوع:** scraping، auto-DM، cold WhatsApp جماعي، أتمتة LinkedIn غير أصيلة — [`PROHIBITED_CLAIMS.md`](PROHIBITED_CLAIMS.md).

**هدف اليوم:** 25 تواصل يدوي، 5 follow-ups، 1 منشور LinkedIn، 1 منشور X، 1 محادثة شريك، 1 محاولة ديمو.

**التقسيم:** 10 وكالات/مسوقين، 5 تدريب/استشارات، 5 B2B SaaS أو خدمات تقنية، 5 شركات خدمات محلية.

### رسالة الوكالات

```text
هلا [الاسم]، أطلقنا Beta محدودة لـ Dealix للوكالات.

Dealix يساعد الوكالة تطلع فرص لعملائها، تجهز رسائل عربية، تدير الموافقات، وتطلع Proof Pack باسم الوكالة والعميل.

أبحث عن وكالة واحدة نجرب معها Pilot مشترك على عميل حقيقي. يناسبك ديمو 15 دقيقة؟
```

### رسالة الشركات

```text
هلا [الاسم]، أطلقنا Beta محدودة لـ Dealix.

الفكرة: نطلع لك 10 فرص B2B مناسبة، نكتب الرسائل بالعربي، وأنت توافق أو ترفض قبل أي تواصل، وبعدها نعطيك Proof Pack يوضح النتائج والمخاطر التي تم منعها.

يناسبك أعطيك Free Growth Diagnostic لشركتكم؟
```

### Follow-up

```text
أقدر أرسل لك عينة صغيرة بدل ديمو كامل:

3 فرص مناسبة لشركتكم + رسالة عربية واحدة + ملاحظة عن أفضل قناة للتواصل.

إذا أعجبتك، نكمل Pilot كامل.
```

**معيار يوم جيد:** 25 رسالة، 3–5 ردود، 1–2 ديمو، عرض pilot واحد، **0** إجراءات غير آمنة.

---

## 6 — Scorecard نهاية اليوم

من **جذر المونوريبو**:

```bash
python dealix/scripts/paid_beta_daily_scorecard.py \
  --messages 25 \
  --replies 0 \
  --demos 0 \
  --pilots 0 \
  --payments 0 \
  --proof-packs 0
```

مع نتائج فعلية:

```bash
python dealix/scripts/paid_beta_daily_scorecard.py \
  --messages 25 \
  --replies 4 \
  --demos 2 \
  --pilots 1 \
  --payments 1 \
  --proof-packs 0 \
  --json
```

بديل: `cd dealix` ثم `python scripts/paid_beta_daily_scorecard.py …`. تفاصيل الأعمدة: [`PRIVATE_BETA_OPERATING_BOARD.md`](PRIVATE_BETA_OPERATING_BOARD.md).

**معيار أسبوع مرجعي:** 70–100 تواصل، 15+ رد، 7 ديمو، 3 pilots، 1–2 مدفوع، Proof Pack واحد على الأقل.

---

## 7 — أول Pilot خلال 48 ساعة

### أول 30 دقيقة — intake

`company_name`، `website`، `sector`، `city`، `offer`، `ideal_customer`، `average_deal_value`، `has_contact_list`، `preferred_channels`، `current_sales_process`.

### خلال 24 ساعة — Diagnostic

3 فرص، 1 رسالة عربية، 1 مخاطرة، 1 توصية خدمة.

### خلال 48 ساعة — Pilot 499

10 فرص، why-now لكل فرصة، صاحب القرار المحتمل، القناة المقترحة، رسالة عربية، risk/contactability، خطة متابعة 7 أيام، Proof Pack مختصر.

### Proof Pack مختصر

`opportunities_created`، `drafts_created`، `approvals_needed`، `risks_blocked`، `recommended_next_action`، `upgrade_offer`.

التفاصيل: [`FIRST_PILOT_DELIVERY_WORKFLOW.md`](FIRST_PILOT_DELIVERY_WORKFLOW.md).

---

## 8 — اليوم لا تبني

أجّل بالكامل:

```text
Marketplace
White-label
Public Launch
Enterprise custom features
LinkedIn automation
Cold WhatsApp
Gmail live send
Moyasar API charge
```

**ابدأ ذلك فقط بعد:** 5–10 pilots، 2+ عملاء مدفوعين، weekly proof cadence، support flow ثابت، **0** unsafe actions.

**لا تضف أي كود منتج جديد الآن.** نفّذ الأقسام **0→7** حرفياً؛ وبعد **أول عميل مدفوع** فقط نقرر ماذا يُبنى بعد ذلك.

---

## مراجع خارجية

- [GitHub — Troubleshooting required status checks](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/collaborating-on-repositories-with-code-quality-features/troubleshooting-required-status-checks?apiVersion=2022-11-28&utm_source=chatgpt.com)  
- [GitHub — About status checks](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/collaborating-on-repositories-with-code-quality-features/about-status-checks)  
- [Railway — Healthchecks](https://docs.railway.com/reference/healthchecks?utm_source=chatgpt.com)  
- [Railway — Exposing your app / public networking](https://docs.railway.com/deploy/exposing-your-app)  
- [Moyasar — Creating invoices](https://docs.moyasar.com/guides/invoices/creating-invoices/?utm_source=chatgpt.com)  

---

**آخر تحديث:** 2026-05-01

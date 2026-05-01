# Runbook واحد — من Private Beta جاهزة إلى أول Proof Pack

**الهدف ليس «نبني أكثر». الهدف:**

```text
Private Beta جاهزة → Staging شغال → PAID_BETA_READY → أول عميل/التزام → Proof Pack → بعدها نقرر ماذا نبني
```

**مواد جاهزة للتنفيذ اليومي:**  
Layer 13 (بوابة عامة) → [`PUBLIC_LAUNCH_READINESS.md`](PUBLIC_LAUNCH_READINESS.md)  
Layer 14 (بريد + battlecards + ديمو ١٢ دقيقة) → [`sales-kit/START_HERE.md`](sales-kit/START_HERE.md) (قسم Layer 14)

**مراجع تقنية:** [`POST_MERGE_VERIFICATION.md`](POST_MERGE_VERIFICATION.md) · [`BRANCH_PROTECTION_AND_CI.md`](BRANCH_PROTECTION_AND_CI.md) · [`STAGING_DEPLOYMENT.md`](STAGING_DEPLOYMENT.md) · [`ops/RAILWAY_AI_COMPANY_BIND.md`](ops/RAILWAY_AI_COMPANY_BIND.md)

---

## المرحلة A — إغلاق GitHub (حماية الفرع)

| الخطوة | ماذا تفعل |
|--------|-----------|
| A1 | على الريبو: **Settings → Branches → Add rule** للفرع المحمي (مثلاً `ai-company` أو `main` حسب سياسة شركتك). |
| A2 | فعّل: **Require a pull request before merging**، **Require status checks to pass**، **Require branches to be up to date before merging**، **Require conversation resolution** (إن كان الفريق يستخدمها)، **Block force pushes**، **Block deletions**. |

**Checks المطلوبة (Dealix API CI):** اختر الأسماء **كما تظهر في واجهة GitHub** بعد أول تشغيل ناجح للـ workflow — عادة:

- `pytest`
- `smoke_inprocess`
- `launch_readiness`

إن ظهرت مُسبوقة باسم الـ workflow (مثل `Dealix API CI / pytest`)، اختر نفس الصيغة. إذا كان عندك check باسم `test` فقط من workflow آخر، **طابق ما يظهر عندك فعلاً** — لا تضف اسماً لا يُشغَّل على الـ PR. انظر أيضاً قسم «تفرّد أسماء الـ jobs» في [`BRANCH_PROTECTION_AND_CI.md`](BRANCH_PROTECTION_AND_CI.md).

**علامة نجاح A:**

```text
الفرع المحمي لا يقبل merge بدون PR + checks خضراء
لا force push ولا حذف للفرع المحمي
```

مرجع GitHub: [Troubleshooting required status checks](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/collaborating-on-repositories-with-code-quality-features/troubleshooting-required-status-checks)

---

## المرحلة B — Railway Staging (رابط حقيقي)

| الخطوة | ماذا تفعل |
|--------|-----------|
| B1 | Railway: **New Project → Deploy from GitHub** → الريبو `VoXc2/system-prompts-and-models-of-ai-tools` → الفرع **`ai-company`** (أو فرع النشر المعتمد). |
| B2 | **Service Root / Root Directory:** `dealix` (حزمة التطبيق). |
| B3 | **Variables (ابدأ بآمنة، بدون live keys):** `APP_ENV=staging`، `WHATSAPP_ALLOW_LIVE_SEND=false`، `MOYASAR_MODE=sandbox`، `PYTHONUNBUFFERED=1` — وأي مفاتيح LLM/DB حسب [`go-to-market/railway_vars_template.txt`](go-to-market/railway_vars_template.txt) أو [`STAGING_DEPLOYMENT.md`](STAGING_DEPLOYMENT.md). |
| B4 | **Start Command:** `uvicorn api.main:app --host 0.0.0.0 --port $PORT` |
| B5 | **Healthcheck Path:** `/health` |

**علامة نجاح B:**

```text
Deployment = Active
GET /health → 200
```

التطبيق يجب أن يستمع على `0.0.0.0` والمنفذ الذي يحقنه المضيف (مثل `$PORT` على Railway). مرجع: [Railway Healthchecks](https://docs.railway.com/reference/healthchecks)

---

## المرحلة C — فحص Staging من جهازك

بعد أن يكون لديك **Base URL** بدون شرطة مائلة أخيرة:

```bash
cd dealix
set STAGING_BASE_URL=https://YOUR-STAGING-URL.example   # Windows PowerShell: $env:STAGING_BASE_URL="https://..."
python scripts/smoke_staging.py --base-url "%STAGING_BASE_URL%"   # أو: --base-url $env:STAGING_BASE_URL
python scripts/launch_readiness_check.py --base-url "%STAGING_BASE_URL%"
```

(Linux/macOS: `export STAGING_BASE_URL=...` ثم نفس الأوامر بدون `%`.)

إذا فرض الـ staging مفتاح API: عيّن `STAGING_API_KEY` (يُرسل كـ `X-API-Key`) — انظر تعليقات [`scripts/smoke_staging.py`](../scripts/smoke_staging.py).

**علامة نجاح C:**

```text
smoke_staging.py ينتهي بنجاح (exit 0)
launch_readiness_check.py → VERDICT: PAID_BETA_READY و exit 0
```

**إذا ظهر NO_GO:** لا تبيع، لا رابط دفع، لا Pilot — عالج سبب الفشل (مسار، متغيرات، landing، إلخ) ثم أعد التشغيل.

---

## المرحلة D — GitHub Secret + Workflow

| الخطوة | ماذا تفعل |
|--------|-----------|
| D1 | **Settings → Secrets and variables → Actions → New repository secret** → `STAGING_BASE_URL` = `https://your-staging-host` (بدون `/` زائدة في النهاية إن أمكن). |
| D2 | **Actions → Dealix staging smoke → Run workflow** (يدوي `workflow_dispatch`). |

الـ workflow يشغّل [`dealix-staging-smoke.yml`](../../.github/workflows/dealix-staging-smoke.yml): `smoke_staging.py` ثم `launch_readiness_check.py --base-url "$STAGING_BASE_URL"`.

**علامة نجاح D:**

```text
Workflow أخضر عندما يكون STAGING_BASE_URL مضبوطاً
نفس PAID_BETA_READY من CI كما من جهازك
```

---

## المرحلة E — Moyasar (أول دخل بدون Billing API كامل)

| الخطوة | ماذا تفعل |
|--------|-----------|
| E1 | من **Moyasar Dashboard**: إنشاء **Invoice** — المبلغ **499 SAR**، وصف واضح (مثلاً: Dealix Private Beta Pilot — 7 days)، صلاحية مناسبة (مثلاً 7 أيام). |
| E2 | أرسل رابط الدفع عبر قناة موثوقة (إيميل أو رسالة **يدوية** مع opt-in). |

**ملاحظة وحدات API (للمستقبل):** في API غالباً المبلغ بالهللات؛ 499 ريال = `49900` هللة. راجع وثائق Moyasar الرسمية عند الربط البرمجي. مرجع مساعد: [Moyasar Dashboard: Invoice](https://help.moyasar.com/en/article/moyasar-dashboard-invoice-rf3kyd/)

**نص جاهز للعميل (مقتبس — عدّل حسب سياسة شركتك):**

```text
تمام، نبدأ Pilot لمدة 7 أيام بـ 499 ريال.
يشمل: 10 فرص مناسبة، رسائل عربية جاهزة للمراجعة، فحص مخاطر القنوات، خطة متابعة 7 أيام، Proof Pack مختصر.
بعد الدفع أحتاج: رابط الموقع، القطاع، المدينة، العرض الرئيسي، وصف العميل المثالي.
```

**علامة نجاح E:**

```text
فاتورة/رابط دفع جاهز + عميل استلم الرابط
```

---

## المرحلة F — مبيعات اليوم (تنفيذ يدوي آمن)

**هدف يوم واحد:**

```text
25 تواصل يدوي
5 follow-ups
1 منشور LinkedIn + 1 منشور X (أو منصة واحدة إن كان الوقت ضيقاً)
1 محادثة شريك
1 محاولة حجز ديمو
```

**قواعد:** لا scraping، لا auto-DM، لا واتساب بارد جماعي. التزم بسياسة المنصات — مثلاً LinkedIn يحدّ من برمجيات الالتقاط والإرسال غير الأصيل. مرجع: [LinkedIn — prohibited software and extensions](https://www.linkedin.com/help/linkedin/answer/a1341387/prohibited-software-and-extensions)

**تقسيم الـ 25:**

```text
10 وكالات B2B / مسوقين
5 شركات تدريب
5 B2B SaaS أو خدمات تقنية
5 خدمات محلية
```

**قوالب مختصرة** (طوّرها من [`sales-kit/layer14_email_sequences_4x7_ar.md`](sales-kit/layer14_email_sequences_4x7_ar.md)):

- **وكالة:** Beta محدودة + Pilot مشترك على عميل حقيقي + ديمو 15 دقيقة؟
- **شركة:** 10 فرص + رسائل عربية + موافقة قبل أي تواصل + Proof Pack + Diagnostic مجاني؟

**Follow-up مقترح:** عينة صغيرة (3 فرص + رسالة واحدة + قناة) بدل ديمو كامل إن احتجت تخفيف الاحتكاك.

**علامة نجاح F:**

```text
25 لمسة مُسجّلة في الـ Operating Board (انظر المرحلة G)
0 إجراءات غير آمنة (لا live send بدون موافقة وسياسة)
```

---

## المرحلة G — Operating Board (جدول تتبّع)

1. أنشئ Google Sheet: **`Dealix Paid Beta Operating Board`**.  
2. الصف الأول (عناوين أعمدة):

```text
company,person,segment,channel,message_sent_at,reply_status,demo_booked,diagnostic_sent,pilot_offered,invoice_sent,paid_or_commitment,proof_pack_sent,next_step,notes
```

3. نهاية اليوم — سجل الأرقام في **Daily Scorecard** (من مجلد `dealix`):

```bash
python scripts/paid_beta_daily_scorecard.py --messages 25 --replies 0 --demos 0 --pilots 0 --payments 0 --proof-packs 0
```

مع نتائج فعلية (مثال):

```bash
python scripts/paid_beta_daily_scorecard.py --messages 25 --replies 4 --demos 2 --pilots 1 --payments 1 --proof-packs 0 --json
```

**يوم جيد (مؤشرات تقريبية):**

```text
25 messages
3–5 replies
1–2 demos
1 pilot offered
0 unsafe actions
```

**علامة نجاح G:** الصفوف مكتملة + scorecard يعكس الواقع.

---

## المرحلة H — ديمو ١٢ دقيقة (خط زمني للمكالمة)

| الوقت | ماذا تقول / تعرض |
|--------|-------------------|
| 0–2 | المشكلة: بيانات وقنوات لكن لا وضوح في من + ماذا + متى + كيف تُثبت النتيجة. |
| 2–4 | Dealix: هدف نمو → خدمة واضحة → فرص، رسائل، موافقات، متابعة، Proof. |
| 4–7 | ثلاث خدمات فقط كأمثلة: First 10 Opportunities، List Intelligence، Growth OS Pilot (اضبط الأسماء مع كتالوجكم). |
| 7–9 | لا واتساب بارد، لا سحب LinkedIn، لا live بدون موافقة — draft وapproval-first. |
| 9–11 | Pilot 7 أيام بـ 499 ريال (أو العرض المعتمد عندكم). |
| 11–12 | «تبغى رابط الدفع ونبدأ اليوم؟» |

**سكربت مفصّل + اعتراضات:** [`sales-kit/layer14_demo_12min_script_ar.md`](sales-kit/layer14_demo_12min_script_ar.md) · جدول الدقائق: [`DEMO_SCRIPT_12_MINUTES.md`](DEMO_SCRIPT_12_MINUTES.md)

---

## المرحلة I — أول Pilot خلال ٤٨ ساعة

### أول ٣٠ دقيقة — Intake (اطلب)

```text
company_name, website, sector, city, offer, ideal_customer, average_deal_value,
has_contact_list, preferred_channels, current_sales_process
```

### خلال ٢٤ ساعة — Diagnostic (سلّم)

```text
3 فرص، 1 رسالة عربية، 1 مخاطرة، 1 توصية خدمة
```

### خلال ٤٨ ساعة — Pilot ٤٩٩ (سلّم)

```text
10 فرص، why-now لكل فرصة، صاحب قرار محتمل، قناة مقترحة، رسالة عربية،
مخاطرة/contactability، خطة متابعة 7 أيام، Proof Pack مختصر
```

**علامة نجاح I:** عميل استلم Diagnostic ثم حزمة Pilot ضمن الإطار الزمني المتفق عليه.

---

## المرحلة J — Proof Pack (هيكل التقرير)

```text
Dealix Proof Pack — Week 1

Client:
Service:
Period:

1. What was created
   - opportunities_created:
   - drafts_created:
   - followups_created:

2. What was protected
   - risks_blocked:
   - unsafe_channels_avoided:

3. What needs approval
   - approvals_needed:
   - recommended_next_actions:

4. Revenue impact estimate
   - potential_pipeline_sar:
   - confidence:

5. Next step
   - upgrade recommendation:
```

**رسالة تسليم مختصرة:** ملخص النقاط الأربع (فرص، رسائل، مخاطر ممنوعة، قناة، توصية تالية) + عرض ترقية منطقي إن وُجد.

**علامة نجاح J:** عميل استلم Proof Pack **مكتوباً ومُرسلاً** ويمكنه إعادة توجيهه داخل شركته.

---

## المرحلة K — بعد أول Pilot

| الحالة | ماذا تعرض / تسأل |
|--------|------------------|
| دفع + رضا | Growth OS شهري (مثلاً 2,999 ريال) — حدّد البنود مع كتالوج الخدمات والـ SLA. |
| لم يدفع | سؤال واحد: «هل المشكلة السعر، التوقيت، الثقة، أم وضوح القيمة؟» — **لا تبنِ ميزة جديدة** قبل فهم السبب. |
| وكالة مهتمة | Agency Partner Pilot: عميل واحد من طرفهم، Proof Pack بشعار مشترك، تقسيم ربح / referral. |

---

## المرحلة L — متى تبني كود جديد؟

فقط إذا تحقق **واحد** مما يلي:

```text
عميل مدفوع طلب نفس الشيء مرتين
3 pilots تعثروا لنفس السبب
التشغيل اليدوي يستهلك وقتاً واضحاً
Proof Pack يحتاج أتمتة لتسليم أسرع
Staging فشل بسبب bug حقيقي وليس إعداداً فقط
```

**قواعد الـ PR:** صغير، اختبار واضح، لا تغيير ضخم، لا «ميزة عامة» بدون طلب متكرر.

---

## تعريف «الإغلاق الكامل»

### تقني + تشغيلي

```text
GitHub: فرع محمي + checks مطلوبة
Railway staging: Active + /health = 200
PAID_BETA_READY من launch_readiness_check على staging
Staging smoke workflow أخضر (عند ضبط STAGING_BASE_URL)
```

### تجاري (Paid Beta «حقيقية»)

```text
PAID_BETA_READY
+ أول دفع أو commitment واضح
+ أول Proof Pack مُسلَّم للعميل
```

### حزمة يوم التنفيذ (مواد جاهزة)

```text
25 outreach + Operating Board + scorecard
ديمو 12 دقيقة (سكربت Layer 14)
تسلسلات بريد + battlecards (Layer 14)
Moyasar invoice جاهز للإرسال
```

---

## خريطة سريعة: أين الملف؟

| موضوع | ملف |
|--------|------|
| تحقق بعد الدمج محلياً | [`POST_MERGE_VERIFICATION.md`](POST_MERGE_VERIFICATION.md) |
| حماية الفرع وأسماء الـ CI jobs | [`BRANCH_PROTECTION_AND_CI.md`](BRANCH_PROTECTION_AND_CI.md) |
| Railway + ربط الريبو | [`ops/RAILWAY_AI_COMPANY_BIND.md`](ops/RAILWAY_AI_COMPANY_BIND.md) |
| بوابة Public Launch (Layer 13) | [`PUBLIC_LAUNCH_READINESS.md`](PUBLIC_LAUNCH_READINESS.md) |
| بريد 4×7 + battlecards + ديمو | [`sales-kit/START_HERE.md`](sales-kit/START_HERE.md) |

---

*آخر تحديث للهيكل: 2026-05-01 — طابق الأوامر مع نسخة السكربتات في الريبو عند التنفيذ.*

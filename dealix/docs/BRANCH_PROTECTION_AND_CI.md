# حماية الفرع و CI — Dealix

**الغرض:** ربط **نجاح الدمج** ببوابات تقنية ثابتة، وتقليل دخول كود غير مختبر إلى `main` (أو فرع الإطلاق الذي تختاره).

**مرجع سير العمل:** [`.github/workflows/dealix-api-ci.yml`](../../.github/workflows/dealix-api-ci.yml) في جذر المونوريبو.

---

## 1. ما الذي يشغّله CI اليوم؟

Workflow باسم **Dealix API CI** يحتوي على **ثلاثة jobs** منفصلة (لتعيينها كـ required status checks في GitHub):

| Job ID | ماذا يفعل |
|--------|-----------|
| **`pytest`** | `compileall` + `pytest -q --no-cov` + placeholder الـ embeddings + `run_evals` |
| **`smoke_inprocess`** | `python scripts/smoke_inprocess.py` |
| **`launch_readiness`** | `python scripts/launch_readiness_check.py` (بوابة **GO_PRIVATE_BETA** محلياً) |

**Staging و PAID_BETA_READY:** لا يُشغَّل تلقائياً على كل PR (يحتاج URL وأسرار بيئة). استخدم [`.github/workflows/dealix-staging-smoke.yml`](../../.github/workflows/dealix-staging-smoke.yml) يدوياً بعد ضبط `STAGING_BASE_URL` في GitHub Secrets، ثم من الجهاز:

```bash
python scripts/launch_readiness_check.py --base-url "$STAGING_BASE_URL"
```

---

## 2. إعداد Branch protection في GitHub

1. **Settings** → **Branches** → **Add branch protection rule** (أو تعديل قاعدة موجودة) للفرع المحمي (مثلاً `main`).
2. فعّل على الأقل:
   - **Require a pull request before merging**
   - **Require status checks to pass before merging**
   - **Require branches to be up to date before merging** (موصى به)
   - **Block force pushes**
   - **Block branch deletion** (للفرع الرئيسي، إن وُجد الخيار)
   - **Require conversation resolution before merging** (إن كان الفريق يستخدم مراجعات على التعليقات)

3. في **Status checks that are required**، أضف الثلاثة التالية (الأسماء كما تظهر غالباً بعد أول تشغيل للـ workflow):

   - `pytest`
   - `smoke_inprocess`
   - `launch_readiness`

   إن ظهرت مُسبوقة باسم الـ workflow، اختر الصيغة التي يعرضها GitHub (مثل `Dealix API CI / pytest`).

4. **ظهور الـ checks في القائمة:** GitHub يعرض عادةً الـ checks التي **اكتملت بنجاح خلال آخر سبعة أيام** حتى تُختار كـ required — إن لم تظهر الأسماء، شغّل الـ workflow مرة ناجحة (أو ادفع commit يمرّر الـ CI).

5. **تفرّد أسماء الـ jobs:** تجنّب تكرار **نفس اسم job** في workflows متعددة على نفس الريبو؛ قد يسبب تضارباً في نتائج status checks ويعطّل الدمج أو يربك القاعدة. احتفِ بـ `pytest` / `smoke_inprocess` / `launch_readiness` داخل **Dealix API CI** كمصدر واحد للبوابة على كل PR.

6. **اسم check مزدوج:** إذا ظهر **check** و**status** بنفس الاسم في القائمة، اختيار ذلك الاسم كـ required قد يجعل **الاثنين** مطلوبين — راجع أسماء الـ workflow/job في الواجهة قبل الحفظ.

**المرجع:** وثائق GitHub عن [required status checks](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/collaborating-on-repositories-with-code-quality-features/about-status-checks) و[Troubleshooting required status checks](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/collaborating-on-repositories-with-code-quality-features/troubleshooting-required-status-checks?apiVersion=2022-11-28&utm_source=chatgpt.com) وحماية الفروع.

---

## 3. ما لا يغطيه CI

- **لا** يثبت `PAID_BETA_READY` على استضافة حقيقية — ذلك يدوي أو عبر workflow staging بعد الأسرار.
- **لا** يستبدل عقداً أو تحصيلاً يدوياً — انظر [`PAID_BETA_OPERATING_PLAYBOOK.md`](PAID_BETA_OPERATING_PLAYBOOK.md).

---

**آخر تحديث:** 2026-05-01

# التحقق من PAID_BETA_READY (محلي + Staging)

السكربت [`../../scripts/launch_readiness_check.py`](../../scripts/launch_readiness_check.py) يطبع أحد الخيارات:

- **`GO_PRIVATE_BETA`:** فحوصات in-process ناجحة (بدون `--base-url` أو قبل الفحص البعيد).
- **`PAID_BETA_READY`:** نفس الفحوصات + نجاح جميع طلبات GET المطلوبة على `--base-url`.
- **`NO_GO`:** فشل بوابة — لا تبيع بجدية حتى العلاج.

---

## ١) محلي (بدون Staging)

من جذر حزمة `dealix`:

```powershell
py -3 scripts/launch_readiness_check.py
```

توقع: **`VERDICT: GO_PRIVATE_BETA`** و `exit 0` عندما يكون الكود والـ landing سليمين.

---

## ٢) ضد Staging الحقيقي

```powershell
$env:STAGING_BASE_URL="https://your-staging.railway.app"
py -3 scripts/launch_readiness_check.py --base-url $env:STAGING_BASE_URL
```

توقع: **`VERDICT: PAID_BETA_READY`** و `exit 0` قبل إرسال روابط دفع جادة للعملاء.

---

## ٣) ما تم التحقق منه في بيئة التطوير (مرجع للـ PR)

| الأمر | النتيجة المتوقعة |
|--------|-------------------|
| `py -3 scripts/smoke_inprocess.py` | نهاية المخرجات تحتوي `SMOKE_INPROCESS_OK` و exit 0 |
| `py -3 scripts/launch_readiness_check.py` (بدون base-url) | `VERDICT: GO_PRIVATE_BETA` و exit 0 |
| `py -3 -m pytest` | جميع الاختبارات المطلوبة خضراء (ما عدا skipped المعتاد) |

> تشغيل **PAID_BETA_READY** على URL فعلي يبقى خطوة بشرية بعد نشر Railway وضبط `STAGING_BASE_URL` في الأسرار وفي جهازك.

---

## روابط

- [`STAGING_HUMAN_GATES_A_D_AR.md`](STAGING_HUMAN_GATES_A_D_AR.md)
- [`../PAID_BETA_FULL_RUNBOOK_AR.md`](../PAID_BETA_FULL_RUNBOOK_AR.md)

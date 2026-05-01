# GitHub Actions — `STAGING_BASE_URL` و Dealix staging smoke

## 1) إضافة السر

1. GitHub → **Settings** → **Secrets and variables** → **Actions**
2. **New repository secret**
   - الاسم: `STAGING_BASE_URL`
   - القيمة: `https://your-staging-host` (بدون `/` في النهاية إن أمكن)

اختياري إذا الـ API يتطلب مفتاحاً:

- `STAGING_API_KEY` — يُستخدم من [`dealix-staging-smoke.yml`](../../../.github/workflows/dealix-staging-smoke.yml) عبر env (راجع الملف).

---

## 2) تشغيل الـ workflow

1. **Actions** → ابحث عن **Dealix staging smoke**
2. **Run workflow** — اختر الفرع الذي **يحتوي ملف** `.github/workflows/dealix-staging-smoke.yml` في الـ commit (غالباً `ai-company` بعد الدمج).

إذا **لم يظهر** الـ workflow في القائمة أو في `gh workflow list`:

- GitHub يحمّل تعريفات الـ workflows من **الفرع الافتراضي** للريبو غالباً. إذا كان `main` لا يحتوي الملف بينما `ai-company` يحتويه، انسخ الملف إلى `main` عبر PR صغير **أو** غيّر الفرع الافتراضي مؤقتاً (سياسة الفريق).

---

## 3) السلوك عند غياب السر

الـ workflow يتخطى الخطوات برسالة ويخرج `0` إذا `STAGING_BASE_URL` فارغ — **لا يعطي إذناً بالبيع**. تأكد يدوياً أن السر مضبوط ثم أعد التشغيل.

---

## مرجع الملف

[`../../../.github/workflows/dealix-staging-smoke.yml`](../../../.github/workflows/dealix-staging-smoke.yml)

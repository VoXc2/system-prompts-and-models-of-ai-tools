# ربط Railway — مسار AI Company (`ai-company`)

نفّذ في [لوحة Railway](https://railway.app) بعد أن يكون الفرع [`ai-company`](https://github.com/VoXc2/system-prompts-and-models-of-ai-tools/tree/ai-company) مرفوعاً على GitHub.

## 0) عندك بالفعل Project على Railway — قائمة إكمال (لا تبدأ من صفر)

افتح **نفس المشروع** وامشِ بالترتيب؛ علّم كل بند عند الانتهاء.

1. **أي خدمة هي التطبيق؟** حدّد بطاقة **Web / Service** اللي تشغّل الـ API (مو Postgres وحدها).
2. **المصدر (Git):** داخل الخدمة → **Settings** → **Source** (أو Connect repo):
   - الريبو: `VoXc2/system-prompts-and-models-of-ai-tools`.
   - **Branch:** `ai-company` (وليس فرعاً قديماً إن غيّرت سياسة النشر).
3. **Root Directory:** لازم يكون **`dealix`**. إن كان فارغاً أو `.` أو جذر المونوريبو، البناء قد ينجح والتشغيل يفشل أو العكس — عدّله واحفظ ثم **Redeploy**.
4. **Start Command:** بالضبط  
   `uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8000}`  
   واحذف أي أمر قديم (مثلاً `python main.py` من جذر خاطئ).
5. **Postgres:** إن وُجدت في المشروع → تأكد أن **`DATABASE_URL`** (أو المرجع منه) **موجود في متغيرات خدمة التطبيق**، ليس فقط داخل خدمة DB.
6. **Variables:** راجع قائمة المتغيرات في **خدمة التطبيق** مقابل [`.env.staging.example`](../../.env.staging.example) — خصوصاً `APP_SECRET_KEY`, `APP_URL`, `APP_ENV`, `CORS_ORIGINS`, `DAILY_EMAIL_LIMIT`, `WHATSAPP_ALLOW_LIVE_SEND`.
7. **Networking:** فعّل **Public URL** / دومين؛ حدّث `APP_URL` و`CORS_ORIGINS` ليطابقا الرابط الظاهر.
8. **Deployments:** آخر نشر — إن كان أحمر، Build Logs ثم Deploy Logs (انظر قسم 8 أدناه).
9. **اختبار:** `/health` ثم `smoke_staging` من جهازك (قسم 5).

إن كان المشروع فيه **أكثر من خدمة** (قديمة + جديدة)، إمّا تعطيل النشر للقديمة أو حذفها لتتجنب لبس الدومين والمتغيرات.

## 1) المشروع والخدمة

1. **New Project** → **Deploy from GitHub** → اختر `VoXc2/system-prompts-and-models-of-ai-tools`.
2. أنشئ خدمة **Web** (أو عدّل الخدمة الحالية) لتشغيل Dealix API.

## 2) إعدادات النشر (إلزامي)

| الحقل | القيمة |
|--------|--------|
| **Branch** | `ai-company` |
| **Root Directory** | `dealix` |
| **Start Command** | `uvicorn api.main:app --host 0.0.0.0 --port ${PORT:-8000}` |

مرجع: [`STAGING_DEPLOYMENT.md`](../STAGING_DEPLOYMENT.md).

## 3) قاعدة البيانات

1. أضف **PostgreSQL** من Railway أو استخدم `DATABASE_URL` خارجي.
2. اربط متغير **`DATABASE_URL`** بخدمة التطبيق (غالباً يُحقن تلقائياً عند الربط).

## 4) متغيرات البيئة

- انسخ **الأسماء** من [`.env.staging.example`](../../.env.staging.example) (staging) أو [`.env.example`](../../.env.example) (production لاحقاً).
- لا تُرفع `.env` إلى Git.
- تأكد من: `APP_SECRET_KEY`, `APP_URL`, `APP_ENV`, `CORS_ORIGINS`, `MOYASAR_*`، و`DAILY_EMAIL_LIMIT` (وليس `EMAIL_DAILY_LIMIT`)، و`WHATSAPP_ALLOW_LIVE_SEND=false` للبيتا حتى الموافقة.

## 5) التحقق بعد النشر

1. المتصفح: `https://<your-host>/health` → 200.
2. محلياً: `STAGING_BASE_URL=https://<host>` ثم `python scripts/smoke_staging.py` من مجلد `dealix`.
3. GitHub Actions: شغّل يدوياً **Dealix staging smoke** بعد ضبط أسرار `STAGING_BASE_URL` / `STAGING_API_KEY` — انظر [`GITHUB_ACTIONS_ENV_SETUP.md`](GITHUB_ACTIONS_ENV_SETUP.md).

## 6) مسار Git الكامل

[`GITHUB_AI_COMPANY_TRACK.md`](GITHUB_AI_COMPANY_TRACK.md)

---

## 7) مسار لوحة Railway بالتفصيل (أين تضغط)

1. **Account** → تأكد أن GitHub مربوط (للاستيراد من GitHub).
2. **New Project** → **Deploy from GitHub repo** → اختر `system-prompts-and-models-of-ai-tools`.
3. إن أنشأ Railway خدمة تلقائياً، افتح **الخدمة** (البطاقة) → **Settings**:
   - **Source** → **Branch** = `ai-company`.
   - **Root Directory** = `dealix` (إن لم يظهر، ابحث في نفس الصفحة عن Root / Watch paths حسب واجهة Railway).
4. **Settings** → **Deploy** (أو Build):
   - **Start Command** كما في الجدول أعلاه.
   - إن وُجد **Builder** أو **Nixpacks**: غالباً يكفي أن يوجد `requirements.txt` داخل `dealix` بعد ضبط Root.
5. أضف **PostgreSQL** من نفس المشروع (**+ New** → **Database** → **PostgreSQL**).
6. في خدمة Postgres: **Variables** → انسخ **`DATABASE_URL`** (أو استخدم **Connect** واربط المرجع بخدمة الويب عبر **Reference Variable** إن ظهرت لك الخاصية).
7. في **خدمة الويب** → **Variables**: أضف باقي المتغيرات يدوياً (لا تلصقها في شات).
8. **Networking** (أو **Settings** → Public Networking): فعّل **Generate Domain** أو اربط دومينك؛ هذا هو الـ host لـ `APP_URL` و`CORS_ORIGINS` و`STAGING_BASE_URL` في GitHub.
9. **Deployments**: راقب آخر build — إن فشل، افتح **Build Logs** ثم **Deploy Logs**.

## 8) أين «توقف» غالباً — تشخيص سريع (بدون أسرار)

| العرض في Railway | ماذا تفعل |
|-------------------|-----------|
| Build failed / `pip install` error | تأكد **Root Directory** = `dealix` وأن `requirements.txt` يظهر في سجل البناء تحت `dealix/`. |
| Deploy OK لكن **502 / Application failed** | Deploy Logs: غالباً خطأ استيراد أو `DATABASE_URL` فارغ أو `APP_SECRET_KEY` ناقص. |
| Container exits immediately | غالباً أمر التشغيل خطأ أو المنفذ؛ استخدم الأمر في الجدول و`PORT` من Railway. |
| `/health` لا يفتح | Networking غير مفعّل أو الخدمة ليست Web على المنفذ الصحيح. |
| `/health` 200 لكن smoke يفشل على مسارات | راجع `API_KEYS` على السيرفر وطابق `STAGING_API_KEY` في الدخان أو GitHub Secrets. |
| DB connection error | تأكد أن `DATABASE_URL` **مرتبط بخدمة التطبيق** وليس فقط داخل Postgres؛ وشكل الرابط متوافق مع async (التطبيق يطبيع `postgres://`). |

## 9) بعد النجاح

- حدّث [`LAUNCH_DAY_VERIFICATION_LOG.md`](../LAUNCH_DAY_VERIFICATION_LOG.md) بصف staging.
- راجع [`BETA_PRIVATE_GATES_CHECKLIST.md`](../BETA_PRIVATE_GATES_CHECKLIST.md) قبل أول عميل.

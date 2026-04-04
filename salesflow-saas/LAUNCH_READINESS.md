# Dealix — جاهزية الإطلاق والتحقق

هذا الملف يلخّص ما يُشغَّل للتحقق قبل الإطلاق، وأين تُوجد المواد (برزنتيشنات، تسويق، استراتيجية)، وما يبقى تشغيلياً خارج الكود.

## التحقق التلقائي (يجب أن تمرّ كلها قبل الإنتاج)

من جذر `salesflow-saas`:

### الواجهة (Next.js — `frontend/`)

```bash
cd frontend
npm run lint
npm test
npm run build
npx playwright install chromium   # مرة واحدة على الجهاز/CI
npx playwright test
```

أو دفعة واحدة: `npm run test:all` (Vitest + Playwright؛ يفترض تشغيل الخادم عبر إعداد Playwright).

### الـ API (FastAPI — `backend/`)

```bash
cd backend
py -3 -m pytest -q
py -3 -m pytest -m launch -q
```

- `pytest -m launch` يغطي مسارات GET العامة وسيناريوهات إطلاق مسجّلة في `tests/test_launch_readiness_scenarios.py`.

**حالة التحقق الأخيرة (محلياً):** اجتياز `49` اختباراً في الـ backend، و`12` اختبار Playwright، وبناء Next بدون أخطاء.

## إصلاحات تقنية مهمة (للمطورين)

1. **`app/models/compat.py`:** `IS_SQLITE` يُؤخذ من `app.database.IS_SQLITE` حتى يتطابق نوع الأعمدة مع محرك SQLite الفعلي عندما لا يوجد `DATABASE_URL` في البيئة.
2. **`app/sqlite_patch.py`:** عند غياب `DATABASE_URL`، يُستخدم نفس الافتراضي `sqlite+aiosqlite:///./dealix.db` مثل `database.py` حتى يُطبَّق تصحيح أنواع PostgreSQL على SQLite في الاختبارات.
3. **نماذج SQLAlchemy:** جميع الحقول `UUID` / `JSONB` / `INET` تُستورد من `app.models.compat` (لا استيراد مباشر من `sqlalchemy.dialects.postgresql` في الملفات النموذجية) لاتساق SQLite ↔ PostgreSQL.

بدون (1) و(2)، كان `create_all` يفشل على SQLite مع أعمدة `JSONB` الحقيقية.

## أصول التسويق والبرزنتيشنات

| المحتوى | المصدر في المستودع | بعد المزامنة إلى الواجهة |
|--------|---------------------|---------------------------|
| مواد تسويقية | `sales_assets/` | `frontend/public/dealix-marketing/` |
| برزنتيشنات قطاعية (HTML) | `presentations/dealix-2026-sectors/` | `frontend/public/dealix-presentations/` |
| مخططات/استراتيجية (نسخ للواجهة) | `docs/*.md` (حسب `sync-marketing-to-public.cjs`) | `frontend/public/strategy/` |

**المزامنة:** من `salesflow-saas` تشغيل `node scripts/sync-marketing-to-public.cjs` (أو الاعتماد على `prebuild` في الواجهة: `npm run build` يستدعيه).

**برزنتيشنات Markdown حسب القطاع:** مجلد `presentations/` (مثل `automotive/`, `healthcare/`, `real-estate/` …) — مرجع للمحتوى والمبيعات؛ الـ HTML المعروض للعملاء يُحدَّث من مسار `dealix-2026-sectors` أعلاه.

## قائمة ما قبل الإطلاق (تشغيل / أمن / امتثال)

- **قاعدة البيانات:** في الإنتاج استخدم PostgreSQL حقيقياً (`DATABASE_URL`) مع النسخ الاحتياطي والمراقبة؛ لا تعتمد على SQLite.
- **أسرار:** `SECRET_KEY`، مفاتيح LLM، WhatsApp، إلخ — عبر متغيرات بيئة أو مدير أسرار؛ لا تُرفع إلى Git.
- **CORS والواجهة:** `FRONTEND_URL` و`CORS_EXTRA_ORIGINS` لنطاقات الإنتاج الفعلية.
- **الواجهة:** `NEXT_PUBLIC_API_URL` يشير إلى الـ API العام.
- **الامتثال والعقود:** الشروط، الخصوصية، اتفاقيات العملاء — مراجعة قانونية خارج نطاق هذا المستودع.
- **المراقبة:** سجلات، صحة الخدمة (`/api/v1/health`, `/api/v1/ready`)، وتنبيهات عند الأعطال.

## ملاحظة واقعية

«جاهزية 100% للسوق» تشمل الجودة التقنية (اختبارات، بناء، أمان أساسي) **و** التجربة التجارية، الدعم، التسعير، والامتثال — وهذا المستند يغطي الجانب التقني والمسارات الثابتة للمواد؛ أكمِل الباقي حسب خطتك التشغيلية.

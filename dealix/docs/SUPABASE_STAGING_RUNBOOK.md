# Supabase — تشغيل Staging وProject Memory

## 1) ربط المشروع

```bash
supabase link --project-ref <YOUR_STAGING_REF>
```

## 2) مراجعة جافّة (اختياري)

```bash
supabase db push --dry-run
```

## 3) تطبيق الهجرة

```bash
supabase db push
```

أو نفّذ محتوى `supabase/migrations/202605010001_v3_project_memory.sql` في SQL Editor.

## 4) تحقق بعد التطبيق

شغّل في SQL Editor:

`scripts/verify_supabase_project_memory.sql`

## متغيرات البيئة (سيرفر فقط)

| المتغير | ملاحظة |
|---------|---------|
| `SUPABASE_URL` | عنوان المشروع |
| `SUPABASE_SERVICE_ROLE_KEY` | **سيرفر فقط** — لا في الواجهة أو الموبايل |
| `SUPABASE_ANON_KEY` | إن لزم للميزات العامة — **ليس** لذاكرة المشروع الحساسة |

## أمان

- **RLS** مفعّل على الجداول؛ السياسات الافتراضية تتطلب مراجعة قبل أي وصول `authenticated`.
- **لا أسرار** داخل `content`/`metadata` المخصصة للـ embeddings.
- فهرسة محلية بدون مفاتيح:

```bash
python scripts/index_project_memory.py --root . --out .dealix/project_index.json
```

## Rollback

احتفظ بنسخة SQL قبل `db push`؛ في حال فشل إنشاء فهرس HNSW على إصدار Postgres، راجع `docs/SUPABASE_PROJECT_MEMORY_SETUP.md` وعدّل نوع الفهرس حسب دعم المشروع.

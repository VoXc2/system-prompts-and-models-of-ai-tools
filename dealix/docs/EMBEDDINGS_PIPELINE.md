# مسار الـ Embeddings — Dealix Project Memory

## الهدف

رفع `project_chunks` + `strategic_memory` إلى Supabase مع **نفس نموذج التضمين** للاستعلام (`match_project_chunks` / `match_strategic_memory`).

## المراحل

1. **فهرسة محلية** (بدون أسرار):  
   `python scripts/index_project_memory.py --root . --out .dealix/project_index.json`
2. **تقطيع + تنقية**: استبعاد `.env`، منع الأسرار عبر `should_block_embedding()` في `project_intelligence.py`.
3. **توليد متجهات**: Edge Function أو worker Python على staging — اختيار النموذج من `docs/SUPABASE_PROJECT_MEMORY_SETUP.md`.
4. **Upsert**: إلى `project_chunks.embedding` بأبعاد **384** كما في الهجرة الحالية (عدّل العمود إن غيّرت النموذج).
5. **تحقق**: `scripts/verify_supabase_project_memory.sql`.

## سكربت placeholder

`scripts/embeddings_pipeline_placeholder.py` — يطبع خطوات التشغيل ويخرج 0 حتى يُربط مزود التضمين.

## أمان

- لا تضع `SUPABASE_SERVICE_ROLE_KEY` في الواجهة أو في الريبو.
- لا تُضمّن نصوصاً فيها مفاتيح API.

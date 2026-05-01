# دليل مراجعة PR #125 (PR كبير)

## لماذا PR كبير؟

دمج **مسار v3 Autonomous Revenue OS** + **Personal Operator** + **طبقة أعمال وGTM** + **وثائق واختبارات** + **هجرة Supabase** + **سكربتات** في مرحلة واحدة.

## المسارات (Tracks)

| المسار | المجلدات |
|--------|-----------|
| v3 API + رادار + امتثال + علوم إيرادات | `api/routers/v3.py`, `auto_client_acquisition/v3/` |
| Personal Operator | `api/routers/personal_operator.py`, `auto_client_acquisition/personal_operator/` |
| Business / GTM API | `api/routers/business.py`, `auto_client_acquisition/business/` |
| AI routing (بدون SDK خارجي) | `auto_client_acquisition/ai/` |
| قاعدة بيانات | `supabase/migrations/`, `db/session.py` |
| وثائق | `docs/*` |
| واجهات ثابتة | `landing/` |
| اختبارات | `tests/test_*.py` |
| CI | `.github/workflows/ci.yml` |

## كيف يراجع الـ Reviewer؟

1. اقرأ `docs/PR125_FINAL_STABILIZATION_REPORT.md` (بعد الدمج من الفرع).  
2. ركّز على **أمان التنفيذ**: لا إرسال واتساب تلقائي، لا أسرار.  
3. راجع **تعارض المسارات**: `python scripts/print_routes.py`.  
4. شغّل أوامر القسم «Commands to run» أدناه.

## Commands to run

```bash
python -m compileall api auto_client_acquisition
pytest -q --no-cov
python scripts/print_routes.py
```

## ملفات عالية المخاطر

- `api/main.py` — تسجيل الراوترات.
- `api/routers/autonomous.py` — تدفقات بيانات.
- `api/security/*` — مفاتيح ومعدلات.
- `db/session.py` — جلسات DB.
- `supabase/migrations/*.sql` — RLS وفهارس.

## ملفات منخفضة المخاطر

- `docs/*.md` (ما عدا أي أسرار — يجب ألا توجد).
- `landing/*.html`.

## قيود أمان

- لا إرسال خارجي بدون موافقة.
- لا PAT في الريبو/الـ PR.

## اختبارات معروفة متخطاة

- `tests/e2e/*` — تتطلب سيرفر على `127.0.0.1:8001` (مُعلّمة skip إن لم يكن السيرفر شغّالاً).

## قائمة دمج (Merge checklist)

- [ ] CI أخضر  
- [ ] `print_routes` بدون تعارض خطير  
- [ ] سامي ألغى أي PAT مكشوف  
- [ ] لا أسرار في diff  
- [ ] مراجعة يدوية لـ `/checkout` إن لمسِّت مفاتيح Moyasar  

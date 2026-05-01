# Growth Curator Strategy

هدف الطبقة: **رفع جودة الصادر** (واتساب، إيميل، اجتماع متابعة) دون المطالبة بوعود غير قابلة للدفاع أو انتهاك سياسات القناة.

## كود

- `auto_client_acquisition/growth_curator/message_curator.py` — `grade_message`
- `auto_client_acquisition/growth_curator/playbook_curator.py` — قواعد مساعدة للقطاعات
- `auto_client_acquisition/growth_curator/curator_report.py` — `build_weekly_curator_report`

## API

- `GET /api/v1/growth-curator/report/demo` — تقرير أسبوعي شكلي للعرض
- `POST /api/v1/growth-curator/messages/grade` — `{ "message_ar": "...", "sector": "", "channel": "whatsapp" }`
- `GET /api/v1/growth-curator/skills/demo` — جرد مهارات/قوالب (درجات MVP)
- `GET /api/v1/growth-curator/missions/curate/demo` — اقتراحات دمج/أرشفة أسبوعية (لا حذف تلقائي)

## تكامل مقترح

1. بعد توليد مسودة من الذكاء: استدعاء `grade_message`؛ إذا انخفض `score` عن عتبة المنتج، أظهر تحذيراً ولا تعرض زر «إرسال» في البيتا.
2. ربط العتبات مع `channel_registry.blocked_actions` (منع جماعي بارد، إلخ).

## اختبارات

`tests/test_growth_tower_stack.py` — `test_grade_message_detects_guarantee`.

# SOP يومي — محرك الإيراد (Dealix)

هدف: دمج مسارات الابتكار والمشغّل في **سير عمل يومي واحد** داخل الشركة.

## الصباح (15–30 دقيقة)

1. **موجز التشغيل:** `GET /api/v1/personal-operator/daily-brief` (أو واجهة داخلية لاحقاً).
2. **لوحة القرار:** `GET /api/v1/innovation/command-feed/live` — إن لم توجد بيانات، راجع `/command-feed/demo` ثم عالج سبب فراغ الـ DB.
3. **10 فرص (Kill feature):** `POST /api/v1/innovation/opportunities/ten-in-ten` مع مدخلات ICP الحالية — **لا إرسال** حتى موافقة.

## منتصف اليوم

4. **غرف صفقات حرجة:** `POST /api/v1/innovation/deal-room/analyze` للصفقات ذات المخاطر.
5. **تجربة شهرية:** `POST /api/v1/innovation/experiments/recommend` مع `past_experiments` من الأسبوع السابق.

## المساء

6. **دفتر الإثبات:** سجّل أحداث اليوم عبر `POST /api/v1/innovation/proof-ledger/events` (تقديرات تشغيلية).
7. **ملخص أسبوعي (يوم محدد):** `GET /api/v1/innovation/proof-ledger/report/week?tenant_id=...` — تفاصيل [`PROOF_LEDGER_WEEKLY_RUNBOOK.md`](PROOF_LEDGER_WEEKLY_RUNBOOK.md) و`scripts/fetch_proof_ledger_weekly.py`.

## حوكمة

- أي رسالة واتساب/بريد: موافقة أولاً — [`WHATSAPP_OPERATOR_FLOW.md`](../WHATSAPP_OPERATOR_FLOW.md).
- PDPL: لا PII في ملاحظات عامة بدون ضرورة — [`SECURITY_PDPL_CHECKLIST.md`](../SECURITY_PDPL_CHECKLIST.md).

## مراجع API

- فهرس المسارات: `python scripts/print_routes.py | findstr innovation` (Windows) أو `rg innovation`.

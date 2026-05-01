# تقرير أثر أسبوعي — Proof Ledger

## الغرض

تلخيص **تقديرات** `revenue_influenced_sar_estimate` لآخر 7 أيام لكل `tenant_id` — ليس إيراداً محاسبياً.

## عبر API

```bash
cd dealix
set BASE_URL=https://api.example.com
set API_KEY=your_key_if_required
python scripts/fetch_proof_ledger_weekly.py --tenant default
```

## عبر المتصفح / Bruno

`GET /api/v1/innovation/proof-ledger/report/week?tenant_id=default`

## قرار التسعير/التجديد

- اربط التقرير باجتماع أسبوعي: هل زادت الأحداث؟ هل التقديرات منطقية؟
- وثّق القرار في CRM أو Notion داخلية.

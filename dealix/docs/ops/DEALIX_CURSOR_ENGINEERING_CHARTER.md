# Dealix — Cursor / Engineering (كود + اختبارات + CI)

**الدور:** تنفيذ تقني، إصلاحات staging، سكربتات smoke، واجهات HTML عند الحاجة — **عبر فرع صغير + PR إلى `ai-company`**.

---

## القواعد

```text
لا commits على ai-company مباشرة
كل تغيير: branch قصير + PR + CI أخضر قبل الدمج
```

---

## أولويات المرحلة الحالية (إغلاق Paid Beta)

1. إصلاحات تمنع فشل `PAID_BETA_READY` فقط (مسارات، env، landing المطلوبة من readiness).
2. [`scripts/smoke_staging.py`](../../scripts/smoke_staging.py) و [`scripts/launch_readiness_check.py`](../../scripts/launch_readiness_check.py) — لا تغيير سلوك البوابات إلا لإصلاح bug موثّق.
3. اختبارات لكل إصلاح.

---

## ممنوع

```text
live send (WhatsApp / Gmail / إلخ)
LinkedIn scraping أو auto-DM
cold WhatsApp
Moyasar charge برمجي
تغيير pricing أو safety rules أو POSITIONING_LOCK بدون موافقة
migrations واسعة بدون سبب عميل/تشغيل مسجّل
```

---

## قبل PR

1. الملفات التي تُلامس.
2. سبب التعديل (سطر واحد).
3. أوامر التحقق التي ستُشغّل.

---

## بعد التعديل (محلياً من `dealix`)

```bash
APP_ENV=test pytest -q --no-cov
python scripts/print_routes.py
python scripts/smoke_inprocess.py
python scripts/launch_readiness_check.py
```

لا تفتح PR إذا فشل أي منها (ما عدا `launch_readiness_check` بدون `--base-url` المتوقع `GO_PRIVATE_BETA` محلياً).

---

## الربط

- لوحة القيادة: [`DEALIX_ACTIVE_COMMAND_BOARD.md`](DEALIX_ACTIVE_COMMAND_BOARD.md)
- الوثائق: [`DEALIX_CLAUDE_WORK_CHARTER.md`](DEALIX_CLAUDE_WORK_CHARTER.md)

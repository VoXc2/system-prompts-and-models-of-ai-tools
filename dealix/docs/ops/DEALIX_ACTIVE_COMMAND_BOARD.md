# DEALIX_ACTIVE_COMMAND_BOARD

صفحة قيادة واحدة — حدّث التاريخ عند تغيير التركيز. الهدف منع تضارب Claude Work و Cursor على نفس الملفات.

---

## North Star

```text
إغلاق Paid Beta حقيقية = PAID_BETA_READY (staging) + أول payment/commitment + أول Proof Pack
```

المرجع التنفيذي: [`../PAID_BETA_FULL_RUNBOOK_AR.md`](../PAID_BETA_FULL_RUNBOOK_AR.md)

---

## الفرع المحمي للنشر

```text
ai-company
```

لا commits مباشرة — PR فقط، CI أخضر.

---

## PR / فرع العمل النشط (عدّل عند الفتح)

```text
(لا يوجد PR نشط مذكور هنا — املأ عند بدء موجة)
```

---

## مسموح الآن (Allowed Work)

```text
Staging + إصلاحات تمنع فشل PAID_BETA_READY فقط
Sales kit + docs + قوالب outreach (بدون تغيير claims)
smoke_staging / launch_readiness_check
اختبارات لأي إصلاح تقني ضروري
```

---

## ممنوع (Do Not Build) — حتى إشعار آخر

```text
Saudi Revenue Graph / patch كبير قبل PAID_BETA_READY
Founder Console / frontend جديد واسع قبل أول عميل
Tenant model + ledger كامل + background jobs (ما لم يُسجّل طلب عميل مرتين أو ألم تشغيلي)
marketplace / white-label
LinkedIn scraping أو auto-DM
cold WhatsApp
live Gmail send
live Moyasar charge (استخدم invoice يدوي)
تغيير pricing أو POSITIONING_LOCK أو safety rules بدون موافقة صريحة
```

---

## تجميد البناء (Build freeze)

لا PR لميزات جديدة قبل:

```text
PAID_BETA_READY على URL staging
```

بعدها: فقط ما يخدم البيع أو يصلح بوابة الإطلاق — انظر شروط «متى تبني كود» في الـ Runbook.

---

## روابط سريعة

| موضوع | ملف |
|--------|------|
| أوامر staging → PAID_BETA_READY | [`STAGING_PAID_BETA_READY_ONE_SHOT.md`](STAGING_PAID_BETA_READY_ONE_SHOT.md) |
| Secret + workflow | [`STAGING_WORKFLOW_GITHUB.md`](STAGING_WORKFLOW_GITHUB.md) |
| تشغيل Claude (وثائق فقط) | [`DEALIX_CLAUDE_WORK_CHARTER.md`](DEALIX_CLAUDE_WORK_CHARTER.md) |
| تشغيل Cursor (كود) | [`DEALIX_CURSOR_ENGINEERING_CHARTER.md`](DEALIX_CURSOR_ENGINEERING_CHARTER.md) |
| إغلاق تجاري (نسخ/قائمة) | [`COMMERCIAL_CLOSE_COPY_CHECKLIST.md`](COMMERCIAL_CLOSE_COPY_CHECKLIST.md) |

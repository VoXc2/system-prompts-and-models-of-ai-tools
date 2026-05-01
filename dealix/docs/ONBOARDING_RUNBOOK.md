# Dealix Onboarding Runbook

> **الهدف:** نقل عميل جديد من "وافق على الـ Pilot" إلى "أول Proof Pack" خلال 5 أيام عمل، بدون خطأ تشغيلي.

---

## 8 خطوات الـ onboarding (محسوبة)

| # | الخطوة | المدة | الاعتماد |
|---|--------|------|---------|
| 1 | اختيار الهدف | 2د | لا |
| 2 | اختيار الباقة | 3د | نعم |
| 3 | بيانات الشركة | 5د | لا |
| 4 | ربط القنوات (drafts فقط) | 8د | نعم |
| 5 | رفع قائمة أو ربط مصدر leads | 5د | نعم |
| 6 | مراجعة المخاطر (PDPL + سمعة) | 4د | نعم |
| 7 | تشغيل أول خدمة | async | نعم |
| 8 | استلام أول Proof Pack | async | لا |

**Endpoints:**
- `POST /api/v1/customer-ops/onboarding/checklist`
- `POST /api/v1/customer-ops/onboarding/update-step`
- `GET /api/v1/customer-ops/onboarding/checklist/demo`

---

## Day-by-day

### Day 1 — Kick-off (60 دقيقة)
- مكالمة 30 دقيقة مع المؤسس / Growth Manager.
- ملء الـ intake (الخطوات 1-3).
- توقيع Pilot Agreement draft + DPA draft (يحتاج محامي للحالة الإنتاجية).
- إنشاء session في `operator_memory` + customer_id.

### Day 2 — Connectors
- ربط Gmail (drafts فقط) — `connector_setup_status` يتعقّب التقدم.
- ربط Google Calendar (drafts فقط).
- ربط Google Sheets للـ exports.
- WhatsApp Cloud (إذا لازم) — opt-in audit أولاً.

### Day 3 — List + Risk Review
- رفع CSV / ربط CRM.
- تشغيل `targeting_os.analyze_uploaded_list_preview`.
- مراجعة الـ contactability (safe / needs_review / blocked).
- اعتماد القنوات الآمنة فقط.

### Day 4 — أول خدمة
- تشغيل First 10 Opportunities Sprint أو List Intelligence.
- توليد 10 opportunity cards + رسائل عربية.
- إرسال Approval Pack للعميل (≤3 أزرار لكل بطاقة).

### Day 5 — Proof Pack v1
- استلام Proof Pack مختصر (PDF + JSON + WhatsApp summary).
- جلسة مراجعة 30 دقيقة.
- تفعيل Customer Success Cadence (weekly check-ins).

---

## Connector Setup Status

11 connectors معرّفة في `customer_ops.connector_setup_status`:

| Connector | Default Mode | Phase | Blocking |
|-----------|--------------|------:|----------|
| gmail | draft_only | 1 | لا |
| google_calendar | draft_only | 1 | لا |
| google_sheets | approved_execute | 1 | لا |
| moyasar | manual | 1 | لا |
| whatsapp_cloud | draft_only | 1 | **نعم** |
| website_forms | approved_execute | 1 | لا |
| linkedin_lead_forms | ingest_only | 2 | لا |
| google_business_profile | draft_only | 2 | لا |
| crm_generic | draft_only | 2 | لا |
| google_meet | ingest_only | 2 | لا |
| instagram_graph | ingest_only | 3 | لا |

`ready_for_first_service` = `True` فقط عندما لا يوجد blocking connector مفقود + ≥1 connector connected.

---

## Connector States

```
not_started → configuring → connected_draft_only
                          → connected_approved_execute
configuring → failed (يحتاج إعادة محاولة)
configuring → skipped (إذا قرر العميل عدم الربط)
```

---

## ما لا يحدث بدون اعتماد

- ربط Gmail لا يفعّل send.
- ربط Calendar لا يفعّل insert.
- ربط Moyasar لا يفعّل charge.
- ربط WhatsApp لا يفعّل cold send.

كل live action يحتاج env flag صريح + اعتماد بشري.

---

## Onboarding Failure Recovery

| فشل | الإجراء |
|-----|--------|
| OAuth Gmail فشل | recheck scopes, retry, fallback to draft-only |
| Moyasar invoice غير موصول | استخدم dashboard manual |
| العميل لم يرفع قائمة | اعرض Free Diagnostic + recommend_accounts |
| Risk review كشف مشكلة | توقّف، أرسل تقرير للمؤسس |

---

## Acceptance Criteria

العميل onboarded إذا:
1. كل الـ 8 خطوات `completed=True` (إلا الـ async منها).
2. `ready_for_first_service=True`.
3. Proof Pack v1 تم تسليمه + اعتماده.
4. Customer Success cadence مفعّل.

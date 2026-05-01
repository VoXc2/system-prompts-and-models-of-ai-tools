# Dealix Incident Response

> **القاعدة:** أي incident يمر بـ triage → severity → response plan → audit. أي تسريب بيانات أو إرسال غير معتمد = SEV1 تلقائي.

---

## Severities

| Severity | الوصف | First Action | Comm Cadence |
|----------|------|-------------:|-------------:|
| **SEV1** | تسريب أمان / إرسال غير معتمد / تعطل كامل | 15 دقيقة | كل 30 دقيقة |
| **SEV2** | خدمة معطلة لـ ≥5 عملاء | 30 دقيقة | كل ساعة |
| **SEV3** | تأثير محدود (عميل واحد / degraded) | 2 ساعة | كل 4 ساعات |

---

## Triage Logic

```python
if has_data_leak or has_unauthorized_send:
    severity = "SEV1"
elif affected_customers >= 5:
    severity = "SEV2"
else:
    severity = "SEV3"
```

**Endpoints:**
- `POST /api/v1/customer-ops/incidents/triage`
- `GET /api/v1/customer-ops/incidents/response-plan/{severity}`

---

## Canonical Response Plan (مشترك)

1. **تجميد** الـ live actions على القناة المعنية فوراً.
2. **إخطار** المؤسس + on-call operator.
3. **إنشاء** incident channel مع timeline.
4. **مراجعة** Action Ledger للأفعال المرتبطة.
5. **إذا تسريب**: إخطار العملاء المتأثرين خلال 72 ساعة (PDPL).

---

## SEV1 Additional Steps

6. تواصل مباشر مع المؤسس + خلية أزمة.
7. كتابة post-mortem خلال 24 ساعة.
8. مراجعة قانونية إن لزم (DPA + PDPL implications).

---

## SEV2 Additional Steps

6. تحديث العملاء المتأثرين كل 60 دقيقة.
7. post-mortem خلال 48 ساعة.

---

## SEV3 Additional Steps

6. تحديث العميل المتأثر مع كل خطوة.
7. post-mortem اختياري (موصى به للأنماط المتكررة).

---

## Post-Mortem Template

```
1. ملخص الحادث
2. timeline (timestamps)
3. السبب الجذري
4. ما اشتغل صح
5. ما اشتغل غلط
6. الـ action items للوقاية
7. الـ owner لكل action item
8. الـ deadline
```

---

## Communication Templates (Arabic)

### SEV1 — أول ساعة
> اكتشفنا حدث أمني/تشغيلي يتعلق بـ [نوع الحادث]. أوقفنا الـ live actions على القناة المتأثرة. نتواصل معك خلال 30 دقيقة بتحديث.

### SEV1 — تسريب بيانات
> نأسف. اكتشفنا تسريب بيانات يتعلق بـ [نوع البيانات]. نراجع الأثر الآن وسنتواصل معك خلال 24 ساعة بتفاصيل + خطوات الحماية. PDPL يلزم بالإبلاغ خلال 72 ساعة لذا سنحرص على إعلامك بكل ما نعرفه.

### SEV2
> خدمة [اسم الخدمة] متعطلة جزئياً. الفريق يعمل على الإصلاح ونتوقع الاستعادة خلال [وقت]. سنحدثك كل ساعة.

---

## Auto-actions

- **Dealix يجمد القناة تلقائياً** عند detection على:
  - bounce_rate > 5%
  - complaint_rate > 0.3%
  - block_rate WhatsApp > 3%
- **Dealix يخطر المؤسس** على أي SEV1 detected.
- **Dealix يضيف entry لـ Action Ledger** لكل incident.

---

## Permission to publish

- Post-mortems خاصة لـ SEV1 لا تُنشر علناً إلا بعد:
  - مراجعة قانونية.
  - موافقة العملاء المتأثرين.
  - إزالة كل PII.
- Post-mortems لـ SEV2/SEV3 يمكن نشرها كـ engineering blog لو مفيدة.

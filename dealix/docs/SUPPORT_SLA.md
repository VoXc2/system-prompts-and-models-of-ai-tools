# Dealix Support SLA

> **القاعدة:** كل tickets تُصنّف P0/P1/P2/P3 آلياً، لها أهداف first-response و resolution محددة، ويتم تتبع كل تجاوز.

---

## Priority Tiers

| Priority | الوصف | First Response | Resolution Target | Owner |
|----------|------|---------------:|------------------:|-------|
| **P0** | حرج جداً — أمان / إرسال خاطئ / تعطل كامل | 30 دقيقة | 4 ساعات | Founder |
| **P1** | خدمة مهمة معطلة | 2 ساعة | 24 ساعة | Operator on-call |
| **P2** | Connector أو Proof Pack متأخر | 8 ساعات | 72 ساعة | Operator on-call |
| **P3** | سؤال عام / تحسين | 24 ساعة | 7 أيام | Operator team |

---

## Endpoints

```
POST /api/v1/customer-ops/support/classify        # تصنيف ticket → priority
POST /api/v1/customer-ops/support/route           # routing مع SLA + first response template
POST /api/v1/customer-ops/sla/event               # تسجيل opened/first_response/resolved/escalated
POST /api/v1/customer-ops/sla/classify-breach     # تحديد إن كان في breach
POST /api/v1/customer-ops/sla/health-report       # تقرير صحة SLA من tickets list
GET  /api/v1/customer-ops/sla/health-report/demo  # demo
```

---

## Auto-classification Keywords

### P0 (حرج جداً)
- أمان
- تسريب
- إرسال خاطئ
- إرسال بدون موافقة / بدون موافقتي
- secret / leak / data breach
- outage / completely down
- live charge / charge بدون موافقة
- unauthorized

### P1 (خدمة معطلة)
- service down / خدمة معطلة
- service failed
- Pilot stopped
- Proof Pack مفقود

### P2 (connector أو proof)
- connector / Gmail / Calendar / Sheets
- WhatsApp setup
- Moyasar invoice

### P3 (افتراضي)
أي ticket لم يتطابق مع P0/P1/P2.

---

## First-Response Templates

كل priority لها قالب رد أولي عربي معد مسبقاً عبر `build_first_response_template(priority)`.

### مثال P0
> وصلني بلاغك الآن. نتعامل معه كأولوية حرجة. سأرد عليك خلال 30 دقيقة بتفاصيل ما حدث + الإجراءات المتخذة. إذا اكتشفت أي إرسال غير معتمد أو تسريب بيانات، سأتواصل معك مباشرة.

---

## Health Report Verdict

عبر `build_sla_health_report`:
- **healthy**: breach_rate < 10%
- **watch**: 10% ≤ breach_rate < 25%
- **critical**: breach_rate ≥ 25%

عند `critical` → escalate تلقائي للمؤسس + إيقاف الـ live actions حتى المراجعة.

---

## Weekly SLA Review

كل اثنين:
1. تجميع كل tickets الأسبوع المنقضي.
2. تشغيل `build_sla_health_report`.
3. مراجعة الـ breaches.
4. تحديث `customer_success_cadence` للعملاء المتأثرين.
5. إذا critical → post-mortem + `incident_router`.

---

## ما لا يحدث في الـ support

- لا response تلقائي للعميل بدون مراجعة بشرية.
- لا تسريب لـ ticket id في القنوات العامة.
- لا فتح ticket بـ priority < classified-priority (الـ system يحدد، البشر يرفع فقط).
- لا إغلاق ticket بدون تأكيد من العميل.

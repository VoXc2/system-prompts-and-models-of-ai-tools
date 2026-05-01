# Public Launch Readiness — Layer 13

> **القاعدة:** الانتقال من Paid Beta إلى Public Launch لا يتم بناءً على رغبة المؤسس. يتم بناءً على 9 معايير deterministic، PDPL compliance، وBrand Moat Score. كل قرار قابل للتدقيق.

---

## 1. الـ 9 معايير

| # | Key | الحد الأدنى | كيف يُقاس |
|---|-----|------------|----------|
| 1 | `pilots_completed` | ≥5 | عدد Pilots سُلّم لها Proof Pack نهائي خلال 7 أيام |
| 2 | `paid_customers` | ≥2 | عملاء دفعوا Moyasar أو وقّعوا Growth OS |
| 3 | `unsafe_sends` | =0 | live actions بدون موافقة في Action Ledger |
| 4 | `proof_cadence_weeks` | ≥3 متتالية | أسابيع متتالية صدر فيها Proof Pack |
| 5 | `support_first_response_minutes_p1` | ≤120 | متوسط استجابة P1 |
| 6 | `funnel_visible` | =True | lead→demo→pilot→paid قابل للقياس |
| 7 | `staging_uptime_days` | ≥14 | أيام متتالية بـ uptime ≥99% |
| 8 | `billing_webhook_verified` | =True | Moyasar webhook signed وتم التحقق |
| 9 | `legal_complete` | =True | Terms + Privacy + DPA منشورة باللغتين |

---

## 2. القرار الناتج

```
GO_PUBLIC_LAUNCH    — كل المعايير الـ9 متحققة → ابدأ Public Launch
NO_GO               — معيار أو أكثر فشل (لكن ليس unsafe_sends)
BLOCKED             — unsafe_sends > 0 (Hard block — incident SEV1 أولاً)
```

---

## 3. الـ Endpoints

```
GET  /api/v1/public-launch/criteria        — قائمة الـ 9 معايير
POST /api/v1/public-launch/gate-check      — تقييم gate من state
POST /api/v1/public-launch/pilot-tracker   — ملخص Pilots
POST /api/v1/public-launch/pdpl-compliance — PDPL audit
POST /api/v1/public-launch/brand-moat      — Brand Moat Score
GET  /api/v1/public-launch/demo            — مثال شامل
```

---

## 4. مثال استدعاء `gate-check`

```bash
curl -X POST https://api.dealix.me/api/v1/public-launch/gate-check \
  -H 'Content-Type: application/json' \
  -d '{
    "state": {
      "pilots_completed": 7,
      "paid_customers": 3,
      "unsafe_sends": 0,
      "proof_cadence_weeks": 4,
      "support_first_response_minutes_p1": 60,
      "funnel_visible": true,
      "staging_uptime_days": 21,
      "billing_webhook_verified": true,
      "legal_complete": true
    }
  }'
```

النتيجة:

```json
{
  "decision": "GO_PUBLIC_LAUNCH",
  "score_passed": 9,
  "score_total": 9,
  "blockers": [],
  "next_actions_ar": [],
  "summary_ar": "✅ جاهز للإطلاق العام — كل المعايير الـ9 متحققة..."
}
```

---

## 5. PDPL Compliance Check (10 فحوصات)

| Severity | Check | لماذا critical |
|----------|-------|---------------|
| critical | `data_residency_saudi` | PDPL يلزم بالـ Saudi region |
| critical | `whatsapp_opt_in_audit` | عقوبات Meta + PDPL |
| critical | `breach_notification_72h_ready` | غرامة PDPL 5M ر.س |
| critical | `privacy_policy_bilingual` | حق العميل بالإطلاع |
| critical | `trace_redaction_active` | منع تسريب PII في logs |
| high | `email_opt_in_audit` | تجنب blacklist |
| high | `dpa_template_published` | عقد DPA لكل عميل |
| high | `data_retention_policy` | حذف 90 يوم |
| high | `action_ledger_audit` | accountability |
| medium | `consent_revocation_path` | حق العميل بإلغاء opt-in |

أي critical فاشل → `non_compliant` → **لا انتقال إلى Public Launch**.

---

## 6. Brand Moat Score (5 طبقات)

| Dimension | Weight | الحد الأدنى لـ "defensible" |
|-----------|-------:|---------------------------|
| Data Moat (Saudi Revenue Graph) | 30% | 1,000 events + 10 sectors |
| Brand Moat (Saudi-First) | 20% | 5K LinkedIn + 1K newsletter |
| Compliance Moat (PDPL Native) | 20% | 100% PDPL + ISO 27001 progress |
| Network Moat (Agency Channel) | 20% | 30 agency partners |
| Distribution Moat (Operator Network) | 10% | 100 certified operators |

```
overall ≥ 80   → dominant   (Series-A ready)
overall ≥ 60   → defensible (GCC expansion ready)
overall ≥ 35   → emerging   (build phase)
overall < 35   → fragile    (focus on weakest)
```

---

## 7. Pilot Tracker

كل Pilot يمر بـ 8 stages:
```
intake → diagnostic_sent → pilot_delivered → proof_pack_sent
       → upgrade_decided → completed | stalled | lost
```

Upgrade outcomes (6):
```
growth_os_monthly | partnership_growth | case_study
| second_pilot    | no_upgrade         | ghost
```

API يحسب:
- `total_pilots`, `completed_pilots`, `proof_packs_delivered`
- `paid_pilots`, `paid_revenue_sar`, `upgrade_revenue_sar`
- `case_studies`, `growth_os_subscribers`
- `completion_rate`, `paid_conversion_rate`, `upgrade_conversion_rate`
- `by_sector`, `by_city`
- `average_proof_pack_days`

---

## 8. كيف تستخدمه عملياً

### يومياً (في الـ Founder Brief)
```bash
curl https://api.dealix.me/api/v1/public-launch/demo
```

تشاهد:
- Gate score الحالي
- Pilots summary
- PDPL status
- Brand Moat tier

### أسبوعياً (في الـ Weekly Strategic Review)
1. حدّث state بأرقام الأسبوع.
2. شغّل `gate-check` + `pdpl-compliance` + `brand-moat`.
3. ركّز على أضعف dimension في Brand Moat.
4. أصلح أي critical في PDPL.

### قبل الانتقال إلى Public Launch
1. `gate-check` يجب يرجع `GO_PUBLIC_LAUNCH`.
2. `pdpl-compliance` يجب يرجع `compliant` (لا critical/high).
3. `brand-moat` يجب يكون ≥ `defensible` (60+).
4. أرسل تقرير شامل للـ founder + advisors.
5. حضّر launch announcement.

---

## 9. ما لا يفعله Layer 13

- ❌ لا يرسل بياناتك خارجياً.
- ❌ لا يستدعي LLM (deterministic 100%).
- ❌ لا يعدّل بياناتك — read-only.
- ❌ لا يستبدل التقييم البشري — يكمّله.

---

## 10. التكامل مع الطبقات الأخرى

| الطبقة | كيف يستفيد منها Public Launch |
|--------|-----------------------------|
| Customer Ops (Layer 6) | يقرأ SLA + tickets للحساب `support_first_response_minutes_p1` |
| Service Excellence (Layer 3) | يضمن أن كل خدمة تظهر لها score ≥80 |
| Revenue Company OS (Layer 9) | يقرأ Action Ledger للحساب `unsafe_sends` |
| Proof Ledger (Layer 10) | يقرأ proof pack history للحساب `proof_cadence_weeks` |
| Service Tower (Layer 2) | يحسب `paid_customers` + `pilots_completed` |
| Targeting OS (Layer 4) | يبني funnel للحساب `funnel_visible` |

---

## 11. القرار التشغيلي

```
لا تنتقل إلى Public Launch بناءً على "الشعور".
انتقل بناءً على /api/v1/public-launch/gate-check = GO_PUBLIC_LAUNCH
+ /api/v1/public-launch/pdpl-compliance = compliant
+ /api/v1/public-launch/brand-moat ≥ defensible.
```

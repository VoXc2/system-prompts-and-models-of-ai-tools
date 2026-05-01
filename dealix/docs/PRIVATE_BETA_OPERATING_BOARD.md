# Dealix Private Beta Operating Board

**الغرض:** لوحة تشغيل يومية تربط **التواصل اليدوي** بالـ **funnel** حتى **الدفع** و**Proof Pack** — بدون أتمتة مخالفة للقنوات.

**مرافق:** [`PAID_BETA_OPERATING_PLAYBOOK.md`](PAID_BETA_OPERATING_PLAYBOOK.md) — سكربت `scripts/paid_beta_daily_scorecard.py` لتلخيص الأرقام اليومية.

---

## 1. إنشاء الـ Sheet (Google Sheets أو Excel)

**اسم المقترح:** `Dealix Private Beta Operating Board`

### أعمدة سجل التواصل (صف واحد = شخص/شركة/لمسة)

| العمود | الوصف |
|--------|--------|
| `date` | تاريخ اللمسة |
| `company` | اسم الشركة |
| `person` | اسم الشخص |
| `segment` | وكالة / SaaS / تدريب / استشارات / … |
| `source` | LinkedIn / إيميل / إحالة / … |
| `channel` | القناة المستخدمة |
| `message_sent` | نعم/لا + اختصار الموضوع |
| `reply_status` | لا رد / رد سلبي / رد إيجابي / محجوز ديمو |
| `demo_booked` | تاريخ/وقت أو فارغ |
| `diagnostic_sent` | نعم/لا |
| `pilot_offered` | نعم/لا |
| `price` | 0 / 499 / 1500 / … |
| `paid` | نعم/لا + المرجع (فاتورة/حوالة) |
| `proof_pack_sent` | نعم/لا + تاريخ |
| `next_step` | جملة واحدة |
| `notes` | حر |

---

## 2. ملخص نهاية اليوم (Executive snapshot)

املأ يومياً (يمكن صفاً ثانياً «Summary» أو تبويب):

| المقياس | قيمة اليوم |
|---------|------------|
| Messages sent | |
| Positive replies | |
| Demos booked | |
| Pilots offered | |
| Payments requested | |
| Payments received | |
| Proof packs delivered | |
| Top objection | |
| Next improvement | |

---

## 3. ربط مع السكربت

1. صدّر ملخص اليوم إلى JSON (يدوياً أو من Sheet بسكربت صغير خارج الريبو إن رغبت).
2. شغّل:

   ```bash
   python scripts/paid_beta_daily_scorecard.py --file path/to/today.json
   ```

   أو مرّر الأرقام كوسائط (انظر `python scripts/paid_beta_daily_scorecard.py --help`).

---

## 4. قواعد الجودة

- لا تسجيل أسرار أو مفاتيح API في الـ Sheet.
- تقليل PII: أسماء الشركات كافية في المرحلة الأولى؛ تجنب تخزين أرقام هواتف غير ضرورية.

---

**آخر تحديث:** 2026-05-01

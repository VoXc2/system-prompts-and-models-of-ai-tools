# إغلاق تجاري — قائمة نسخ جاهزة (مالك المنتج)

لا أتمتة هنا — نفّذ يدوياً بعد `PAID_BETA_READY`. المرجع الكامل: [`../PAID_BETA_FULL_RUNBOOK_AR.md`](../PAID_BETA_FULL_RUNBOOK_AR.md).

---

## 1) Moyasar

- فاتورة **499 SAR** — وصف واضح (Pilot 7 أيام).
- أرسل الرابط عبر قناة موثوقة (إيميل / رسالة يدوية مع opt-in حيث ينطبق).

---

## 2) 25 لمسة + Operating Board

- أنشئ Google Sheet: **Dealix Paid Beta Operating Board**
- الأعمدة كما في الـ Runbook: `company`, `person`, `segment`, `channel`, `message_sent_at`, `reply_status`, `demo_booked`, …

قوالب بريد ومتابعة: [`../sales-kit/layer14_email_sequences_4x7_ar.md`](../sales-kit/layer14_email_sequences_4x7_ar.md)

---

## 3) ديمو + Diagnostic + Pilot

- سكربت ديمو 12 دقيقة: [`../sales-kit/layer14_demo_12min_script_ar.md`](../sales-kit/layer14_demo_12min_script_ar.md)
- Battlecards: [`../sales-kit/layer14_battlecards_6_ar.md`](../sales-kit/layer14_battlecards_6_ar.md)

---

## 4) Proof Pack

الهيكل في الـ Runbook (قسم Proof Pack). سلّم نسخة واحدة مكتوبة بعد أول أسبوع تشغيل متفق عليه.

---

## 5) Scorecard يومي

من مجلد `dealix`:

```bash
python scripts/paid_beta_daily_scorecard.py --messages 25 --replies 0 --demos 0 --pilots 0 --payments 0 --proof-packs 0
```

حدّث الأرقام حسب الـ Sheet.

---

## علامة «إغلاق تجاري»

```text
دفع أو commitment مكتوب + Proof Pack مُرسل + سجل في الـ Operating Board
```

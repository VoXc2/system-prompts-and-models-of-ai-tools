# Prohibited Claims — ممنوع تماماً

> أي landing page / رسالة بيع / ديمو / قائمة مزايا تحتوي إحدى هذه العبارات يجب رفضها فوراً.

---

## 1. ادعاءات نتائج مضمونة

- ❌ "نضمن لك عملاء"
- ❌ "نضمن مبيعات"
- ❌ "نتائج مضمونة 100%"
- ❌ "ROI مضمون 10x"
- ❌ "Money-back guarantee" (إلا في حالة Pilot واضح بشروط محدودة)

**القاعدة:** نقول "Proof Pack بالأرقام" بدلاً من "نتيجة مضمونة".

---

## 2. ادعاءات scraping أو بيانات غير مصرّح بها

- ❌ "نسحب كل بيانات LinkedIn"
- ❌ "نستخرج جميع الأرقام من Google"
- ❌ "نجمع leads من أي مكان"
- ❌ "نحصل على إيميلات decision makers من Apollo"

**القاعدة:** نقول "مصادر مصرّح بها: CRM، LinkedIn Lead Forms، website forms، manual research معتمد".

---

## 3. ادعاءات automation كاملة

- ❌ "نرسل تلقائياً للجميع"
- ❌ "Dealix يدير كل شيء بدونك"
- ❌ "Auto-DM على LinkedIn"
- ❌ "Cold WhatsApp campaigns جاهزة"

**القاعدة:** نقول "Approval-first — لا إرسال بدون موافقتك. Drafts فقط افتراضياً".

---

## 4. ادعاءات تجاوز الموافقات

- ❌ "بدون مكالمة"
- ❌ "بدون فريق"
- ❌ "بدون مراجعة"
- ❌ "Ai-only — لا تدخل بشري"

**القاعدة:** نقول "بشرية القرار، آلية التنفيذ — Approval Center في كل خطوة".

---

## 5. ادعاءات منصات منافسة

- ❌ "بديل HubSpot"
- ❌ "أرخص من Salesforce"
- ❌ "نقتل CRM التقليدي"
- ❌ "أقوى من Gong"

**القاعدة:** نقول "Saudi Revenue Execution OS — يكمّل CRMs، لا يستبدلها".

---

## 6. ادعاءات قانونية/مالية

- ❌ "نتجاوز PDPL"
- ❌ "نخفي بياناتك من الجهات الرسمية"
- ❌ "نضمن عودة استثمارك"
- ❌ "Tax-deductible automatically"

**القاعدة:** نقول "PDPL-aware. DPA draft جاهز. أي عقد يحتاج مراجعة قانونية".

---

## 7. ادعاءات طبية أو جدية

- ❌ "يعالج مشاكل العمل"
- ❌ "يشفي شركتك من الركود"
- ❌ "علاج مضمون لقلة العملاء"

**القاعدة:** لا تستخدم لغة طبية أو علاجية. نقول "نحسّن الـ pipeline".

---

## 8. ادعاءات سرعة مبالغ فيها

- ❌ "10 عملاء خلال 24 ساعة"
- ❌ "مليون ريال خلال شهر"
- ❌ "نمو 1000% أسبوعياً"

**القاعدة:** نقول "10 فرص خلال 7 أيام، ضمن workflow approval-first".

---

## كيف نفرضها تقنياً

1. **Safety Eval** — `agent_observability.safety_eval()` يكتشف "ضمان 100%" و"آخر فرصة" تلقائياً.
2. **Saudi Tone Eval** — يرفض "best-in-class" و"synergy".
3. **Quality Review Gate** — في `service_excellence.quality_review` أي خدمة بدون proof_metrics blocked.
4. **Tool Action Planner** — يحظر LinkedIn scraping و auto-DM في الكود مباشرة.
5. **Test `test_positioning_lock.py`** — يفحص landing pages وlanding/services.html والـ docs ضد هذه القائمة.

---

## القاعدة الذهبية

> **لو تحتاج إثبات قبل القول، لا تقله.**
> Dealix يبيع نتائج محسوبة بـ Proof Pack، لا وعود تسويقية.

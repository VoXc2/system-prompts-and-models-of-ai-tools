# Revenue Today — دليل تشغيل دخل اليوم (Private Beta)

> جمع بين المنتج والبيع دون كسر قواعد الأمان: **لا إرسال حي تلقائي، لا شحن من API داخل Dealix في هذه المرحلة، لا واتساب بارد، لا أتمتة LinkedIn المخالفة.**

## 1. عرض ٤٩٩ ريال (Pilot ٧ أيام)

- **الوعد:** ١٠ فرص B2B، لماذا الآن، رسائل عربية (مسودات)، فحص قابلية التواصل، خطة متابعة ٧ أيام، Proof Pack مختصر.
- **التحصيل:** فاتورة أو رابط دفع يدوي من لوحة Moyasar (sandbox أو live حسب سياسة شركتك) — راجع [وثائق Moyasar](https://docs.moyasar.com/).
- **API للمرجعية:** `GET /api/v1/revenue-launch/offer` (يحتوي `pilot_499`)؛ للتسميات الإنجليزية بجانب العربية: `GET /api/v1/revenue-launch/offer?lang=en`.

## 2. عرض Growth OS Pilot (١٥٠٠–٣٠٠٠ ريال / ٣٠ يوم)

- تشغيل أوسع: موجز، فرص، ذكاء قوائم، مسودات قنوات، Proof أسبوعي — كلها **مسودات وموافقة** ما لم تُفعّل سياسات الإنتاج صراحةً لاحقاً.

## 3. من نستهدف اليوم

- ٥ وكالات B2B، ٥ تدريب/استشارات، ٥ SaaS صغيرة، ٥ خدمات بواتساب نشط (يدوياً — لا scraping).

## 4. أول ٢٠ تواصل

- قوالب: `GET /api/v1/launch/outreach/first-20` و`GET /api/v1/revenue-launch/outreach/first-20` (عينات + شرائح).
- **نسخ يدوي فقط** من الرسائل.

## 5. سيناريو الردود

- `GET /api/v1/revenue-launch/demo-flow` → قسم `objections`.

## 6. حجز الديمو

- ديمو ١٢ دقيقة: `docs/DEMO_SCRIPT_12_MINUTES.md` و`GET /api/v1/revenue-launch/demo-flow`.

## 7. إغلاق أول Pilot

- `GET /api/v1/revenue-launch/pilot-delivery` — نموذج intake، خطة ٢٤ ساعة، مخرجات First 10 و List Intelligence.

## 8. ماذا نطلب من العميل

- حقول intake في نفس الـ endpoint أعلاه (موقع، قطاع، مدينة، عرض، قائمة، قنوات، موافق واتساب).

## 9. ماذا نسلّم خلال ٢٤ ساعة

- حسب الاتفاق: عينة فرص + مسودات + تقرير مخاطر — **بعد موافقة داخلية** على الصياغة.

## 10. قالب Proof Pack

- `GET /api/v1/revenue-launch/proof-pack/template`.

## 11. الدفع اليدوي (Moyasar)

- `GET /api/v1/revenue-launch/payment/manual-flow` — تعليمات لوحة التحكم، قالب رسالة، قائمة تأكيد بعد الدفع.
- **تذكير:** المبالغ غالباً بالهللات (١ ريال = ١٠٠ هللة) — راجع وثائق Moyasar.

## 12. ما لا نفعله اليوم

- لا charge من كود Dealix، لا إرسال Gmail/واتساب/تقويم حي، لا scraping LinkedIn، لا وعود بنتائج مضمونة.

## روابط تقنية

| الغرض | المسار |
|--------|--------|
| حزمة العروض | `GET /api/v1/revenue-launch/offer` |
| ديمو + إغلاق | `GET /api/v1/revenue-launch/demo-flow` |
| مخطط pipeline | `GET /api/v1/revenue-launch/pipeline/schema` |
| تسليم Pilot | `GET /api/v1/revenue-launch/pilot-delivery` |
| دفع يدوي | `GET /api/v1/revenue-launch/payment/manual-flow` |
| Proof template | `GET /api/v1/revenue-launch/proof-pack/template` |

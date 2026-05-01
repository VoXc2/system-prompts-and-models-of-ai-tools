# ديمو Dealix — ١٢ دقيقة

مرجع تنفيذي يطابق `GET /api/v1/launch/demo-script` في الكود.

| الدقائق | المحتوى | API اختياري |
|--------|---------|-------------|
| 0–2 | المشكلة والوعد: ليس CRM وليس بوت واتساب فقط — إشارة → قرار → موافقة → Proof | — |
| 2–4 | Daily Brief للمدير | `GET /api/v1/personal-operator/daily-brief` |
| 4–6 | مهمات النمو / ١٠ فرص | `GET /api/v1/growth-operator/missions` |
| 6–8 | Inbox موحّد (كروت عربية) | `GET /api/v1/platform/inbox/feed` |
| 8–10 | برج الخدمات والأسعار التقديرية | `GET /api/v1/services/catalog` |
| 10–12 | Pilot، Proof Pack، الخطوة التالية | `GET /api/v1/launch/private-beta/offer` |

**جملة إغلاق:** لا نعد نتائج مضمونة — نعد مسودات، موافقات، وتقارير قياس.

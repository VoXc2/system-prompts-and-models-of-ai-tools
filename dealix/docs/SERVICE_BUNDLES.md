# Service Bundles

باقات منتَجة تربط عدة `service_id` من [Service Tower](SERVICE_TOWER_STRATEGY.md) بسعر وزمن وProof.

## التعريف البرمجي

- [`auto_client_acquisition/autonomous_service_operator/service_bundles.py`](../auto_client_acquisition/autonomous_service_operator/service_bundles.py)
- `GET /api/v1/operator/bundles` — قائمة JSON للعرض.

## الباقات

| bundle_id | فكرة | نطاق سعر تقريبي (ريال) |
|-----------|--------|-------------------------|
| growth_starter | تشخيص + ١٠ فرص | ٤٩٩ |
| data_to_revenue | ذكاء قوائم + فرص | ١٥٠٠–٢٥٠٠ |
| executive_growth_os | موجز تنفيذي + Growth OS | من ٢٩٩٩ |
| partnership_growth | شراكات + اجتماعات | ٣٠٠٠–٧٥٠٠ |
| local_growth_os | نمو محلي | ٩٩٩–٢٩٩٩ |
| full_growth_control_tower | مخصص ٩٠ يوماً | ١٥٠٠٠+ |

الأرقام توضيحية للعرض؛ العقد يُحدّد بعد الـ pilot.

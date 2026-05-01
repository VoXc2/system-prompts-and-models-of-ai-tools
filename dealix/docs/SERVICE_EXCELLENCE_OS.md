# Service Excellence OS — مصنع جودة الخدمات

## الرؤية

طبقة فوق **Service Tower** تضمن أن كل خدمة لها: مصفوفة ميزات، درجة جاهزية، مسار موافقة، مقاييس Proof، حزمة إطلاق، وفجوات مقابل الفئات التنافسية — **كلها deterministic** في الـ MVP (بدون استدعاء ويب).

## المكوّنات (`auto_client_acquisition/service_excellence/`)

| الملف | الدور |
|-------|--------|
| `feature_matrix.py` | must_have / advanced / premium |
| `service_scoring.py` | درجة 0–100 وحالة `launch_ready` / `beta_only` / `needs_work` |
| `workflow_builder.py` | التحقق من وجود خطوة موافقة |
| `research_lab.py` | فرضيات وتجارب مقترحة (نص ثابت) |
| `competitor_gap.py` | نقاط قوة المنافس + مزايا Dealix + `do_not_copy` |
| `proof_metrics.py` | مقاييس إلزامية لكل خدمة |
| `quality_review.py` | فحص قبل الإطلاق + `review_all_services` |
| `service_improvement_backlog.py` | عناصر تحسين أسبوعية |
| `launch_package.py` | مخطط صفحة + سكربت مبيعات + onboarding |

## مسارات API

بادئة: `/api/v1/service-excellence`

- `GET /review/all` — فحص جميع خدمات البرج.
- `GET /{service_id}/feature-matrix` — المصفوفة + التصنيف.
- `GET /{service_id}/score` — الدرجة والحالة.
- `GET /{service_id}/workflow` — مسار + تحقق + خطة أيام + موافقات.
- `GET /{service_id}/proof-metrics` — المقاييس والقالب.
- `GET /{service_id}/gap-analysis` — فجوات تنافسية.
- `GET /{service_id}/launch-package` — حزمة إطلاق كاملة.
- `GET /{service_id}/backlog` — تحسينات مقترحة.
- `GET /{service_id}/research-brief` — موجز بحث داخلي.
- `GET /{service_id}/review` — فحص خدمة واحدة.

## منع الخدمات الضعيفة

- درجة أقل من ٨٠ → `beta_only` (تشجيع تحسين قبل التسويق الواسع).
- خدمة عالية المخاطر + درجة غير كافية → `needs_work`.
- سياسات غير آمنة (`auto_send`) تُكتشف عبر `block_if_unsafe_channel` (لا تظهر في كتالوج البرج الحالي).

## التكامل

يُستهلك مع **Service Tower** و**Targeting OS** و**Platform Services**؛ لا يكرر التنفيذ الخارجي — يقيّم ويُصدِر خططاً ووثائق عرض.

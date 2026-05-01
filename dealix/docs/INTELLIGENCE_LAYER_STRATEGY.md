# استراتيجية Intelligence Layer — Growth Control Tower

## الهدف

طبقة رفيعة تحت `/api/v1/intelligence/*` تُخرج هياكل JSON **deterministic** (بدون LLM إلزامي في MVP): Growth Brain، Trust Score، Revenue DNA، محاكاة فرص، موجز للمجلس، حركات تنافسية، و**Intel Command Feed** منفصل عن مسار `innovation/command-feed` لتفادي التعارض في الأسماء.

## مكوّنات الكود

| وحدة | وظيفة MVP |
|------|-----------|
| `growth_brain` | بناء ملف شركة/نمو من JSON مدخل |
| `intel_command_feed` | بطاقات إضافية: تسرب إيراد، موجز مجلس — من بيانات ثابتة/مدخلات |
| `trust_score` | درجة ثقة 0–100 مع عوامل |
| `revenue_dna` | لقطات بنية إيراد (قنوات، دورة، مخاطر) |
| `opportunity_simulator` | سيناريوهات رقمية بسيطة |
| `board_brief` | فقرة تنفيذية للإدارة |
| `competitive_moves` | قائمة مقترحات تنافسية آمنة عرضياً |
| `action_graph` | مخطط signal→proof عبر `POST /api/v1/intelligence/action-graph/demo` |
| `mission_engine` | كتالوج مهمات + روابط canonical عبر `GET /api/v1/intelligence/missions/catalog` |
| `decision_memory` | سجل قرارات in-memory عبر `.../decision-memory/*` |

## الربط بـ Innovation / Proof

- **Ten-in-ten:** المسار `POST /api/v1/innovation/opportunities/ten-in-ten` يبقى المصدر؛ يمكن للـ intelligence استدعاء `build_ten_opportunities` داخلياً عند الحاجة (`include_ten_in_ten` اختياري في جسم الطلب).
- **Proof:** مفاهيم «إثبات الإيراد» تبقى متسقة مع [`INNOVATION_STRATEGY.md`](INNOVATION_STRATEGY.md) ودفتر الابتكار؛ طبقة الذكاء **لا تستبدل** سجل الأحداث الدائم.

## Action Graph

رسم بياني موجّه (عُقد/حواف) يُعاد كـ JSON في MVP عبر `action-graph/demo`. التنفيذ المتين لاحقاً مع [`AGENT_WORKFLOW_ARCHITECTURE.md`](AGENT_WORKFLOW_ARCHITECTURE.md) دون LangGraph حتى موافقة صريحة.

## مخاطر

- ازدواج مع `innovation`: يُحل بالأسماء (`intel_command_feed`) واختبارات عقد API.
- توقعات زائدة: التسمية «Intelligence» لا تعني نماذج توليدية في هذا الإصدار.

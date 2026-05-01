# Autonomous Service Operator

> واجهة منتج موحّدة: **نية المستخدم → تصنيف → خدمة موصى بها → intake → مسودة → موافقة → Proof** — بدون LLM إلزامي في الموجة الأولى.

## الكود

- الحزمة: [`auto_client_acquisition/autonomous_service_operator/`](../auto_client_acquisition/autonomous_service_operator/)
- الـ API: `GET|POST /api/v1/operator/*` — انظر [`API_CANONICAL_ALIASES.md`](architecture/API_CANONICAL_ALIASES.md).

## المكوّنات

| ملف | وظيفة |
|-----|--------|
| `intent_classifier.py` | تصنيف قواعد عربي/إنجليزي |
| `service_orchestrator.py` | ربط النية بـ `service_id` من Service Tower |
| `conversation_router.py` | `handle_message` — نقطة دخول المحادثة |
| `session_state.py` | جلسات in-memory (MVP) |
| `approval_manager.py` | موافقة / تعديل / تخطي |
| `workflow_runner.py` | حالات intake → draft → pending_approval → proof |
| `intake_collector.py` | حقول مطلوبة من كتالوج الخدمة |
| `tool_action_planner.py` | مصفوفة Safe Tool Gateway |
| `proof_pack_dispatcher.py` | هيكل Proof Pack |
| `upsell_engine.py` | ترقية من `upgrade_path` في الكتالوج |
| `whatsapp_renderer.py` | نصوص مسودة واتساب (لا إرسال) |
| `operator_memory.py` | سجل أدوار المحادثة |
| `service_bundles.py` | باقات Growth Starter وغيرها |
| `executive_mode.py` / `client_mode.py` / `agency_mode.py` | أولويات العرض حسب الدور |

## الامتثال

لا تنفيذ live للأدوات المحظورة — [`SAFE_TOOL_GATEWAY_POLICY.md`](SAFE_TOOL_GATEWAY_POLICY.md).

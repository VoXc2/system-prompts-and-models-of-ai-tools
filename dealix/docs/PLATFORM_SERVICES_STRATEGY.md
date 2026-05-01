# استراتيجية Platform Services — Growth Control Tower

## الهدف

طبقة موحّدة تحت `/api/v1/platform/*` تجمع: **أحداث موحّدة**، **سياسة قنوات**، **بوابة أدوات بدون إرسال حي**، **Inbox موحّد** (بطاقات عربية)، **سجل قرارات**، و**تلخيص Proof** متوافق مع `auto_client_acquisition/innovation/proof_ledger.py` — دون تكرار «مصدر الحقيقة» للأحداث الدائمة في DB.

## مكوّنات الكود

| وحدة | مسؤولية |
|------|----------|
| `event_bus` | أنواع أحداث + تحقق من الحقول الإلزامية (يشمل أنماطاً موسّعة مثل `email.received`, `payment.paid`, `review.created`) |
| `channel_registry` | قدرات القناة، `beta_status`, `allowed_actions`, `blocked_actions`, `risk_level` |
| `action_policy` | قواعد deterministic: إرسال خارجي → موافقة؛ واتساب بارد → محظور؛ دفع → تأكيد؛ مصدر غير معروف → مراجعة |
| `tool_gateway` | لا شبكة ولا live — `draft_created` / `blocked` / `approval_required` / `unsupported` |
| `unified_inbox` | تحويل حدث → بطاقة (`title_ar`, `summary_ar`, أزرار ≤ 3)؛ يمكن دمج لمسات من `build_demo_command_feed` كمرجع عرض |
| `action_ledger` | سجل قرارات in-memory في MVP (قابل للاستبدال بـ DB) |
| `proof_summary` | تلخيص يستند إلى `build_demo_proof_ledger()` |
| `service_catalog` | خدمات قابلة للبيع كبيانات ثابتة + metadata |

## ما يُنفَّذ الآن مقابل مؤجل

**الآن (MVP):** مسارات read-only / مسودات؛ `WHATSAPP_ALLOW_LIVE_SEND` يبقى افتراضياً `false` في [`core/config/settings.py`](../core/config/settings.py).

**مؤجل:** OAuth، توقيع webhook إنتاجي كامل، قاعدة أحداث دائمة لـ platform خارج نموذج الابتكار، تنفيذ فعلي لـ Gmail/Calendar/Moyasar.

## Inbox و Command Cards

- كل بطاقة: عنوان عربي، ملخص، **ثلاثة أزرار كحد أقصى** (`label_ar` + `action_id`).
- مصادر الحدث: نماذج leads موثّقة، أحداث داخلية، لاحقاً قنوات مسجّلة فقط.

## امتثال PDPL / opt-in

- لا تخزين بيانات حساسة في سجل الـ MVP بدون سياسة موثّقة.
- أي إرسال جماعي أو بارد يمر عبر `action_policy` + موافقة بشرية؛ راجع [`PRIVATE_BETA_RUNBOOK.md`](PRIVATE_BETA_RUNBOOK.md) و[`BETA_PRIVATE_GATES_CHECKLIST.md`](BETA_PRIVATE_GATES_CHECKLIST.md).

## العلاقة بـ Innovation

`innovation` يبقى مسار العرض والـ Kill features (`ten-in-ten`, command feed demo/live). Platform **تلتف** على الدوال التجريبية للـ Proof حيث يلزم، ولا تعيد تعريف أحداث الـ ledger الدائمة.

## طبقات «برج التحكم» الإضافية (كود حالي)

| طبقة | مجلد | مسارات API رئيسية |
|------|------|---------------------|
| Security curator | `auto_client_acquisition/security_curator/` | `/api/v1/security-curator/*` — redact، inspect-diff |
| Growth curator | `auto_client_acquisition/growth_curator/` | `/api/v1/growth-curator/*` — grade، تقرير أسبوعي demo |
| Meeting intelligence | `auto_client_acquisition/meeting_intelligence/` | `/api/v1/meeting-intelligence/*` — تلخيص نص، متابعة، brief |
| Model router | `auto_client_acquisition/model_router/` | `/api/v1/model-router/*` — tasks، route، providers |
| Connectors | `auto_client_acquisition/connectors/` | `GET /api/v1/connectors/catalog` |
| Agent observability | `auto_client_acquisition/agent_observability/` | `/api/v1/agent-observability/*` — evals، trace shape |
| Growth operator (aliases) | `api/routers/growth_operator.py` | `/api/v1/growth-operator/missions`، `.../proof-pack/demo` |

**Growth operator** لا يضاعف المنطق: يضيف `canonical_route` للإشارة إلى مصدر الحقيقة في `innovation` و`business`.

لخطة تنفيذ بالعربية: [`EXECUTION_ROADMAP_AR.md`](EXECUTION_ROADMAP_AR.md).

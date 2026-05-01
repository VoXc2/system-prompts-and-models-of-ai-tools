# خارطة تنفيذ — برج النمو (Growth Control Tower) — عربي

> مرجع تنفيذي يربط الكود الحالي بالخطوات التالية. **MVP الحالي: مسودات، سياسات، عروض deterministic — بدون إرسال حي أو شحن تلقائي.**

## المرحلة 0 — تثبيت (يوم 0–2)

1. `python -m compileall` على جذر `dealix`.
2. `pytest` (الريبو يفعّل `--cov` افتراضياً؛ للسرعة: `pytest --no-cov tests/test_growth_tower_stack.py`).
3. `python scripts/print_routes.py` للتحقق من تضمين الراوترات الجديدة.
4. نشر staging ثم `python scripts/smoke_staging.py` (المسارات موسّعة في السكربت).

## المرحلة 1 — دمج الواجهة والعرض (أسبوع 1–3)

| مخرج | إجراء |
|------|--------|
| Inbox و Command cards | ربط الواجهة بـ `GET /api/v1/platform/inbox/feed` و`GET /api/v1/intelligence/command-feed/demo` حسب التصميم. |
| Proof موحّد | `GET /api/v1/platform/proof/overview` + روابط demo من `innovation` و`business`. |
| Growth operator في الوثائق | استخدام `GET /api/v1/growth-operator/*` للعرض مع احترام `canonical_route` في الاستجابة. |
| Targeting OS | [`TARGETING_ACQUISITION_OS.md`](TARGETING_ACQUISITION_OS.md) و`POST /api/v1/targeting/*` لاستهداف الحسابات والقوائم بشكل متوافق. |

## المرحلة 2 — Curator + Security في مسار المراجعة (أسبوع 2–4)

1. **قبل** أي لصق diff من الوكيل: `POST /api/v1/security-curator/inspect-diff`.
2. **قبل** تخزين/إرسال نصوص طويلة: `POST /api/v1/security-curator/redact`.
3. رسائل الصادر: `POST /api/v1/growth-curator/messages/grade` كبوابة جودة (لا تستبدل المراجعة البشرية للبيتا).
4. تنقية traces قبل المراقبة: `POST /api/v1/security-curator/trace/sanitize`.

## المرحلة 3 — اجتماعات ومتابعة (أسبوع 3–6)

- تدفق: لصق transcript → `POST /api/v1/meeting-intelligence/transcript/summarize` → اعتراضات → `POST .../followup/draft`.
- Pre-call: `POST .../brief/pre-meeting` مع JSON منظّم (شركة، جهة، فرصة).
- لا ربط تقويم حي من هذه المسارات في MVP.

## المرحلة 4 — موجه النماذج والمزودين (متوازي)

- استخدام `POST /api/v1/model-router/route` كطبقة **تلميحات** فقط؛ التوجيه الحقيقي يبقى في `core/llm/router.py` عند التشغيل.
- توثيق المزودين في الكود: `GET /api/v1/model-router/providers`.

## المرحلة 5 — Connectors وبوابة الأدوات

1. عرض للعملاء: `GET /api/v1/connectors/catalog` (مخاطر و`blocked_actions` واضحة).
2. تنفيذ أدوات من الوكيل فقط عبر `POST /api/v1/platform/tools/execute` — راجع `tool_gateway` لحالات `blocked` و`approval_required`.

## المرحلة 6 — مراقبة وتقييم (staging → prod)

- تشغيل evals على عينات: `POST /api/v1/agent-observability/eval/safety` و`.../eval/saudi-tone`.
- بناء أحداث trace متوافقة مع Langfuse: `POST .../trace/build` ثم ربط SDK في التطبيق عند الجاهزية.
- راجع [`AI_OBSERVABILITY_AND_EVALS.md`](AI_OBSERVABILITY_AND_EVALS.md).

## المرحلة 7 — إطلاق بيتا خاص (قرار go/no-go)

- [`PRIVATE_BETA_LAUNCH_TODAY.md`](PRIVATE_BETA_LAUNCH_TODAY.md) و[`BETA_PRIVATE_GATES_CHECKLIST.md`](BETA_PRIVATE_GATES_CHECKLIST.md).
- صفحة عرض: [`landing/private-beta.html`](../landing/private-beta.html).

## المرحلة 8 — ما بعد البيتا (90 يوم)

OAuth كامل لـ Gmail/Calendar، Moyasar live خلف موافقة وتدقيق، واتساب إنتاجي مع `WHATSAPP_ALLOW_LIVE_SEND`، أحداث platform في DB، وتقارير PDF من الـ ledger — كما في [`DEALIX_100_PERCENT_LAUNCH_PLAN.md`](DEALIX_100_PERCENT_LAUNCH_PLAN.md) القسم 3 و21.

## تتبع المهام المقترح

| أسبوع | تركيز |
|-------|--------|
| 1 | smoke + ربط UI للـ inbox وproof |
| 2–3 | security + growth curator في workflow المراجعة |
| 4–6 | meeting intelligence + نماذج أولى من pilot |
| 7–10 | connectors أولوية pilot (whatsapp, gmail, moyasar) مع OAuth |
| 11+ | Langfuse، SLOs، PDPL تشغيلية |

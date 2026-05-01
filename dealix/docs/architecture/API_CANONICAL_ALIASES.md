# Growth Control Tower — مسارات canonical و aliases

> مرجع مواءمة بين وثائق المنتج ومسارات الريبو الفعلية. **لا تُولَّد تلقائياً** — حدّثها عند إضافة alias جديد.

## مبدأ

- **Canonical**: المسار الذي يُنصح به في الكود الجديد والاختبارات.
- **Alias**: نفس السلوك أو لفّ رفيع حول منطق موجود (مثل `ten-in-ten` في `innovation`).

| المفهوم في الوثائق | Canonical في الريبو | ملاحظة |
|--------------------|---------------------|---------|
| Growth Brain build | `POST /api/v1/intelligence/growth-profile` | نفس الـ handler؛ اسم «growth-brain/build» في الوثائق القديمة يُعامل كمرادف لفظي. |
| Command Feed (intel) | `GET /api/v1/intelligence/command-feed` | `GET .../command-feed/demo` **alias** — نفس الاستجابة. |
| Command Feed (innovation demo) | `GET /api/v1/innovation/command-feed/demo` | مصدر بطاقات الابتكار؛ شكل الحقول قد يختلف قليلاً عن طبقة الذكاء. |
| 10 فرص في 10 دقائق | `POST /api/v1/innovation/opportunities/ten-in-ten` | المنطق: `build_ten_opportunities`. |
| First 10 opportunities (alias منتجي) | `POST /api/v1/intelligence/missions/first-10-opportunities` | يستدعي نفس `build_ten_opportunities` دون تكرار المنطق. |
| Unified inbox من حدث | `POST /api/v1/platform/inbox/from-event` | |
| Inbox feed (عرض تجريبي) | `GET /api/v1/platform/inbox/feed` | قائمة بطاقات deterministic للعرض — لا إرسال. |
| Proof ledger demo (innovation) | `GET /api/v1/innovation/proof-ledger/demo` | أحداث تجريبية. |
| Proof pack (أعمال) | `GET /api/v1/business/proof-pack/demo` | أقسام ROI تجريبية. |
| Proof — نظرة موحّدة | `GET /api/v1/platform/proof/overview` | يلخص demo ledger + proof pack + إشارة للتقارير. |
| Gmail draft (payload) | `POST /api/v1/platform/integrations/gmail/draft` | لا OAuth في المسار. |
| Calendar draft | `POST /api/v1/platform/integrations/calendar/draft` | |
| Moyasar payment draft | `POST /api/v1/platform/integrations/moyasar/payment-draft` | هللات + مسودة رابط دفع شكلية. |
| Lead form ingest | `POST /api/v1/platform/ingest/lead-form` | مصدر `trusted_simulation` في MVP. |
| استيراد جهات (معاينة) | `POST /api/v1/platform/contacts/import-preview` | CSV/صفوف — لا إرسال. |
| Growth missions (اسم منتجي) | `GET /api/v1/growth-operator/missions` | Alias رفيع: نفس `list_growth_missions` + `canonical_route` → `GET /api/v1/innovation/growth-missions`. |
| Proof pack demo (اسم منتجي) | `GET /api/v1/growth-operator/proof-pack/demo` | Alias → `GET /api/v1/business/proof-pack/demo`. |
| Security curator | `GET /api/v1/security-curator/demo`، `POST /api/v1/security-curator/redact`، `POST /api/v1/security-curator/inspect-diff` | لا تطبيق patch تلقائياً — فحص وإرجاع قرار. |
| Growth curator | `GET /api/v1/growth-curator/report/demo`، `POST /api/v1/growth-curator/messages/grade` | تقدير رسائل وتقرير أسبوعي تجريبي. |
| Meeting intelligence | `POST /api/v1/meeting-intelligence/transcript/summarize`، `.../followup/draft`، `.../brief/pre-meeting` | نص فقط — بدون إدراج تقويم حي. |
| Model router | `GET /api/v1/model-router/tasks`، `POST /api/v1/model-router/route`، `GET /api/v1/model-router/providers` | تلميحات تكوين deterministic. |
| Connector catalog | `GET /api/v1/connectors/catalog` | بيانات ثابتة + `risk_level` — لا OAuth في الاستجابة. |
| Agent observability | `GET /api/v1/agent-observability/demo`، `POST .../eval/safety`، `POST .../eval/saudi-tone`، `POST .../trace/build` | أشكال تقييم/تتبع للربط بـ Langfuse لاحقاً. |
| Platform — ingest حدث | `POST /api/v1/platform/events/ingest` | حدث موحّد (مثلاً `trusted_simulation`). |
| Platform — موافقة (stub) | `POST /api/v1/platform/actions/approve` | MVP: استجابة شكلية — ربط دفتر قرارات لاحقاً. |
| Platform — خدمات (alias كتالوج) | `GET /api/v1/platform/services/catalog` | يعادل `GET /api/v1/platform/service-catalog`. |
| Platform — proof ledger demo | `GET /api/v1/platform/proof-ledger/demo` | يلف `build_demo_proof_ledger` للعرض. |
| Platform — هوية (تجريبي) | `GET /api/v1/platform/identity/resolve-demo` | عرض توضيحي فقط. |
| Targeting — توصية حسابات | `POST /api/v1/targeting/accounts/recommend` | بيانات demo deterministic. |
| Targeting — لجنة شراء | `POST /api/v1/targeting/buying-committee/map` | |
| Targeting — تقييم جهة | `POST /api/v1/targeting/contacts/evaluate` | سياسات مصدر + قنوات مقترحة. |
| Targeting — تحليل قائمة مرفوعة | `POST /api/v1/targeting/uploaded-list/analyze` | نفس منطق `platform/contacts/import-preview`. |
| Targeting — خطة تواصل | `POST /api/v1/targeting/outreach/plan` | مسودات وموافقة فقط. |
| Targeting — LinkedIn آمن | `POST /api/v1/targeting/linkedin/strategy` | Lead Gen أولاً؛ `do_not_do` صريحة. |
| Targeting — خدمات | `GET /api/v1/targeting/services` | |
| Targeting — تشخيص مجاني | `POST /api/v1/targeting/free-diagnostic` | |
| Targeting — قوالب عقود | `GET /api/v1/targeting/contracts/templates` | ليست استشارة قانونية — مراجعة بشرية. |
| Targeting — trust score | `POST /api/v1/targeting/trust-score` | جسر إلى منطق intelligence. |
| Intelligence — كتالوج المهمات | `GET /api/v1/intelligence/missions/catalog` | يضم metadata + رابط لـ innovation. |
| Intelligence — تفصيل مهمة | `GET /api/v1/intelligence/missions/{mission_id}` | |
| Intelligence — Action graph | `POST /api/v1/intelligence/action-graph/demo` | مخطط signal→proof (عرض). |
| Intelligence — ذاكرة قرارات | `GET /api/v1/intelligence/decision-memory/demo`، `POST .../decision-memory/record` | in-memory MVP. |
| Security — تنقية trace | `POST /api/v1/security-curator/trace/sanitize` | بيانات متداخلة آمنة للمراقبة. |
| Growth curator — جرد مهارات | `GET /api/v1/growth-curator/skills/demo` | |
| Growth curator — تنسيق مهمات | `GET /api/v1/growth-curator/missions/curate/demo` | |
| Platform — تقييم إجراء (alias) | `POST /api/v1/platform/actions/evaluate` | يعادل `POST /api/v1/platform/policy/evaluate`. |
| Platform — موافقة بشرية | `POST /api/v1/platform/actions/approve` | يسجّل في `action_ledger` — لا تنفيذ live. |
| أحداث منصة موسّعة | `email.received`, `payment.paid`, `review.created`, … | انظر `EventType` في `event_bus.py`. |
| Service Tower — كتالوج + توصية | `GET /api/v1/services/catalog`، `POST /api/v1/services/recommend`، `POST /api/v1/services/start` | [`SERVICE_TOWER_STRATEGY.md`](../SERVICE_TOWER_STRATEGY.md) |
| Service Tower — تشغيل عرض | `GET /api/v1/services/demo/dashboard`، `GET /api/v1/services/ceo/daily-brief`، `GET /api/v1/services/ceo/end-of-day`، `POST /api/v1/services/approval-card` | أزرار ≤٣ — لا live send |
| Service Tower — تفاصيل خدمة | `GET /api/v1/services/{service_id}/workflow`، `POST .../quote`، `GET .../intake-questions`، `POST .../validate`، `GET .../deliverables`، `GET .../upgrade` | |
| Service Tower — خرائط ثابتة | `GET /api/v1/services/verticals`، `GET /api/v1/services/upgrade-paths`، `GET /api/v1/services/contracts/templates` | ثلاثة أبواب + ترقيات + مسودات عقود (ليست استشارة قانونية) |
| Launch Ops — بيتا وديمو | `GET /api/v1/launch/private-beta/offer`، `GET /api/v1/launch/demo-script`، `GET /api/v1/launch/outreach/first-20`، `GET /api/v1/launch/go-no-go`، `POST /api/v1/launch/go-no-go`، `GET /api/v1/launch/scorecard` | [`PRIVATE_BETA_LAUNCH_TODAY.md`](../PRIVATE_BETA_LAUNCH_TODAY.md) |
| Revenue Today (عروض + تسليم + دفع يدوي) | `GET /api/v1/revenue-launch/offer` (معامل اختياري `lang=en` يضيف `title_en` بجانب `title_ar`)، `.../outreach/first-20`، `.../demo-flow`، `.../pipeline/schema`، `.../pilot-delivery`، `.../payment/manual-flow`، `.../proof-pack/template` | [`REVENUE_TODAY_PLAYBOOK.md`](../REVENUE_TODAY_PLAYBOOK.md) — لا charge من API داخل Dealix |
| Service Excellence OS | `GET /api/v1/service-excellence/review/all`، `GET /api/v1/service-excellence/{id}/feature-matrix`، `.../score`، `.../workflow`، `.../proof-metrics`، `.../gap-analysis`، `.../launch-package`، `.../backlog`، `.../research-brief`، `.../review` | [`SERVICE_EXCELLENCE_OS.md`](../SERVICE_EXCELLENCE_OS.md) |
| Autonomous Service Operator | `POST /api/v1/operator/chat/message`، `POST /api/v1/operator/chat/decision`، `GET /api/v1/operator/session/{id}`، `GET /api/v1/operator/cards/pending`، `POST /api/v1/operator/service/start`، `POST /api/v1/operator/service/continue`، `GET /api/v1/operator/proof-pack/demo`، `GET /api/v1/operator/whatsapp/daily-brief`، `GET /api/v1/operator/bundles`، `GET /api/v1/operator/tools/matrix`، `GET /api/v1/operator/upsell` | [`AUTONOMOUS_SERVICE_OPERATOR.md`](../AUTONOMOUS_SERVICE_OPERATOR.md) |
| Revenue Company OS | `GET /api/v1/revenue-os/company-os/command-feed/demo`، `POST /api/v1/revenue-os/company-os/events/ingest`، `GET .../work-units/demo`، `GET .../channel-health/demo`، `GET .../opportunity-factory/demo`، `GET .../action-graph/demo`، `GET .../self-improvement/weekly-report`، `GET .../proof-ledger/demo`، `GET .../services/snapshot` | [`AUTONOMOUS_REVENUE_COMPANY_OS.md`](../AUTONOMOUS_REVENUE_COMPANY_OS.md) |
| Customer Ops — تشغيل Pilot ودعم | `GET /api/v1/customer-ops/onboarding/checklist`، `GET /api/v1/customer-ops/support/sla`، `GET /api/v1/customer-ops/connectors/status`، `GET /api/v1/customer-ops/success/cadence`، `GET /api/v1/customer-ops/incidents/playbook`، `POST /api/v1/customer-ops/support/route` (JSON: `issue_ar`)، `GET /api/v1/customer-ops/incidents/classify?severity=P0` | [`ONBOARDING_RUNBOOK.md`](../ONBOARDING_RUNBOOK.md)، [`SUPPORT_SLA.md`](../SUPPORT_SLA.md) — لا إرسال live |

## Staging smoke

مسارات يُنصح بفحصها بعد النشر: انظر [`STAGING_DEPLOYMENT.md`](../STAGING_DEPLOYMENT.md) و`scripts/smoke_staging.py`.

# Safe Tool Gateway — سياسة Dealix

كل إجراء خارجي يمر: **نية → سياسة → موافقة (عند الحاجة) → تنفيذ/تصدير → تدقيق**.

## أوضاع الأداة (MVP)

| وضع | معنى |
|-----|--------|
| suggest_only | اقتراح نصي فقط |
| draft_only | مسودة دون إرسال |
| approval_required | لا تنفيذ بدون موافقة بشرية |
| approved_execute | مسموح بعد موافقة صريحة (نادر في البيتا) |
| blocked | ممنوع |

## المصفوفة البرمجية

- [`tool_action_planner.py`](../auto_client_acquisition/autonomous_service_operator/tool_action_planner.py)
- `GET /api/v1/operator/tools/matrix`

## قواعد صارمة (البيتا)

- لا **Gmail send** تلقائي من المنصة.
- لا **LinkedIn scraping** ولا **auto-DM**.
- لا **واتساب بارد** غير موافق.
- لا **Moyasar charge** من API — روابط/فواتير يدوية حسب [`REVENUE_TODAY_PLAYBOOK.md`](REVENUE_TODAY_PLAYBOOK.md).

## مراجع

- [`PRIVATE_BETA_RUNBOOK.md`](PRIVATE_BETA_RUNBOOK.md)، [`AGENT_SECURITY_CURATOR.md`](AGENT_SECURITY_CURATOR.md).

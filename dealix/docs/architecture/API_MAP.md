# Dealix API Map
**Auto-generated** from `api/routers/*.py`. Total: 145 endpoints.

| Method | Path | Router | Function | Description |
|---|---|---|---|---|
| GET | `/api/v1/admin/approvals/pending` | admin | `approvals_pending` |  |
| POST | `/api/v1/admin/approvals/request` | admin | `approvals_request` |  |
| GET | `/api/v1/admin/approvals/stats` | admin | `approvals_stats` |  |
| GET | `/api/v1/admin/approvals/{request_id}` | admin | `approvals_get` |  |
| POST | `/api/v1/admin/approvals/{request_id}/decide` | admin | `approvals_decide` | Trigger a Sentry test error — verify DSN is live. |
| GET | `/api/v1/admin/cache/stats` | admin | `cache_stats` | Semantic cache hit/miss stats. |
| GET | `/api/v1/admin/costs` | admin | `costs` | Aggregate LLM spend over the last N hours. |
| GET | `/api/v1/admin/dlq/stats` | admin | `dlq_stats` | Dead-letter queue depth and last errors across all queues. |
| POST | `/api/v1/admin/dlq/{queue}/drain` | admin | `dlq_drain` | Remove up to `limit` items from a DLQ. Caller is responsible for replay. |
| GET | `/api/v1/admin/dlq/{queue}/peek` | admin | `dlq_peek` | Inspect the first N items in a DLQ without removing them. |
| GET | `/api/v1/admin/sentry-check` | admin | `sentry_check` | Trigger a Sentry test error — verify DSN is live. |
| POST | `/api/v1/agents/icp-match` | agents | `run_icp_match` |  |
| POST | `/api/v1/agents/intake` | agents | `run_intake` |  |
| POST | `/api/v1/agents/pain-extractor` | agents | `run_pain_extractor` |  |
| POST | `/api/v1/agents/research` | agents | `run_research` |  |
| POST | `/api/v1/automation/daily-targeting/run` | automation | `run_daily_targeting` |  |
| POST | `/api/v1/automation/followups/run` | automation | `run_followups` |  |
| POST | `/api/v1/automation/reply/classify` | automation | `classify_reply_endpoint` | Health summary — counts of today's sends, replies, suppressions. |
| GET | `/api/v1/automation/status` | automation | `automation_status` | Health summary — counts of today's sends, replies, suppressions. |
| POST | `/api/v1/compliance/check-outreach` | automation | `compliance_check` |  |
| GET | `/api/v1/admin/db-diag` | autonomous | `db_diag` | Show DATABASE_URL prefix (redacted) + try a simple query. |
| POST | `/api/v1/admin/init-db` | autonomous | `admin_init_db` | Force-create all tables. Idempotent. Public for debug — secure in prod. |
| POST | `/api/v1/admin/test-insert` | autonomous | `admin_test_insert` | Insert one test row and report exact error if it fails. |
| POST | `/api/v1/channels/policy` | autonomous | `channel_policy` |  |
| POST | `/api/v1/companies/intake` | autonomous | `company_intake` |  |
| POST | `/api/v1/conversations` | autonomous | `create_conversation` |  |
| GET | `/api/v1/conversations` | autonomous | `list_conversations` |  |
| POST | `/api/v1/customers/onboard` | autonomous | `customer_onboard` | Mark customer onboarding milestone. |
| GET | `/api/v1/dashboard/metrics` | autonomous | `dashboard_metrics` |  |
| POST | `/api/v1/deals` | autonomous | `create_deal` |  |
| GET | `/api/v1/deals` | autonomous | `list_deals` |  |
| PATCH | `/api/v1/deals/{deal_id}` | autonomous | `update_deal` |  |
| POST | `/api/v1/integrations/google-lead-form` | autonomous | `alias_google_lead` |  |
| POST | `/api/v1/integrations/meta-lead-form` | autonomous | `alias_meta_lead` |  |
| POST | `/api/v1/leads/import/google-ads` | autonomous | `import_google_lead` |  |
| POST | `/api/v1/leads/import/meta` | autonomous | `import_meta_lead` |  |
| POST | `/api/v1/outreach/queue` | autonomous | `queue_outreach` | Add an outreach item to queue (one-by-one human-final-send model for restricted channels). |
| GET | `/api/v1/outreach/queue` | autonomous | `list_queue` |  |
| PATCH | `/api/v1/outreach/queue/{queue_id}` | autonomous | `update_queue_item` |  |
| POST | `/api/v1/partners/intake` | autonomous | `partner_intake` | Add a partner (agency / implementation / referral / strategic). |
| POST | `/api/v1/payments/manual-request` | autonomous | `manual_payment_request` | Mark deal as payment_requested + create matching task. |
| POST | `/api/v1/payments/mark-paid` | autonomous | `mark_paid` | Mark deal as paid + auto-create customer onboarding. |
| POST | `/api/v1/tasks` | autonomous | `create_task` |  |
| GET | `/api/v1/tasks` | autonomous | `list_tasks` |  |
| PATCH | `/api/v1/tasks/{task_id}` | autonomous | `update_task` |  |
| GET | `/api/v1/data/accounts` | data | `list_accounts` |  |
| GET | `/api/v1/data/accounts/{account_id}` | data | `get_account` |  |
| POST | `/api/v1/data/accounts/{account_id}/score` | data | `score_account` | Recompute score from current data in the graph. |
| POST | `/api/v1/data/import` | data | `create_import` |  |
| POST | `/api/v1/data/import/{import_id}/dedupe` | data | `dedupe_import` | Match accounts created by this import against the existing graph. |
| POST | `/api/v1/data/import/{import_id}/enrich` | data | `enrich_import` |  |
| POST | `/api/v1/data/import/{import_id}/normalize` | data | `normalize_import` |  |
| GET | `/api/v1/data/import/{import_id}/report` | data | `import_report` |  |
| GET | `/api/v1/data/imports` | data | `list_imports` |  |
| GET | `/api/v1/data/sources/catalog` | data | `list_data_sources` | Compliance-graded Saudi business data source catalog. |
| POST | `/api/v1/data/suppression` | data | `add_suppression` |  |
| GET | `/api/v1/data/suppression` | data | `list_suppression` |  |
| POST | `/api/v1/accounts/{account_id}/brief` | dominance | `account_brief` |  |
| POST | `/api/v1/automation/score-tuner/run` | dominance | `score_tuner_run` |  |
| POST | `/api/v1/customers/{customer_id}/proof-pack` | dominance | `customer_proof_pack` |  |
| GET | `/api/v1/dashboard/dominance` | dominance | `dashboard_dominance` |  |
| GET | `/api/v1/objections/bank` | dominance | `objections_bank` | Return all 13 objection categories with response drafts. |
| POST | `/api/v1/offers/route` | dominance | `offers_route` |  |
| POST | `/api/v1/partners/revenue-machine/run` | dominance | `partners_revenue_machine_run` |  |
| GET | `/api/v1/signals/account/{account_id}` | dominance | `get_signals_for_account` | Return persisted SignalRecord rows + freshly-detected signals. |
| POST | `/api/v1/automation/daily-report/generate` | drafts | `automation_daily_report_generate` |  |
| GET | `/api/v1/automation/revenue-machine/export` | drafts | `revenue_machine_export` |  |
| POST | `/api/v1/automation/revenue-machine/run` | drafts | `revenue_machine_run` |  |
| GET | `/api/v1/dashboard/revenue-machine/history` | drafts | `dashboard_revenue_machine_history` | Last N days of revenue machine output (default 14). |
| GET | `/api/v1/dashboard/revenue-machine/today` | drafts | `dashboard_revenue_machine_today` |  |
| POST | `/api/v1/gmail/drafts/create` | drafts | `gmail_drafts_create` | Create a single Gmail draft. Body: to_email, subject, body_plain, account_id. |
| POST | `/api/v1/gmail/drafts/create-batch` | drafts | `gmail_drafts_create_batch` |  |
| GET | `/api/v1/gmail/drafts/today` | drafts | `gmail_drafts_today` |  |
| POST | `/api/v1/linkedin/drafts/create` | drafts | `linkedin_drafts_create` | Create a LinkedIn draft. NEVER auto-sent. Body: company_name, message_ar, optional rest. |
| GET | `/api/v1/linkedin/drafts/today` | drafts | `linkedin_drafts_today` |  |
| POST | `/api/v1/linkedin/drafts/{draft_id}/manual-capture` | drafts | `linkedin_drafts_manual_capture` |  |
| PATCH | `/api/v1/linkedin/drafts/{draft_id}/mark-sent` | drafts | `linkedin_drafts_mark_sent` | Sami marks 'I sent this manually'. Updates status + sent_at. |
| POST | `/api/v1/replies/respond` | drafts | `replies_respond` |  |
| POST | `/api/v1/replies/route` | drafts | `replies_route` |  |
| POST | `/api/v1/email/connect/gmail` | email_send | `connect_gmail` | Returns the exact 8-step OAuth setup Sami runs once locally. |
| POST | `/api/v1/email/replies/sync` | email_send | `replies_sync` |  |
| POST | `/api/v1/email/send-approved` | email_send | `send_approved` |  |
| POST | `/api/v1/email/send-batch` | email_send | `send_batch` |  |
| GET | `/api/v1/email/status` | email_send | `email_status` |  |
| POST | `/api/v1/os/bulk-process` | full_os | `os_bulk_process` |  |
| POST | `/api/v1/os/process` | full_os | `os_process` |  |
| POST | `/api/v1/os/process-and-act` | full_os | `os_process_and_act` |  |
| GET | `/api/v1/os/stages` | full_os | `list_stages` | Show all 12 stages + allowed transitions. |
| POST | `/api/v1/os/test-send` | full_os | `os_test_send` |  |
| GET | `/api/v1/os/whatsapp-providers` | full_os | `whatsapp_providers_status` | Which WhatsApp providers are configured + the smart-fallback chain order. |
| GET | `/_test_sentry` | health | `test_sentry` | Deliberate error to verify Sentry integration. |
| GET | `/health` | health | `health` | Liveness + config summary. |
| GET | `/health/deep` | health | `health_deep` | Deep health check — verifies DB, Redis, LLM providers. |
| GET | `/healthz` | health | `healthz` | Standard healthz alias for UptimeRobot/K8s probes. |
| GET | `/live` | health | `live` | Liveness probe. |
| GET | `/ready` | health | `ready` | Readiness probe. |
| POST | `/api/v1/leads` | leads | `create_lead` | Submit a new lead — runs through the full acquisition pipeline. |
| POST | `/api/v1/leads/discover/local` | leads | `discover_local_endpoint` | Saudi local lead engine — chains Google Places → SerpApi → Apify → static. |
| GET | `/api/v1/leads/discover/local-industries` | leads | `list_local_industries` | Saudi local lead engine — chains Google Places → SerpApi → Apify → static. |
| POST | `/api/v1/leads/discover/web` | leads | `discover_web_endpoint` | Web lead discovery via SearchProvider chain (Google CSE → Tavily → static). |
| POST | `/api/v1/leads/enrich/batch` | leads | `enrich_batch_endpoint` |  |
| POST | `/api/v1/leads/enrich/full` | leads | `enrich_full_endpoint` |  |
| POST | `/api/v1/outreach/prepare-from-data` | outreach | `prepare_from_data` |  |
| GET | `/api/v1/outreach/queue` | outreach | `list_queue` |  |
| POST | `/api/v1/outreach/queue/{queue_id}/approve` | outreach | `approve_queue` |  |
| POST | `/api/v1/outreach/queue/{queue_id}/skip` | outreach | `skip_queue` |  |
| POST | `/api/v1/checkout` | pricing | `create_checkout` |  |
| GET | `/api/v1/pricing/plans` | pricing | `list_plans` | List available plans. Not linked from landing — required for approval-gated quotes. |
| POST | `/api/v1/webhooks/moyasar` | pricing | `moyasar_webhook` |  |
| POST | `/api/v1/prospect/bulk-enrich` | prospect | `bulk_enrich` |  |
| POST | `/api/v1/prospect/contacts` | prospect | `contacts` |  |
| POST | `/api/v1/prospect/demo` | prospect | `demo` | Canned demo response for landing UI preview. No LLM call. |
| POST | `/api/v1/prospect/discover` | prospect | `discover` |  |
| POST | `/api/v1/prospect/enrich-domain` | prospect | `enrich_domain` |  |
| POST | `/api/v1/prospect/enrich-tech` | prospect | `enrich_tech` |  |
| POST | `/api/v1/prospect/inbound/email` | prospect | `inbound_email` |  |
| POST | `/api/v1/prospect/inbound/form` | prospect | `inbound_form` |  |
| POST | `/api/v1/prospect/inbound/handle` | prospect | `inbound_handle` |  |
| POST | `/api/v1/prospect/inbound/linkedin` | prospect | `inbound_linkedin` |  |
| POST | `/api/v1/prospect/inbound/sms` | prospect | `inbound_sms` |  |
| POST | `/api/v1/prospect/inbound/whatsapp` | prospect | `inbound_whatsapp` |  |
| POST | `/api/v1/prospect/message` | prospect | `message_endpoint` |  |
| POST | `/api/v1/prospect/route` | prospect | `route_endpoint` |  |
| POST | `/api/v1/prospect/score` | prospect | `score_endpoint` |  |
| POST | `/api/v1/prospect/search` | prospect | `search` |  |
| GET | `/api/v1/prospect/search-diag` | prospect | `search_diag` | Diagnose env var presence without revealing values. |
| GET | `/api/v1/prospect/use-cases` | prospect | `list_use_cases` |  |
| POST | `/api/v1/public/demo-request` | public | `demo_request` | Public landing form — captures demo request and returns Calendly booking URL. |
| GET | `/api/v1/public/health` | public | `public_health` | Unauthenticated health probe for landing page to show live status. |
| POST | `/api/v1/public/partner-application` | public | `partner_application` | Public partner signup — for agencies/freelancers/consultants. |
| POST | `/api/v1/customers/daily-report` | revenue | `customers_daily_report` |  |
| POST | `/api/v1/leads/score` | revenue | `score_lead_body` |  |
| POST | `/api/v1/negotiation/respond` | revenue | `negotiation_respond` |  |
| POST | `/api/v1/partners/deal` | revenue | `partners_deal` |  |
| POST | `/api/v1/partners/outreach` | revenue | `partners_outreach` |  |
| POST | `/api/v1/sales/proposal` | sales | `generate_proposal` | Generate a proposal on demand (outside the pipeline). |
| POST | `/api/v1/sales/script` | sales | `build_script` | Return a bilingual sales script for a given sector + type. |
| GET | `/api/v1/sectors/best/opportunity` | sectors | `best_opportunity` | Return the highest-leverage sector. |
| POST | `/api/v1/sectors/content` | sectors | `generate_content` | Generate a content piece for a sector topic. |
| GET | `/api/v1/sectors/target/list` | sectors | `target_sectors` | Our top-5 target sectors. |
| GET | `/api/v1/sectors/{sector}` | sectors | `sector_intel` | Deep intel for one Saudi sector. |
| POST | `/api/v1/webhooks/calendly` | webhooks | `calendly_webhook` | Receive Calendly event lifecycle notifications. |
| POST | `/api/v1/webhooks/hubspot` | webhooks | `hubspot_webhook` | Receive HubSpot subscription events. |
| GET | `/api/v1/webhooks/whatsapp` | webhooks | `whatsapp_verify` | Meta WhatsApp webhook verification. |
| POST | `/api/v1/webhooks/whatsapp` | webhooks | `whatsapp_incoming` | Handle incoming WhatsApp messages — route them as leads. |

## By router

- **admin**: 11 endpoints
- **agents**: 4 endpoints
- **automation**: 5 endpoints
- **autonomous**: 25 endpoints
- **data**: 12 endpoints
- **dominance**: 8 endpoints
- **drafts**: 14 endpoints
- **email_send**: 5 endpoints
- **full_os**: 6 endpoints
- **health**: 6 endpoints
- **leads**: 6 endpoints
- **outreach**: 4 endpoints
- **pricing**: 3 endpoints
- **prospect**: 18 endpoints
- **public**: 3 endpoints
- **revenue**: 5 endpoints
- **sales**: 2 endpoints
- **sectors**: 4 endpoints
- **webhooks**: 4 endpoints

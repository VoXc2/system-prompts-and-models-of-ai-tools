# Dealix — Revenue Readiness Checklist

## Pricing Path
- [x] 3 plans defined in API (Starter 999 / Growth 2999 / Scale 7999 SAR)
- [x] Pilot offer (499 SAR / 7 days) documented
- [x] Agency pricing (setup 3K-15K + 20-30% MRR) documented
- [ ] Pricing page on dealix.me (exists in API, not as public page)

## Invoice Path
- [x] Manual invoice template ready (FIRST_REVENUE_ATTEMPT.md)
- [ ] Moyasar live invoice — blocked (502, KYC/key issue)
- [x] Bank transfer info ready
- [x] STC Pay ready

## Payment Path
- [x] Manual payment: bank transfer + STC Pay + proof workflow
- [x] Payment confirmation → onboarding trigger documented
- [ ] Moyasar automated: checkout returns 502
- [ ] Moyasar sandbox: no test key in Railway

**Verdict: Manual payment path = READY. Automated = BLOCKED.**

## Booking Path
- [x] Calendly link active (calendly.com/sami-assiri11/dealix-demo)
- [x] Landing page links to Calendly
- [x] Trial signup form redirects to Calendly on success
- [x] Email templates include Calendly link
- [ ] Calendly webhook → CRM sync (code exists, E2E untested)

## CRM Sync Path
- [x] HubSpot connector code exists (services/crm_sync_service.py)
- [ ] HubSpot API key in Railway — missing
- [ ] E2E test: lead → HubSpot contact — untested
- [x] Manual CRM: Google Sheet tracker template ready

**Verdict: Manual CRM (Google Sheet) = READY. HubSpot = BLOCKED on key.**

## Follow-up Path
- [x] Automation endpoint: reply classifier (12 categories)
- [x] Follow-up templates: Day +2, +5, +10
- [x] Reply response templates in Arabic
- [ ] Gmail OAuth send adapter — needs Google Cloud setup
- [x] Manual follow-up: copy-paste from templates

**Verdict: Manual follow-up = READY. Automated = needs Gmail OAuth.**

## Overall Revenue Readiness

| Component | Manual | Automated |
|-----------|--------|-----------|
| Pricing | READY | READY (API) |
| Invoice | READY | BLOCKED (Moyasar) |
| Payment | READY | BLOCKED (Moyasar) |
| Booking | READY | READY (Calendly) |
| CRM | READY (Sheet) | BLOCKED (HubSpot key) |
| Follow-up | READY (copy-paste) | BLOCKED (Gmail OAuth) |
| Outreach | READY (manual) | READY (automation endpoints) |

**GO/NO-GO: GO for manual revenue. First sale possible today.**

## Definition of Done for "Revenue Live"
- [ ] First 5 outreach messages sent (WhatsApp warm)
- [ ] First demo booked via Calendly
- [ ] First pilot payment received (499 SAR bank/STC)
- [ ] First customer onboarded (Day 0 checklist)
- [ ] First daily report sent to customer

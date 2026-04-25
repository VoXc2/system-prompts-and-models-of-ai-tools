# Dealix — Revenue Readiness Checklist

**Last verified:** 2026-04-25
**Railway healthz:** 200 (verified)
**Pricing API:** 200 (verified: Starter 999 / Growth 2999 / Scale 7999 SAR)

---

## 1. Pricing Path

| Item | Status | Evidence |
|------|--------|---------|
| Plans in API | DONE | `/api/v1/pricing/plans` returns 3 plans, SAR currency |
| Pilot offer defined | DONE | 499 SAR / 7 days / documented in COMMAND_CENTER.md |
| Agency pricing defined | DONE | AGENCY_PARTNER_OFFER.md: setup 3K-15K + 20-30% MRR |
| Public pricing page | NOT DONE | API exists but no public-facing pricing page on dealix.me |

**Blocker:** None for manual sales. Pricing page is P1 for inbound.

## 2. Invoice Path

| Item | Status | Evidence |
|------|--------|---------|
| Manual invoice template | DONE | FIRST_REVENUE_ATTEMPT in revenue-activation/ |
| Bank transfer details | DONE | Documented in COMMAND_CENTER.md |
| STC Pay | DONE | Ready |
| Moyasar live invoice | BLOCKED | `/api/v1/checkout` returns 502 — Moyasar-side issue |
| Moyasar sandbox | NOT TESTED | No `MOYASAR_TEST_SECRET_KEY` in Railway env |

**Workaround:** Manual invoice via bank transfer or STC Pay. Works today.

## 3. Payment Path

| Item | Status | Evidence |
|------|--------|---------|
| Bank transfer acceptance | READY | Account info available |
| STC Pay acceptance | READY | Number available |
| Manual proof workflow | READY | Customer sends screenshot → Sami confirms → onboarding starts |
| Moyasar automated payment | BLOCKED | 502 on checkout — Moyasar dashboard issue (KYC or key) |
| Moyasar test payment (1 SAR) | NOT TESTED | Needs `MOYASAR_TEST_SECRET_KEY` or Sami to test `sk_live_` via curl |
| Payment → onboarding trigger | MANUAL | On payment proof → start onboarding checklist within 4h |

**Manual payment path: FULLY OPERATIONAL.**

## 4. Booking Path

| Item | Status | Evidence |
|------|--------|---------|
| Calendly link | ACTIVE | calendly.com/sami-assiri11/dealix-demo |
| Landing → Calendly | DONE | trial-signup.html redirects on form submit |
| Email templates → Calendly | DONE | All email templates include Calendly link |
| Outreach messages → Calendly | DONE | All DM templates include Calendly link |
| Calendly → webhook | NOT TESTED | Code exists but no E2E booking verified |
| Calendly → CRM | NOT TESTED | HubSpot key missing in Railway |

**Booking path: OPERATIONAL for manual flow (link → booking → Sami sees in Calendly).**

## 5. CRM Sync Path

| Item | Status | Evidence |
|------|--------|---------|
| HubSpot connector code | EXISTS | `services/crm_sync_service.py` |
| HubSpot API key in Railway | MISSING | Not set in Railway env Dealix/web |
| E2E: lead → HubSpot contact | NOT TESTED | Cannot test without key |
| Manual CRM (Google Sheet) | READY | Tracker template in ops docs |
| Pipeline stages defined | DONE | new → sent → replied → demo → pilot → paid → churned |

**Manual CRM: READY. HubSpot automated: BLOCKED on API key.**

## 6. Follow-up Path

| Item | Status | Evidence |
|------|--------|---------|
| Reply classifier | DONE | `POST /api/v1/automation/reply/classify` — 12 categories |
| Follow-up templates (Day +2/+5/+10) | DONE | Generated per lead in email/generate endpoint |
| Arabic response templates | DONE | Pre-written Khaliji response per category |
| Gmail OAuth adapter | NOT BUILT | Needs Google Cloud OAuth setup |
| Manual follow-up | READY | Copy-paste from templates |

**Manual follow-up: READY. Gmail auto-send: BLOCKED on OAuth setup.**

## 7. Test Payment Path

| Test | Status | How to Test |
|------|--------|-------------|
| Moyasar sandbox | NOT TESTED | Add `MOYASAR_TEST_SECRET_KEY` (sk_test_...) in Railway → hit `/api/v1/checkout` |
| Moyasar live | BLOCKED | sk_live_ exists in Railway but returns 502 |
| Manual bank transfer | READY | Ask friend to transfer 1 SAR → verify receipt |
| Manual STC Pay | READY | Ask friend to STC Pay 1 SAR → verify receipt |

**Recommended first test:** Manual bank transfer from a friend. Zero technical dependency.

## 8. Manual Fallback Summary

| Function | Automated | Manual Fallback | Status |
|----------|-----------|----------------|--------|
| Lead response | AI endpoint exists | Sami responds manually | READY |
| Qualification | Automation endpoint | Sami asks questions manually | READY |
| Booking | Calendly auto | Sami proposes 2 times | READY |
| Payment | Moyasar | Bank/STC Pay + proof | READY |
| CRM | HubSpot | Google Sheet | READY |
| Follow-up | Gmail OAuth | Copy-paste templates | READY |
| Reporting | Dashboard | Manual WhatsApp/email to client | READY |

**Every function has a working manual fallback. No function is truly blocked.**

---

## Definition of Done for "Revenue Live"

| Gate | Status | What Proves It |
|------|--------|---------------|
| First 5 outreach messages sent | NOT DONE | Sami confirms SENT |
| First demo booked via Calendly | NOT DONE | Calendly notification |
| First pilot payment received (499 SAR) | NOT DONE | Bank/STC Pay screenshot |
| First customer onboarded (Day 0 checklist) | NOT DONE | Checklist filled |
| First daily report sent to customer | NOT DONE | WhatsApp/email sent |
| PostHog receives at least 1 event | NOT DONE | PostHog dashboard check |
| Manual payment log has 1 entry | NOT DONE | File updated |

**0/7 done. Revenue is NOT live. Product is live. The gap is sales activity, not engineering.**

---

## Moyasar Diagnostic Checklist (for Sami)

If 502 persists, check these in order:
1. Moyasar dashboard → Account Status: Active? Pending KYC? Suspended?
2. Moyasar dashboard → API Keys: Is `sk_live_` the latest generated key?
3. Test from terminal: `curl -u "sk_live_...:" https://api.moyasar.com/v1/invoices -d "amount=100" -d "currency=SAR"`
4. If "authentication_error" → key wrong or regenerated. Get new key.
5. If "account_inactive" → KYC not complete. Finish KYC in Moyasar.
6. If success → Railway env has whitespace or wrong value. Re-paste key carefully.

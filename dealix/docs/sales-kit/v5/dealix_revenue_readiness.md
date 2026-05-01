# Dealix — Revenue Readiness Plan
> End-to-end path: lead → quote → invoice → payment → CRM → fulfillment → renewal.

## 1) Pricing Path
| Plan | Price (SAR) | Billing | Lead cap |
|---|---|---|---|
| Pilot | 1 | 7-day one-time | 50 |
| Starter | 999 | monthly | 500 |
| Growth | 2,999 | monthly | 2,500 |
| Scale | 7,999 | monthly | unlimited |

**ARPU (40/30/10 mix Starter/Growth/Scale)**: 2,099 SAR
**Annual value per customer**: ~25,200 SAR (excl. churn)

## 2) Quote Path
1. Prospect books demo via Calendly
2. Post-demo: Sami sends quote via `docs/sales-kit/dealix_pilot_agreement.md` (template)
3. Customer signs (DocuSign or WhatsApp confirmation for pilot)
4. Move to invoice step

## 3) Invoice Path (Moyasar Invoices API)
**Implementation**: `dealix/payments/moyasar.py::create_invoice()`

```python
# Production usage
async def issue_invoice(customer_email: str, amount_sar: int, plan: str):
    client = MoyasarClient()
    inv = await client.create_invoice(
        amount=amount_sar * 100,  # halalas
        currency="SAR",
        description=f"Dealix {plan} — شهر واحد",
        callback_url="https://dealix.sa/payment/callback",
        metadata={"customer": customer_email, "plan": plan}
    )
    # Send inv['url'] via WhatsApp + email
    return inv['url']
```

**Flow**:
1. Sales confirms deal
2. `issue_invoice(...)` → Moyasar hosted invoice URL
3. URL sent via WhatsApp + email
4. Customer pays → Moyasar webhook fires → `api/routers/webhooks.py`
5. Handler verifies signature → updates lead.status = "paid"
6. Posthog event fired: `payment_completed`
7. Sentry breadcrumb logged

## 4) Payment Path
- **Gateway**: Moyasar (Saudi-licensed, SAMA-regulated)
- **Webhook**: `/api/webhooks/moyasar` — signature verified with `X-Moyasar-Signature`
- **Retry**: via existing DLQ (`dealix/reliability/dlq.py`) — 3 retries, exponential backoff
- **Reconciliation**: daily via `cron/reconcile_payments.py` (P1 — needs scheduling)

## 5) Booking Path
- **Tool**: Calendly (free → Premium if need webhooks)
- **Flow**: prospect picks slot → Calendly confirm email → webhook (P1) → lead.stage=demo_booked
- **Reminders**: Calendly native (24h + 1h)

## 6) CRM Path
- **Current CRM**: internal DB via `api/routers/leads.py`
- **Stages**: new → qualified → demo_booked → proposal_sent → paid → onboarding → active → renewal_due → churned
- **Fields**: name, email, phone_e164, company, plan, invoice_id, payment_status, created_at, last_contact_at, owner
- **Sync to HubSpot**: P2 (not needed now)

## 7) ZATCA E-Invoice Readiness
**Trigger**: When annual revenue crosses the e-invoice mandate threshold (per ZATCA phased rollout).

**Plan**:
- **Phase 1 (now)**: Moyasar Invoices — simplified tax invoice sufficient for early pilots
- **Phase 2 (when mandated)**: integrate with ZATCA Fatoora platform
  - Generate XML (UBL 2.1) per ZATCA spec
  - Sign with ZATCA cert
  - Submit to reporting/clearance endpoint
  - Store cleared invoice + QR code
- **Owner**: Sami + external accountant
- **Estimated effort**: 2–3 weeks dev + certification

## 8) Proof Path (case studies)
- First 3 pilots = case study candidates
- Collect: before/after metrics, quote, logo permission
- Publish: `landing/case-studies/*.html` (P2)
- Video testimonial: within 30 days of go-live

## 9) Follow-up Path
| Day | Channel | Content |
|---|---|---|
| 0 | WhatsApp | Welcome + onboarding link |
| 1 | Email | Full feature walkthrough video |
| 3 | WhatsApp | "Any questions?" |
| 7 | Email | First week report |
| 14 | WhatsApp | Mid-pilot check-in |
| 25 | Email | Upgrade offer (end of pilot) |
| 30 | WhatsApp | Close: paid or churned |

## 10) Renewal Path
- Day -7: email "renewal coming up"
- Day -3: WhatsApp "confirm?"
- Day 0: auto-invoice (once subscription infra built, P2)
- Day +7: if unpaid → grace period ends, archive

## 11) What's ready vs what's not
| Item | Code ready | Tested E2E | In production |
|---|---|---|---|
| Moyasar Invoice create | ✅ | ❌ | ❌ |
| Moyasar webhook | ✅ | ❌ | ❌ |
| Lead status update | ✅ | ❌ | ❌ |
| PostHog events | ✅ | 🟡 partial | 🟡 |
| Calendly booking | ✅ (link) | ✅ | ✅ |
| Calendly → CRM sync | ❌ | ❌ | ❌ |
| ZATCA e-invoice | ❌ | ❌ | ❌ |
| Reconciliation cron | ❌ | ❌ | ❌ |
| Renewal automation | ❌ | ❌ | ❌ |

**Verdict**: revenue infrastructure is **70% coded, 10% tested, 0% battle-proven**. Must run 1 SAR test before claiming ready.

## 12) Definition of "Revenue Ready"
All must be true:
- [ ] Moyasar secret rotated
- [ ] 1 SAR test invoice issued
- [ ] 1 SAR test payment completed
- [ ] Webhook fired and verified
- [ ] Lead DB updated to `paid`
- [ ] PostHog `payment_completed` event visible
- [ ] Sentry breadcrumb recorded
- [ ] Sami received email + WhatsApp confirmation
- [ ] Invoice retrievable via `fetch_invoice(id)`
- [ ] Reconciliation manually verifiable

# 💰 Dealix — Revenue Readiness Status

**Last updated:** 2026-04-24
**Status:** PARTIALLY READY — can collect via manual Moyasar invoices; full automation blocked by Railway deploy.

---

## Revenue Path (7 Layers)

| Layer | Status | Evidence | Gap |
|-------|--------|----------|-----|
| 1. Pricing | ✅ VERIFIED READY | Defined in repo + landing | — |
| 2. Quote/Proposal | 🟡 PARTIAL | Enterprise template exists | No self-serve quote |
| 3. Invoice generation | 🟡 PARTIAL | HTML template + Moyasar API | Not automated |
| 4. Payment gateway | 🟡 PARTIAL | Moyasar integration code ready | Not deployed |
| 5. Confirmation | ❌ NOT READY | No email on payment | Needs Railway + email service |
| 6. Customer record | ❌ NOT READY | No CRM active | Needs HubSpot setup |
| 7. Follow-up | ✅ VERIFIED READY | Cadence defined, manual | — |

**Launch-ready via manual fallback:** YES
**Fully automated revenue:** NO (requires Railway + HubSpot + SendGrid setup)

---

## Manual Revenue Flow (Available Today)

```
Lead contacts you (WhatsApp/LinkedIn/email)
    ↓
You send Calendly link for demo
    ↓
Demo call (30 min, your Zoom/Meet)
    ↓
You verbally close pilot (1 SAR)
    ↓
You manually create Moyasar invoice (2 min in dashboard)
    ↓
You send payment link via WhatsApp
    ↓
Customer pays → Moyasar confirms
    ↓
You manually send welcome email
    ↓
You manually start onboarding
```

**Volume ceiling:** ~10 customers before breaking.

---

## Automated Revenue Flow (Future, after Railway deploy)

```
Lead submits form on landing page
    ↓
Dealix AI qualifies via chat
    ↓
Auto-books demo in Calendly
    ↓
Day of demo: auto-reminder sent
    ↓
Post-demo: auto-sends Moyasar invoice
    ↓
Payment → webhook updates DB
    ↓
Welcome email automated
    ↓
Onboarding sequence starts
```

**Volume ceiling:** 1000+ customers.

---

## Pricing Architecture

### Self-serve Tiers
| Plan | Price/mo (SAR) | Target |
|------|----------------|--------|
| Pilot | 1 (7-day trial) | Evaluation |
| Starter | 999 | 1-3 reps |
| Growth | 2,999 | 4-10 reps |
| Scale | 7,999 | 10+ reps |

### Setup Fees (one-time, optional)
| Service | Price (SAR) |
|---------|-------------|
| Basic setup | 1,000 |
| CRM integration | 3,000 |
| White-label | 15,000 |

### Partner Pricing (commissions paid from MRR)
| Partner type | Commission % |
|--------------|--------------|
| Referral only | 10% for 12 months |
| Service provider | 20% lifetime |
| Agency partner | 25% lifetime |

---

## Invoice Numbering Scheme

Format: `DLX-YYYY-NNNNN`
- DLX-2026-00001 (first invoice)
- DLX-2026-00002
- ... sequential

Keep tracker in Google Sheet:
| Invoice # | Date | Customer | Amount | Plan | Status | Paid Date |
|-----------|------|----------|--------|------|--------|-----------|

---

## ZATCA / VAT Requirements

**Current state:**
- Freelance license allows issuing basic invoices
- NOT subject to VAT until annual revenue exceeds 375,000 SAR
- Voluntary VAT registration allowed above 187,500 SAR

**Operational approach:**
1. Year 1 (< 187,500 SAR revenue): Simple invoices, no VAT
2. Approaching threshold: Consult accountant
3. Register for VAT + ZATCA e-invoicing when required
4. **Do not claim legal compliance** — consult CPA for your specific case

**Tool recommendation:** Wafeq (29 SAR/month) — Saudi-native, ZATCA-ready when needed.

---

## Refund Policy

**Pilot (1 SAR, 7 days):**
- Unconditional refund if requested within trial period
- Processed within 7 days

**Starter/Growth/Scale (monthly):**
- 30-day money-back guarantee
- Prorated refund for unused month after 30 days
- No refund after 90 days

**Scale (annual):**
- 30-day full refund
- After 30 days: prorated monthly-equivalent refund
- Enterprise contracts: custom terms in MSA

---

## Payment Methods Supported

| Method | Status | Gateway |
|--------|--------|---------|
| Mada | Via Moyasar | ✅ |
| Visa / Mastercard | Via Moyasar | ✅ |
| Apple Pay | Via Moyasar | ✅ |
| STC Pay | Via Moyasar | ✅ |
| Bank Transfer | Direct to bank | ✅ Manual |
| SADAD | Not yet | 🟡 Future |
| Crypto | Not planned | ❌ |

---

## Daily Revenue Operations

See `docs/growth/DAILY_REVENUE_OPERATING_SYSTEM.md` for the full operating rhythm.

**Key daily checks:**
1. Morning: Moyasar dashboard for overnight payments
2. Process new payments → confirmation email
3. Onboard any new customers within 4 hours
4. Update CRM with payment data

---

## Final Readiness Verdict

**Can Dealix collect money today?**
✅ YES — via manual Moyasar invoicing.

**Can Dealix collect money at scale?**
❌ NO — requires Railway backend deployment first.

**First Revenue:**
Expected within 7-14 days if outreach is started today.

**Sustainable $10K+ MRR:**
Expected month 3-4 if daily system is followed.

**$100K+ MRR:**
Expected month 9-12 with successful partner channel.

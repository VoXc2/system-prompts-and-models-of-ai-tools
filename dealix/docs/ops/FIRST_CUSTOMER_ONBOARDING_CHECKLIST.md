# 🎯 Dealix — First Customer Onboarding Checklist

**Status:** Manual for first 10 customers. Automate after.
**Goal:** From "yes" to "live" in 48 hours.

---

## Section 1 — Customer Intake Form

Ask customer (over call or form):

1. **Business Info**
   - Legal company name:
   - CR number (if available):
   - Primary contact name + role:
   - Email + WhatsApp:
   - Website URL:

2. **Business Type**
   - [ ] SaaS  [ ] E-commerce  [ ] Agency  [ ] Consulting
   - [ ] Healthcare  [ ] Real Estate  [ ] Education
   - [ ] Logistics  [ ] Other: ___

3. **Lead Sources (where do leads come from today?)**
   - [ ] Website form  [ ] WhatsApp  [ ] Instagram DM
   - [ ] Phone calls  [ ] Ads  [ ] Referrals  [ ] Other

4. **Current CRM**
   - [ ] HubSpot  [ ] Zoho  [ ] Salesforce
   - [ ] Excel  [ ] None  [ ] Other: ___

5. **Current booking tool**
   - [ ] Calendly  [ ] Google Calendar  [ ] Outlook
   - [ ] None (manual)

6. **Qualification Questions (8 they want Dealix to ask)**
   1. ___
   2. ___
   3. ___
   4. ___
   5. ___
   6. ___
   7. ___
   8. ___

7. **Offer / Pricing rules**
   - Price range: ___
   - Currencies accepted: ___
   - Payment terms: ___

8. **Handoff recipient**
   - Who gets the qualified lead alert?
   - Email + WhatsApp for notifications:

9. **Go-Live Requirements**
   - [ ] Arabic dialect preference (Saudi / Gulf / Egyptian / Levantine)
   - [ ] Business hours to respond:
   - [ ] Language mix (Arabic only / Arabic + English)

---

## Section 2 — Sami's Setup Tasks (2-4 hours)

- [ ] Receive payment confirmation
- [ ] Log in pipeline_tracker.csv with payment_status=paid
- [ ] Send welcome email
- [ ] Create customer Notion/Google Doc with all intake info
- [ ] Schedule 60-min kick-off call within 48 hours
- [ ] Prepare custom BANT questions based on their segment
- [ ] Test Dealix prompts manually against their 3 typical customers
- [ ] Document handoff flow specific to their team

---

## Section 3 — Manual Operation (First Week)

Since product dashboard isn't built yet, operate manually:

### Daily ritual (founder runs this for customer)
1. Customer shares their incoming leads (forwarded email / CSV / form copy)
2. Sami responds to each lead within 1 hour
3. Uses Dealix conversation framework manually (via Claude or own AI)
4. Books demo in customer's Calendly
5. Sends qualification brief to customer team
6. Reports daily numbers to customer

### Tools for manual ops
- Dealix internal: use backend via `/api/v1/checkout` or demo-request endpoints
- Calendly customer's account (ask for API key/integration)
- WhatsApp Business for outreach to their leads
- Google Sheet per customer to track leads

---

## Section 4 — Week 1 Milestones

| Day | Action |
|-----|--------|
| Day 0 | Payment + kick-off call + intake form |
| Day 1 | First test leads processed by Sami (manually) |
| Day 2 | Customer team trained on handoff flow |
| Day 3 | First real customer leads routed through Dealix process |
| Day 5 | Mid-week check-in with customer |
| Day 7 | Week 1 report: leads in, qualified %, demos booked |

---

## Section 5 — Success Metrics (report to customer weekly)

- Leads received: N
- Leads qualified: N (%)
- Demos booked: N
- No-shows: N (%)
- Pipeline value: X SAR
- Customer team time saved: X hours

---

## Section 6 — When to Transition to Automated Dashboard

Move this customer from manual to automated when:
- Dealix dashboard for customer accounts is built (post first 10 customers)
- Customer is comfortable with AI doing the conversation vs. Sami supervising
- Metrics are stable (< 2% error rate on qualification)

---

## Section 7 — If Customer Wants Refund

- Within 7 days (Pilot): Full refund, no questions
- 8-30 days (Starter): Prorated refund
- After 30 days: Month-end cancel, keep data for 30 days for recovery

Process:
1. Refund initiated via same payment channel (bank transfer back / STC Pay)
2. Issue credit note
3. Update tracker: payment_status=refunded
4. Exit interview: 15 min call to learn why
5. Document learnings in `docs/ops/churn_reasons.md`

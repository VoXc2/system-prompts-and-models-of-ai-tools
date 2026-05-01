# Dealix — Customer Success Playbook

**For first 10 customers: manual-first delivery. After that, convert manual steps into product.**
Paired with `FIRST_CUSTOMER_DELIVERY_TEMPLATE.md` (tactical) and `first_customer_delivery_template.md` (intake form).

---

## Principles

1. **Delight beats feature count.** First customer's referral is worth more than 10 features.
2. **Manual acceleration > broken automation.** If an automation isn't solid, do it by hand.
3. **Every ticket is product research.** Log objection/question/pain → tomorrow's prompt upgrade.
4. **One reply thread = one success metric.** Never context-switch mid-thread.
5. **Arabic default, English on request.** Even with English-only customers, offer bilingual.

---

## Support modes (what Dealix actually helps with)

| Mode | What Dealix does | Customer expectation |
|------|------------------|---------------------|
| **Product question** | Answer via FAQ + route complex to Sami within 2h | Answered accurately within hours |
| **Pricing question** | Route to demo OR quote within 4h | Clear quote same day |
| **Pilot explanation** | 1 SAR × 7 days, unlimited refund — explain upfront | Full clarity, no surprise |
| **Privacy objection** | Send PDPL compliance sheet + answer data-residency | Sheet within 1h |
| **Arabic quality doubt** | Send 3 live sample threads + offer 20-min Zoom demo | Samples within 30min |
| **Integration limit** | Confirm HubSpot/Salesforce/Zoho/Bitrix/webhook | Same-day answer |
| **Route to demo** | Calendly → 20 min → Sami personal | Zero friction |
| **Route to payment** | Manual SOP (bank/STC Pay/invoice) | Invoice within 15 min of verbal yes |
| **Route to onboarding** | kickoff call within 4 hours of payment | Onboarded Day 1 |

---

## First customer onboarding (step-by-step)

### Day 0 — Sale closed
- [ ] Payment received (manual or Moyasar)
- [ ] Confirmation email sent within 30 min
- [ ] Calendly kickoff call booked for Day 1

### Day 1 — Kickoff call (45 min)
Agenda (hard time-boxed):
- **0-5 min:** Welcome, confirm scope of pilot
- **5-20 min:** Intake form (see `first_customer_delivery_template.md`)
- **20-35 min:** Walk through how Dealix will work for their specific business
- **35-40 min:** Set success metric (e.g., "respond to 20 leads within 45 sec, 5 demos booked")
- **40-45 min:** Daily check-in schedule + next steps

### Day 2-6 — Manual delivery
Sami does this manually for first 10 customers:
- Every incoming lead → Sami reads → crafts Arabic reply (use Dealix prompt as draft) → sends → logs
- Daily 10-minute check-in message to customer: "اليوم: رددنا على X leads، حجزنا Y demos"
- Capture:
  - Which objections appeared?
  - Which messages converted best?
  - Did the customer express delight or frustration?

### Day 7 — Pilot review
- [ ] 30-min review call
- [ ] Share metrics + learnings
- [ ] Upgrade path: Pilot → Starter (999 SAR/mo)
- [ ] Ask for testimonial (even if they don't upgrade)
- [ ] Ask for referral

### Day 8+ — If they upgrade
- [ ] Switch to Starter billing
- [ ] Weekly check-ins for first month
- [ ] Monthly optimization review
- [ ] Move to automation as trust builds

---

## Success metrics per customer

Track in `docs/ops/customer_success_tracker.csv` (create on first customer):

| customer_id | start_date | pilot_end | leads_handled | demos_booked | replies_arabic | avg_response_time | nps_score | churn_risk | upgrade_status |

---

## Red flags → escalate to Sami within 1h

- Customer threatens to churn
- Customer says "your Arabic is wrong" (go immediately to Zoom call)
- Customer asks for feature not built (don't lie — offer roadmap ETA or alternative)
- Customer misses 3 consecutive daily check-ins
- Customer says "this is not what I expected"
- Integration breaks or Dealix misses a lead (apologize + manual recovery within 1 hour)

---

## Conversion from pilot → Starter

**Day 5 soft ask:**
> "أيام قليلة باقية في pilot. بناءً على النتائج حتى الآن، هل تتوقع الاستمرار؟"

**Day 7 firm ask:**
> "الـ pilot انتهى اليوم. النتائج كانت [X leads, Y demos, Z response time]. تبغى تكمل Starter (999 ريال/شهر) من الاثنين؟"

If yes → continue.
If no → ask: "ما اللي منع الاستمرار؟" → log → make them feel great about saying no (it's valuable data).

---

## Escalation path

1. **Customer ticket / question** → Dealix answers via template or Sami within 4h
2. **Objection** → Use `reply_playbooks_ar.md` → resolve OR escalate
3. **Complaint / churn signal** → Sami personal call within 1 business day
4. **Technical issue / integration failure** → manual recovery + root-cause within 48h
5. **Legal / compliance question** → Sami + legal consult (if retained) within 3 business days

---

## Manual-to-automation playbook

After 10 paying customers:

| Manual today | Auto in v2 | Auto in v3 |
|--------------|------------|------------|
| Sami crafts every Arabic reply | LLM drafts, human approves | Fully auto for "confirmed" message types |
| Manual daily check-in message | Templated daily digest | Auto-fire on low-activity day |
| Manual invoice generation | Moyasar auto-invoice on verbal yes | Zero-touch checkout flow |
| Sami reads every objection | Classified by AI + logged | Router handles 80%+ auto |
| Onboarding kickoff call | Same (calls stay human) | Same |
| Success review call | Same | Same |

**Principle:** automate low-risk high-volume, keep human on high-context high-stakes.

---

## What Dealix will NOT do

- Do not make customer commitments beyond written scope
- Do not answer legal or financial advice questions (route to Sami + disclaimer)
- Do not send anything outside pilot scope without customer request
- Do not share one customer's data with another customer
- Do not offer refund beyond written policy
- Do not modify Dealix product prompts for one customer without written request
- Do not auto-send without approval during first 30 days per customer

---

## Weekly customer success review (Fridays, 17:00)

- [ ] Review all active customers (dashboard)
- [ ] Identify top 1 at-risk → proactive outreach before Monday
- [ ] Identify top 1 delighted → ask for testimonial + referral
- [ ] Log top 3 recurring objections → update `objection_library_ar.md`
- [ ] Log top 3 positive threads → capture message templates → update `today_send_queue.md`

---

**The sovereign asset isn't code. It's the log of every conversation.** After 10 customers, the Arabic-specific message library + objection responses + timing patterns become the moat.

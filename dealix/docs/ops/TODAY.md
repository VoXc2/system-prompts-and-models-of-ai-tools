# 🌅 Dealix — TODAY Command Page

**The only page Sami opens each morning. Everything else is reference.**

Target time-box: **60 minutes of execution + async monitoring**.
Read this → act → close tab.

---

## ⏱️ 60-Minute Morning Block

| Minute | Task | File | Check |
|--------|------|------|-------|
| 0–5 | Open `COMPANY_CONTROL_CENTER.md`, re-read Decision State table | `docs/ops/COMPANY_CONTROL_CENTER.md` | ☐ |
| 5–10 | Scan `pipeline_tracker.csv` for any replies since yesterday | `docs/ops/pipeline_tracker.csv` | ☐ |
| 10–15 | Check Railway backend: `curl -s https://web-dealix.up.railway.app/healthz` | — | ☐ |
| 15–20 | Check bank app for any payment received (manual path) | — | ☐ |
| 20–45 | Send 5 messages from `today_send_queue.md` (5 per hour cap) | `docs/ops/today_send_queue.md` | ☐ |
| 45–55 | Update `pipeline_tracker.csv` with `sent_at` timestamps | `docs/ops/pipeline_tracker.csv` | ☐ |
| 55–60 | Publish 1 LinkedIn post (founder voice) from `launch_content_queue.md` | `docs/ops/launch_content_queue.md` | ☐ |

---

## 📬 Afternoon Async (30 min, split across day)

- [ ] Reply to any inbound within 30 min
- [ ] Send 2 agency partner DMs (template in `launch_content_queue.md`)
- [ ] Run Day+2 follow-ups on yesterday's DMs (if any)
- [ ] Update `daily_scorecard.md` with today's numbers before close

---

## 💰 If a Customer Says Yes (TODAY)

**Don't wait for Moyasar KYC. Collect manually.**

1. Confirm plan verbally: Pilot 1 SAR / Starter 999 / Growth 2,999 / Scale 7,999
2. Open `docs/ops/MANUAL_PAYMENT_SOP.md`
3. Copy invoice template → fill customer name, plan, amount
4. Send via WhatsApp + Email
5. Customer pays → Sami sees bank/STC Pay notification within minutes
6. Update `pipeline_tracker.csv`: `payment_status=paid, revenue_sar=[amount]`
7. Start `FIRST_CUSTOMER_ONBOARDING_CHECKLIST.md` kickoff call within 4 hours
8. Deliver per `FIRST_CUSTOMER_DELIVERY_TEMPLATE.md` (manual for first 10)

---

## 🧪 If Moyasar KYC Activates Today

The moment Sami gets the activation email:

```bash
# 1. Copy new sk_live_... from Moyasar dashboard
# 2. Set in Railway env
railway variables set MOYASAR_SECRET_KEY=sk_live_xxxxxxxxx

# 3. Generate 1 SAR test invoice to own email (proof)
bash docs/ops/moyasar_live_test.sh sami.assiri11@gmail.com

# 4. Pay the invoice with own card (1 SAR, refundable)
# 5. Confirm bank credit within 24h
# 6. Flip COMPANY_CONTROL_CENTER.md: Revenue (Moyasar live) 🟢 LIVE
```

Script: `docs/ops/moyasar_live_test.sh` (created below).

---

## 🚦 Decision Triggers

| Signal | Action |
|--------|--------|
| 0 replies by end of Day 3 | Tighten message → test new angle on 5 fresh leads |
| 1 demo booked | Prepare per `dealix_demo_script_30min.md` + rehearse 10 min |
| 1 verbal yes | Do NOT wait on anything — send manual invoice within 15 min |
| 1 payment received | Send welcome email + Calendly kickoff link within 30 min |
| 3 "not now" | Document objection → update `dealix_objection_handler.md` |
| Healthcheck failure | Auto-issue labeled `P0` is created; follow `INCIDENT_RUNBOOK.md` |

---

## 🧱 What NOT to Do Today

- Don't rebuild code that already works
- Don't write more sales copy until 10 messages are out
- Don't add a new tool/integration until it's blocking a specific customer
- Don't wait on Moyasar KYC — manual path is fully operational
- Don't batch DMs into one hour — spread across 9am/11am/2pm/4pm

---

## 📊 End-of-Day (5 min)

Fill `docs/ops/daily_scorecard.md` with today's row:

```
Date: YYYY-MM-DD
DMs sent: __ / 5 target
Replies: __
Demos booked: __
Pilots signed: __
Revenue received (SAR): __
Tomorrow's top change: ____________
```

---

## 🎯 One-Sentence Mission This Week

**Move 5 leads from "pending" to "replied" and sign 1 pilot — even at 1 SAR, even from a friend.**

First paid customer unlocks social proof. Everything after is easier.

---

*Updated automatically by `scripts/refresh_today.sh` (future). For now, edit manually each Sunday night for the week ahead.*

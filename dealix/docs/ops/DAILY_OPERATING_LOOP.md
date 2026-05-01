# 🌅 Dealix — Daily Operating Loop

**Run this every Sun-Thu. 3-4 focused hours.**

---

## Morning (8:00 - 11:00)

### 8:00 — Systems Check (10 min)
- [ ] GitHub Actions healthcheck passing? (last run within 15 min)
- [ ] web-dealix.up.railway.app/healthz returns 200 in browser?
- [ ] Any email notifications from Sami's accounts (payments, replies)?

### 8:15 — Pipeline Review (15 min)
- [ ] Open `docs/ops/pipeline_tracker.csv`
- [ ] Find all rows where `next_followup` ≤ today
- [ ] Move any paid → onboarding list

### 8:30 — Today's outreach batch (2 hours)
- [ ] Open `docs/ops/launch_content_queue.md`
- [ ] Send 5 LinkedIn DMs (from priority leads 1-50)
- [ ] Send 5 follow-ups (Day +2/+5/+10)
- [ ] Send 2 agency partner messages
- [ ] Update tracker with `sent_at` for each

---

## Midday (11:00 - 14:00)

### 11:00 — Reply Handling (continuous)
- [ ] Respond to every reply within 30 min during business hours
- [ ] Book demos via Calendly link
- [ ] Log "Replied" → "Demo Booked" in tracker

### 12:00 — Demos (if booked)
- [ ] Pre-read the prospect 10 min before call
- [ ] Follow demo script from `docs/sales-kit/dealix_demo_script_30min.md`
- [ ] Always end with Pilot offer (1 SAR via manual invoice until Moyasar active)
- [ ] Post-demo: send Moyasar hosted invoice or bank details from `MANUAL_PAYMENT_SOP.md`

### 13:00 — Payment check
- [ ] Check bank for new transfers
- [ ] Check STC Pay notifications
- [ ] If payment received: update tracker + start onboarding

---

## Afternoon (14:00 - 17:00)

### 14:00 — Content (if M/W/F)
- [ ] Publish 1 post from `launch_content_queue.md`
- [ ] Engage with 10 target accounts (comment, like)

### 15:00 — Partner motion
- [ ] Send 2-3 agency DMs
- [ ] Respond to any partner inquiries
- [ ] Update partner tracker column

### 16:00 — Tomorrow prep
- [ ] Which 10 leads tomorrow?
- [ ] Research + personalize messages
- [ ] Calendar block demos

---

## Evening (17:00 - 18:00)

### 17:00 — Daily Scoreboard
Write this in a Google Sheet or here:

```
Date: ____
INPUTS
  Leads contacted: __
  Follow-ups sent: __
  Agency DMs: __
  Content posts: __

RESPONSES
  Positive replies: __
  Demos booked: __
  Demos completed: __

REVENUE
  Pilots started: __
  Payments received: __
  New MRR: __ SAR
  Total cumulative: __ SAR

LEARNING
  Best channel today: __
  Biggest blocker: __
  Change for tomorrow: __
```

### 17:30 — Improve
- [ ] Any message that got 0 replies in 10 sends? Rewrite.
- [ ] Any message that got multiple replies? Double down.

### 18:00 — STOP
Close laptop. Recovery = strategy.

---

## Weekly (Friday afternoon)

- [ ] Review total funnel metrics
- [ ] Kill weak segments
- [ ] Double down on best segment
- [ ] Update landing copy if objections repeat
- [ ] Update `FOLLOW_UP_CADENCE.md` based on what's working
- [ ] Plan next week's 50 leads

---

## 7-Day Target

| Day | Touches | Follow-ups | Demos | Paid |
|-----|---------|-----------|-------|------|
| 1 | 10 | 0 | 0 | 0 |
| 2 | 10 | 3 | 0 | 0 |
| 3 | 10 | 3 | 1-2 | 0 |
| 4 | 10 | 5 | 1-2 | 0 |
| 5 | 10 | 5 | 2 | 0-1 |
| 6 | 5 (partial Fri) | 5 | 1 | 0-1 |
| 7 | Off | 0 | 0 | 0 |
| **Week** | **55** | **21** | **5-7** | **0-2** |

**Week 1 realistic outcome:** 1-2 pilots signed, 0-1 paid (pending Moyasar).

---

## 30-Day Target

- 250 touches
- 100 follow-ups
- 20-25 demos
- 5-10 pilots
- 2-3 paid customers (after Moyasar active)
- 1 agency partner signed
- 500+ LinkedIn followers gained

---

## 90-Day Target (Stage 3 exit)

- 750 touches
- 60-80 demos
- 25-30 pilots
- 10-15 paid customers (realistic)
- 3-5 agency partners
- First referral won
- First case study published
- First $10K+ MRR

---

## Bottleneck Signals

Watch for:
- Reply rate < 2% → rewrite opening
- Demo booking rate < 20% from replies → shorten ask
- Demo show rate < 60% → add 24h confirmation
- Close rate < 10% → fix demo script or pricing
- Payment completion < 60% → simplify checkout (once Moyasar active)

Fix narrowest funnel point first.

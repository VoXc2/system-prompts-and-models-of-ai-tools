# Dealix — Pricing Discovery Worksheet

> **Never ask "what would you pay?"** — answer is biased toward zero.
> Use Van Westendorp Price Sensitivity Meter (PSM) after 8+ discovery interviews.
> Combine with value-based sanity check.

---

## 1. Van Westendorp — four questions

Asked at end of discovery call, after pain + quantitative discovery:

1. **Too cheap**: "At what annual price would this feel so cheap you'd question its quality or seriousness?"
2. **Bargain**: "At what annual price would this be a good deal — strong value for the cost?"
3. **Getting expensive**: "At what price would this start feeling expensive, but you'd still consider if the value is there?"
4. **Too expensive**: "At what price is it simply too expensive, regardless of value?"

Record in SAR/year, unprompted. No anchoring from you.

---

## 2. Raw data table

| # | Company | Interview date | Too cheap (SAR/yr) | Bargain | Getting expensive | Too expensive |
|---|---------|----------------|--------------------|----|-------------------|---------------|
| 1 | | | | | | |
| 2 | | | | | | |
| 3 | | | | | | |
| 4 | | | | | | |
| 5 | | | | | | |
| 6 | | | | | | |
| 7 | | | | | | |
| 8 | | | | | | |
| 9 | | | | | | |
| 10 | | | | | | |

---

## 3. Intersections (fill after ≥8 data points)

Plot cumulative curves; find intersection points.

| Point | Definition | Value (SAR/yr) |
|-------|------------|----------------|
| Point of Marginal Cheapness | "too cheap" ∩ "getting expensive" | |
| Optimal Price Point (indifference) | "bargain" ∩ "getting expensive" | |
| Point of Marginal Expensiveness | "bargain" ∩ "too expensive" | |

**Acceptable pricing band**: Marginal Cheapness → Marginal Expensiveness.
**Initial list price**: start at Optimal Price Point, test both sides.

---

## 4. Value-based sanity check (per customer)

For each interviewed customer, compute:

```
Annual value =
   (hours_saved_per_week × 52 × avg_hourly_cost_of_role)
 + (num_better_decisions × avg_decision_value)
 + (risk_avoided_per_year)
```

**Rule**: price ≤ 20% of annual value; customers rarely accept above 25%.

| Company | Hours saved/wk | Hourly cost | Better decisions/yr | Risk avoided | Annual value | Max price (25%) |
|---------|---------------|-------------|---------------------|--------------|--------------|-----------------|
| | | | | | | |
| | | | | | | |

---

## 5. Pricing-model A/B experiment matrix

After first 5 interviews, prototype and test **one model per prospect** (never three — creates indecision).

| Model | Structure | Best when |
|-------|-----------|-----------|
| Per seat | SAR/user/month | Predictable user count, horizontal role |
| Per workflow | SAR/workflow/month + seats | Workflow count drives value |
| Platform + usage | Base SAR + SAR/approval or SAR/evidence-pack | Usage tracks with realized value |

Track acceptance rate:

| Model | Offered to (# prospects) | Continued to demo | Signed pilot |
|-------|---------------------------|-------------------|--------------|
| Per seat | | | |
| Per workflow | | | |
| Platform + usage | | | |

---

## 6. Red flags in pricing discovery

- All "too cheap" answers ≥ current plan price → pricing too low; room to raise.
- Large gap between "bargain" and "too expensive" across interviews → market isn't segmented yet; stratify by company size/sector.
- "Annual value" computed < 5× price → cannot justify the ROI pitch; either raise value or lower price.
- Customer names zero competing tools → category is unknown to them; education cost is your hidden CAC.

---

## 7. Pricing decision log

Every price change logged here with reason + evidence:

| Date | Tier | Old price | New price | Reason | Evidence source |
|------|------|-----------|-----------|--------|-----------------|
| | | | | | |

# Dealix — Unit Economics Worksheet

> Fill in ONLY after 3 paying customers. Filling it earlier is fiction.
> All figures in SAR unless stated.
> Re-run at end of each month once populated.

---

## 1. Per-customer monthly economics

### Revenue
- MRR per customer (avg): ______

### Cost to serve (per customer / month)
| Line | Amount (SAR) |
|------|--------------|
| Infrastructure (AWS + DB + Redis) | ______ |
| LLM API (Anthropic + OpenAI + Groq, at observed usage) | ______ |
| Third-party services (Sentry, OTel backend, etc.) | ______ |
| CS time (hours × hourly cost) | ______ |
| Support time (eng on-call, tickets) | ______ |
| **Total Cost to Serve** | ______ |

### Gross Margin
- GM per customer (SAR): ______
- GM %: ______ %
- **Target**: GM ≥ 70% (SaaS healthy)
- **Red flag**: GM < 60% → LLM spend dominates; audit model routing.

---

## 2. Customer Acquisition Cost (CAC)

| Line | Amount (SAR) |
|------|--------------|
| Founder time spent closing (hrs × opportunity cost) | ______ |
| Marketing spend (ads, events) | ______ |
| Sales tools (CRM, LinkedIn Sales Nav, etc.) | ______ |
| Referral incentives | ______ |
| **Total CAC (amortized across paid customers)** | ______ |

---

## 3. Lifetime Value (LTV)

- Expected contract length (months, honest not aspirational): ______
- Monthly gross margin per customer: ______
- **LTV** = months × monthly GM = ______

---

## 4. Health ratios

| Metric | Value | Target | Red flag |
|--------|-------|--------|----------|
| LTV / CAC | ______ | ≥ 3× | < 2× |
| CAC payback period (months) | ______ | < 18 | > 24 |
| Gross margin % | ______ | ≥ 70% | < 60% |
| Net revenue retention (12m forward) | ______ | ≥ 120% | < 100% |

---

## 5. 12-month scenario (fill after M3)

Re-forecast every month.

| Month | New logos | Churn | MRR | Cumulative revenue | Burn | Cash position |
|-------|-----------|-------|-----|--------------------|----|-----|
| M3 (today) | ___ | 0 | ___ | ___ | ___ | ___ |
| M4 | ___ | ___ | ___ | ___ | ___ | ___ |
| M5 | ___ | ___ | ___ | ___ | ___ | ___ |
| M6 | ___ | ___ | ___ | ___ | ___ | ___ |
| M7 | ___ | ___ | ___ | ___ | ___ | ___ |
| M8 | ___ | ___ | ___ | ___ | ___ | ___ |
| M9 | ___ | ___ | ___ | ___ | ___ | ___ |
| M10 | ___ | ___ | ___ | ___ | ___ | ___ |
| M11 | ___ | ___ | ___ | ___ | ___ | ___ |
| M12 | ___ | ___ | ___ | ___ | ___ | ___ |

---

## 6. Red-flag diagnostics

If a ratio is off, diagnose in this order (cheapest fix first):

| Symptom | First suspect | Diagnostic |
|---------|--------------|------------|
| GM < 60% | LLM spend | Review model_routing dashboard; downgrade non-reasoning calls |
| GM < 60% | Infra waste | k6 baseline says p95 vs actual load — overprovisioned? |
| CAC too high | Founder-only sales | Is anyone else closing? if not, motion is not yet repeatable |
| CAC too high | Lead mix | Cold outbound vs warm referrals ratio — shift if skewed |
| LTV/CAC < 3 | Contract length | Are pilots renewing verbally but not signing annual? Why? |
| Payback > 24 | Pricing | Van Westendorp says prices could be higher — test |
| NRR < 100 | Churn | Exit interview every churn — real reason, not stated reason |

---

## 7. Evidence pointer

Do not fill in this worksheet from memory. Sources of truth:

- Revenue: Stripe / invoice ledger
- LLM spend: `backend/app/services/model_routing_dashboard.py` monthly export
- Infra: AWS cost explorer export
- CS/Support hours: weekly time logs
- CAC: founder calendar + marketing ledger

Cite the source file/export in the margin when filling each row.

# Pricing Guide | دليل الأسعار

## 💰 Default pricing tiers

All tiers are configurable via `.env` — see `PRICING_*` variables.

### 🇸🇦 Saudi Arabia (primary market)

| Offering | Range |
| --- | --- |
| Setup fee (one-time) | **12,000 – 40,000 SAR** |
| Monthly retainer | **3,000 – 12,000 SAR** |
| Discovery workshop (2 days) | 8,000 – 15,000 SAR |
| Proof-of-concept (2–4 weeks) | 25,000 – 60,000 SAR |

### 🌍 GCC (UAE, Kuwait, Bahrain, Qatar, Oman)

| Offering | Range |
| --- | --- |
| Setup fee | **15,000 – 50,000 SAR-equivalent** |
| Monthly retainer | **4,000 – 15,000 SAR-equivalent** |

### 🌐 Global SMB

| Offering | Range |
| --- | --- |
| Setup fee | **$3,000 – $10,000** |
| Monthly retainer | **$800 – $3,000** |

---

## 🏷️ How regional pricing is applied

`ProposalAgent._pricing_for_region()` inspects the lead's `region` field and returns the appropriate tier:

```python
# integrations/saudi_market.py::region_tier() mapping:
"Saudi Arabia" → saudi tier
"UAE", "Kuwait", "Bahrain", "Qatar", "Oman" → gcc tier
anything else → global tier
```

Override via `.env`:

```dotenv
PRICING_SA_SETUP_MIN=15000
PRICING_SA_SETUP_MAX=50000
PRICING_SA_RETAINER_MIN=4000
PRICING_SA_RETAINER_MAX=15000
```

---

## 📊 Positioning guidelines

Based on lead Fit tier (computed by `ICPMatcherAgent`):

| Tier | Score | Positioning |
| --- | --- | --- |
| **A** (hot) | ≥ 0.80 | Premium tier, emphasize outcomes over cost |
| **B** (warm) | 0.60 – 0.79 | Mid-range, emphasize ROI + time-to-value |
| **C** (cold) | 0.40 – 0.59 | Entry-level offer, workshop-first |
| **D** | < 0.40 | Nurture sequence, no proposal |

---

## 💡 Common offerings

### Setup engagements (one-time)

1. **AI Readiness Assessment** (1 week) — current state audit + roadmap
2. **Discovery Workshop** (2 days) — identify use-cases, prioritize ROI
3. **Proof of Concept** (2–4 weeks) — build one use-case end-to-end
4. **Full Integration** (4–8 weeks) — deploy into production
5. **Training & Enablement** (1 week) — knowledge transfer

### Retainer offerings (monthly)

1. **Managed AI Ops** — monitoring, optimization, incident response
2. **Continuous Development** — ongoing feature work at a fixed monthly rate
3. **Advisory Retainer** — AI strategy + architectural guidance

---

## 📜 Sample proposal line-items (SAR)

| Line item | Starter | Growth | Enterprise |
| --- | --- | --- | --- |
| Discovery workshop | 8,000 | 12,000 | included |
| ICP + lead funnel setup | 12,000 | 20,000 | 30,000 |
| WhatsApp automation | 6,000 | 10,000 | 15,000 |
| HubSpot integration | 5,000 | 8,000 | 12,000 |
| Custom Arabic LLM tuning | — | 15,000 | 25,000 |
| Monthly retainer | 3,000 | 7,000 | 12,000 |

---

## ⚖️ Pricing philosophy

- **Value-based for enterprise** — tie price to measurable business outcomes
- **Fixed-price for SMB** — predictable, easy to approve
- **Always in the client's currency mentally** — SAR first for Saudi, USD for global
- **Show 3 tiers** in every proposal (price anchoring)
- **Never discount the retainer** — discount setup fee if you must

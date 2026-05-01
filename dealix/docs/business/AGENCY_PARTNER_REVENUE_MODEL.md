# Dealix Agency / Partner Revenue Model

3 partner tracks. All bring distribution. Different revenue split per track.

## Track 1: Referral Partner

**Partner does:** Recommends Dealix to one of their clients. No fulfillment.

**You give:** 10% of first-12-months MRR. Tracked via UTM + closed-won attribution.

**Sami sends:**

> أهلاً [الشريك],
> فكرة سريعة: لو وصلتك شركة سعودية تواجه مشكلة الرد على leads بالعربي، رشحلها Dealix.
> أعطيك 10% من اشتراكها لمدة سنة كاملة.
> رابط متابعة المراجعات: dealix.me/partners
> لا التزام، لا setup. فقط تنبيه.

**Best for:** consultants, freelance Saudi sales advisors, current Dealix customers.

## Track 2: Agency Reseller

**Partner does:** Includes Dealix in their client packages. Bundles with their service.

**You give:** Setup fee 1,000 SAR (taken from the client's price). 25% of client's MRR while the client stays active.

**Numbers (illustrative):**
- Agency sells Dealix Growth (2,499 SAR/mo) bundled with their service.
- Dealix gets 75% × 2,499 = 1,874 SAR/mo.
- Agency gets 25% × 2,499 = 625 SAR/mo recurring.
- 10 clients = 6,250 SAR/mo passive recurring for the agency.

**What agency commits to:**
- Sell to ≥ 3 clients in first 90 days.
- Use Dealix's Khaliji Arabic prompts (no rewriting without approval).
- Pass customer support tickets to Dealix's queue.

**What Dealix commits to:**
- White-label admin badge in dashboard ("Powered by [Agency]").
- Dedicated Slack channel for the agency.
- 24h SLA on agency-flagged customer issues.

**Sami's pitch:**

> [الوكالة], عندكم عملاء سعوديين يحتاجون AI sales rep بالعربي.
> نحن نبنيه. أنتم تبيعونه. كل عميل = 625 ريال/شهر passive لكم لمدى الشراكة.
> أول 3 عملاء — Dealix يدفع لكم setup مجاني.
> 30 دقيقة هذا الأسبوع نوضح؟

## Track 3: Implementation Partner

**Partner does:** Custom integrations, prompt engineering, training, onboarding for Dealix customers.

**You give:** 2,500 SAR per setup (paid by you to them) + 15% MRR for 6 months.

**Best for:** Saudi automation/CRM consulting firms, Salla/Zid implementation specialists.

**Use case:** A customer pays Dealix Pro 5,000 SAR/mo, but needs custom integration with their internal warehouse system. Implementation partner does the work, both sides earn.

## Track 4 (Future): White-Label

**Partner does:** Full white-label. Their brand, their billing, their customers.

**You give:** Engine access at 30% MRR share. They handle all sales + delivery + support.

**Setup fee:** 25,000 SAR one-time.

**Why later:** First need 50+ direct customers + battle-tested prompts before letting partners brand it.

## Track 5 (Future): Pay-per-Result

**Partner does:** Sends qualified leads to Dealix customers (e.g., real-estate referral platforms, lead gen agencies).

**You give:**
- 25 SAR per qualified Arabic-replied lead
- 150 SAR per booked demo
- 5–10% success fee on closed customers

**Why later:** Need lead-quality measurement before paying per outcome.

## Partner agreement (light, before the lawyer)

Before any first deal, a 1-page MOU covering:

1. **Track type** (Referral / Agency / Implementation / White-Label / Pay-per-Result)
2. **Revenue split %** + duration + cap
3. **Attribution rules** (UTM + first-touch + customer disclosure)
4. **What partner CAN'T do:** Misrepresent Dealix capabilities, sign customers without Dealix approval, share prompts with non-customers, scrape LinkedIn for outreach.
5. **What Dealix CAN'T do:** Hire partner's customer directly without 90-day cooling-off.
6. **Payment terms:** Monthly, after Dealix collects from end customer.
7. **Termination:** 30 days written notice, no clawback on already-collected MRR.

## Day 1 partner queue (from the directory)

Only 2 explicit marketing agencies in the uploaded directory + 35 Saudi software companies (potential implementation partners).

**Day 1 partner outreach: 7 contacts**
- 2 marketing agencies → Track 2 (Reseller) pitch
- 5 SaaS founders (top by score) → Track 3 (Implementation Partner) pitch (they have Saudi B2B reach)

After deploy, run `POST /api/v1/leads/discover/local` with `industry=marketing_agency` city=`riyadh|jeddah` to fill the partner pipeline (Saudi agencies are mostly outside the chamber-style directory).

## Tracking

Each partner closed → log in `partners` table with:
- partner_type
- contact_name + email
- track
- commission_terms
- mrr_share_pct
- clients_signed (incremented on each win)
- next_action
- next_action_at

Already wired in Dealix's `db.models.PartnerRecord`.

# Worked Example — SaaS Landing Page

A filled-in version of the 9-prompt chain for a **fictional B2B SaaS**. Shows exactly how the `[BRACKETS]` in the main chain file get resolved.

## The product

- **Name:** TicketFlow
- **Category:** AI-powered customer support triage for mid-market SaaS companies
- **Price:** $99–$499/month
- **Audience:** Heads of Support at 50–500 employee SaaS companies
- **Goal of the site:** book demos

---

## Filled-in prompts

### 1. Architecture

```
تخيل إنك Principal Architect في Vercel. ابنِ SaaS marketing site (single-product, demo-booking funnel).

المتطلبات:
Target:   Heads of Support at 50–500 emp SaaS companies, North America + EU
Features: AI triage demo, ROI calculator, integration grid (Zendesk/Intercom/Front), customer case studies, pricing
Tech:     RESPONSIVE + strong SEO (keyword: "ai customer support triage") + <2s LCP on 4G

سلّم لي:
- Site map
- User flows (3 رحلات: visitor → demo booked, visitor → ROI calc → demo, returning visitor → pricing → self-serve signup)
- Data models (demo requests, calculator inputs, newsletter)
- API requirements
- قائمة مكوّنات (30+)
- قوالب صفحات (wireframes)
- Tech stack ترشيح
- ميزانيات الأداء (LCP<2s, CLS<0.1, INP<200ms)
- SEO هيكلة
```

### 2. Design system

```
تخيل إنك Design Director في Apple. سوّ نظام لـ TicketFlow.
الصفات: MINIMAL + BOLD (tech-forward, serious, trustworthy)

طلّع:
- لوحة ألوان (primary: deep indigo #3730A3، secondary: electric cyan #06B6D4، semantic success/warn/error، dark mode كامل)
- سلم خطوط (9 مستويات، Inter for UI, IBM Plex Mono for code snippets)
- نظام مسافات (شبكة 8px)
- مواصفات المكوّنات (30 مكوّن بكل الحالات: default/hover/active/disabled/loading)
- أنماط التخطيط (12-col grid, max-width 1280px)
```

### 3. Content

```
Imagine you're a Conversion Copywriter at Ogilvy.
Write all the texts for the TicketFlow marketing site.

Tone:   BOLD but PROFESSIONAL (technical credibility, no fluff)
Target: Head of Support, 50–500 emp SaaS, drowning in tickets, KPI = first response time
Goal:   CONVERSION (book a demo)

For each page:
- Hero           (6-word headline: "Triage 10,000 tickets in seconds." / 15-word desc / CTA "Book a 15-min demo")
- Features       (3 blocks: AI triage, smart routing, SLA dashboards)
- Social proof   (3 testimonials + "used by teams at X, Y, Z" + "$1.2M saved on average")
- FAQ            (8 Qs: integrations, pricing, SOC2, data residency, training time, accuracy, onboarding, cancellation)
- Footer

Use emotional triggers (overwhelm relief, career hero, peace of mind) + powerful words (instantly, finally, ruthlessly).
Specify H1/H2/body tags.
```

### 4. Component logic

```
تخيل إنك Frontend Architect. صمّم المنطق لـ:

- Multi-step form         — "Book a demo" (email → company size → current tool → calendar slot)
- Dynamic pricing calc    — seats × ticket volume → monthly price + ROI estimate
- Search مع فلاتر         — case studies filtered by industry + company size + use case
- User dashboard          — post-demo portal showing next steps, contract, trial metrics
- Auth flow               — self-serve trial signup (email OTP → company → start 14-day trial)

لكل مكوّن:
- State machine  (idle → validating → submitting → success | error)
- Data flow      (props, events, APIs)
- التعامل مع الأخطاء (network, validation, 429, 500)
- حالات التحميل / الفاضي (skeleton, empty state)
- Edge cases (browser back, form autofill, slow 3G)

واطلع لي هيكل React (App Router, server components where possible).
```

### 5. Figma Make prompts

Paste the merged output of 1–4 into the `[PASTE SPEC FROM CLAUDE]` slot, then ask for 5 variants. Example of the "complex" variant you'd expect back:

```
Build a B2B SaaS landing page for "TicketFlow" with a minimal-bold aesthetic.
Brand: deep indigo (#3730A3) primary, electric cyan (#06B6D4) accent,
Inter for UI, IBM Plex Mono for code. 8px grid, 12-col layout, max 1280px.

Include:
1) Sticky navbar (80px → 60px on scroll) with logo, Product, Pricing,
   Customers, Docs, and a cyan "Book demo" CTA.
2) Hero: left-aligned H1 "Triage 10,000 tickets in seconds." subhead,
   primary CTA + secondary "Watch 90s demo", right-side product mock with
   subtle parallax.
3) Logo strip (6 customer logos, grayscale, hover color).
4) Features grid (3 cards with icon, title, 2-line body, hover lift 4px).
5) Interactive ROI calculator (two sliders + animated price readout).
6) Testimonial carousel with photo, quote, name, company, 5-star rating.
7) Pricing table (3 tiers, middle tier highlighted, feature checklist).
8) FAQ accordion (8 items, smooth height transitions).
9) Final CTA section with gradient background.
10) Footer with 4 link columns, newsletter signup, social icons.

Make it fully responsive (375 / 768 / 1440). Animations:
- Page load: 0.6s stagger fade-up for hero content (0.1s between lines)
- Scroll reveals with 0.4s ease-out at 60% viewport
- Hover: 200ms translateY(-4px) + shadow bloom on cards
- Button press: 100ms scale(0.97)

Dark mode by default, with a light-mode toggle.
```

### 6–9

Same pattern. The point of this example is to show how specific the brackets become in practice — **the more concrete you are in prompts 1–4, the better Figma Make's output in prompt 5**.

---

## Timing reality check

Based on the author's 118-minute claim, rough time budget:

| Stage | Time |
|---|---|
| 1 — Architecture | 15 min (incl. reading + one tweak) |
| 2 — Design system | 10 min |
| 3 — Content | 15 min |
| 4 — Component logic | 15 min |
| 5 — Figma Make prompts | 8 min (5 variants) |
| 6 — Motion spec | 10 min |
| 7 — Responsive plan | 8 min |
| 8 — Data integration | 12 min |
| 9 — QA checklist | 10 min |
| **Figma Make generation + manual tweaks** | **15 min** |
| **Total** | **~118 min** |

Your mileage will vary based on how clear your initial brief is.

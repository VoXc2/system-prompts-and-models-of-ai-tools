# Dealix — Marketers Page Execution Plan

## Current State
The `/marketers` page (131 lines TSX) exists as a **link hub** — links to strategy, resources, WhatsApp templates, and static files. It does NOT sell services or convert visitors to leads.

## Required Transformation
Convert from **resource hub** to **service sales page** that answers:
1. What can a marketer/agency DO with Dealix?
2. How much does it cost?
3. How do I start?

## Target Audience
- Marketing agency owners (5-50 people)
- Performance marketers managing Saudi B2B clients
- Freelance digital marketers
- CRM/automation consultants

## Proposed Sections (top to bottom)

### Hero
**العنوان:** "حوّل وكالتك إلى ماكينة إيرادات متكررة"
**الفرعي:** "أضف خدمة رد ذكي + تأهيل leads لعملائك — setup fee + MRR شهري"
**CTA:** "احجز مكالمة شراكة" → Calendly

### Problem
"عملاءك يصرفون على الإعلانات ويجيبون leads — لكن 70% تضيع بسبب تأخر الرد.
أنت تعرف المشكلة. Dealix يعطيك الحل تبيعه لهم."

### 3 Service Packages Marketers Can Sell

| الباقة | Setup Fee | Monthly | ما يحصل العميل |
|--------|-----------|---------|---------------|
| الأساسية | 3,000 SAR | 990 SAR/شهر | رد + تأهيل على واتساب |
| المتقدمة | 7,000 SAR | 2,490 SAR/شهر | رد + تأهيل + حجز مواعيد + CRM sync |
| المؤسسية | 15,000 SAR | مخصص | كل شي + تقارير executive |

**هامش الوكالة:** 20-30% من MRR + 100% من setup fee

### How It Works (3 Steps)
1. **اربط عميلك** — ندخل واتساب/فورم/CRM عميلك في Dealix
2. **فعّل الرد الذكي** — AI يرد بالعربي، يؤهل، يحجز
3. **اجمع MRR** — أنت تحصّل من عميلك، ونحن نشغّل النظام

### Trust/Proof
- "مبني للسوق السعودي — عربي أولاً"
- "متوافق PDPL"
- "بدون عقد طويل — شهري"
- "ضمان استرداد 30 يوم"

### FAQ
- "كم ياخذ الإعداد؟" → "يوم واحد للأساسية، 3 أيام للمتقدمة"
- "هل أحتاج خبرة تقنية؟" → "لا — نحن نسوي الإعداد"
- "كم أقدر أربح؟" → "عميل واحد = 3,000 setup + ~990/شهر = 14,880/سنة"

### CTA Final
"ابدأ بأول عميل — مجاناً"
→ calendly.com/sami-assiri11/dealix-demo

## Implementation
File: `frontend/src/app/marketers/page.tsx` — rewrite 131 lines to proper sales page.
No new dependencies. Uses existing Tailwind + lucide-react.

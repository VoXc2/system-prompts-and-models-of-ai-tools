# Figma Make — 9-Prompt Website Builder Chain

> **Source:** X/Twitter thread by [@_TALEBM_](https://x.com/_TALEBM_) — 28/03/2026
> **Type:** Community prompt chain (not the Figma Make system prompt itself)
> **Stack:** Claude Opus 4.6 (architecture + logic + complex reasoning) + Figma Make (pixel-perfect UI + interactions + publishing)
> **Result claimed by author:** a full site valued around **$5,000** built in **118 minutes**

## Author's framing

> **أكبر كذبة تقولها لنفسك:** «مشروعي واقف عشان ما عندي ميزانية للموقع».
>
> الأعذار انتهت اليوم يا صاحبي. الذكاء الاصطناعي كسر حاجز التكلفة تماماً.
>
> هذي الـ 9 أوامر بتخليك تطلق موقعك الليلة وبدون ما تدفع ريال.

> توني بنيت موقع لعميل بقيمة 💰 خلال 118 دقيقة.
>
> **الستاك:**
> - **Claude Opus 4.6** — للمعمارية والمنطق والتفكير المعقّد
> - **Figma Make** — لواجهة Pixel-perfect والتفاعلات والنشر
>
> جرّبت أكثر من 100 برومبت عشان ما تتعب أنت. هذي الـ 9 برومبتات اللي فعلاً تنفع.

---

## How to use this chain

Run the prompts **in order**. Each one feeds its output into the next. Every prompt is **role-based** ("Imagine you're a \_\_\_ at \_\_\_") — a classic technique to anchor Claude in a specific mental model and terminology set.

Placeholders in `[BRACKETS]` are things you fill in before running the prompt.

| # | Role | Output |
|---|------|--------|
| 1 | Vercel Principal Architect | Architecture: site map, user flows, data models, API, 30+ component list, wireframes, tech stack, perf budgets, SEO structure |
| 2 | Apple Design Director | Brand design system (colors, type scale, spacing, component specs) |
| 3 | Ogilvy Conversion Copywriter | All page copy (hero, features, social proof, FAQ, footer) |
| 4 | Frontend Architect | React logic for multi-step form, pricing calculator, search, dashboard, auth |
| 5 | Figma Make Prompt Engineer | 5 Figma Make prompts (simple → complex) |
| 6 | Apple Motion Designer | Animation/interaction specs in Figma-Make-friendly prose |
| 7 | Responsive Design Specialist | Breakpoint plan (mobile / tablet / desktop) |
| 8 | Full-Stack Architect | Data models, API endpoints, auth, caching, Supabase schema |
| 9 | Google QA Engineer | Quality + optimization checklist (perf, a11y, SEO, security) |

---

## PROMPT 1 — مخطط المعمارية (Architecture Plan)

**Role:** Principal Architect @ Vercel

```
تخيل إنك Principal Architect في Vercel. ابنِ [WEBSITE TYPE].

المتطلبات:
Target:   [AUDIENCE]
Features: [LIST 3-5]
Tech:     [RESPONSIVE / SEO / PERFORMANCE]

سلّم لي:
- Site map (تسلسل الصفحات)
- User flows (3 رحلات)
- Data models (إذا فيه ديناميكية)
- API requirements
- قائمة مكوّنات (30+ عنصر)
- قوالب صفحات (wireframes)
- Tech stack ترشيح
- ميزانيات الأداء
- SEO هيكلة
```

**Output feeds into:** PROMPT 2 (design system), PROMPT 4 (component logic), PROMPT 8 (data integration).

---

## PROMPT 2 — مولّد نظام التصميم (Design System Generator)

**Role:** Design Director @ Apple

```
تخيل إنك Design Director في Apple. سوّ نظام لـ [BRAND].
الصفات: [MINIMAL / BOLD / LUXURY / PLAYFUL]

طلّع:
- لوحة ألوان (أساسي، ثانوي، دلالي، وضع داكن)
- سلم خطوط (9 مستويات)
- نظام مسافات (شبكة 8px)
- مواصفات المكوّنات (30 مكوّن بكل الحالات)
- أنماط التخطيط
```

**Output feeds into:** PROMPT 5 (Figma Make prompts reference the brand tokens).

---

## PROMPT 3 — Content Engineer

**Role:** Conversion Copywriter @ Ogilvy

```
Imagine you're a Conversion Copywriter at Ogilvy.
Write all the texts for [WEBSITE TYPE].

Tone:   [PROFESSIONAL / CASUAL / BOLD]
Target: [AUDIENCE]
Goal:   [CONVERSION / AWARENESS / RETENTION]

For each page:
- Hero           (6-word headline, 15-word description, CTA)
- Features       (3 blocks)
- Social proof   (testimonials + numbers)
- FAQ            (8 questions and answers)
- Footer

Use emotional triggers + powerful words.
Specify H1/H2/body tags.
```

**Output feeds into:** PROMPT 5 (copy goes straight into the Figma Make hero/features blocks).

---

## PROMPT 4 — بانى منطق المكوّنات (Component Logic Builder)

**Role:** Frontend Architect

```
تخيل إنك Frontend Architect. صمّم المنطق لـ:

- Multi-step form              (تحقق، تقدم، حالات)
- Dynamic pricing calculator   (لحظي)
- Search مع فلاتر              (faceted، ترتيب، صفحات)
- User dashboard               (عرض بيانات، CRUD)
- Auth flow                    (login / signup / reset)

لكل مكوّن:
- State machine  (مخطط نصي)
- Data flow      (props, events, APIs)
- التعامل مع الأخطاء
- حالات التحميل / الفاضي
- Edge cases

واطلع لي هيكل React.
```

**Output feeds into:** PROMPT 5 (logic → Figma Make component prompts) and PROMPT 8 (APIs/data).

---

## PROMPT 5 — مهندس برومبتات Figma Make

**Role:** AI Prompt Engineer specializing in Figma Make

```
تخيل إنك AI Prompt Engineer متخصص في Figma Make.
حوّل هالمواصفات التقنية إلى 5 برومبتات لـ Figma Make:

[PASTE SPEC FROM CLAUDE]

كل برومبت لازم:
1) يبدأ بالنتيجة (مو بالطريقة)
2) يذكر سياق البراند (الألوان، الخطوط، الجو العام)
3) يحدد التفاعلات (hover, click, scroll, animate)
4) يوضح الاستجابة (mobile / tablet / desktop)
5) يطلب أقسام محددة (hero, features, CTA, footer)

مثال على الصيغة:
"Build a [TYPE] website with [MOOD] aesthetic.
 Use [COLOR] primary and [FONT] typography.
 Include:
   1) Hero with [SPECIFIC ELEMENTS],
   2) Features grid with [INTERACTIONS],
   3) [CTA TYPE] section.
 Make it fully responsive with [ANIMATION STYLE] animations."

طلّع 5 نسخ من البسيط إلى المعقّد.
```

**Tip:** Paste the merged output of PROMPTS 1–4 where `[PASTE SPEC FROM CLAUDE]` appears.

---

## PROMPT 6 — مصمم الأنيميشن والتفاعل (Motion & Interaction Designer)

**Role:** Motion Designer @ Apple

```
تخيل إنك Motion Designer في Apple.
صمّم التفاعلات لـ [WEBSITE SECTION].

متطلبات التفاعل:
- تسلسل تحميل الصفحة  (stagger، مدة، easing)
- سلوكيات السكّول     (parallax، pin، reveal)
- حالات hover         (micro-interactions، feedback)
- انتقالات الضغط      (page transitions، فتح مودال)
- دعم الإيماءات       (swipe، pinch، pull)

مواصفات تقنية:
- Easing curves (spring, ease-out, cubic-bezier)
- المدد (ms لكل نوع تفاعل)
- GPU acceleration, will-change — وبرضو انتبه للأداء

يفهمه Figma Make — اوصف الأنيميشن بكلام يقدر يفهمه:

"On scroll: Navbar shrinks from 80px to 60px with ease-out over 300ms.
 Hero text fades up from 20px below with 0.6s duration and 0.1s stagger between lines..."

أنا بلصق هالأوصاف داخل برومبت Figma Make.
```

---

## PROMPT 7 — مخطط الاستجابة (Responsive Plan)

**Role:** Responsive Design Specialist

```
تخيل إنك Responsive Design Specialist.
خطط الـ breakpoints لـ [WEBSITE].

Breakpoints:
  Mobile:  375px
  Tablet:  768px
  Desktop: 1440px

لكل قسم في الصفحة، حدّد:
1) تغيّر التخطيط (grid → stack, sidebar → drawer)
2) تحجيم الخط (أحجام الخط بكل breakpoint)
3) سلوك الصور (قص، تكبير/تصغير، إخفاء، تبديل)
4) تكيّف التنقل (hamburger, sidebar, أفقي)
5) تعديلات المسافات (padding, margin, gap)
6) أولوية المحتوى
```

---

## PROMPT 8 — مخطط دمج البيانات (Data Integration Plan)

**Role:** Full-Stack Architect

```
تخيل إنك Full-Stack Architect.
صمّم دمج البيانات لـ [WEBSITE TYPE].

مصادر البيانات: [CMS / API / DATABASE]

المتطلبات:
1) Data models (تعريفات الـ schema)
2) الـ API endpoints المطلوبة (GET, POST, PUT, DELETE)
3) استراتيجية التوثيق (JWT, OAuth, API keys)
4) اعتبارات الوقت الحقيقي (WebSockets, polling)
5) استراتيجية الكاش (CDN, local storage)
6) التعامل مع الأخطاء (fallbacks, retries, offline)

ميزات تهم المستخدم:
- تحميل محتوى ديناميكي (infinite scroll, pagination)
- إرسال النماذج (validation، حالات نجاح/خطأ)
- حسابات مستخدمين (profiles, preferences)
- البحث (indexing, filters, sorting)

Figma Make يتصل بـ Supabase عشان بيانات حقيقية —
صمّم الـ schema لهالدمج.
```

---

## PROMPT 9 — Quality & Optimization Checklist

**Role:** QA Engineer @ Google

```
Imagine you're a QA Engineer at Google.
Review the specifications of this website:

[PASTE FIGMA MAKE OUTPUT OR DESCRIBE]

Checklist:
  ☐ Performance          (Core Web Vitals targets)
  ☐ Accessibility        (WCAG 2.2 AA compliance)
  ☐ SEO                  (meta tags, structured data, sitemap)
  ☐ Security             (HTTPS, CSP, input sanitization)
  ☐ Browser Compatibility (Chrome, Safari, Firefox, Edge)
  ☐ Mobile Optimization  (touch targets, viewport)
  ☐ Analytics Integration (events, goals, funnels)
```

---

## Execution flow

```
┌───────────────┐   ┌──────────────┐   ┌─────────────┐
│ 1. Architecture│ → │ 2. Design    │ → │ 3. Content  │
│    (Vercel)    │   │    System    │   │    Copy     │
└───────────────┘   └──────────────┘   └─────────────┘
                                              │
                                              ▼
┌─────────────┐   ┌──────────────┐   ┌─────────────┐
│ 6. Motion   │ ← │ 5. Figma     │ ← │ 4. Component│
│  & Interact │   │    Make Prmt │   │    Logic    │
└─────────────┘   └──────────────┘   └─────────────┘
       │
       ▼
┌─────────────┐   ┌──────────────┐   ┌─────────────┐
│ 7.Responsive│ → │ 8. Data      │ → │ 9. QA       │
│    Plan     │   │   Integration│   │   Checklist │
└─────────────┘   └──────────────┘   └─────────────┘
```

## Credits

Chain authored by **@_TALEBM_** ([x.com/_TALEBM_](https://x.com/_TALEBM_)) — thread dated 28/03/2026.
Transcribed verbatim for archival purposes as part of the `system-prompts-and-models-of-ai-tools` collection.

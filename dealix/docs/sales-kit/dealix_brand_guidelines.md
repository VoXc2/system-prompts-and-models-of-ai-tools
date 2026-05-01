# Dealix — Brand Guidelines

> دليل الهوية البصرية الكامل لـ Dealix. كل assets لازم تتبع هذا الدليل.

**آخر تحديث**: أبريل 2026 | **الإصدار**: 1.0

---

## 🎯 Brand Essence

### Core Promise
**"الذكاء الاصطناعي يفهم تجارتك السعودية."**

### Brand Personality
| البُعد | الصفة | الضد |
|--------|--------|------|
| Voice | واثق بدون غرور | متردّد ❌ |
| Tone | محترف + دافئ | بارد ❌ |
| Approach | عملي ومباشر | مبهم ❌ |
| Values | موثوق + شفّاف | مخفي ❌ |

### الكلمات المفتاحية (تستخدم في كل محتوى)
- **ذكي** (Smart)
- **موثوق** (Reliable)
- **سعودي** (Saudi)
- **بسيط** (Simple)
- **قياسي** (Measurable)

### الكلمات المحظورة (ممنوعة)
- ❌ "ثوري" / "Revolutionary" — ادعاء مبالغ فيه
- ❌ "الأفضل" / "Best" — ما نقدر نثبته
- ❌ "Disruptive" — كليشيه
- ❌ "AI-powered" لحالها — لازم "AI يفهم السياق السعودي"
- ❌ أي مصطلح شامي (شلون، شي، منيح)

---

## 🎨 Color Palette

### Primary Colors
```
Dealix Deep Green   #0A4D3F   rgb(10, 77, 63)    — الأساسي (خلفيات header)
Dealix Gold         #C9A961   rgb(201, 169, 97)  — التأكيد (CTAs, accents)
Dealix Sand         #F4F0E8   rgb(244, 240, 232) — خلفيات فاتحة
```

### Secondary Colors
```
Deep Charcoal       #1A1A1A   — النصوص
Warm Gray           #6B6B6B   — النصوص الثانوية
Cool Gray           #E5E5E5   — الحدود + dividers
```

### Semantic Colors
```
Success Green       #2D7A4F   — نجاح
Warning Amber       #E8A33D   — تحذير
Error Red           #C73E3E   — خطأ
Info Blue           #3B6B8C   — معلومات
```

### قواعد الاستخدام
- **60-30-10 rule**: 60% neutral (sand/white) + 30% primary (green) + 10% accent (gold)
- ❌ **لا تستخدم**: Green + Gold بنفس الـ weight — Gold دائماً accent
- ❌ **لا تستخدم**: أي لون غير هذي الـ palette في marketing materials

---

## ✍️ Typography

### Arabic (الأساسي)
```
Primary: IBM Plex Sans Arabic
  - Headings: Bold 700
  - Body: Regular 400
  - Captions: Light 300

Fallback: Tajawal (Google Fonts)
```

### English
```
Primary: Inter
  - Headings: SemiBold 600
  - Body: Regular 400
  - Code: JetBrains Mono

Fallback: system-ui
```

### Hierarchy
| العنصر | الحجم (Arabic) | الحجم (English) | Weight | Line Height |
|--------|----------------|------------------|--------|-------------|
| H1 | 48px / 3rem | 40px | 700 | 1.2 |
| H2 | 36px / 2.25rem | 32px | 700 | 1.3 |
| H3 | 28px / 1.75rem | 24px | 600 | 1.4 |
| Body | 18px / 1.125rem | 16px | 400 | 1.6 |
| Caption | 14px | 13px | 400 | 1.5 |

### قواعد RTL
- **دائماً** `direction: rtl; text-align: right;` للعربي
- **لا تستخدم** `<i>` للتأكيد — استخدم Bold بدلاً
- **الأرقام**: Arabic-Indic (١٢٣) في المحتوى السردي، Western (123) في الجداول + الأكواد

---

## 🖼️ Logo Usage

### Primary Logo
- **اسم الملف**: `dealix_logo_primary.svg`
- **استخدام**: header الموقع، pitch deck cover، business cards
- **الحد الأدنى للحجم**: 120px width

### Variants
| Variant | متى يستخدم |
|---------|-------------|
| Full (icon + wordmark) | Headers, covers |
| Icon only | Favicons, app icons, small spaces |
| Wordmark only | Footer, watermarks |
| Monochrome (white on green) | Dark backgrounds |
| Monochrome (green on white) | Light backgrounds |

### Clear Space
مسافة لا تقل عن ارتفاع الحرف "D" حول الشعار من جميع الجهات.

### الممنوعات
- ❌ تغيير ألوان الشعار (خارج monochrome)
- ❌ تمطيط أو تشويه
- ❌ إضافة ظلال أو effects
- ❌ وضع الشعار على خلفية مشوّشة (صور بدون overlay)
- ❌ تدوير الشعار

---

## 📐 Visual Style

### Iconography
- **Style**: Line icons (2px stroke)، rounded corners (2px radius)
- **Library**: Lucide (primary) + custom ZATCA/Saudi-specific icons
- **Color**: Match surrounding text OR Gold #C9A961 للـ CTAs
- **Size**: 16px، 20px، 24px (avoid odd sizes)

### Imagery
- **Photography style**:
  - صور عملية (شركات سعودية حقيقية، مكاتب بسيطة)
  - ❌ ممنوع stock photos عامة (business people shaking hands)
  - ❌ ممنوع صور أجنبية (Europe/US offices)
  - ✅ مفضّل: أيدي سعودية تستخدم Dealix، فواتير مطبوعة، لوحة مفاتيح عربية

- **Illustrations**:
  - Flat design، لا gradient
  - استخدم palette الأساسي فقط
  - تحاكي الـ Saudi context (ثوب، عقال، شماغ عند الحاجة)

### Patterns
- **Islamic geometric patterns**: مسموح للـ backgrounds بـ opacity 5-10% فقط
- **Arabic calligraphy**: محظور كـ decoration (احترام للفن)

---

## 📱 UI Components

### Buttons
```css
/* Primary CTA */
.btn-primary {
  background: #0A4D3F;
  color: #FFFFFF;
  padding: 12px 24px;
  border-radius: 8px;
  font-weight: 600;
  font-size: 16px;
}
.btn-primary:hover { background: #083D32; }

/* Secondary CTA */
.btn-secondary {
  background: transparent;
  color: #0A4D3F;
  border: 2px solid #0A4D3F;
}

/* Gold Accent (للـ high-conversion CTAs فقط) */
.btn-accent {
  background: #C9A961;
  color: #1A1A1A;
  font-weight: 700;
}
```

### Cards
- Background: #FFFFFF
- Border: 1px solid #E5E5E5
- Border-radius: 12px
- Shadow: `0 2px 8px rgba(10, 77, 63, 0.08)`
- Padding: 24px

### Forms
- Label: 14px Medium 500، لون #6B6B6B
- Input: 16px Regular، border #E5E5E5، border-radius 6px
- Focus: border 2px #0A4D3F + shadow
- Error: border #C73E3E + message تحت

---

## 🗣️ Voice & Tone

### The Dealix Voice (ثابت)
- **صادق**: نقول الحقيقة حتى لو مو لصالحنا
- **مباشر**: جملة واحدة بدل فقرة
- **محترم**: ما نتكلم فوقاني على العميل

### Tone يتغيّر حسب السياق
| الموقف | Tone | مثال |
|--------|------|------|
| Landing page | حماسي + واثق | "قلّل ساعات المحاسبة، زد وقت البيع." |
| Email cold | محترم + موجز | "كيفك عبدالله — رأيت شركتك تنمو في القصيم..." |
| Support ticket | صبور + حل-focused | "سامي، شفت المشكلة. الحل بنطبّقه خلال ساعة." |
| VC pitch | واثق + بيانات-driven | "72x LTV/CAC، profitable بعد 14 شهر." |
| Social media | دافئ + مفيد | "٥ أخطاء محاسبية شائعة — تجنّبها بـ ٣ نقاط:" |

### قواعد الكتابة
1. **جملة قصيرة** (< 18 كلمة في المتوسط)
2. **لا تكرار**: لو قلت "سريع" في الـ H1، ما تقوله في الـ subtitle
3. **ابدأ بالفعل**: "احسب فاتورتك" أفضل من "يمكنك حساب الفاتورة"
4. **أرقام محدّدة**: "توفير 18 ساعة/شهر" أفضل من "توفير وقت كبير"
5. **لا كليشيهات**: احذف "في عصر التكنولوجيا"، "في عالم يتطور"، "كما تعلم"

---

## 📊 Presentation Templates

### Pitch Deck
- **Slide ratio**: 16:9
- **Font**: IBM Plex Sans Arabic
- **Max words per slide**: 30
- **One idea per slide**
- **Cover slide**: شعار + "Dealix — [tagline]" + اسم المقدّم
- **Closing slide**: CTA واحد + معلومات التواصل

### Sales Demo
- **Open**: سؤال (مو عرض) — "قبل ما أبدأ، وش أكبر مشكلة تحاسبية عندكم؟"
- **Middle**: 3 use cases + دقة 95%+ دائماً مذكورة
- **Close**: "وش اللي يمنعك تجرّب 7 أيام بـ 1 ر.س؟"

---

## 🌐 Social Media

### LinkedIn (الأساسي)
- **Posting cadence**: 3 مرات/أسبوع (ثلاثاء، أربعاء، خميس صباحاً)
- **Format**: نص (بدون صور) للثوت leadership + carousel للـ tips
- **Hashtags**: #Dealix #السعودية #رؤية2030 #محاسبة #AI (حد أقصى 3)

### Twitter/X
- **Cadence**: يومياً (thread أسبوعي)
- **Language**: عربي أساسي، إنجليزي للـ international VCs
- **Tone**: أكثر casual من LinkedIn

### ممنوع
- ❌ Instagram reels (جمهوره مو ICP)
- ❌ TikTok (بعد 2027 ممكن)
- ❌ Snapchat (ما يجيب عملاء B2B)

---

## 📧 Email Signature Template

```
سامي العسيري
Founder & CEO | Dealix

📧 sami@dealix.sa (سيُفعّل)
📅 https://calendly.com/sami-assiri11/dealix-demo
🌐 dealix.sa

—
Dealix | الذكاء الاصطناعي للتجارة السعودية
```

---

## 🎬 Video Production Guidelines

راجع `dealix_video_scripts.md` للسكربتات.

### Technical Specs
- **Resolution**: 1080p minimum (4K preferred للـ thumbnails)
- **Frame rate**: 30fps
- **Audio**: 48kHz، -14 LUFS (broadcast standard)
- **Captions**: دائماً (عربي + إنجليزي)
- **Length limits**:
  - LinkedIn: ≤ 3 min
  - Twitter: ≤ 2:20
  - YouTube: حسب المحتوى
  - Website: ≤ 90 sec (hero video)

### B-roll Required
- مكتب سامي بالرياض
- شاشة Dealix (screen recordings)
- عميل حقيقي يستخدم (مع إذن كتابي)
- لقطات ZATCA portal + Moyasar dashboard

---

## 📏 Measurement & Consistency

### Brand Audits (شهري)
- [ ] جميع الـ marketing materials تستخدم الـ palette
- [ ] Logo متسق في كل الأماكن
- [ ] Typography ما فيها fonts خارجية
- [ ] Voice + Tone يتّبع الدليل

### Brand Score (من 10)
- 8+: ممتاز
- 5-7: يحتاج مراجعة
- < 5: إعادة تصميم مطلوبة

---

## 📞 Brand Approval

قبل نشر أي asset جديد:
1. Sami يراجع مقابل الدليل
2. Check ضد "ممنوعات" القسم
3. Test على 2 عملاء موجودين للـ feedback
4. Published مع date + version في الـ metadata

---

**Dealix Brand — Consistent. Confident. Distinctly Saudi.**
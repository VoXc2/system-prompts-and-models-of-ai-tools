/**
 * مساعد معرفة محلي (عربي) — يكمّل الردود عند عدم توفر الـ API.
 * يُفضّل مطابقة الكلمات المفتاحية بعد تطبيع بسيط للعربية.
 *
 * يُحدَّث مع إصدار الـ blueprint في الباكند (`strategy_summary._BLUEPRINT_VERSION`).
 */
export const DEALIX_PRODUCT_BLUEPRINT_VERSION = "4.0.0-legendary";

export type AssistantVariant = "marketer" | "company" | "preview";

export type KnowledgeEntry = {
  keywords: string[];
  answer: string;
  links?: { label: string; href: string }[];
};

function normalizeAr(s: string): string {
  return s
    .toLowerCase()
    .replace(/[أإآٱ]/g, "ا")
    .replace(/ؤ/g, "و")
    .replace(/ئ/g, "ي")
    .replace(/ة/g, "ه")
    .replace(/ى/g, "ي")
    .replace(/[^\p{L}\p{N}\s]/gu, " ")
    .replace(/\s+/g, " ")
    .trim();
}

const MARKETER: KnowledgeEntry[] = [
  {
    keywords: ["عموله", "عمولة", "هيكل", "فضه", "فضة", "ذهبي", "بلاتيني", "arsenal"],
    answer:
      "هيكل العمولات والمستويات (Silver / Gold / Platinum) موضّح في أداة الأرسنال داخل الموقع. الأرقام النهائية تُثبَّت في عقد الشريك المعتمد — اطلب المراجعة القانونية قبل وعد عميل بمبلغ محدد.",
    links: [
      { label: "هيكل التسويق (Markdown)", href: "/dealix-marketing/arsenal" },
      { label: "صفقات المسوّقين", href: "/marketers/deals" },
    ],
  },
  {
    keywords: ["مسوق", "شريك", "تسجيل", "حساب", "ايبان", "آيبان", "بانك", "بنك"],
    answer:
      "من بوابة المسوّقين: عرّف حسابك وبيانات التحويل في «حسابي»، راجع قائمة التحقق وقوالب واتساب، ثم سجّل إحالاتك مع فريق Dealix قبل الإغلاق لضمان الربط.",
    links: [
      { label: "حساب المسوّق", href: "/marketers/account" },
      { label: "فريقي ودعوات", href: "/marketers/team" },
    ],
  },
  {
    keywords: ["عرض", "قطاع", "برزنتيشن", "pdf", "طباعه", "طباعة", "شركه", "شركة"],
    answer:
      "العروض القطاعية جاهزة كصفحات HTML للطباعة أو الإرسال. ابدأ من الملف التعريفي ثم اختر رقم القطاع. نفس الحزمة داخل أرشيف التحميل من مركز الأصول.",
    links: [
      { label: "عروض القطاعات", href: "/dealix-presentations/00-dealix-company-master-ar.html" },
      { label: "بوابة HTML للأصول", href: "/dealix-marketing/index.html" },
    ],
  },
  {
    keywords: ["مستثمر", "استثمار", "استثماري"],
    answer:
      "العرض الاستثماري عام للمشاركة مع المستثمرين المؤهلين. سجّل إحالة المستثمر معنا قبل الاجتماع الختامي لربط المكافأة وفق الاتفاقية.",
    links: [
      { label: "العرض الاستثماري", href: "/investors" },
      { label: "مسار المسوّقين", href: "/marketers" },
    ],
  },
  {
    keywords: ["واتساب", "قوالب", "رساله", "رسالة"],
    answer:
      "قوالب جاهزة للنسخ واللصق في ملف نصي داخل مجلد المسوّقين — عدّل الاسم والقطاع فقط.",
    links: [{ label: "قوالب واتساب", href: "/dealix-marketing/marketers/whatsapp-playbook-ar.txt" }],
  },
  {
    keywords: ["موارد", "تحميل", "حزمه", "حزمة", "zip"],
    answer:
      "مركز الموارد يجمع الروابط الرئيسية؛ حزمة ZIP الكاملة تُحمَّل من بوابة الأصول التسويقية عند توفر الملف بعد المزامنة.",
    links: [
      { label: "مركز الموارد", href: "/resources" },
      { label: "التحميل والأصول", href: "/dealix-marketing/index.html" },
    ],
  },
  {
    keywords: ["لوحه", "لوحة", "داشبورد", "dashboard", "منصه", "منصة"],
    answer:
      "لوحة Dealix (بعد تسجيل الدخول) تجمع المراقبة، الوكلاء، التحصيل، العروض، والسكربتات في مسار واحد. للمسوّق: ركّز على المواد العامة ثم أحِل العميل إلى تجربة منظّمة على المنصة.",
    links: [
      { label: "دليل لوحة التحكم (قراءة)", href: "/dealix-marketing/dashboard-guide" },
      { label: "دخول المنصة", href: "/login?next=%2Fdashboard" },
    ],
  },
  {
    keywords: ["دعم", "مساعده", "مساعدة", "هاتف", "تواصل"],
    answer:
      "للاستفسارات التشغيلية أو تفعيل الشراكة: صفحة المساعدة تجمع الأسئلة الاستراتيجية، ويمكن التواصل عبر القنوات المعتمدة في بوابة الأصول.",
    links: [{ label: "المساعدة والأسئلة", href: "/help" }],
  },
];

const COMPANY: KnowledgeEntry[] = [
  {
    keywords: ["gong", "outreach", "سيلزفورس", "salesforce", "منافس", "مقارنه", "مقارنة"],
    answer:
      "أدوات مثل Gong وOutreach قوية في سوقها — لكن Dealix يُبنى لسياق B2B السعودي: ريال، PDPL، واتساب كقناة، وحوكمة إرسال. راجع قسم «التمييز أمام السوق» في الصفحة الرئيسية ثم صفحة الاستراتيجية للتفاصيل.",
    links: [
      { label: "الصفحة الرئيسية (قسم التمييز)", href: "/#market-moat" },
      { label: "الاستراتيجية", href: "/strategy" },
    ],
  },
  {
    keywords: ["اصدار", "إصدار", "نسخه", "نسخة", "blueprint", "ميزات", "changelog", "تحديث", "roadmap", "خارطه", "خارطة"],
    answer:
      `إصدار المنتج الحالي (Blueprint) هو ${DEALIX_PRODUCT_BLUEPRINT_VERSION}. الميزات المعروضة في الواجهة والـ API تتبع نفس خطة التنفيذ الظاهرة في صفحة الاستراتيجية وليس نصوصاً عامة — للتفاصيل التقنية راجع ملخص الـ API أو لوحة التحكم بعد الدخول.`,
    links: [
      { label: "الاستراتيجية والمراحل", href: "/strategy" },
      { label: "JSON الملخص (BFF)", href: "/api/strategy-summary" },
    ],
  },
  {
    keywords: ["لماذا", "فرق", "ميزه", "ميزة", "قوي", "اقوى", "أقوى", "dealix"],
    answer:
      "Dealix يجمع اكتشافاً وتأهيلاً وقنوات متعددة وحوكمة قبل الإرسال الحساس وذاكرة صفقة — أي ليس «شات عام» بل نظام تشغيل إيرادات B2B مُهندَس للسياق السعودي (عربي، عملة محلية، قنوات واقعية).",
    links: [
      { label: "الصفحة الرئيسية", href: "/" },
      { label: "الاستراتيجية", href: "/strategy" },
    ],
  },
  {
    keywords: ["داشبورد", "dashboard", "لوحه", "لوحة", "ماذا", "ايش", "ايش في"],
    answer:
      "لوحة التحكم تعرض نظرة أداء، مسار صفقات، توليد عملاء، وكلاء، مالية، عروض قطاعية، سكربتات، واتفاقيات — حسب تفعيل حسابكم. دليل القراءة الكامل متوفر كوثيقة عربية.",
    links: [
      { label: "دليل لوحة التحكم", href: "/dealix-marketing/dashboard-guide" },
      { label: "تسجيل الدخول", href: "/login?next=%2Fdashboard" },
    ],
  },
  {
    keywords: ["وكلاء", "agents", "ذكاء", "ai", "بوت"],
    answer:
      "طبقات وكلاء تغطي مسارات مختلفة (تأهيل، إغلاق، دعم، إلخ) مع إشراف وحوكمة. التفاصيل التشغيلية تظهر داخل تبويب «الوكلاء الأذكياء» بعد الدخول.",
    links: [{ label: "دخول المنصة", href: "/login?next=%2Fdashboard" }],
  },
  {
    keywords: ["سعر", "تكلفه", "تكلفة", "باقه", "باقة", "اشتراك"],
    answer:
      "التسعير يُعرض في العروض والصفحة العامة كمرجع؛ الالتزام المالي يُثبَّت في العقد أو العرض الرسمي حسب قطاعكم وحجم التفعيل.",
    links: [
      { label: "الصفحة العامة", href: "/" },
      { label: "الموارد", href: "/resources" },
    ],
  },
  {
    keywords: ["قطاع", "صحه", "صحة", "عقار", "تجزئه", "تجزئة", "مصنع"],
    answer:
      "لدينا عروض HTML لكل قطاع رئيسي في السوق السعودي — تحليل، جداول، ومؤشرات يمكن طباعتها وإرسالها للعميل.",
    links: [{ label: "العروض القطاعية", href: "/dealix-presentations/00-dealix-company-master-ar.html" }],
  },
  {
    keywords: ["امان", "أمان", "خصوصيه", "خصوصية", "حوكمه", "حوكمة"],
    answer:
      "التصميم يفترض عزل بيانات متعدد المستأجرين ومسارات موافقة قبل المحتوى الحساس — التفاصيل القانونية تُدار ضمن عقدكم وسياسات الامتثال لقطاعكم.",
    links: [{ label: "الاستراتيجية والامتثال (نظرة عامة)", href: "/strategy" }],
  },
  {
    keywords: ["تجربه", "تجربة", "pilot", "ديمو", "demo"],
    answer:
      "نمط العمل الشائع: تجربة محدودة النطاق ثم توسيع — نسّق مع فريق Dealix لتحديد نطاق الـ POC والمؤشرات التي تُقاس من يوم واحد.",
    links: [{ label: "التواصل والمساعدة", href: "/help" }],
  },
  {
    keywords: ["مسوق", "شريك", "احاله", "إحالة"],
    answer:
      "برنامج الشركاء يوفّر مواداً عامة ومسار صفقات — للتفاصيل المالية راجع اتفاقية الشريك وليس الوعد الشفهي فقط.",
    links: [{ label: "بوابة المسوّقين", href: "/marketers" }],
  },
];

const PREVIEW: KnowledgeEntry[] = [
  {
    keywords: ["جوله", "جولة", "تجربه", "تجربة", "معاينه", "معاينة", "استكشاف"],
    answer:
      "أنت في وضع جولة: انقر التبويبات في الشريط الجانبي لرؤية نماذج لوحة التحكم — القيادة، الوكلاء، المالية، العروض، والسكربتات. لا يُحفظ شيء هنا؛ للبيانات الحقيقية أنشئ حساباً.",
    links: [
      { label: "إنشاء حساب", href: "/register?next=%2Fdashboard" },
      { label: "تسجيل الدخول", href: "/login?next=%2Fdashboard" },
    ],
  },
  {
    keywords: ["تبويب", "tab", "قائمه", "قائمة", "وش", "ايش", "ماذا", "اشوف", "أشوف"],
    answer:
      "كل تبويب يعرض طبقة من المنصة: نظرة عامة، قيمة للشركات، مسار العميل، ذكاء، توليد عملاء، عقار، مسوّقون، وكلاء، تحصيل، تحليلات، معرفة، عروض، سكربتات، اتفاقيات… جرّب التنقل لرؤية النطاق الكامل.",
    links: [{ label: "الصفحة الرئيسية", href: "/" }],
  },
  {
    keywords: ["دفع", "فلوس", "سعر", "اشتراك", "باقه", "باقة", "فاتوره", "فاتورة"],
    answer:
      "الجولة لا تتطلب دفعاً. التسعير والعقود تُناقش مع فريق Dealix حسب قطاعك؛ بعد التسجيل تربط بياناتك ولا تُفرض رسوم قبل اتفاق واضح.",
    links: [
      { label: "إنشاء حساب", href: "/register?next=%2Fdashboard" },
      { label: "المساعدة", href: "/help" },
    ],
  },
  {
    keywords: ["فرق", "بعد", "تسجيل", "حساب", "حقيقي"],
    answer:
      "بعد التسجيل: نفس الشكل لكن مع JWT وبياناتك — ربط CRM، صفقات حقيقية، صلاحيات فريق، وتكاملات. الجولة تشرح الشكل فقط.",
    links: [
      { label: "تسجيل", href: "/register?next=%2Fdashboard" },
      { label: "دليل القراءة", href: "/dealix-marketing/dashboard-guide" },
    ],
  },
];

export function matchLocalKnowledge(
  variant: AssistantVariant,
  rawMessage: string
): { reply: string; links?: { label: string; href: string }[] } {
  const q = normalizeAr(rawMessage);
  if (q.length < 2) {
    return {
      reply:
        variant === "marketer"
          ? "اكتب سؤالك باختصار: عمولات، عروض، واتساب، لوحة التحكم، أو إحالة مستثمر."
          : variant === "preview"
            ? "اسأل عن: التبويبات، الفرق بعد التسجيل، الدفع، أو ما تراه في الجولة. أو اختر سؤالاً سريعاً."
            : "اكتب سؤالك: لوحة التحكم، الأسعار، القطاعات، الأمان، أو التجربة.",
    };
  }

  const pool = variant === "marketer" ? MARKETER : variant === "preview" ? PREVIEW : COMPANY;
  let best: { score: number; entry: KnowledgeEntry } | null = null;

  for (const entry of pool) {
    let score = 0;
    for (const kw of entry.keywords) {
      const nk = normalizeAr(kw);
      if (nk.length >= 2 && q.includes(nk)) score += nk.length;
    }
    if (score > 0 && (!best || score > best.score)) {
      best = { score, entry };
    }
  }

  if (best && best.score >= 3) {
    return { reply: best.entry.answer, links: best.entry.links };
  }

  if (best && best.score > 0) {
    return { reply: best.entry.answer, links: best.entry.links };
  }

  return {
    reply:
      variant === "marketer"
        ? "لم أجد مطابقة دقيقة. جرّب: «عمولات»، «عروض القطاعات»، «واتساب»، أو «لوحة التحكم». يمكنك أيضاً زيارة مركز الموارد أو صفحة المساعدة للأسئلة المطوّلة."
        : variant === "preview"
          ? "لم أجد مطابقة دقيقة. جرّب: «التبويبات»، «الجولة»، «الدفع»، أو «بعد التسجيل». يمكنك فتح الصفحة الرئيسية أو إنشاء حساب عندما تكون جاهزاً."
          : "لم أجد مطابقة دقيقة. جرّب: «لماذا Dealix»، «لوحة التحكم»، «الأسعار»، أو «العروض القطاعية». زر صفحة المساعدة للقائمة الكاملة.",
    links:
      variant === "preview"
        ? [
            { label: "الرئيسية", href: "/" },
            { label: "إنشاء حساب", href: "/register?next=%2Fdashboard" },
          ]
        : [
            { label: "المساعدة", href: "/help" },
            { label: "الموارد", href: "/resources" },
          ],
  };
}

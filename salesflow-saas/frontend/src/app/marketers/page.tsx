import Link from "next/link";
import {
  MessageCircle,
  Users,
  TrendingUp,
  Zap,
  Shield,
  Clock,
  CheckCircle,
  ArrowLeft,
  Calendar,
  DollarSign,
  Briefcase,
  HelpCircle,
} from "lucide-react";

export const metadata = {
  title: "Dealix — برنامج شراكة الوكالات والمسوّقين",
  description:
    "حوّل وكالتك إلى ماكينة إيرادات متكررة. أضف خدمة الرد الذكي + تأهيل leads لعملائك — setup fee + MRR شهري.",
};

const packages = [
  {
    name: "الأساسية",
    setupFee: "3,000",
    monthly: "990",
    partnerShare: "30%",
    features: [
      "رد AI بالعربي على واتساب أو فورم",
      "5 أسئلة تأهيل مخصصة",
      "تصنيف leads: حار / دافئ / بارد",
      "تقرير أسبوعي",
    ],
    cta: "ابدأ بأول عميل",
    highlight: false,
  },
  {
    name: "المتقدمة",
    setupFee: "7,000",
    monthly: "2,490",
    partnerShare: "25%",
    features: [
      "كل مميزات الأساسية",
      "حجز مواعيد تلقائي (Calendly)",
      "ربط CRM ثنائي (HubSpot)",
      "متابعة تلقائية Day +2 / +5 / +10",
      "تقرير يومي",
    ],
    cta: "الأنسب للوكالات",
    highlight: true,
  },
  {
    name: "المؤسسية",
    setupFee: "15,000+",
    monthly: "مخصص",
    partnerShare: "20-30%",
    features: [
      "كل مميزات المتقدمة",
      "قنوات متعددة (واتساب + إيميل + صوت)",
      "لوحة تحكم تنفيذية",
      "سير عمل موافقات",
      "مدير حساب مخصص",
    ],
    cta: "تواصل معنا",
    highlight: false,
  },
];

const workflows = [
  {
    icon: TrendingUp,
    title: "وكالة أداء (Performance)",
    desc: "تشغّل حملة → Leads تنزل → Dealix يرد فوراً → العميل يشوف ROI أعلى → يجدد → أنت تحصّل MRR",
  },
  {
    icon: Briefcase,
    title: "مسوّق مستقل (Freelancer)",
    desc: 'تقدم عرض "إدارة حملات + رد ذكي" → Dealix يشتغل بالخلفية → أنت تركز على الاستراتيجية → دخل شهري متكرر',
  },
  {
    icon: Users,
    title: "مستشار CRM / RevOps",
    desc: "تنفذ HubSpot لعميل → تضيف Dealix كطبقة response → CRM يمتلئ بـ leads مؤهلة → العميل يشوف قيمة CRM أسرع",
  },
];

const faqs = [
  {
    q: "كم ياخذ الإعداد لكل عميل؟",
    a: "يوم واحد للأساسية، 3 أيام للمتقدمة.",
  },
  {
    q: "هل أحتاج خبرة تقنية؟",
    a: "لا — نحن نسوي الإعداد والتشغيل بالكامل.",
  },
  {
    q: "كم أقدر أربح من عميل واحد؟",
    a: "عميل واحد = 3,000 setup + ~990/شهر = 14,880 ريال/سنة.",
  },
  {
    q: "هل فيه عقد طويل؟",
    a: "لا — شهري لك ولعميلك. بدون التزام سنوي.",
  },
  {
    q: "ماذا لو العميل ما عجبه؟",
    a: "30 يوم ضمان استرداد كامل.",
  },
  {
    q: "هل يشتغل مع HubSpot / Zoho؟",
    a: "نعم — CRM sync متاح في الباقة المتقدمة.",
  },
  {
    q: "هل يفهم العربي السعودي؟",
    a: "نعم — مبني Arabic-first بلهجة خليجية.",
  },
  {
    q: "كيف أبدأ؟",
    a: "احجز مكالمة شراكة 20 دقيقة → نسوي pilot مجاني لأول عميل عندك.",
  },
];

const CALENDLY = "https://calendly.com/sami-assiri11/dealix-demo";

export default function MarketersPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950 text-slate-100">
      {/* ── Hero ── */}
      <section className="mx-auto max-w-4xl px-6 pb-16 pt-20 text-center">
        <span className="inline-block rounded-full bg-amber-500/10 px-4 py-1.5 text-sm font-medium text-amber-400 ring-1 ring-amber-500/20">
          برنامج شراكة الوكالات والمسوّقين
        </span>
        <h1 className="mt-6 text-4xl font-extrabold leading-tight tracking-tight lg:text-5xl">
          حوّل وكالتك إلى{" "}
          <span className="bg-gradient-to-l from-amber-400 to-amber-600 bg-clip-text text-transparent">
            ماكينة إيرادات متكررة
          </span>
        </h1>
        <p className="mx-auto mt-6 max-w-2xl text-lg leading-relaxed text-slate-300">
          أضف خدمة الرد الذكي + تأهيل leads لعملائك. أنت تحصّل setup fee كامل + نسبة
          شهرية متكررة. نحن نشغّل النظام.
        </p>
        <div className="mt-8 flex flex-wrap justify-center gap-4">
          <a
            href={CALENDLY}
            target="_blank"
            rel="noopener noreferrer"
            className="inline-flex items-center gap-2 rounded-xl bg-amber-500 px-8 py-3.5 text-base font-bold text-slate-900 transition hover:bg-amber-400"
          >
            <Calendar className="h-5 w-5" />
            احجز مكالمة شراكة
          </a>
          <a
            href="#packages"
            className="inline-flex items-center gap-2 rounded-xl border border-white/20 px-8 py-3.5 text-base font-medium transition hover:bg-white/10"
          >
            شوف الباقات
          </a>
        </div>
      </section>

      {/* ── Problem ── */}
      <section className="border-y border-white/10 bg-slate-900/50 py-16">
        <div className="mx-auto max-w-3xl px-6 text-center">
          <h2 className="text-2xl font-bold">المشكلة اللي تعرفها</h2>
          <p className="mt-4 text-lg leading-relaxed text-slate-300">
            عملاءك يصرفون <strong className="text-white">10,000+ ريال/شهر</strong> على
            إعلانات ويجيبون leads. لكن{" "}
            <strong className="text-amber-400">70% تضيع</strong> لأن:
          </p>
          <div className="mt-6 grid gap-4 text-start sm:grid-cols-3">
            {[
              { icon: Clock, text: "ما أحد يرد خلال أول ساعة" },
              { icon: MessageCircle, text: "المتابعة يدوية وعشوائية" },
              { icon: Users, text: "فريق العميل مشغول" },
            ].map((item) => (
              <div
                key={item.text}
                className="flex items-start gap-3 rounded-xl border border-white/10 bg-white/5 p-4"
              >
                <item.icon className="mt-0.5 h-5 w-5 shrink-0 text-red-400" />
                <span className="text-sm text-slate-300">{item.text}</span>
              </div>
            ))}
          </div>
          <p className="mt-6 text-base text-slate-400">
            العميل يلوم الوكالة. الحقيقة: المشكلة مو في الإعلان — المشكلة في الرد.
          </p>
        </div>
      </section>

      {/* ── Solution ── */}
      <section className="py-16">
        <div className="mx-auto max-w-3xl px-6 text-center">
          <h2 className="text-2xl font-bold">
            Dealix يعطيك الحل{" "}
            <span className="text-amber-400">تبيعه لعملائك</span>
          </h2>
          <div className="mt-8 grid gap-6 text-start sm:grid-cols-2">
            {[
              "AI يرد بالعربي خلال 45 ثانية على كل lead",
              "يسأل أسئلة التأهيل (ميزانية؟ جدية؟ موعد؟)",
              "يحجز اجتماع أو يحوّل للمبيعات",
              "يرسل تقرير يومي عن كل lead",
            ].map((text) => (
              <div key={text} className="flex items-start gap-3">
                <CheckCircle className="mt-0.5 h-5 w-5 shrink-0 text-emerald-400" />
                <span className="text-slate-300">{text}</span>
              </div>
            ))}
          </div>
          <p className="mt-8 rounded-xl border border-amber-500/20 bg-amber-500/5 p-4 text-base text-amber-200">
            أنت تبيع الخدمة. نحن نشغّل النظام. تحصّل setup fee + نسبة شهرية.
          </p>
        </div>
      </section>

      {/* ── Workflows ── */}
      <section className="border-y border-white/10 bg-slate-900/50 py-16">
        <div className="mx-auto max-w-4xl px-6">
          <h2 className="text-center text-2xl font-bold">كيف تشتغل حسب نوعك</h2>
          <div className="mt-10 grid gap-6 sm:grid-cols-3">
            {workflows.map((w) => (
              <div
                key={w.title}
                className="rounded-2xl border border-white/10 bg-white/5 p-6"
              >
                <w.icon className="h-8 w-8 text-amber-400" />
                <h3 className="mt-4 text-lg font-semibold">{w.title}</h3>
                <p className="mt-2 text-sm leading-relaxed text-slate-400">{w.desc}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Packages ── */}
      <section id="packages" className="py-16">
        <div className="mx-auto max-w-5xl px-6">
          <h2 className="text-center text-2xl font-bold">
            باقات تبيعها لعملائك
          </h2>
          <p className="mt-2 text-center text-slate-400">
            Setup fee كامل لك + نسبة شهرية متكررة
          </p>
          <div className="mt-10 grid gap-6 lg:grid-cols-3">
            {packages.map((pkg) => (
              <div
                key={pkg.name}
                className={`relative flex flex-col rounded-2xl border p-6 ${
                  pkg.highlight
                    ? "border-amber-500/50 bg-amber-500/5 ring-1 ring-amber-500/20"
                    : "border-white/10 bg-white/5"
                }`}
              >
                {pkg.highlight && (
                  <span className="absolute -top-3 start-4 rounded-full bg-amber-500 px-3 py-0.5 text-xs font-bold text-slate-900">
                    الأكثر طلباً
                  </span>
                )}
                <h3 className="text-xl font-bold">{pkg.name}</h3>
                <div className="mt-3">
                  <span className="text-sm text-slate-400">Setup fee لك:</span>
                  <span className="ms-2 text-2xl font-extrabold text-amber-400">
                    {pkg.setupFee}
                  </span>
                  <span className="text-sm text-slate-400"> ريال</span>
                </div>
                <div className="mt-1">
                  <span className="text-sm text-slate-400">العميل يدفع:</span>
                  <span className="ms-2 font-bold text-white">{pkg.monthly}</span>
                  <span className="text-sm text-slate-400"> ريال/شهر</span>
                </div>
                <div className="mt-1">
                  <span className="text-sm text-slate-400">نصيبك الشهري:</span>
                  <span className="ms-2 font-bold text-emerald-400">
                    {pkg.partnerShare}
                  </span>
                </div>
                <ul className="mt-4 flex-1 space-y-2">
                  {pkg.features.map((f) => (
                    <li key={f} className="flex items-start gap-2 text-sm text-slate-300">
                      <CheckCircle className="mt-0.5 h-4 w-4 shrink-0 text-emerald-500" />
                      {f}
                    </li>
                  ))}
                </ul>
                <a
                  href={CALENDLY}
                  target="_blank"
                  rel="noopener noreferrer"
                  className={`mt-6 block rounded-xl py-3 text-center font-bold transition ${
                    pkg.highlight
                      ? "bg-amber-500 text-slate-900 hover:bg-amber-400"
                      : "border border-white/20 text-white hover:bg-white/10"
                  }`}
                >
                  {pkg.cta}
                </a>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Revenue Calculator ── */}
      <section className="border-y border-white/10 bg-slate-900/50 py-16">
        <div className="mx-auto max-w-3xl px-6 text-center">
          <DollarSign className="mx-auto h-10 w-10 text-amber-400" />
          <h2 className="mt-4 text-2xl font-bold">كم تقدر تربح؟</h2>
          <div className="mt-6 grid gap-4 sm:grid-cols-3">
            <div className="rounded-xl border border-white/10 bg-white/5 p-4">
              <div className="text-3xl font-extrabold text-amber-400">14,880</div>
              <div className="mt-1 text-sm text-slate-400">ريال/سنة من عميل واحد</div>
            </div>
            <div className="rounded-xl border border-white/10 bg-white/5 p-4">
              <div className="text-3xl font-extrabold text-amber-400">74,400</div>
              <div className="mt-1 text-sm text-slate-400">ريال/سنة من 5 عملاء</div>
            </div>
            <div className="rounded-xl border border-white/10 bg-white/5 p-4">
              <div className="text-3xl font-extrabold text-amber-400">223,800</div>
              <div className="mt-1 text-sm text-slate-400">ريال/سنة كشريك نشط</div>
            </div>
          </div>
          <p className="mt-4 text-sm text-slate-500">
            بناءً على: setup 3,000 ريال + 990 ريال/شهر × 30% نصيبك
          </p>
        </div>
      </section>

      {/* ── Trust / Proof ── */}
      <section className="py-16">
        <div className="mx-auto max-w-3xl px-6">
          <div className="grid gap-4 sm:grid-cols-2">
            {[
              { icon: Shield, text: "متوافق مع نظام حماية البيانات (PDPL)" },
              { icon: Zap, text: "مبني للسوق السعودي — عربي أولاً" },
              { icon: Clock, text: "بدون عقد سنوي — شهري" },
              { icon: CheckCircle, text: "ضمان استرداد 30 يوم" },
            ].map((item) => (
              <div
                key={item.text}
                className="flex items-center gap-3 rounded-xl border border-white/10 bg-white/5 p-4"
              >
                <item.icon className="h-5 w-5 shrink-0 text-emerald-400" />
                <span className="text-sm text-slate-300">{item.text}</span>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── FAQ ── */}
      <section className="border-y border-white/10 bg-slate-900/50 py-16">
        <div className="mx-auto max-w-3xl px-6">
          <h2 className="flex items-center justify-center gap-2 text-2xl font-bold">
            <HelpCircle className="h-6 w-6 text-amber-400" />
            أسئلة شائعة
          </h2>
          <div className="mt-8 space-y-4">
            {faqs.map((faq) => (
              <div
                key={faq.q}
                className="rounded-xl border border-white/10 bg-white/5 p-5"
              >
                <h3 className="font-semibold text-white">{faq.q}</h3>
                <p className="mt-2 text-sm text-slate-400">{faq.a}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ── Final CTA ── */}
      <section className="py-20">
        <div className="mx-auto max-w-2xl px-6 text-center">
          <h2 className="text-3xl font-extrabold">
            ابدأ بأول عميل —{" "}
            <span className="text-amber-400">مجاناً</span>
          </h2>
          <p className="mt-4 text-lg text-slate-300">
            نسوي pilot 7 أيام لأول عميل عندك بدون تكلفة.
            <br />
            لو اشتغل — تبدأ تحصّل. لو ما اشتغل — لا التزام.
          </p>
          <div className="mt-8 flex flex-wrap justify-center gap-4">
            <a
              href={CALENDLY}
              target="_blank"
              rel="noopener noreferrer"
              className="inline-flex items-center gap-2 rounded-xl bg-amber-500 px-8 py-4 text-lg font-bold text-slate-900 transition hover:bg-amber-400"
            >
              <Calendar className="h-5 w-5" />
              احجز مكالمة شراكة
            </a>
          </div>
          <p className="mt-4 text-sm text-slate-500">
            20 دقيقة • بدون التزام • نسوي pilot لأول عميل مجاناً
          </p>
        </div>
      </section>

      {/* ── Footer nav ── */}
      <footer className="border-t border-white/10 py-8">
        <div className="mx-auto flex max-w-4xl flex-wrap items-center justify-center gap-6 px-6 text-sm text-slate-500">
          <Link href="/" className="hover:text-teal-400">
            الرئيسية
          </Link>
          <Link href="/resources" className="hover:text-teal-400">
            الموارد
          </Link>
          <Link href="/dashboard" className="hover:text-teal-400">
            المنصة
          </Link>
          <Link href="/privacy" className="hover:text-teal-400">
            الخصوصية
          </Link>
          <Link href="/terms" className="hover:text-teal-400">
            الشروط
          </Link>
          <span>© {new Date().getFullYear()} Dealix</span>
        </div>
      </footer>
    </div>
  );
}

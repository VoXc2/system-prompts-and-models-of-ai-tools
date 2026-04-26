import Link from "next/link";
import { CheckCircle, Calendar, Star, Zap, Building2, Handshake } from "lucide-react";

export const metadata = {
  title: "Dealix — الباقات والأسعار",
  description: "من audit مجاني لـ pilot 499 ريال لـ starter 990/شهر. ابدأ بعميل واحد.",
};

const CALENDLY = "https://calendly.com/sami-assiri11/dealix-demo";

const plans = [
  {
    name: "Speed-to-Lead Audit",
    price: "مجاني",
    period: "",
    desc: "تحليل أين تضيع leads عندك — يفتح الباب",
    features: [
      "تحليل سرعة الرد الحالية",
      "تقييم follow-up",
      "توصية flow بسيط",
      "اقتراح pilot مخصص",
    ],
    cta: "اطلب Audit مجاني",
    highlight: false,
    icon: Zap,
  },
  {
    name: "Pilot",
    price: "499",
    period: "ريال — 7 أيام",
    desc: "أول تجربة حقيقية — ضمان استرداد كامل",
    features: [
      "قناة واحدة (واتساب أو إيميل أو نماذج)",
      "حد 20 lead",
      "رسائل متابعة مخصصة",
      "تصنيف ردود (7 categories)",
      "تقرير نهاية التجربة",
      "ضمان استرداد كامل",
    ],
    cta: "ابدأ Pilot",
    highlight: true,
    icon: Star,
  },
  {
    name: "Starter",
    price: "990",
    period: "ريال/شهر",
    desc: "للشركات الجادة — واتساب + إيميل + تقارير",
    features: [
      "واتساب + إيميل",
      "follow-up sequences",
      "lead tracker",
      "booking CTA",
      "تقرير أسبوعي",
      "بدون عقد سنوي",
    ],
    cta: "اشترك بـ Starter",
    highlight: false,
    icon: Building2,
  },
  {
    name: "Agency Add-on",
    price: "1,499 — 2,999",
    period: "ريال",
    desc: "للوكالات — خدمة جديدة تبيعونها لعملائكم",
    features: [
      "إعداد لعميل واحد",
      "سكريبتات متابعة مخصصة",
      "tracker + تقارير",
      "تدريب بسيط للوكالة",
      "قوالب بيع للعميل",
      "20% MRR + 50% setup fee لكم",
    ],
    cta: "كن شريك وكالة",
    highlight: false,
    icon: Handshake,
  },
];

export default function PricingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-slate-950 via-slate-900 to-slate-950 text-slate-100">
      {/* Hero */}
      <section className="mx-auto max-w-4xl px-6 pb-12 pt-20 text-center">
        <h1 className="text-4xl font-extrabold lg:text-5xl">
          باقات{" "}
          <span className="bg-gradient-to-l from-amber-400 to-amber-600 bg-clip-text text-transparent">
            بسيطة وواضحة
          </span>
        </h1>
        <p className="mx-auto mt-6 max-w-2xl text-lg text-slate-300">
          ابدأ بـ audit مجاني أو pilot بـ 499 ريال. لا عقود طويلة. ضمان استرداد.
        </p>
      </section>

      {/* Plans */}
      <section className="pb-20">
        <div className="mx-auto max-w-5xl px-6">
          <div className="grid gap-6 sm:grid-cols-2 lg:grid-cols-4">
            {plans.map((plan) => (
              <div
                key={plan.name}
                className={`relative flex flex-col rounded-2xl border p-6 ${
                  plan.highlight
                    ? "border-amber-500/50 bg-amber-500/5 ring-1 ring-amber-500/20"
                    : "border-white/10 bg-white/5"
                }`}
              >
                {plan.highlight && (
                  <span className="absolute -top-3 start-4 rounded-full bg-amber-500 px-3 py-0.5 text-xs font-bold text-slate-900">
                    الأكثر طلباً
                  </span>
                )}
                <plan.icon className={`h-7 w-7 ${plan.highlight ? "text-amber-400" : "text-teal-400"}`} />
                <h3 className="mt-3 text-lg font-bold">{plan.name}</h3>
                <div className="mt-2">
                  <span className="text-3xl font-extrabold text-white">{plan.price}</span>
                  {plan.period && <span className="text-sm text-slate-400"> {plan.period}</span>}
                </div>
                <p className="mt-2 text-sm text-slate-400">{plan.desc}</p>
                <ul className="mt-4 flex-1 space-y-2">
                  {plan.features.map((f) => (
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
                    plan.highlight
                      ? "bg-amber-500 text-slate-900 hover:bg-amber-400"
                      : "border border-white/20 text-white hover:bg-white/10"
                  }`}
                >
                  {plan.cta}
                </a>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Bank Transfer */}
      <section className="border-y border-white/10 bg-slate-900/50 py-12">
        <div className="mx-auto max-w-2xl px-6 text-center">
          <h2 className="text-xl font-bold">الدفع عبر تحويل بنكي</h2>
          <div className="mt-4 rounded-xl border border-white/10 bg-white/5 p-6 text-start" dir="rtl">
            <p className="text-sm text-slate-300">البنك: <strong className="text-white">مصرف الإنماء</strong></p>
            <p className="mt-1 text-sm text-slate-300">الاسم: <strong className="text-white">سامي محمد زايد عسيري — ذكاء الاعمال</strong></p>
            <p className="mt-1 text-sm text-slate-300">IBAN: <strong className="text-white font-mono" dir="ltr">SA3305000068207328877000</strong></p>
          </div>
          <p className="mt-4 text-sm text-slate-500">بعد التحويل أرسل الإيصال ونفعّل النظام خلال 24 ساعة</p>
          <p className="mt-2 text-sm text-slate-400">أي سؤال: <a href="tel:+966597788539" className="text-amber-400 hover:text-amber-300" dir="ltr">0597788539</a></p>
        </div>
      </section>

      {/* Footer */}
      <footer className="border-t border-white/10 py-8">
        <div className="mx-auto flex max-w-4xl flex-wrap items-center justify-center gap-6 px-6 text-sm text-slate-500">
          <Link href="/" className="hover:text-teal-400">الرئيسية</Link>
          <Link href="/marketers" className="hover:text-teal-400">المسوّقين</Link>
          <Link href="/partners" className="hover:text-teal-400">الشراكات</Link>
          <Link href="/use-cases" className="hover:text-teal-400">حالات الاستخدام</Link>
          <Link href="/trust" className="hover:text-teal-400">الأمان</Link>
          <span>© {new Date().getFullYear()} Dealix</span>
        </div>
      </footer>
    </div>
  );
}
